"""Corpus selection: decide exactly which files and pages are eligible for indexing.

This runs before any text extraction or chunking. It uses two hand-maintained files:

* a corpus manifest - controlled metadata for each document, e.g.
  data/metadata/prototype_corpus.json (prototype_v1) or data/metadata/expanded_corpus_v2.json
* data/metadata/corpus_decisions.csv   - the per-file decisions from the corpus review

A document is selected only if it is listed in the manifest, its decision is one the
manifest allows (default: the PROTOTYPE_V1 decisions), the file exists, and its SHA-256
matches the manifest. Anything else stops ingestion with an error rather than being
silently skipped.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.ingestion.metadata import file_sha256

MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "prototype_corpus.json"
DECISIONS_PATH = PROJECT_ROOT / "data" / "metadata" / "corpus_decisions.csv"
ALLOWED_DECISIONS = {"PROTOTYPE_V1", "PROTOTYPE_V1_PAGE_RANGE"}


@dataclass
class PrototypeDocument:
    """One selected document plus the controlled metadata copied onto every chunk."""

    document_id: str
    filename: str
    path: Path
    document_hash: str
    title: str
    organization: str
    publication_date: str | None
    publication_date_review_flag: str | None
    source_type: str
    layout: str  # gao_original | gao_accessible_text | dote_annual_report
    pdf_page_range: tuple[int, int] | None  # inclusive; None = all pages
    printed_page_method: str  # footer | manual_map | none
    printed_page_map: dict[int, str]
    # Temporal metadata for future date-bounded retrieval (publication_date <= analysis_date).
    publication_year: int | None = None
    reporting_period: str | None = None  # e.g. "FY2024" for annual reports
    content_not_before: str | None = None  # "YYYY-MM" of a dated event in the text; publication cannot precede it

    def includes_page(self, pdf_page: int) -> bool:
        if self.pdf_page_range is None:
            return True
        first, last = self.pdf_page_range
        return first <= pdf_page <= last

    def chunk_metadata(self) -> dict:
        """Document-level fields stored on every chunk."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "document_hash": self.document_hash,
            "title": self.title,
            "organization": self.organization,
            "publication_date": self.publication_date,
            "publication_year": self.publication_year,
            "publication_date_uncertain": self.publication_date is None or self.publication_date_review_flag is not None,
            "reporting_period": self.reporting_period,
            "content_not_before": self.content_not_before,
            "source_type": self.source_type,
        }


def load_decisions(path: Path = DECISIONS_PATH) -> dict[str, str]:
    """Return {filename: decision} from corpus_decisions.csv."""
    with open(path, newline="", encoding="utf-8") as f:
        return {row["filename"]: row["decision"] for row in csv.DictReader(f)}


def load_manifest_file(path: Path = MANIFEST_PATH) -> dict:
    """The whole manifest: version, output stem, allowed decisions and documents."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_manifest(path: Path = MANIFEST_PATH) -> list[dict]:
    return load_manifest_file(path)["documents"]


def publication_year(entry: dict) -> int | None:
    """Explicit publication_year, else the year of publication_date; None when the date is unknown."""
    if entry.get("publication_year") is not None:
        return int(entry["publication_year"])
    date = entry.get("publication_date")
    return int(date[:4]) if date else None


def select_prototype_documents(
    source_dir: Path,
    manifest: list[dict] | None = None,
    decisions: dict[str, str] | None = None,
    verify_hash: bool = True,
    allowed_decisions: set[str] | None = None,
) -> list[PrototypeDocument]:
    """Validate the manifest against the source folder and the corpus decisions."""
    manifest = load_manifest() if manifest is None else manifest
    decisions = load_decisions() if decisions is None else decisions
    allowed = ALLOWED_DECISIONS if allowed_decisions is None else set(allowed_decisions)

    selected: list[PrototypeDocument] = []
    seen_hashes: dict[str, str] = {}
    for entry in manifest:
        name = entry["filename"]
        decision = decisions.get(name)
        if decision not in allowed:
            raise ValueError(f"{name!r} has decision {decision!r}; only {sorted(allowed)} may be indexed")

        path = Path(source_dir) / name
        if not path.is_file():
            raise FileNotFoundError(f"Prototype source missing: {path}")

        if verify_hash:
            actual = file_sha256(path)
            if actual != entry["document_hash"]:
                raise ValueError(f"Hash mismatch for {name!r}: expected {entry['document_hash'][:12]}…, got {actual[:12]}…")

        if entry["document_hash"] in seen_hashes:
            raise ValueError(f"{name!r} is an exact duplicate of {seen_hashes[entry['document_hash']]!r}")
        seen_hashes[entry["document_hash"]] = name

        page_range = entry.get("pdf_page_range")
        selected.append(
            PrototypeDocument(
                document_id=entry["document_id"],
                filename=name,
                path=path,
                document_hash=entry["document_hash"],
                title=entry["title"],
                organization=entry["organization"],
                publication_date=entry.get("publication_date"),
                publication_date_review_flag=entry.get("publication_date_review_flag"),
                source_type=entry["source_type"],
                layout=entry["layout"],
                pdf_page_range=tuple(page_range) if page_range else None,
                printed_page_method=entry.get("printed_page_method", "none"),
                printed_page_map={int(k): v for k, v in entry.get("printed_page_map", {}).items()},
                publication_year=publication_year(entry),
                reporting_period=entry.get("reporting_period"),
                content_not_before=entry.get("content_not_before"),
            )
        )
    return selected


def select_manifest_documents(source_dir: Path, manifest_path: Path, decisions: dict[str, str] | None = None):
    """Select the documents of a manifest file using the decisions it allows. Returns (manifest, documents)."""
    manifest = load_manifest_file(manifest_path)
    allowed = set(manifest.get("allowed_decisions", ALLOWED_DECISIONS))
    return manifest, select_prototype_documents(source_dir, manifest["documents"], decisions, allowed_decisions=allowed)
