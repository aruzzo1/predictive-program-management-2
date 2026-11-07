"""Tests for the grounding verifier and grounded prompt.

The evidence chunks are produced by the real retriever over a small in-memory
Chroma collection (toy 3-d embeddings), so they carry exactly the production
result schema (pdf_page, printed_page, ...) rather than hand-written dicts.
"""

import uuid

import chromadb

from ppm_agent.agents.retrieval_agent import build_grounded_prompt
from ppm_agent.agents.verifier import verify_grounding
from ppm_agent.retrieval.retriever import retrieve
from ppm_agent.retrieval.vector_store import get_collection, upsert_chunks

SOURCE_CHUNKS = [
    {
        "chunk_id": "GAO-11-325-p012-c00",
        "text": "Delays in mission systems software reduced the flight test points accomplished.",
        "document_id": "GAO-11-325",
        "filename": "GAO-11-325.pdf",
        "title": "Joint Strike Fighter: Restructuring Places Program on Firmer Footing, but Progress Still Lags",
        "organization": "U.S. Government Accountability Office (GAO)",
        "pdf_page": 12,
        "printed_page": None,
        "chunk_index": 0,
    },
    {
        "chunk_id": "DOTE-FY2010-F35-p030-c00",
        "text": "The program completed 410 flight sciences sorties during the year.",
        "document_id": "DOTE-FY2010-F35",
        "filename": "2010DOTEAnnualReport.pdf",
        "title": "DOT&E FY 2010 Annual Report: F-35 Joint Strike Fighter (JSF)",
        "organization": "Director, Operational Test & Evaluation (DOT&E)",
        "pdf_page": 30,
        "printed_page": "14",
        "chunk_index": 0,
    },
]
VECTORS = [[1.0, 0.0, 0.0], [0.8, 0.2, 0.0]]


def retrieved_chunks():
    collection = get_collection(chromadb.EphemeralClient(), name=f"test_{uuid.uuid4().hex}")
    upsert_chunks(collection, SOURCE_CHUNKS, VECTORS)
    return retrieve("anything", top_k=2, collection=collection, embed_fn=lambda _q: [1.0, 0.0, 0.0])


CHUNKS = retrieved_chunks()


def test_chunks_use_production_page_schema():
    assert [c["pdf_page"] for c in CHUNKS] == [12, 30]
    assert "page" not in CHUNKS[0]


def test_prompt_contains_rules_citations_and_dependency():
    prompt = build_grounded_prompt("question?", CHUNKS)
    assert "[GAO-11-325.pdf, p. 12]" in prompt
    assert "[2010DOTEAnnualReport.pdf, p. 30] (printed page 14)" in prompt
    assert "Mission-System Software Maturity → Flight-Test Execution" in prompt
    assert "INSUFFICIENT EVIDENCE" in prompt


def test_retrieval_only_mode_checks_evidence_coverage():
    report = verify_grounding(None, CHUNKS)
    assert report["evidence_coverage"]["ranks_with_both_sides"] == [1]
    assert report["evidence_coverage"]["per_passage"][1]["printed_page"] == "14"
    assert report["citations"] is None


def test_well_grounded_answer_passes():
    answer = (
        "DIRECT EVIDENCE: Software delays reduced flight test points accomplished [GAO-11-325.pdf, p. 12].\n"
        "DEPENDENCY VERDICT: PARTIALLY SUPPORTED"
    )
    report = verify_grounding(answer, CHUNKS)
    assert report["overall"] == "PASS"
    assert report["verdict"] == "PARTIALLY SUPPORTED"


def test_fabricated_citation_and_uncited_causal_claim_are_flagged():
    answer = (
        "Software immaturity caused the program to be cancelled [GAO-99-999.pdf, p. 1]. "
        "This led to a five-year slip.\n"
        "DEPENDENCY VERDICT: SUPPORTED"
    )
    report = verify_grounding(answer, CHUNKS)
    assert report["overall"] == "WARN"
    assert ("GAO-99-999.pdf", 1) in report["citations"]["citations_not_in_retrieved_evidence"]
    assert "This led to a five-year slip." in report["causal_language"]["uncited_causal_sentences"]


def test_evidence_about_only_one_side_fails_coverage():
    one_sided = [CHUNKS[1]]
    report = verify_grounding(None, one_sided)
    assert report["evidence_coverage"]["passed"] is False
