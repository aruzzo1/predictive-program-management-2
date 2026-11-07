"""Tests for BM25, rank fusion and the retrieval benchmark strategies (toy embeddings, stand-in reranker)."""

import math
import uuid

import chromadb
import pytest

from ppm_agent.retrieval.lexical import BM25Index, tokenize
from ppm_agent.retrieval.retriever import retrieve_deduplicated
from ppm_agent.retrieval.strategies import RRF_K, RetrievalBench, rrf_fuse
from ppm_agent.retrieval.vector_store import get_collection, upsert_chunks

# --- BM25 ---------------------------------------------------------------------------------


def test_tokenize_lowercases_splits_and_drops_generic_stopwords():
    assert tokenize("The F-35 program's concurrency, and THE testing.") == ["f", "35", "program", "s", "concurrency", "testing"]


def test_bm25_ranks_the_explicit_term_first_and_matches_the_formula():
    index = BM25Index(["a", "b", "c"], ["production concurrency risk", "flight testing schedule", "flight testing production"])
    ranked = index.search("concurrency")

    assert [cid for cid, _ in ranked] == ["a"]  # zero-score texts are not returned
    idf = math.log(1 + (3 - 1 + 0.5) / (1 + 0.5))
    norm = 1.5 * (1 - 0.75 + 0.75 * 3 / 3)
    assert ranked[0][1] == pytest.approx(idf * 1 * 2.5 / (1 + norm))


def test_bm25_ties_are_broken_by_id_deterministically():
    index = BM25Index(["z", "m", "a"], ["retrofit cost", "retrofit cost", "retrofit cost"])
    assert [cid for cid, _ in index.search("retrofit")] == ["a", "m", "z"]
    assert index.search("retrofit") == index.search("retrofit")


def test_bm25_stopword_only_query_returns_nothing():
    assert BM25Index(["a"], ["the program"]).search("what is the") == []


# --- rank fusion --------------------------------------------------------------------------


def test_rrf_fuse_sums_reciprocal_ranks_with_fixed_constant():
    fused = dict(rrf_fuse([["a", "b"], ["b", "c"]]))
    assert fused["b"] == pytest.approx(1 / (RRF_K + 2) + 1 / (RRF_K + 1))
    assert fused["a"] == pytest.approx(1 / (RRF_K + 1))
    assert fused["c"] == pytest.approx(1 / (RRF_K + 2))
    assert [d for d, _ in rrf_fuse([["a", "b"], ["b", "c"]])] == ["b", "a", "c"]


# --- benchmark strategies ------------------------------------------------------------------

TEXTS = [
    "mission systems software delays slowed flight testing",            # semantically closest
    "highly concurrent development and production before testing",     # the only lexical match for "concurrent"
    "engine manufacturing problems and late part deliveries",
    "design drawings released after the critical design review",
    "cost estimates grew because of schedule slips",
]
VECTORS = [[1.0, 0.0, 0.0], [0.6, 0.8, 0.0], [0.9, 0.1, 0.4], [0.5, 0.0, 0.86], [0.8, 0.0, 0.6]]
DATES = ["2010-03-19", "2006-03-15", "2008-03-11", "2024-12-01", "2009-03-12"]


def chunk(i):
    return {"chunk_id": f"DOC{i}-p{10 + i:03d}-c00", "text": TEXTS[i], "document_id": f"DOC{i}", "filename": f"d{i}.pdf",
            "title": "t", "organization": "GAO", "pdf_page": 10 + i, "printed_page": str(i + 1),
            "section_type": "highlights" if i == 1 else None, "publication_date": DATES[i], "publication_year": int(DATES[i][:4])}


class FakeReranker:
    """Stand-in cross-encoder: scores by the number of query words in the passage."""

    def predict(self, pairs):
        return [float(sum(w in passage for w in query.split())) for query, passage in pairs]


def bench():
    col = get_collection(chromadb.EphemeralClient(), name=f"test_{uuid.uuid4().hex}")
    upsert_chunks(col, [chunk(i) for i in range(5)], VECTORS)
    return RetrievalBench(col, embed_fn=lambda q: [1.0, 0.0, 0.0], reranker=FakeReranker())


def ids(out):
    return [r["chunk_id"] for r in out["results"]]


def test_semantic_strategy_is_the_existing_retriever():
    b = bench()
    out = b.run("semantic", "concurrent testing", top_k=3)
    assert ids(out) == [r["chunk_id"] for r in retrieve_deduplicated("concurrent testing", 3, b.collection, b.embed_fn)["results"]]


def test_bm25_strategy_surfaces_the_lexical_match_first():
    out = bench().run("bm25", "concurrent production", top_k=3)
    assert ids(out)[0] == "DOC1-p011-c00"
    assert out["results"][0]["bm25_rank"] == 1


def test_hybrid_fuses_both_rankings():
    out = bench().run("hybrid", "concurrent production", top_k=2)
    # DOC1 is first in BM25 and second in dense, DOC0 first in dense: both must lead the fused list
    assert set(ids(out)) == {"DOC0-p010-c00", "DOC1-p011-c00"}
    assert all("rrf_score" in r for r in out["results"])


def test_reranked_hybrid_reorders_the_fused_pool():
    out = bench().run("hybrid_reranked", "concurrent development production", top_k=1)
    assert ids(out) == ["DOC1-p011-c00"]  # the stand-in reranker prefers the passage with the query words
    assert out["results"][0]["rerank_score"] == 3.0  # all three query words occur in the passage


def test_every_strategy_preserves_provenance_and_temporal_metadata():
    b = bench()
    for strategy in ("semantic", "bm25", "hybrid", "hybrid_reranked"):
        for r in b.run(strategy, "concurrent production testing", top_k=5)["results"]:
            i = int(r["document_id"][3:])
            assert (r["pdf_page"], r["printed_page"], r["section_type"]) == (10 + i, str(i + 1), "highlights" if i == 1 else None)
            assert r["metadata"]["publication_date"] == DATES[i] and r["temporal_status"] == "VERIFIED_PUBLICATION_DATE"
            assert "semantic_similarity" in r and "dense_rank" in r


def test_rankings_are_deterministic():
    b = bench()
    for strategy in ("bm25", "hybrid", "hybrid_reranked"):
        assert ids(b.run(strategy, "testing production cost")) == ids(b.run(strategy, "testing production cost"))


def test_every_strategy_excludes_future_sources_with_an_analysis_date():
    b = bench()
    for strategy in ("semantic", "bm25", "hybrid", "hybrid_reranked"):
        out = b.run(strategy, "design drawings review", top_k=5, analysis_date="2011-12-31")
        assert "DOC3-p013-c00" not in ids(out)  # published 2024
        assert out["ineligible_count"] == 1
