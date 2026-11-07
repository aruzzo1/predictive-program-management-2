"""Baseline retrieval evaluation - no LLM, no grading, no store changes.

Runs every question in data/metadata/rag_evaluation_questions.json through the
current retriever (same settings as scripts/run_retrieval.py) and records the
top-k results plus objective retrieval statistics. Human relevance judgments
are left as empty placeholders to be filled in by hand.

Outputs:
    outputs/evaluation/<name>.json   full results (including chunk text)
    outputs/evaluation/<name>.md     human-readable review sheet

Usage:
    python scripts/run_baseline_evaluation.py
    python scripts/run_baseline_evaluation.py --name rag_baseline_5doc
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import datetime, timezone

from ppm_agent.config import PROJECT_ROOT, get_settings
from ppm_agent.retrieval.retriever import retrieve_deduplicated
from ppm_agent.retrieval.vector_store import get_client, get_collection

QUESTIONS_PATH = PROJECT_ROOT / "data" / "metadata" / "rag_evaluation_questions.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "evaluation"
JUDGMENT_VALUES = ["RELEVANT", "PARTIALLY_RELEVANT", "NOT_RELEVANT", "NEEDS_REVIEW"]
EXCERPT_CHARS = 400


def excerpt(text: str, limit: int = EXCERPT_CHARS) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[:limit].rsplit(" ", 1)[0] + " ..."


def evaluate_question(q: dict, top_k: int, collection) -> dict:
    out = retrieve_deduplicated(q["question"], top_k=top_k, collection=collection)
    results = out["results"]
    sims = [r["similarity"] for r in results]
    docs = Counter(r["document_id"] for r in results)
    return {
        **q,
        "metrics": {
            "results_returned": len(results),
            "distinct_documents": len(docs),
            "documents": dict(docs),
            "duplicate_suppression_events": len(out["suppressed"]),
            "candidates_considered": out["candidates_considered"],
            "top_similarity": max(sims) if sims else None,
            "mean_top_k_similarity": round(statistics.mean(sims), 4) if sims else None,
            "min_top_k_similarity": min(sims) if sims else None,
            "highlights_chunks": sum(1 for r in results if r["section_type"] == "highlights"),
        },
        "results": [
            {
                "rank": r["rank"],
                "original_rank": r["original_rank"],
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "organization": r["organization"],
                "publication_date": r["metadata"].get("publication_date"),
                "publication_year": r["metadata"].get("publication_year"),
                "filename": r["filename"],
                "pdf_page": r["pdf_page"],
                "printed_page": r["printed_page"],
                "section_type": r["section_type"],
                "extraction_quality": r["metadata"].get("extraction_quality"),
                "similarity": r["similarity"],
                "distance": r["distance"],
                "excerpt": excerpt(r["text"]),
                "text": r["text"],
                "human_judgment": None,  # one of JUDGMENT_VALUES, filled in by a reviewer
                "reviewer_notes": "",
            }
            for r in results
        ],
        "suppressed_duplicates": [
            {k: s[k] for k in ("chunk_id", "original_rank", "similarity", "duplicate_of", "shared_word_run")}
            for s in out["suppressed"]
        ],
        "question_level_human_judgment": None,  # does the top-k contain usable evidence? (JUDGMENT_VALUES)
        "question_level_reviewer_notes": "",
    }


def summarize(evaluated: list[dict], store_docs: Counter) -> dict:
    all_results = [r for q in evaluated for r in q["results"]]
    result_docs = Counter(r["document_id"] for r in all_results)
    total_results, total_chunks = len(all_results), sum(store_docs.values())
    return {
        "questions": len(evaluated),
        "categories": dict(Counter(q["category"] for q in evaluated)),
        "total_results": total_results,
        "mean_top_similarity": round(statistics.mean(q["metrics"]["top_similarity"] for q in evaluated), 4),
        "mean_of_mean_top_k_similarity": round(statistics.mean(q["metrics"]["mean_top_k_similarity"] for q in evaluated), 4),
        "total_duplicate_suppression_events": sum(q["metrics"]["duplicate_suppression_events"] for q in evaluated),
        "mean_distinct_documents_per_question": round(statistics.mean(q["metrics"]["distinct_documents"] for q in evaluated), 2),
        "source_concentration": {
            doc: {
                "results": result_docs.get(doc, 0),
                "share_of_results": round(result_docs.get(doc, 0) / total_results, 3),
                "chunks_in_store": n,
                "share_of_store": round(n / total_chunks, 3),
                "representation_ratio": round((result_docs.get(doc, 0) / total_results) / (n / total_chunks), 2),
                "questions_with_rank1_from_doc": sum(1 for q in evaluated if q["results"] and q["results"][0]["document_id"] == doc),
            }
            for doc, n in sorted(store_docs.items())
        },
        "repeated_chunks": {cid: n for cid, n in Counter(r["chunk_id"] for r in all_results).most_common() if n > 1},
    }


def write_markdown(report: dict, path) -> None:
    s, cfg = report["summary"], report["configuration"]
    lines = [
        f"# RAG Baseline Evaluation: {report['name']}",
        "",
        f"- Run: {report['run_timestamp']}",
        f"- Stage: {report['stage']}",
        f"- Store: `{cfg['vector_store_dir']}`, collection `{cfg['collection']}`, {cfg['store_chunk_count']} chunks, "
        f"{len(cfg['store_documents'])} documents (ingested {cfg['ingested_at']})",
        f"- Retrieval: {cfg['embedding_model']}, top_k={cfg['top_k']}, candidate_k={cfg['candidate_k']}, "
        f"chunks {cfg['chunk_size']}/{cfg['chunk_overlap']} tokens, dedup >= {cfg['dedup_min_shared_words']} shared words",
        f"- Questions: `{cfg['questions_file']}` ({s['questions']} questions)",
        "",
        "Similarity is cosine similarity (1 - Chroma cosine distance). It measures closeness of embeddings, "
        "**not** relevance. All relevance judgments below are left blank for human review.",
        "",
        f"Judgment values: {', '.join('`' + v + '`' for v in JUDGMENT_VALUES)}",
        "",
        "## Objective summary",
        "",
        "| ID | Category | Expected | Top sim. | Mean top-5 | Docs | Suppressed | Rank-1 document |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for q in report["questions"]:
        m = q["metrics"]
        top_doc = q["results"][0]["document_id"] if q["results"] else "-"
        lines.append(f"| {q['question_id']} | {q['category']} | {q['current_corpus_answer_expected']} | {m['top_similarity']:.4f} | "
                     f"{m['mean_top_k_similarity']:.4f} | {m['distinct_documents']} | {m['duplicate_suppression_events']} | {top_doc} |")
    lines += [
        "",
        f"Mean top similarity {s['mean_top_similarity']:.4f}; mean of mean top-5 similarity {s['mean_of_mean_top_k_similarity']:.4f}; "
        f"mean distinct documents per question {s['mean_distinct_documents_per_question']}; "
        f"duplicate suppression events {s['total_duplicate_suppression_events']}.",
        "",
        "## Source concentration across all results",
        "",
        "| Document | Results | Share of results | Chunks in store | Share of store | Representation ratio | Rank-1 count |",
        "|---|---|---|---|---|---|---|",
    ]
    for doc, c in s["source_concentration"].items():
        lines.append(f"| {doc} | {c['results']} | {c['share_of_results']:.1%} | {c['chunks_in_store']} | {c['share_of_store']:.1%} | "
                     f"{c['representation_ratio']:.2f} | {c['questions_with_rank1_from_doc']} |")
    lines += ["", "Representation ratio = share of results / share of store (1.00 = proportional)."]
    if s["repeated_chunks"]:
        lines += ["", "Chunks returned for more than one question: "
                  + ", ".join(f"`{cid}` ({n}x)" for cid, n in s["repeated_chunks"].items())]
    lines += ["", "## Results by question", ""]
    for q in report["questions"]:
        m = q["metrics"]
        lines += [
            f"### {q['question_id']}: {q['category']}",
            "",
            f"**Question:** {q['question']}",
            "",
            f"- Why it matters: {q['why_it_matters']}",
            f"- Expected evidence type: {q['expected_evidence_type']}",
            f"- Prior expectation for current corpus: **{q['current_corpus_answer_expected']}** ({q['expectation_basis']})",
            f"- Results {m['results_returned']}, distinct documents {m['distinct_documents']} {m['documents']}, "
            f"suppressed {m['duplicate_suppression_events']} (of {m['candidates_considered']} candidates), "
            f"top {m['top_similarity']:.4f}, mean {m['mean_top_k_similarity']:.4f}",
            "",
        ]
        for r in q["results"]:
            printed = r["printed_page"] or "n/a"
            lines += [
                f"**#{r['rank']}** `{r['chunk_id']}` | {r['document_id']} | PDF p. {r['pdf_page']} (printed {printed}) | "
                f"similarity {r['similarity']:.4f} | original rank {r['original_rank']}"
                + (f" | section {r['section_type']}" if r["section_type"] else ""),
                "",
                f"> {r['excerpt']}",
                "",
                "Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:",
                "",
            ]
        for sup in q["suppressed_duplicates"]:
            lines.append(f"- Suppressed `{sup['chunk_id']}` (original rank {sup['original_rank']}, similarity {sup['similarity']:.4f}): "
                         f"duplicate of `{sup['duplicate_of']}`, {sup['shared_word_run']} shared words")
        lines += [
            "",
            "**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:",
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", default="rag_baseline_5doc", help="output file stem")
    parser.add_argument("--ingestion-report", default="data/metadata/prototype_ingestion_report.json",
                        help="ingestion report of the store being evaluated")
    args = parser.parse_args()

    settings = get_settings()
    question_set = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    if not (settings.vector_store_dir / "chroma.sqlite3").is_file():
        raise SystemExit("Vector store not found. Run scripts/ingest_corpus.py first.")
    collection = get_collection(get_client(settings.vector_store_dir), settings.collection_name)
    store_docs = Counter(m["document_id"] for m in collection.get(include=["metadatas"])["metadatas"])
    ingestion = json.loads((PROJECT_ROOT / args.ingestion_report).read_text(encoding="utf-8"))
    if ingestion["total_chunks"] != collection.count():
        raise SystemExit(f"{args.ingestion_report} describes {ingestion['total_chunks']} chunks but the store has "
                         f"{collection.count()}: wrong report for this store")

    evaluated = [evaluate_question(q, settings.top_k, collection) for q in question_set["questions"]]
    report = {
        "name": args.name,
        "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stage": "baseline semantic retrieval only (no LLM, no automatic grading)",
        "judgment_values": JUDGMENT_VALUES,
        "configuration": {
            "questions_file": str(QUESTIONS_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "question_set_version": question_set["version"],
            "embedding_model": settings.embedding_model,
            "top_k": settings.top_k,
            "candidate_k": settings.candidate_k,
            "dedup_min_shared_words": settings.dedup_min_shared_words,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "vector_store_dir": str(settings.vector_store_dir.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "collection": settings.collection_name,
            "store_chunk_count": collection.count(),
            "store_documents": dict(sorted(store_docs.items())),
            "ingested_at": ingestion["ingested_at"],
            "corpus_manifest_version": ingestion.get("manifest_version", "prototype_v1"),
            "ingestion_report": args.ingestion_report,
        },
        "summary": summarize(evaluated, store_docs),
        "questions": evaluated,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path, md_path = OUT_DIR / f"{args.name}.json", OUT_DIR / f"{args.name}.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report, md_path)

    s = report["summary"]
    print(f"{s['questions']} questions, {s['total_results']} results, store {collection.count()} chunks")
    for q in evaluated:
        m = q["metrics"]
        print(f"  {q['question_id']} {q['category']:30s} exp={q['current_corpus_answer_expected']:8s} top={m['top_similarity']:.4f} "
              f"mean={m['mean_top_k_similarity']:.4f} docs={m['distinct_documents']} supp={m['duplicate_suppression_events']} {m['documents']}")
    print(f"Saved: {json_path}\n       {md_path}")


if __name__ == "__main__":
    main()
