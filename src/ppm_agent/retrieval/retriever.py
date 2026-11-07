"""Semantic retrieval: embed the query, return the top-k nearest chunks.

Simple post-retrieval duplicate suppression: more candidates than top_k are
retrieved, then a candidate is dropped when it is near a higher-ranked result
(same document, same or adjacent PDF page) AND the two share a long run of
identical words (typically the chunk overlap). Ranking is otherwise unchanged:
no reranking and no balancing by organization.
"""

from __future__ import annotations

import re
from datetime import date
from difflib import SequenceMatcher
from typing import Callable

from ppm_agent.config import get_settings
from ppm_agent.retrieval.embeddings import embed_query
from ppm_agent.retrieval.temporal import partition_by_eligibility
from ppm_agent.retrieval.vector_store import get_client, get_collection


def _to_result(rank: int, chunk_id: str, text: str, metadata: dict, distance: float) -> dict:
    return {
        "rank": rank,
        "chunk_id": chunk_id,
        "text": text,
        "document_id": metadata.get("document_id"),
        "title": metadata.get("title"),
        "organization": metadata.get("organization"),
        "filename": metadata.get("filename"),
        "pdf_page": metadata.get("pdf_page"),
        "printed_page": metadata.get("printed_page"),
        "section_type": metadata.get("section_type"),
        "distance": round(float(distance), 4),
        "similarity": round(1.0 - float(distance), 4),
        "metadata": metadata,
    }


def search(query_embedding: list[float], n: int, collection) -> list[dict]:
    """Plain semantic search: the n nearest chunks, best first."""
    response = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )
    return [
        _to_result(rank, cid, text, meta, dist)
        for rank, (cid, text, meta, dist) in enumerate(
            zip(response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]),
            start=1,
        )
    ]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def shared_word_run(a: str, b: str) -> int:
    """Length of the longest run of identical consecutive words in a and b."""
    wa, wb = _words(a), _words(b)
    match = SequenceMatcher(None, wa, wb, autojunk=False).find_longest_match(0, len(wa), 0, len(wb))
    return match.size


def is_near_duplicate(candidate: dict, kept: dict, min_shared_words: int) -> int:
    """Return the shared word run if candidate duplicates kept, else 0."""
    if candidate["document_id"] != kept["document_id"]:
        return 0
    if abs((candidate["pdf_page"] or 0) - (kept["pdf_page"] or 0)) > 1:
        return 0
    run = shared_word_run(candidate["text"], kept["text"])
    return run if run >= min_shared_words else 0


def suppress_near_duplicates(candidates: list[dict], top_k: int, min_shared_words: int) -> tuple[list[dict], list[dict]]:
    """Walk a ranked candidate list and keep up to top_k results that are not near-duplicates of a kept one.

    Shared by every retrieval strategy, so all strategies apply the same duplicate rule.
    """
    kept, suppressed = [], []
    for c in candidates:
        if len(kept) == top_k:
            break
        dup = next(((k, run) for k in kept if (run := is_near_duplicate(c, k, min_shared_words))), None)
        if dup:
            suppressed.append({
                "chunk_id": c["chunk_id"], "original_rank": c["rank"], "similarity": c["similarity"],
                "duplicate_of": dup[0]["chunk_id"], "shared_word_run": dup[1], "text": c["text"],
            })
        else:
            kept.append(c)
    return kept, suppressed


def retrieve_deduplicated(
    query: str,
    top_k: int | None = None,
    collection=None,
    embed_fn: Callable[[str], list[float]] | None = None,
    candidate_k: int | None = None,
    min_shared_words: int | None = None,
    analysis_date: str | date | None = None,
    **temporal_policy,
) -> dict:
    """Retrieve candidates, suppress near-duplicates, return the top_k distinct results.

    Returns {"results": [...], "suppressed": [...], "candidates_considered": n}.
    Each result keeps its original semantic rank as "original_rank".

    With ``analysis_date`` (date-bounded retrieval), only temporally ELIGIBLE chunks are ranked; the
    whole collection is ranked first so eligibility filtering cannot starve the result list. The
    output then also has "requires_review" (never silently included) and "ineligible_count".
    ``temporal_policy`` is passed to ``temporal_eligibility`` (approximate_policy, undated_policy).
    """
    settings = get_settings()
    top_k = top_k or settings.top_k
    candidate_k = max(candidate_k or settings.candidate_k, top_k)
    min_shared_words = min_shared_words or settings.dedup_min_shared_words
    if collection is None:
        collection = get_collection(get_client(settings.vector_store_dir), settings.collection_name)
    if embed_fn is None:
        embed_fn = lambda q: embed_query(q, settings.embedding_model)  # noqa: E731

    query_embedding = embed_fn(query)
    total = collection.count()
    if analysis_date is not None:
        parts = partition_by_eligibility(search(query_embedding, total, collection), analysis_date, **temporal_policy)
        kept, suppressed = suppress_near_duplicates(parts["eligible"], top_k, min_shared_words)
        out = {"results": kept, "suppressed": suppressed, "candidates_considered": total,
               "analysis_date": str(analysis_date), "requires_review": parts["requires_review"],
               "ineligible_count": len(parts["ineligible"])}
    else:
        n = min(candidate_k, total)
        while True:
            kept, suppressed = suppress_near_duplicates(search(query_embedding, n, collection), top_k, min_shared_words)
            if len(kept) == top_k or n >= total:
                break
            n = min(n * 2, total)  # not enough distinct results yet: look further down the ranking
        out = {"results": kept, "suppressed": suppressed, "candidates_considered": n}

    for rank, r in enumerate(kept, start=1):
        r["original_rank"] = r["rank"]
        r["rank"] = rank
    return out


def retrieve(
    query: str,
    top_k: int | None = None,
    collection=None,
    embed_fn: Callable[[str], list[float]] | None = None,
    dedupe: bool = True,
    analysis_date: str | date | None = None,
) -> list[dict]:
    """Return the ``top_k`` chunks most similar to ``query``, best first.

    ``collection`` and ``embed_fn`` default to the project's Chroma store and
    embedding model; tests pass small stand-ins instead. With dedupe=False this
    is plain semantic search.

    Each result: {"rank", "chunk_id", "text", "document_id", "title", "organization",
                  "filename", "pdf_page", "printed_page", "section_type",
                  "distance", "similarity", "metadata"}
    where distance is Chroma's cosine distance and similarity = 1 - distance.
    Fields that were null at ingestion (e.g. printed_page) come back as None.

    With ``analysis_date``, only temporally ELIGIBLE chunks are returned (see
    ``ppm_agent.retrieval.temporal``); use ``retrieve_deduplicated`` to also see the
    REQUIRES_REVIEW chunks.
    """
    if dedupe or analysis_date is not None:
        return retrieve_deduplicated(query, top_k, collection, embed_fn, analysis_date=analysis_date)["results"]
    settings = get_settings()
    top_k = top_k or settings.top_k
    if collection is None:
        collection = get_collection(get_client(settings.vector_store_dir), settings.collection_name)
    if embed_fn is None:
        embed_fn = lambda q: embed_query(q, settings.embedding_model)  # noqa: E731
    return search(embed_fn(query), top_k, collection)
