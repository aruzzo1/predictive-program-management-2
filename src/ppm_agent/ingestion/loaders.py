"""Source discovery, duplicate detection, and PDF text loading.

The source directory is only ever read. Nothing here writes to, moves, or
deletes source files.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

from ppm_agent.ingestion.metadata import file_sha256, infer_organization, pdf_title

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf"}


@dataclass
class SourceDocument:
    """Basic information about one file in the source corpus."""

    path: Path
    filename: str
    size_bytes: int
    sha256: str


@dataclass
class DuplicateRecord:
    """A file skipped because its content is identical to an already-kept file."""

    skipped: str
    duplicate_of: str
    sha256: str


@dataclass
class LoadedDocument:
    """Text and metadata extracted from one PDF."""

    source: SourceDocument
    title: str | None
    organization: str | None
    organization_basis: str | None
    ingested_at: str
    num_pages: int
    pages: list[dict] = field(default_factory=list)  # [{"pdf_page": 1, "text": "..."}]
    page_errors: list[str] = field(default_factory=list)


# --- Step 1: source discovery ----------------------------------------------------


def discover_documents(source_dir: Path) -> list[SourceDocument]:
    """Find supported files under ``source_dir`` (recursively) and hash each one."""
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    documents = []
    for path in sorted(source_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(
                SourceDocument(
                    path=path,
                    filename=path.name,
                    size_bytes=path.stat().st_size,
                    sha256=file_sha256(path),
                )
            )
    return documents


# --- Step 2: duplicate detection -------------------------------------------------


def deduplicate(documents: list[SourceDocument]) -> tuple[list[SourceDocument], list[DuplicateRecord]]:
    """Keep one file per SHA-256 hash; report the rest as duplicates.

    When several files share a hash, the one with the shortest filename is kept
    (so "6764.pdf" is preferred over "6764 (1).pdf"). Source files are not touched.
    """
    kept: dict[str, SourceDocument] = {}
    duplicates: list[DuplicateRecord] = []

    for doc in sorted(documents, key=lambda d: (len(d.filename), d.filename)):
        original = kept.get(doc.sha256)
        if original is None:
            kept[doc.sha256] = doc
        else:
            duplicates.append(DuplicateRecord(doc.filename, original.filename, doc.sha256))
            logger.info("Duplicate skipped: %r is identical to %r", doc.filename, original.filename)

    unique = sorted(kept.values(), key=lambda d: d.filename)
    return unique, duplicates


# --- Step 3: PDF extraction ------------------------------------------------------


def load_pdf(doc: SourceDocument) -> LoadedDocument:
    """Extract page-level text and metadata from a PDF.

    Raises if the file cannot be opened at all. Individual pages that fail to
    extract are recorded in ``page_errors`` and skipped.
    """
    reader = PdfReader(doc.path)
    organization, basis = infer_organization(doc.filename)
    loaded = LoadedDocument(
        source=doc,
        title=pdf_title(reader),
        organization=organization,
        organization_basis=basis,
        ingested_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        num_pages=len(reader.pages),
    )

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # malformed page: record and keep going
            loaded.page_errors.append(f"page {page_number}: {exc}")
            continue
        loaded.pages.append({"pdf_page": page_number, "text": text})

    return loaded
