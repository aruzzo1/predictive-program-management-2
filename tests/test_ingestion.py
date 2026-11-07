"""Tests for source discovery, duplicate detection, metadata, and chunking."""

from pypdf import PdfWriter

from ppm_agent.ingestion.chunking import chunk_pages
from ppm_agent.ingestion.loaders import deduplicate, discover_documents, load_pdf
from ppm_agent.ingestion.metadata import infer_organization
from ppm_agent.ingestion.page_extraction import ExtractedPage


def write_pdf(path, pages=1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)


# --- source discovery ---------------------------------------------------------


def test_discovery_finds_only_pdfs_and_leaves_files_unchanged(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"%PDF-a")
    (tmp_path / "B.PDF").write_bytes(b"%PDF-b")
    (tmp_path / "notes.txt").write_text("ignore me")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}

    docs = discover_documents(tmp_path)

    assert sorted(d.filename for d in docs) == ["B.PDF", "a.pdf"]
    assert all(len(d.sha256) == 64 for d in docs)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


# --- duplicate detection ------------------------------------------------------


def test_exact_duplicates_are_skipped_and_recorded(tmp_path):
    (tmp_path / "6764.pdf").write_bytes(b"same content")
    (tmp_path / "6764 (1).pdf").write_bytes(b"same content")
    (tmp_path / "other.pdf").write_bytes(b"different content")

    unique, duplicates = deduplicate(discover_documents(tmp_path))

    assert sorted(d.filename for d in unique) == ["6764.pdf", "other.pdf"]
    assert len(duplicates) == 1
    assert duplicates[0].skipped == "6764 (1).pdf"
    assert duplicates[0].duplicate_of == "6764.pdf"
    assert (tmp_path / "6764 (1).pdf").exists()  # never deleted


# --- metadata -----------------------------------------------------------------


def test_organization_inferred_only_when_safe():
    assert infer_organization("GAO-10-382 Joint Strike Fighter.pdf")[0].endswith("(GAO)")
    assert infer_organization("2009DOTEAnnualReport.pdf")[0].endswith("(DOT&E)")
    assert infer_organization("6764.pdf") == (None, None)


def test_load_pdf_preserves_document_metadata(tmp_path):
    write_pdf(tmp_path / "GAO-06-356 test.pdf", pages=2)
    doc = discover_documents(tmp_path)[0]

    loaded = load_pdf(doc)

    assert loaded.num_pages == 2
    assert [p["pdf_page"] for p in loaded.pages] == [1, 2]
    assert loaded.title is None  # blank PDF has no title; nothing is invented


# --- chunking -----------------------------------------------------------------

DOC_META = {
    "document_id": "GAO-10-382",
    "filename": "GAO-10-382 test.pdf",
    "document_hash": "ab" * 32,
    "title": "Joint Strike Fighter: Test Title",
    "organization": "GAO",
    "publication_date": "2010-03-19",
    "source_type": "GAO report",
}


def page(pdf_page, paragraphs, printed_page=None, section_type=None):
    return ExtractedPage(
        document_id="GAO-10-382",
        pdf_page=pdf_page,
        printed_page=printed_page,
        paragraphs=[{"text": t, "section_type": section_type} for t in paragraphs],
    )


def test_long_paragraph_is_split_within_limit_with_overlap():
    sentence = "Mission system software delays reduced the flight test points accomplished in 2009. "
    pages = [page(27, [sentence.strip() + " " + sentence * 30])]  # ~2,600 characters

    chunks = chunk_pages(pages, DOC_META, chunk_size=1200, chunk_overlap=175)

    assert len(chunks) >= 2
    assert all(len(c["text"]) <= 1200 for c in chunks)
    # the second chunk starts with the last whole sentence of the first
    assert chunks[1]["text"].startswith(sentence.strip())


def test_short_paragraphs_are_packed_not_split_per_sentence():
    paras = [f"Paragraph {i} discusses software block {i} and its effect on flight testing." for i in range(5)]

    chunks = chunk_pages([page(10, paras)], DOC_META, chunk_size=1200, chunk_overlap=175)

    assert len(chunks) == 1
    assert chunks[0]["text"].count("\n\n") == 4  # paragraph boundaries preserved inside the chunk


def test_chunks_never_span_pages_or_mix_highlights():
    pages = [
        page(2, ["Highlights summary text about JSF software and test delays."], section_type="highlights"),
        page(5, ["Letter text about the JSF program restructuring and flight testing."], printed_page="1"),
    ]

    chunks = chunk_pages(pages, DOC_META, chunk_size=1200, chunk_overlap=175)

    assert [(c["pdf_page"], c["section_type"]) for c in chunks] == [(2, "highlights"), (5, None)]


def test_token_aware_chunks_respect_target_and_hard_ceiling():
    words = lambda t: len(t.split())  # stand-in tokenizer: one token per word  # noqa: E731
    paras = [f"Paragraph {i} explains how late software blocks delayed mission systems flight testing in that year. " * 3
             for i in range(12)]

    chunks = chunk_pages([page(30, paras)], DOC_META, chunk_size=60, chunk_overlap=10, length_fn=words, max_length=64)

    assert len(chunks) > 1
    assert all(c["token_count"] <= 64 for c in chunks)  # never above the hard ceiling
    assert all(c["token_count"] == words(c["text"]) for c in chunks)


def test_every_chunk_preserves_source_metadata():
    pages = [page(31, ["Software is developed, integrated, and released in five increments."], printed_page="27")]

    chunk = chunk_pages(pages, DOC_META, chunk_size=1200, chunk_overlap=175)[0]

    for key, value in DOC_META.items():
        assert chunk[key] == value
    assert chunk["pdf_page"] == 31
    assert chunk["printed_page"] == "27"
    assert chunk["chunk_id"] == "GAO-10-382-p031-c00"
    assert chunk["extraction_quality"] == "clean"
