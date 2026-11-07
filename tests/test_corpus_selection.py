"""Tests for prototype-source filtering, duplicate exclusion, and the DOT&E page range."""

import pytest
from pypdf import PdfWriter

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.ingestion.corpus_selection import (
    load_decisions,
    load_manifest,
    load_manifest_file,
    select_prototype_documents,
)
from ppm_agent.ingestion.metadata import file_sha256

V2_MANIFEST = PROJECT_ROOT / "data" / "metadata" / "expanded_corpus_v2.json"
from ppm_agent.ingestion.corpus_selection import DECISIONS_PATH  # noqa: E402
from ppm_agent.ingestion.page_extraction import extract_document

# The per-file corpus decision records are kept locally and are not distributed with the public repository;
# tests that check the real manifests against them run only where the records exist.
needs_local_corpus_records = pytest.mark.skipif(not DECISIONS_PATH.is_file(),
                                                reason="local-only corpus decision records not present")


def write_pdf(path, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)


def entry(name, sha, **extra):
    return {
        "document_id": name.split(".")[0],
        "filename": name,
        "document_hash": sha,
        "title": "t",
        "organization": "GAO",
        "publication_date": None,
        "source_type": "GAO report",
        "layout": "gao_original",
        **extra,
    }


# --- the real manifest and decisions (no source files needed) ----------------


@needs_local_corpus_records
def test_real_manifest_selects_exactly_the_five_approved_sources():
    manifest = load_manifest()
    decisions = load_decisions()

    ids = [d["document_id"] for d in manifest]
    assert ids == ["GAO-06-356", "GAO-09-303", "GAO-10-382", "GAO-11-325", "DOTE-FY2010-F35"]
    assert all(decisions[d["filename"]] in {"PROTOTYPE_V1", "PROTOTYPE_V1_PAGE_RANGE"} for d in manifest)
    assert len({d["document_hash"] for d in manifest}) == 5  # no duplicate content


def test_real_manifest_uses_canonical_gao_09_303_only():
    names = [d["filename"] for d in load_manifest()]
    assert "GAO-09-303, Joint Strike Fighter_ Accelerating Procurement.pdf" not in names
    assert any(n.startswith("GAO-09-303") and "Financial Risk" in n for n in names)


def test_real_manifest_restricts_dote_to_f35_pages_with_printed_page_map():
    dote = next(d for d in load_manifest() if d["document_id"] == "DOTE-FY2010-F35")
    assert dote["pdf_page_range"] == [29, 34]
    assert dote["printed_page_map"] == {str(p): str(p - 16) for p in range(29, 35)}


@needs_local_corpus_records
def test_expanded_v2_manifest_is_prototype_plus_approved_first_wave():
    manifest = load_manifest_file(V2_MANIFEST)
    decisions = load_decisions()
    docs = manifest["documents"]

    assert manifest["manifest_version"] == "rag_expanded_v2" and manifest["output_stem"] == "expanded_v2"
    assert [d["document_id"] for d in docs[:5]] == [d["document_id"] for d in load_manifest()]  # prototype unchanged
    assert [d["document_id"] for d in docs[5:]] == ["GAO-02-39", "GAO-05-271", "GAO-07-360", "GAO-08-388", "DOTE-FY2024-F35"]
    assert all(decisions[d["filename"]] in set(manifest["allowed_decisions"]) for d in docs)
    assert all(decisions[d["filename"]] == "RAG_EXPANDED_V2" for d in docs[5:])
    assert len({d["document_hash"] for d in docs}) == len(docs)


def test_every_v2_document_has_explicit_temporal_metadata():
    for d in load_manifest_file(V2_MANIFEST)["documents"]:
        assert "publication_date" in d and "publication_year" in d
        if d["publication_date"]:
            assert d["publication_year"] == int(d["publication_date"][:4])
        else:  # undated annual report: no invented date, a review flag and a verified lower bound instead
            assert d["publication_year"] is None
            assert d["publication_date_review_flag"].startswith("REVIEW")
            assert d["reporting_period"] and d["content_not_before"]


