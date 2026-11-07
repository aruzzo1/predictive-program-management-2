"""RAG_RANKING_V2_1 benchmark: the same 13 questions through every retrieval strategy.

No LLM, no automatic relevance grading, no store changes. Writes, per strategy,
outputs/evaluation/rag_<strategy>_v2_1.json/.md, plus outputs/evaluation/rag_ranking_v2_1_diagnostics.json
with (a) where known passages rank under each strategy and (b) the Q13 temporal demonstration.

The "known passage" sets are located with simple text patterns. They are reporting diagnostics only
and are never used by any retrieval strategy.

Usage:
    python scripts/run_retrieval_benchmark.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.retrieval.strategies import POOL_SIZE, RERANKER_MODEL, RRF_K, RetrievalBench

QUESTIONS = PROJECT_ROOT / "data" / "metadata" / "rag_evaluation_questions.json"
OUT = PROJECT_ROOT / "outputs" / "evaluation"
V2_RESULTS = OUT / "rag_expanded_v2.json"
RUNS = {"semantic": "SEMANTIC_V2", "bm25": "BM25_V2_1", "hybrid": "HYBRID_V2_1", "hybrid_reranked": "HYBRID_RERANKED_V2_1"}
FILES = {"semantic": "rag_semantic_v2_1", "bm25": "rag_bm25_v2_1", "hybrid": "rag_hybrid_v2_1", "hybrid_reranked": "rag_hybrid_reranked_v2_1"}
ANALYSIS_DATE = "2011-12-31"
JUDGMENTS = ["RELEVANT", "PARTIALLY_RELEVANT", "NOT_RELEVANT", "NEEDS_REVIEW"]

# Diagnostic passage sets (reporting only): question -> {label: pattern over chunk text}
DIAGNOSTICS = {
    "Q02": {"kpp": r"key performance parameter|\bKPPs?\b"},
    "Q07": {"explicit_weight_redesign": r"single largest factor causing", "weight_fragment": r"\bweight\b"},
    "Q08": {"concurrency": r"\bconcurren(cy|t|tly)\b"},
    "Q12": {"retrofit": r"\bretrofit"},
}


def excerpt(text, n=400):
    flat = " ".join(text.split())
    return flat if len(flat) <= n else flat[:n].rsplit(" ", 1)[0] + " ..."


def record(r):
    keys = ("rank", "original_rank", "chunk_id", "document_id", "organization", "pdf_page", "printed_page", "section_type",
            "temporal_status", "semantic_similarity", "dense_rank", "bm25_score", "bm25_rank", "rrf_score", "rerank_score",
            "strategy_score")
    out = {k: r.get(k) for k in keys}
    out.update(publication_date=r["metadata"].get("publication_date"), publication_year=r["metadata"].get("publication_year"),
               excerpt=excerpt(r["text"]), text=r["text"], human_judgment=None, reviewer_notes="")
    return out


def summarize(questions, bench):
    results = [r for q in questions for r in q["results"]]
    store = Counter(m["document_id"] for m in bench.metas)
    got = Counter(r["document_id"] for r in results)
    appear = Counter(r["chunk_id"] for r in results)
    q_by_chunk = {cid: [q["question_id"] for q in questions if any(r["chunk_id"] == cid for r in q["results"])] for cid in appear}
    return {
        "mean_distinct_documents_per_question": round(sum(q["metrics"]["distinct_documents"] for q in questions) / len(questions), 2),
        "total_duplicate_suppression_events": sum(q["metrics"]["duplicate_suppression_events"] for q in questions),
        "highlights_results": sum(r["section_type"] == "highlights" for r in results),
        "agency_comments_results": sum(r["section_type"] == "agency_comments" for r in results),
        "source_concentration": {d: {"results": got.get(d, 0), "share_of_results": round(got.get(d, 0) / len(results), 3),
                                     "chunks_in_store": n, "share_of_store": round(n / len(bench.ids), 3),
                                     "rank1_questions": sum(q["results"][0]["document_id"] == d for q in questions)}
                                 for d, n in sorted(store.items())},
        "hub_chunks_3plus": {cid: {"appearances": n, "questions": q_by_chunk[cid]} for cid, n in appear.most_common() if n >= 3},
    }


def write_md(report, path):
    cfg = report["configuration"]
    L = [f"# Retrieval benchmark: {report['name']}", "",
         f"- Strategy: `{cfg['strategy']}`. {cfg['description']}",
         f"- Store: {cfg['store_chunk_count']} chunks, {cfg['corpus']}; questions: `{cfg['questions_file']}` (unedited)",
         f"- Run: {report['run_timestamp']}. No LLM; relevance judgments left blank.",
         "- Scores: *strategy score* is this strategy's own score (similarity, BM25, RRF or cross-encoder logit) and is **not comparable "
         "across strategies**. *sem* is the dense cosine similarity and *dense/bm25* are whole-store ranks, given for every result.", ""]
    if "reproduces_rag_expanded_v2" in cfg:
        L += [f"- Reproduces RAG_EXPANDED_V2 top-5 chunk IDs for all 13 questions: **{cfg['reproduces_rag_expanded_v2']}**", ""]
    s = report["summary"]
    L += [f"Mean distinct documents per question {s['mean_distinct_documents_per_question']}; duplicate suppressions "
          f"{s['total_duplicate_suppression_events']}; Highlights results {s['highlights_results']}; agency_comments results {s['agency_comments_results']}.", ""]
    for q in report["questions"]:
        L += [f"## {q['question_id']}: {q['category']}", "", q["question"], "",
              "| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |", "|---|---|---|---|---|---|---|---|---|---|"]
        for r in q["results"]:
            L.append(f"| {r['rank']} | {r['document_id']} ({r['publication_year'] or '?'}) | {r['pdf_page']} | `{r['chunk_id']}` | "
                     f"{r['strategy_score'] if r['strategy_score'] is not None else r['semantic_similarity']} | {r['semantic_similarity']} | "
                     f"{r['dense_rank']} | {r['bm25_rank'] or '-'} | {r['excerpt'][:260].replace('|', '/')} |  |")
        L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


def main():
    qset = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    bench = RetrievalBench()
    v2 = {q["question_id"]: [r["chunk_id"] for r in q["results"]] for q in json.loads(V2_RESULTS.read_text(encoding="utf-8"))["questions"]}
    descriptions = {
        "semantic": "Existing dense retrieval (Chroma cosine, candidate_k 15, near-duplicate suppression), unchanged.",
        "bm25": "Okapi BM25 (k1 1.5, b 0.75) over the same chunk texts; generic stopwords, no stemming.",
        "hybrid": f"Reciprocal Rank Fusion (k = {RRF_K}) of the top {POOL_SIZE} dense and top {POOL_SIZE} BM25 chunks.",
        "hybrid_reranked": f"Hybrid pool (union of top {POOL_SIZE} dense and BM25) re-scored by {RERANKER_MODEL} (local cross-encoder, max 512 tokens).",
    }
    raw, diagnostics = {}, {"analysis_date": ANALYSIS_DATE, "known_passages": {}, "temporal_q13": {}}
    for strategy, name in RUNS.items():
        questions = []
        raw[strategy] = {}
        for q in qset["questions"]:
            out = bench.run(strategy, q["question"])
            raw[strategy][q["question_id"]] = out
            res = [record(r) for r in out["results"]]
            questions.append({**q, "results": res, "suppressed_duplicates": [
                {k: s[k] for k in ("chunk_id", "original_rank", "duplicate_of", "shared_word_run")} for s in out["suppressed"]],
                "metrics": {"results_returned": len(res), "distinct_documents": len({r["document_id"] for r in res}),
                            "duplicate_suppression_events": len(out["suppressed"]), "candidate_pool_size": out["pool_size"]},
                "question_level_human_judgment": None})
        cfg = {"strategy": strategy, "description": descriptions[strategy], "store_chunk_count": len(bench.ids),
               "corpus": "RAG_EXPANDED_V2 (10 documents; frozen, see data/metadata/rag_expanded_v2_freeze.json)",
               "questions_file": "data/metadata/rag_evaluation_questions.json", "question_set_version": qset["version"],
               "embedding_model": bench.settings.embedding_model, "top_k": bench.settings.top_k,
               "dedup_min_shared_words": bench.settings.dedup_min_shared_words}
        if strategy == "semantic":
            cfg["reproduces_rag_expanded_v2"] = all([r["chunk_id"] for r in q["results"]] == v2[q["question_id"]] for q in questions)
        report = {"name": name, "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"), "configuration": cfg,
                  "judgment_values": JUDGMENTS, "summary": summarize(questions, bench), "questions": questions}
        (OUT / f"{FILES[strategy]}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        write_md(report, OUT / f"{FILES[strategy]}.md")
        print(f"{name}: written ({'reproduces V2' if cfg.get('reproduces_rag_expanded_v2') else 'n/a' if strategy != 'semantic' else 'DOES NOT reproduce V2'})")

    # (a) known passages: where they rank under each strategy
    qtext = {q["question_id"]: q["question"] for q in qset["questions"]}
    for qid, sets in DIAGNOSTICS.items():
        diagnostics["known_passages"][qid] = {}
        for label, pattern in sets.items():
            cids = [cid for cid, t in zip(bench.ids, bench.texts) if re.search(pattern, t, re.I)]
            located = bench.locate(qtext[qid], cids, {s: raw[s][qid] for s in RUNS})
            diagnostics["known_passages"][qid][label] = {
                "pattern": pattern, "chunks": len(cids),
                "in_top5": {s: sorted((r["rank"], r["chunk_id"]) for r in raw[s][qid]["results"] if r["chunk_id"] in set(cids)) for s in RUNS},
                "best": sorted(({"chunk_id": c, **located[c]} for c in cids), key=lambda d: d["dense_rank"])[:60],
            }

    # (b) Q13 temporal demonstration
    for strategy in RUNS:
        full = raw[strategy]["Q13"]
        dated = bench.run(strategy, qtext["Q13"], analysis_date=ANALYSIS_DATE)
        diagnostics["temporal_q13"][strategy] = {
            "unrestricted": [record(r) for r in full["results"]],
            "analysis_date": ANALYSIS_DATE,
            "restricted": [record(r) for r in dated["results"]],
            "ineligible_count": dated["ineligible_count"],
            "requires_review": sorted(Counter(r["document_id"] for r in dated["requires_review"]).items()),
        }
    (OUT / "rag_ranking_v2_1_diagnostics.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("diagnostics written")


if __name__ == "__main__":
    main()
