"""Retrieval benchmark API: run the same query through several ranking strategies.

  semantic         existing dense retrieval (retriever.retrieve_deduplicated), unchanged
  bm25             Okapi BM25 over the same chunk texts (ppm_agent.retrieval.lexical)
  hybrid           Reciprocal Rank Fusion of the dense and BM25 rankings
  hybrid_reranked  the hybrid candidate pool re-scored by a local cross-encoder

All strategies rank the same stored chunks, apply the same near-duplicate suppression, and accept
the same optional analysis_date (only temporally ELIGIBLE chunks are ranked). Every result carries,
besides the usual fields, its exact dense similarity/rank and BM25 score/rank over the whole store,
so results from different strategies can be compared on the same footing. Scores of different
strategies (similarity, BM25, RRF, cross-encoder) are not comparable with each other.

Fixed parameters (documented in docs/retrieval_ranking_experiment.md, not tuned on the evaluation):
  RRF_K = 60, POOL_SIZE = 30 per ranking, cross-encoder cross-encoder/ms-marco-MiniLM-L-6-v2.
"""

from __future__ import annotations

from datetime import date

import numpy as np

from ppm_agent.config import get_settings
from ppm_agent.retrieval.embeddings import embed_query
from ppm_agent.retrieval.lexical import BM25Index
from ppm_agent.retrieval.retriever import _to_result, retrieve_deduplicated, suppress_near_duplicates
from ppm_agent.retrieval.temporal import ELIGIBLE, INELIGIBLE, REQUIRES_REVIEW, temporal_eligibility, temporal_status
from ppm_agent.retrieval.vector_store import get_client, get_collection