def test_temporal_metadata_reaches_every_chunk(tmp_path):
    write_pdf(tmp_path / "a.pdf")
    dated = entry("a.pdf", file_sha256(tmp_path / "a.pdf"), publication_date="2005-03-15")
    doc = select_prototype_documents(tmp_path, [dated], {"a.pdf": "PROTOTYPE_V1"})[0]
    meta = doc.chunk_metadata()
    assert meta["publication_year"] == 2005 and meta["publication_date_uncertain"] is False

    undated = entry("a.pdf", dated["document_hash"], reporting_period="FY2024", content_not_before="2024-11",
                    publication_date_review_flag="REVIEW: not printed")
    meta = select_prototype_documents(tmp_path, [undated], {"a.pdf": "PROTOTYPE_V1"})[0].chunk_metadata()
    assert meta["publication_year"] is None and meta["publication_date_uncertain"] is True
    assert meta["reporting_period"] == "FY2024" and meta["content_not_before"] == "2024-11"


def test_manifest_allowed_decisions_are_enforced(tmp_path):
    write_pdf(tmp_path / "a.pdf")
    e = entry("a.pdf", file_sha256(tmp_path / "a.pdf"))
    with pytest.raises(ValueError, match="RAG_EXPANDED_V2"):
        select_prototype_documents(tmp_path, [e], {"a.pdf": "RAG_EXPANDED_V2"})  # not allowed by default
    assert select_prototype_documents(tmp_path, [e], {"a.pdf": "RAG_EXPANDED_V2"}, allowed_decisions={"RAG_EXPANDED_V2"})


# --- filtering rules on synthetic files -----------------------------------------


def test_excluded_decisions_are_rejected(tmp_path):
    for name, decision in [
        ("BoletinSumarios12.pdf", "EXCLUDED_PENDING_REVIEW"),
        ("restricted_example.pdf", "EXCLUDED_FROM_PROTOTYPE_INFORMATION_HANDLING"),
        ("Ahern-report.pdf", "DEFERRED_NEEDS_OCR"),
        ("GAO-09-303 short.pdf", "EXCLUDED_NEAR_DUPLICATE"),
    ]:
        (tmp_path / name).write_bytes(name.encode())
        manifest = [entry(name, file_sha256(tmp_path / name))]
        with pytest.raises(ValueError, match="only"):
            select_prototype_documents(tmp_path, manifest, {name: decision})


def test_unlisted_file_is_rejected(tmp_path):
    (tmp_path / "x.pdf").write_bytes(b"x")
    with pytest.raises(ValueError):
        select_prototype_documents(tmp_path, [entry("x.pdf", file_sha256(tmp_path / "x.pdf"))], {})


def test_exact_duplicate_content_is_rejected(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"same")
    (tmp_path / "a (1).pdf").write_bytes(b"same")
    sha = file_sha256(tmp_path / "a.pdf")
    manifest = [entry("a.pdf", sha), entry("a (1).pdf", sha)]
    decisions = {"a.pdf": "PROTOTYPE_V1", "a (1).pdf": "PROTOTYPE_V1"}
    with pytest.raises(ValueError, match="duplicate"):
        select_prototype_documents(tmp_path, manifest, decisions)


def test_hash_mismatch_is_rejected(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"content")
    with pytest.raises(ValueError, match="Hash mismatch"):
        select_prototype_documents(tmp_path, [entry("a.pdf", "0" * 64)], {"a.pdf": "PROTOTYPE_V1"})


def test_dote_page_range_limits_extraction_and_maps_printed_pages(tmp_path):
    write_pdf(tmp_path / "dote.pdf", pages=40)
    manifest = [
        entry(
            "dote.pdf",
            file_sha256(tmp_path / "dote.pdf"),
            layout="dote_annual_report",
            pdf_page_range=[29, 34],
            printed_page_method="manual_map",
            printed_page_map={str(p): str(p - 16) for p in range(29, 35)},
        )
    ]
    doc = select_prototype_documents(tmp_path, manifest, {"dote.pdf": "PROTOTYPE_V1_PAGE_RANGE"})[0]

    pages = extract_document(doc)

    assert [p.pdf_page for p in pages] == [29, 30, 31, 32, 33, 34]
    assert [p.printed_page for p in pages] == ["13", "14", "15", "16", "17", "18"]
