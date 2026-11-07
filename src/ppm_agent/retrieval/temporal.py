"""Temporal availability of evidence, for date-bounded retrieval (future-information-leakage control).

A chunk's temporal status is derived from its stored metadata; no date is invented and an
approximate date is never promoted to a verified one:

  VERIFIED_PUBLICATION_DATE  publication_date is set
  APPROXIMATE_AVAILABILITY   no publication_date, but content_not_before ("YYYY-MM": a dated event in
                             the text, so the document cannot predate that month)
  UNDATED_REQUIRES_REVIEW    neither

Given an analysis_date, eligibility is conservative:

  verified     ELIGIBLE if publication_date <= analysis_date, else INELIGIBLE
  approximate  INELIGIBLE if analysis_date precedes the content_not_before month (it cannot have existed);
               otherwise REQUIRES_REVIEW, unless approximate_policy="assume_available" (ELIGIBLE)
               or "exclude" (INELIGIBLE) is passed explicitly
  undated      REQUIRES_REVIEW, unless undated_policy="exclude" (INELIGIBLE)
"""

from __future__ import annotations

from datetime import date

VERIFIED = "VERIFIED_PUBLICATION_DATE"
APPROXIMATE = "APPROXIMATE_AVAILABILITY"
UNDATED = "UNDATED_REQUIRES_REVIEW"

ELIGIBLE = "ELIGIBLE"
INELIGIBLE = "INELIGIBLE"
REQUIRES_REVIEW = "REQUIRES_REVIEW"

APPROXIMATE_POLICIES = {"review", "assume_available", "exclude"}
UNDATED_POLICIES = {"review", "exclude"}


def to_date(value: str | date) -> date:
    """'2011-12-31' or a date -> date."""
    return value if isinstance(value, date) else date.fromisoformat(value)


def month_start(value: str) -> date:
    """'2024-11' -> date(2024, 11, 1)."""
    year, month = value.split("-")[:2]
    return date(int(year), int(month), 1)


def temporal_status(metadata: dict) -> str:
    if metadata.get("publication_date"):
        return VERIFIED
    if metadata.get("content_not_before"):
        return APPROXIMATE
    return UNDATED


def temporal_eligibility(
    metadata: dict,
    analysis_date: str | date,
    approximate_policy: str = "review",
    undated_policy: str = "review",
) -> str:
    """ELIGIBLE / INELIGIBLE / REQUIRES_REVIEW for evidence as of ``analysis_date``."""
    if approximate_policy not in APPROXIMATE_POLICIES or undated_policy not in UNDATED_POLICIES:
        raise ValueError("unknown temporal policy")
    cutoff = to_date(analysis_date)
    status = temporal_status(metadata)
    if status == VERIFIED:
        return ELIGIBLE if to_date(metadata["publication_date"]) <= cutoff else INELIGIBLE
    if status == APPROXIMATE:
        if cutoff < month_start(metadata["content_not_before"]):
            return INELIGIBLE  # the text describes events after the analysis date
        return {"review": REQUIRES_REVIEW, "assume_available": ELIGIBLE, "exclude": INELIGIBLE}[approximate_policy]
    return REQUIRES_REVIEW if undated_policy == "review" else INELIGIBLE


def partition_by_eligibility(items: list[dict], analysis_date, metadata_key: str = "metadata", **policy) -> dict:
    """Split result-like dicts into {"eligible", "requires_review", "ineligible"}, each item annotated."""
    out = {"eligible": [], "requires_review": [], "ineligible": []}
    for item in items:
        meta = item[metadata_key] if metadata_key else item
        verdict = temporal_eligibility(meta, analysis_date, **policy)
        item["temporal_status"] = temporal_status(meta)
        item["temporal_eligibility"] = verdict
        out[{ELIGIBLE: "eligible", REQUIRES_REVIEW: "requires_review", INELIGIBLE: "ineligible"}[verdict]].append(item)
    return out
