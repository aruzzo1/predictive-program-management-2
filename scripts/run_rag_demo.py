"""Semantic retrieval + grounded answer demo over the JSF corpus.

Usage:
    python scripts/run_rag_demo.py
    python scripts/run_rag_demo.py "your question" --top-k 5

If OPENAI_API_KEY is set in .env, a grounded answer is generated from the
retrieved chunks only. Otherwise the demo runs in retrieval-only mode.
Every run writes a JSON trace to outputs/retrieval_traces/.
"""

from __future__ import annotations

import argparse
import textwrap
from datetime import datetime, timezone

from ppm_agent.agents.retrieval_agent import DEFAULT_DEPENDENCY, answer
from ppm_agent.agents.verifier import verify_grounding
from ppm_agent.config import get_settings
from ppm_agent.retrieval.retriever import retrieve
from ppm_agent.utils.logging_utils import write_retrieval_trace

DEFAULT_QUERY = "What evidence indicates that F-35 software maturity affected flight-test execution?"


def excerpt(text: str, limit: int = 600) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[:limit].rsplit(" ", 1)[0] + " ..."


def print_results(results: list[dict]) -> None:
    for r in results:
        print(f"\n#{r['rank']}  {r['filename']}  |  PDF page {r['pdf_page']}  |  printed page {r['printed_page'] or 'n/a'}")
        print(f"    similarity: {r['similarity']:.4f}   (cosine distance: {r['distance']:.4f})   chunk: {r['chunk_id']}")
        if r["metadata"].get("organization"):
            print(f"    organization: {r['metadata']['organization']}")
        print(textwrap.indent(textwrap.fill(excerpt(r["text"]), width=96), "    | "))


def print_verifier(report: dict) -> None:
    cov = report["evidence_coverage"]
    print(f"Overall: {report['overall']}  —  {report['notes']}")
    print(f"[1] Evidence coverage (passage mentions software AND flight test): "
          f"{'PASS' if cov['passed'] else 'FAIL'}  ranks {cov['ranks_with_both_sides']}")
    for p in cov["per_passage"]:
        print(f"      #{p['rank']}: software terms {p['cause_terms']}  |  flight-test terms {p['effect_terms']}")
    if report["citations"] is not None:
        c = report["citations"]
        print(f"[2] Source metadata / citations: {'PASS' if c['passed'] else 'FAIL'}  "
              f"({c['citations_found']} found, {len(c['citations_not_in_retrieved_evidence'])} not in retrieved set)")
        cl = report["causal_language"]
        print(f"[3] Causal language: {'PASS' if cl['passed'] else 'WARN'}  "
              f"uncited causal sentences: {len(cl['uncited_causal_sentences'])}, "
              f"phrases not in evidence: {cl['causal_phrases_not_in_evidence']}")
        print(f"    Dependency verdict found: {report['verdict']}")
    else:
        print("[2] Citations / [3] causal language: not run (no generated answer)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", nargs="?", default=DEFAULT_QUERY)
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--no-llm", action="store_true", help="force retrieval-only mode")
    args = parser.parse_args()

    settings = get_settings()
    top_k = args.top_k or settings.top_k

    print("=" * 100)
    print(f"QUERY: {args.query}")
    print(f"top_k={top_k}  |  embedding model: {settings.embedding_model}  |  store: {settings.vector_store_dir}")
    print("=" * 100)

    results = retrieve(args.query, top_k=top_k)
    if not results:
        raise SystemExit("No results. Has the corpus been ingested? Run scripts/ingest_corpus.py first.")

    print(f"\nTOP-{len(results)} RETRIEVED CHUNKS (ranked by cosine similarity)")
    print_results(results)

    api_key = None if args.no_llm else settings.openai_api_key
    generation = answer(args.query, results, api_key=api_key, model=settings.openai_model)

    print("\n" + "=" * 100)
    print(f"GROUNDED ANSWER  (mode: {generation['mode']})")
    print("=" * 100)
    if generation["answer"]:
        print(generation["answer"])
    else:
        if generation["error"]:
            print(f"Generation FAILED: {generation['error']}")
        print("Retrieval-only mode: no LLM answer generated (set OPENAI_API_KEY in .env to enable).")
        print("The grounded prompt that would be sent is saved in the trace file.")
        print(f'Candidate dependency to assess: "{DEFAULT_DEPENDENCY}"')

    report = verify_grounding(generation["answer"], results)
    print("\n" + "=" * 100)
    print("GROUNDING VERIFIER")
    print("=" * 100)
    print_verifier(report)

    trace = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": args.query,
        "top_k": top_k,
        "embedding_model": settings.embedding_model,
        "collection": settings.collection_name,
        "candidate_dependency": DEFAULT_DEPENDENCY,
        "results": results,
        "generation": generation,
        "verifier": report,
    }
    path = write_retrieval_trace(trace, settings.traces_dir)
    print(f"\nTrace saved: {path}")


if __name__ == "__main__":
    main()
