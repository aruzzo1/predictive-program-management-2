"""Tests for the recorded human-review disposition: internal consistency, preservation of the original Module 6 records
and traces, and that rejected episodes cannot be released downstream. No model calls."""

import hashlib
import importlib.util
import json

import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.safety.safety_guardrails import FROZEN_BASELINE_SHA256, PRESERVED_TRACES, check_baseline_integrity

SAFETY_DIR = PROJECT_ROOT / "outputs" / "safety"
ORIGINAL_RECORDS_SHA256 = "674ff76fefea7b2de2bbca902a843b0e9f682c83b5b12c1fba5d462121ac0dd4"


@pytest.fixture(scope="module")
def reviewed():
    return json.loads((SAFETY_DIR / "human_review_records_reviewed.json").read_text(encoding="utf-8"))


def test_reviewed_records_are_internally_consistent(reviewed):
    recs = reviewed["records"]
    assert reviewed["episodes_reviewed"] == len(recs) == 3
    assert [r["trace_path"] for r in recs] == list(PRESERVED_TRACES)
    assert reviewed["decision_tally"] == {"PENDING": 0, "APPROVED_AS_ADVISORY": 0, "REJECTED": 3, "REVISE_AND_RERUN": 0,
                                          "ESCALATED": 0}
    assert [r["original_validator_error_count"] for r in recs] == [6, 5, 17]  # episode 3: 17, not 18
    original = json.loads((SAFETY_DIR / "human_review_records.json").read_text(encoding="utf-8"))
    for r in recs:
        o = original[r["original_record_ref"]["index"]]
        assert (r["trace_id"], r["original_safety_route"]) == (o["trace_id"], o["safety_route"])
        assert r["original_validation_category_counts"] == o["validation_summary"]["failures_by_category"]
        assert r["trace_sha256"] == FROZEN_BASELINE_SHA256[r["trace_path"]]
        assert r["review_scope"] == "LLM-generated interpretation / recommendation only"
        assert "DSM" in r["deterministic_results_not_affected"]
    assert reviewed["process"] == {"llm_rerun": False, "prompt_tuned": False, "failed_responses_repaired": False,
                                   "original_traces_preserved": True}


def test_original_human_review_records_are_unchanged():
    path = SAFETY_DIR / "human_review_records.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == ORIGINAL_RECORDS_SHA256
    assert all(r["reviewer_decision"] == "PENDING" for r in json.loads(path.read_text(encoding="utf-8")))


def test_original_traces_and_frozen_artifacts_are_unchanged(reviewed):
    assert check_baseline_integrity(PROJECT_ROOT) == []
    assert reviewed["frozen_artifacts_verified"] == {"pinned": 22, "unchanged": 22, "discrepancies": []}


def test_rejected_episodes_cannot_be_released_downstream(reviewed):
    for r in reviewed["records"]:
        assert r["reviewer_decision"] == "REJECTED" and r["original_safety_route"] == "BLOCKED_VALIDATION_FAILURE"
        assert r["released_downstream"] is False and r["implementation_authorized"] is False
        assert r["recommendation_approved"] is False
    assert reviewed["released_downstream"] == 0


def test_reviewed_outputs_are_reproducible(reviewed):
    spec = importlib.util.spec_from_file_location("record_human_review", PROJECT_ROOT / "scripts" / "record_human_review.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    doc = mod.build()
    assert json.dumps(doc, indent=2) + "\n" == (SAFETY_DIR / "human_review_records_reviewed.json").read_text(encoding="utf-8")
    assert mod.summary(doc) == (SAFETY_DIR / "human_review_summary.md").read_text(encoding="utf-8")
