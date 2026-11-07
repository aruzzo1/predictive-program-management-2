"""Tests for temporal status, eligibility and date-bounded retrieval (future-information-leakage control)."""

import uuid

import chromadb
import pytest

from ppm_agent.retrieval.retriever import retrieve, retrieve_deduplicated
from ppm_agent.retrieval.temporal import (
    APPROXIMATE,
    ELIGIBLE,
    INELIGIBLE,
    REQUIRES_REVIEW,
    UNDATED,
    VERIFIED,
    temporal_eligibility,
    temporal_status,
)
from ppm_agent.retrieval.vector_store import get_collection, upsert_chunks

DATED_2010 = {"publication_date": "2010-03-19", "publication_year": 2010}
DATED_2024 = {"publication_date": "2024-12-01", "publication_year": 2024}
APPROX_2010 = {"reporting_period": "FY2010", "content_not_before": "2010-11", "publication_date_uncertain": True}
APPROX_2024 = {"reporting_period": "FY2024", "content_not_before": "2024-11", "publication_date_uncertain": True}
UNDATED_META = {"publication_date_uncertain": True}


def test_temporal_status_is_derived_without_inventing_dates():
    assert temporal_status(DATED_2010) == VERIFIED
    assert temporal_status(APPROX_2024) == APPROXIMATE
    assert temporal_status(UNDATED_META) == UNDATED


def test_dated_source_before_and_after_cutoff():
    assert temporal_eligibility(DATED_2010, "2011-12-31") == ELIGIBLE
    assert temporal_eligibility(DATED_2010, "2010-03-19") == ELIGIBLE  # published on the analysis date
    assert temporal_eligibility(DATED_2024, "2011-12-31") == INELIGIBLE


def test_approximate_source_requires_review_and_is_never_promoted_silently():
    assert temporal_eligibility(APPROX_2010, "2011-12-31") == REQUIRES_REVIEW
    assert temporal_eligibility(APPROX_2010, "2011-12-31", approximate_policy="assume_available") == ELIGIBLE
    assert temporal_eligibility(APPROX_2010, "2011-12-31", approximate_policy="exclude") == INELIGIBLE


def test_approximate_source_describing_later_events_is_ineligible_under_every_policy():
    for policy in ("review", "assume_available", "exclude"):
        assert temporal_eligibility(APPROX_2024, "2011-12-31", approximate_policy=policy) == INELIGIBLE
    assert temporal_eligibility(APPROX_2024, "2024-10-31") == INELIGIBLE  # day before the content month
    assert temporal_eligibility(APPROX_2024, "2024-11-01") == REQUIRES_REVIEW


def test_undated_source_requires_review():
    assert temporal_eligibility(UNDATED_META, "2011-12-31") == REQUIRES_REVIEW
    assert temporal_eligibility(UNDATED_META, "2011-12-31", undated_policy="exclude") == INELIGIBLE


def test_unknown_policy_is_rejected():
    with pytest.raises(ValueError):
        temporal_eligibility(APPROX_2010, "2011-12-31", approximate_policy="include")


# --- retrieval integration ---------------------------------------------------------------

def make_chunk(i, meta):
    return {"chunk_id": f"DOC{i}-p001-c00", "text": f"evidence passage number {i}", "document_id": f"DOC{i}",
            "filename": f"doc{i}.pdf", "title": "t", "organization": "GAO", "pdf_page": i + 1, **meta}


CHUNKS = [make_chunk(0, DATED_2024), make_chunk(1, DATED_2010), make_chunk(2, APPROX_2010), make_chunk(3, UNDATED_META)]
VECTORS = [[1.0, 0.0, 0.0], [0.95, 0.05, 0.0], [0.9, 0.1, 0.0], [0.85, 0.15, 0.0]]  # future source ranks first


def collection():
    col = get_collection(chromadb.EphemeralClient(), name=f"test_{uuid.uuid4().hex}")
    upsert_chunks(col, CHUNKS, VECTORS)
    return col


def query_vector(_q):
    return [1.0, 0.0, 0.0]


def test_analysis_date_excludes_future_source_and_reports_review_items():
    out = retrieve_deduplicated("q", top_k=4, collection=collection(), embed_fn=query_vector, analysis_date="2011-12-31")

    assert [r["document_id"] for r in out["results"]] == ["DOC1"]  # only the verified pre-cutoff source
    assert {r["document_id"] for r in out["requires_review"]} == {"DOC2", "DOC3"}
    assert out["ineligible_count"] == 1
    assert all(r["temporal_eligibility"] == REQUIRES_REVIEW for r in out["requires_review"])


def test_explicit_override_admits_approximate_source():
    out = retrieve_deduplicated("q", top_k=4, collection=collection(), embed_fn=query_vector, analysis_date="2011-12-31",
                                approximate_policy="assume_available")
    assert [r["document_id"] for r in out["results"]] == ["DOC1", "DOC2"]


def test_no_analysis_date_is_backwards_compatible():
    col = collection()
    plain = retrieve_deduplicated("q", top_k=4, collection=col, embed_fn=query_vector)
    assert [r["document_id"] for r in plain["results"]] == ["DOC0", "DOC1", "DOC2", "DOC3"]
    assert "requires_review" not in plain and "analysis_date" not in plain
    assert [r["chunk_id"] for r in retrieve("q", top_k=4, collection=col, embed_fn=query_vector)] == \
        [r["chunk_id"] for r in plain["results"]]