STRATEGIES = ("semantic", "bm25", "hybrid", "hybrid_reranked")
RRF_K = 60
POOL_SIZE = 30
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def rrf_fuse(rankings: list[list[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion: score(d) = sum over rankings of 1 / (k + rank(d)), rank starting at 1.

    A document absent from a ranking contributes nothing for it. Ties are broken by id.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda p: (-p[1], p[0]))


class RetrievalBench:
    """In-memory view of the Chroma collection (ids, texts, metadata, embeddings) plus a BM25 index."""

    def __init__(self, collection=None, embed_fn=None, reranker=None):
        settings = get_settings()
        self.settings = settings
        self.collection = collection or get_collection(get_client(settings.vector_store_dir), settings.collection_name)
        self.embed_fn = embed_fn or (lambda q: embed_query(q, settings.embedding_model))
        got = self.collection.get(include=["documents", "metadatas", "embeddings"])
        order = sorted(range(len(got["ids"])), key=lambda i: got["ids"][i])  # deterministic order
        self.ids = [got["ids"][i] for i in order]
        self.texts = [got["documents"][i] for i in order]
        self.metas = [got["metadatas"][i] for i in order]
        emb = np.asarray([got["embeddings"][i] for i in order], dtype=float)
        self.embeddings = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        self.index = {cid: i for i, cid in enumerate(self.ids)}
        self.bm25 = BM25Index(self.ids, self.texts)
        self._reranker = reranker

    # --- full rankings (used by strategies and diagnostics) --------------------------------

    def rankings(self, query: str) -> dict:
        """Exact dense similarity and BM25 score for every chunk, with 1-based ranks."""
        q = np.asarray(self.embed_fn(query), dtype=float)
        sims = self.embeddings @ (q / np.linalg.norm(q))
        bm = self.bm25.scores(query)
        dense_order = sorted(range(len(self.ids)), key=lambda i: (-sims[i], self.ids[i]))
        bm_order = sorted((i for i in range(len(self.ids)) if bm[i] > 0), key=lambda i: (-bm[i], self.ids[i]))
        return {
            "sims": sims, "bm25": bm, "dense_order": dense_order, "bm25_order": bm_order,
            "dense_rank": {self.ids[i]: r for r, i in enumerate(dense_order, start=1)},
            "bm25_rank": {self.ids[i]: r for r, i in enumerate(bm_order, start=1)},
        }

    @property
    def reranker(self):
        if self._reranker is None:
            from sentence_transformers import CrossEncoder

            self._reranker = CrossEncoder(RERANKER_MODEL)
        return self._reranker

    def _result(self, i: int, rank: int, ranks: dict, **extra) -> dict:
        sim = float(ranks["sims"][i])
        r = _to_result(rank, self.ids[i], self.texts[i], self.metas[i], 1.0 - sim)
        cid = self.ids[i]
        r.update(semantic_similarity=round(sim, 4), dense_rank=ranks["dense_rank"][cid],
                 bm25_score=round(float(ranks["bm25"][i]), 4), bm25_rank=ranks["bm25_rank"].get(cid),
                 temporal_status=temporal_status(self.metas[i]), **extra)
        return r

    # --- strategies ---------------------------------------------------------------------------

    def run(self, strategy: str, query: str, top_k: int | None = None, analysis_date: str | date | None = None,
            **temporal_policy) -> dict:
        """Top-k distinct results for one strategy.

        Returns {"strategy", "results", "suppressed", "pool_size", and with analysis_date also
        "analysis_date", "requires_review", "ineligible_count"}.
        """
        if strategy not in STRATEGIES:
            raise ValueError(f"unknown strategy {strategy!r}")
        top_k = top_k or self.settings.top_k
        min_shared = self.settings.dedup_min_shared_words
        ranks = self.rankings(query)

        verdict = {}
        if analysis_date is not None:
            verdict = {cid: temporal_eligibility(m, analysis_date, **temporal_policy) for cid, m in zip(self.ids, self.metas)}
        eligible = (lambda i: verdict[self.ids[i]] == ELIGIBLE) if verdict else (lambda i: True)

        if strategy == "semantic":
            out = retrieve_deduplicated(query, top_k, self.collection, self.embed_fn, analysis_date=analysis_date, **temporal_policy)
            for r in out["results"]:
                i = self.index[r["chunk_id"]]
                r.update(semantic_similarity=round(float(ranks["sims"][i]), 4), dense_rank=ranks["dense_rank"][r["chunk_id"]],
                         bm25_score=round(float(ranks["bm25"][i]), 4), bm25_rank=ranks["bm25_rank"].get(r["chunk_id"]),
                         temporal_status=temporal_status(r["metadata"]))
            out["pool_size"] = out.pop("candidates_considered")
            ordered = None
        else:
            dense_pool = [i for i in ranks["dense_order"] if eligible(i)][:POOL_SIZE]
            bm25_pool = [i for i in ranks["bm25_order"] if eligible(i)][:POOL_SIZE]
            if strategy == "bm25":
                ordered = [(i, {"strategy_score": round(float(ranks["bm25"][i]), 4)}) for i in [j for j in ranks["bm25_order"] if eligible(j)]]
                pool = None
            else:
                fused = rrf_fuse([[self.ids[i] for i in dense_pool], [self.ids[i] for i in bm25_pool]])
                pool = [self.index[cid] for cid, _ in fused]
                rrf = dict(fused)
                if strategy == "hybrid":
                    ordered = [(i, {"strategy_score": round(rrf[self.ids[i]], 6), "rrf_score": round(rrf[self.ids[i]], 6)}) for i in pool]
                else:
                    scores = self.reranker.predict([(query, self.texts[i]) for i in pool])
                    order = sorted(range(len(pool)), key=lambda k: (-float(scores[k]), self.ids[pool[k]]))
                    ordered = [(pool[k], {"strategy_score": round(float(scores[k]), 4), "rerank_score": round(float(scores[k]), 4),
                                          "rrf_score": round(rrf[self.ids[pool[k]]], 6)}) for k in order]
            candidates = [self._result(i, rank, ranks, **extra) for rank, (i, extra) in enumerate(ordered, start=1)]
            for c in candidates:
                c["similarity"] = c["semantic_similarity"]  # duplicate records report semantic similarity
            kept, suppressed = suppress_near_duplicates(candidates, top_k, min_shared)
            for rank, r in enumerate(kept, start=1):
                r["original_rank"], r["rank"] = r["rank"], rank
            out = {"results": kept, "suppressed": suppressed,
                   "pool_size": len(ordered) if strategy == "bm25" else len(pool)}
            if analysis_date is not None:
                out.update(analysis_date=str(analysis_date),
                           requires_review=[self._result(i, 0, ranks, temporal_eligibility=REQUIRES_REVIEW)
                                            for i in ranks["dense_order"] if verdict[self.ids[i]] == REQUIRES_REVIEW],
                           ineligible_count=sum(v == INELIGIBLE for v in verdict.values()))
        out["strategy"] = strategy
        # full candidate order before duplicate suppression (None for semantic: use dense_rank)
        out["strategy_order"] = [self.ids[i] for i, _ in ordered] if ordered is not None else None
        return out

    def locate(self, query: str, chunk_ids: list[str], strategy_outputs: dict) -> dict:
        """Diagnostics: where specific chunks rank under each strategy.

        dense_rank / bm25_rank are over the whole store; "<strategy>_order_rank" is the position in that
        strategy's candidate order before duplicate suppression (None = not a candidate); "<strategy>_top_k"
        is the final rank if the chunk is in the returned top_k.
        """
        ranks = self.rankings(query)
        out = {}
        for cid in chunk_ids:
            row = {"dense_rank": ranks["dense_rank"].get(cid), "bm25_rank": ranks["bm25_rank"].get(cid)}
            for name, res in strategy_outputs.items():
                order = res.get("strategy_order")
                if order is not None:
                    row[f"{name}_order_rank"] = order.index(cid) + 1 if cid in order else None
                row[f"{name}_top_k"] = next((r["rank"] for r in res["results"] if r["chunk_id"] == cid), None)
            out[cid] = row
        return out
