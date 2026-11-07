"""Metadata extraction.

Only records metadata that is actually present. If a value cannot be found or
safely inferred, it is left as None rather than guessed.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

# Conservative filename rules for inferring the issuing organization.
# Each rule is (regex applied to the filename, organization). A file that matches
# no rule gets organization=None — we do not guess.
ORGANIZATION_RULES: list[tuple[str, str]] = [
    (r"^GAO-", "U.S. Government Accountability Office (GAO)"),
    (r"^NSIAD-", "U.S. Government Accountability Office (GAO)"),  # GAO NSIAD report numbers
    (r"DOTE", "Director, Operational Test and Evaluation (DOT&E)"),
    (r"^CHRG-", "U.S. Congress (hearing record)"),
    (r"^ANAO_", "Australian National Audit Office (ANAO)"),
    (r"\brand\b", "RAND Corporation"),
]


def file_sha256(path: Path, block_size: int = 1 << 20) -> str:
    """Return the SHA-256 hex digest of a file's bytes (read-only)."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def infer_organization(filename: str) -> tuple[str | None, str | None]:
    """Infer the source organization from the filename.

    Returns (organization, basis) where basis records which rule matched, or
    (None, None) if no rule applies.
    """
    for pattern, organization in ORGANIZATION_RULES:
        if re.search(pattern, filename, flags=re.IGNORECASE):
            return organization, f"filename matches /{pattern}/"
    return None, None


def pdf_title(reader) -> str | None:
    """Return the PDF's embedded /Title, or None if missing or blank."""
    try:
        title = reader.metadata.title if reader.metadata else None
    except Exception:
        return None
    if isinstance(title, str) and title.strip():
        return title.strip()
    return None
