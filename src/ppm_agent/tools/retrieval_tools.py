"""Retrieval tools.

Thin, agent-callable wrappers around the retriever. Future deterministic
analysis tools (DSM, WTM, system dynamics) will live alongside this module.
"""

from __future__ import annotations

from ppm_agent.retrieval.retriever import retrieve


def search_corpus(query: str, k: int = 5) -> list[dict]:
    """Search the JSF corpus and return the top-k evidence chunks with citations."""
    return retrieve(query, top_k=k)
