"""Semantic retrieval only - no LLM, no generation, no verifier.

Prints the top-k distinct chunks for a query (after simple near-duplicate
suppression) and saves a timestamped JSON trace to outputs/retrieval_traces/
so retrieval quality can be inspected by hand.

Usage:
    python scripts/run_retrieval.py
    python scripts/run_retrieval.py "your question" --top-k 5
"""

from __future__ import annotations

import argparse
import textwrap
from collections import Counter
from datetime import datetime, timezone

from ppm_agent.config import get_settings
from ppm_agent.retrieval.retriever import retrieve_deduplicated
from ppm_agent.utils.logging_utils import write_retrieval_trace

DEFAULT_QUERY = "What evidence indicates that F-35 software maturity affected flight-test execution?"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", nargs="?", default=DEFAULT_QUERY)
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()

    settings = get_settings()
    top_k = args.top_k or settings.top_k
    out = retrieve_deduplicated(args.query, top_k=top_k)
    results, suppressed = out["results"], out["suppressed"]
    if not results:
        raise SystemExit("No results. Run scripts/ingest_corpus.py first.")

    print("=" * 100)
    print(f"QUERY: {args.query}")
    print(f"top_k={top_k} | model={settings.embedding_model} | chunk_size={settings.chunk_size} tokens | "
          f"overlap={settings.chunk_overlap} tokens | candidates={out['candidates_considered']} | "
          f"dedup: same doc, page +/-1, shared run >= {settings.dedup_min_shared_words} words")
    print("=" * 100)
    for r in results:
        print(f"\n#{r['rank']}  similarity {r['similarity']:.4f}  (cosine distance {r['distance']:.4f})   original rank {r['original_rank']}")
        print(f"    title:        {r['title']}")
        print(f"    organization: {r['organization']}   document_id: {r['document_id']}")
        print(f"    filename:     {r['filename']}")
        print(f"    PDF page:     {r['pdf_page']}   printed page: {r['printed_page'] or 'n/a'}   "
              f"section_type: {r['section_type'] or 'n/a'}   quality: {r['metadata'].get('extraction_quality')}")
        print(f"    chunk ID:     {r['chunk_id']}   ({r['metadata'].get('token_count')} tokens, {len(r['text'])} chars)")
        print("    " + "-" * 92)
        for para in r["text"].split("\n\n"):
            print(textwrap.indent(textwrap.fill(para, width=92), "    | "))

    orgs = Counter(r["organization"] for r in results)
    highlights = sum(1 for r in results if r["section_type"] == "highlights")
    print("\n" + "=" * 100)
    print(f"Suppressed near-duplicates: {len(suppressed)}")
    for s in suppressed:
        print(f"  - {s['chunk_id']} (original rank {s['original_rank']}, similarity {s['similarity']:.4f}) "
              f"duplicates {s['duplicate_of']} - {s['shared_word_run']} consecutive shared words")
    print(f"Organizations in top-{len(results)}: {dict(orgs)}   |   Highlights chunks: {highlights}/{len(results)}")

    trace = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stage": "semantic_retrieval_only (no generation, no verifier)",
        "query": args.query,
        "embedding_model": settings.embedding_model,
        "top_k": top_k,
        "chunk_unit": "tokens (embedding-model tokenizer)",
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "candidate_k": settings.candidate_k,
        "candidates_considered": out["candidates_considered"],
        "dedup_rule": f"same document_id, pdf_page within 1, and >= {settings.dedup_min_shared_words} consecutive shared words",
        "collection": settings.collection_name,
        "results": results,
        "suppressed_duplicates": suppressed,
    }
    path = write_retrieval_trace(trace, settings.traces_dir)
    print(f"Trace saved: {path}")


if __name__ == "__main__":
    main()
