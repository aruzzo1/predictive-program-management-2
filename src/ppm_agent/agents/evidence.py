"""Evidence retrieval for the agents: the existing retrieval API -> structured Evidence objects.

No evidence is ever inserted by hand; every Evidence object comes from a retrieval result and keeps
its provenance (document, organization, pages, chunk id, section, publication date, method, rank).
"""

from __future__ import annotations

from ppm_agent.models import Evidence
from ppm_agent.retrieval.strategies import RetrievalBench

PREFERRED_STRATEGY = "hybrid_reranked"  # HYBRID_RERANKED_V2_1
STRATEGY_NAMES = {"semantic": "SEMANTIC_V2", "bm25": "BM25_V2_1", "hybrid": "HYBRID_V2_1",
                  "hybrid_reranked": "HYBRID_RERANKED_V2_1"}


def results_to_evidence(results: list[dict], strategy: str) -> list[Evidence]:
    """Retrieval results (strategies.RetrievalBench output) -> Evidence objects E1..En in rank order."""
    return [
        Evidence(
            evidence_id=f"E{i}",
            source_document=r["document_id"],
            source_organization=r.get("organization"),
            pdf_page=r["pdf_page"],
            printed_page=r.get("printed_page"),
            chunk_id=r["chunk_id"],
            text=r["text"],
            section_type=r.get("section_type"),
            publication_date=r["metadata"].get("publication_date"),
            retrieval_method=STRATEGY_NAMES.get(strategy, strategy),
            retrieval_rank=r["rank"],
            retrieval_score=r.get("strategy_score", r.get("similarity")),
        )
        for i, r in enumerate(results, start=1)
    ]


def retrieve_evidence(query: str, top_k: int = 5, strategy: str = PREFERRED_STRATEGY, bench: RetrievalBench | None = None,
                      analysis_date=None) -> tuple[list[Evidence], list[str]]:
    """Run the retrieval API; return (evidence, chunk ids exactly as returned by retrieval)."""
    bench = bench or RetrievalBench()
    out = bench.run(strategy, query, top_k=top_k, analysis_date=analysis_date)
    return results_to_evidence(out["results"], strategy), [r["chunk_id"] for r in out["results"]]
