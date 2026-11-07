"""Record the human-review disposition of the three preserved real agent episodes (no model calls).

The human reviewer's decision (REJECTED for all three, scope: the LLM-generated interpretation / recommendation only) is
recorded in a separate file. The original Module 6 records (outputs/safety/human_review_records.json), the traces and
all hash-pinned artifacts are read, never modified. Deterministic analytical results are not affected by the review.

Outputs:
    outputs/safety/human_review_records_reviewed.json
    outputs/safety/human_review_summary.md

Usage:
    python scripts/record_human_review.py           # write the reviewed records and summary
    python scripts/record_human_review.py --check   # confirm they match a fresh build
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.safety.models import HumanReviewRecord
from ppm_agent.safety.safety_guardrails import FROZEN_BASELINE_SHA256, check_baseline_integrity

SAFETY_DIR = PROJECT_ROOT / "outputs" / "safety"
ORIGINAL = SAFETY_DIR / "human_review_records.json"
REVIEW_DATE = "2026-11-06"
DECISION = "REJECTED"
REVIEWER = "Capstone human reviewer (project owner); decision recorded at the reviewer's explicit instruction"
SCOPE = "LLM-generated interpretation / recommendation only"
RATIONALE = [
    "The LLM-generated interpretation contains one or more deterministic validation failures.",
    "The interpretation / recommendation is therefore not sufficiently trustworthy for downstream use.",
    "No intervention recommendation from this episode is approved.",
    "No implementation is authorized.",
]
NOT_AFFECTED = ["frozen synthetic baseline v1.1", "DSM", "WTM", "schedule-to-WTM mapping",
                "deterministic trajectory simulation", "deterministic intervention comparison"]
STATEMENTS = [
    "The human reviewer did not reject the deterministic simulation results. The reviewer rejected the LLM-generated "
    "interpretations because each failed one or more deterministic validation checks.",
    "The preserved episodes demonstrate bounded autonomy: an LLM may generate interpretations and recommendations, but "
    "deterministic validation and human review govern whether those recommendations can be trusted.",
]
LABEL = {"predictive_intervention_agent_20261106_101319": "Episode 1 (contract v1)",
         "predictive_intervention_agent_20261106_102300": "Episode 2 (contract v2)",
         "predictive_intervention_agent_20261106_104715": "Episode 3 (contract v3)"}


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _failure_text(counts: dict[str, int]) -> str:
    parts = [f"{n} {c}" for c, n in counts.items() if n]
    return f"{sum(counts.values())} validation errors ({', '.join(parts)})"


def build() -> dict:
    originals = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    integrity = check_baseline_integrity(PROJECT_ROOT)
    reviewed = []
    for i, rec in enumerate(originals):
        trace = json.loads((PROJECT_ROOT / rec["trace_path"]).read_text(encoding="utf-8"))
        counts = rec["validation_summary"]["failures_by_category"]
        version = rec["validation_summary"]["contract_version"]
        validator_errors = len(trace["validation"]["errors"])
        if version == 1:  # v1 recorded objective disagreement as an advisory flag, not as a validator error
            found = (f"{validator_errors} validation errors recorded by the contract-v1 validator (all citation), plus "
                     f"{counts.get('objective', 0)} objective-selection disagreement flagged as advisory under contract v1 "
                     f"and counted as a failure by the Module 6 safety layer")
        else:
            found = f"{_failure_text(counts)} recorded by the contract-v{version} validator"
        note = (f"Validation failures reviewed and confirmed: {found}. The raw trace remains preserved "
                f"unchanged. The LLM recommendation remains withheld and no downstream implementation is authorized. The "
                f"deterministic analytical results remain usable independently. Human oversight prevented an invalid agent "
                f"interpretation from being trusted.")
        disposition = HumanReviewRecord.model_validate({**rec, "reviewer_decision": DECISION, "reviewer": REVIEWER,
                                                        "reviewer_notes": note})
        reviewed.append({
            "trace_id": rec["trace_id"], "trace_path": rec["trace_path"],
            "trace_sha256": FROZEN_BASELINE_SHA256[rec["trace_path"]],
            "original_record_ref": {"file": "outputs/safety/human_review_records.json", "index": i,
                                    "file_sha256": _sha(ORIGINAL)},
            "original_timestamp": trace["meta"].get("timestamp"),
            "original_execution_status": rec["validation_summary"]["agent_status"],
            "original_contract_version": rec["validation_summary"]["contract_version"],
            "original_safety_route": rec["safety_route"],
            "original_validation_category_counts": counts,  # as counted by the Module 6 safety layer
            "original_validator_error_count": validator_errors,  # as recorded in the trace by the agent's validator
            "original_material_failures": rec["validation_summary"]["material_failures"],
            "reviewer_decision": disposition.reviewer_decision, "reviewer": disposition.reviewer,
            "review_date": REVIEW_DATE, "review_scope": SCOPE, "rationale": RATIONALE,
            "reviewer_notes": disposition.reviewer_notes,
            "recommendation_approved": False, "implementation_authorized": disposition.authorizes_implementation,
            "released_downstream": False,
            "deterministic_results_not_affected": NOT_AFFECTED,
        })
    tally = {d: sum(r["reviewer_decision"] == d for r in reviewed)
             for d in ("PENDING", "APPROVED_AS_ADVISORY", "REJECTED", "REVISE_AND_RERUN", "ESCALATED")}
    return {"statements": STATEMENTS, "review_date": REVIEW_DATE, "reviewer": REVIEWER, "review_scope": SCOPE,
            "process": {"llm_rerun": False, "prompt_tuned": False, "failed_responses_repaired": False,
                        "original_traces_preserved": True},
            "episodes_reviewed": len(reviewed), "decision_tally": tally,
            "released_downstream": sum(r["released_downstream"] for r in reviewed),
            "frozen_artifacts_verified": {"pinned": len(FROZEN_BASELINE_SHA256),
                                          "unchanged": len(FROZEN_BASELINE_SHA256) - len(integrity),
                                          "discrepancies": integrity},
            "frozen_artifact_sha256": FROZEN_BASELINE_SHA256, "records": reviewed}


def summary(doc: dict) -> str:
    t = doc["decision_tally"]
    rows = "\n".join(f"| {LABEL[r['trace_id']]} | {r['original_execution_status']} | {r['original_validator_error_count']} | "
                     f"{', '.join(f'{c} {n}' for c, n in r['original_validation_category_counts'].items() if n)} | "
                     f"{r['original_safety_route']} | **{r['reviewer_decision']}** | {r['released_downstream']} |"
                     for r in doc["records"])
    notes = "\n".join(f"- **{LABEL[r['trace_id']]}:** {r['reviewer_notes']}" for r in doc["records"])
    fv = doc["frozen_artifacts_verified"]
    return f"""# Human review of the preserved real agent episodes

> **{doc['statements'][0]}**
>
> **{doc['statements'][1]}**

Reviewed on {doc['review_date']}. Reviewer: {doc['reviewer']}. Scope: {doc['review_scope']}. Records:
`human_review_records_reviewed.json`. The original Module 6 records (`human_review_records.json`, decision PENDING) are
preserved unchanged and referenced by index and hash.

| Measure | Count |
|---|---|
| Episodes reviewed | {doc['episodes_reviewed']} |
| APPROVED_AS_ADVISORY | {t['APPROVED_AS_ADVISORY']} |
| REJECTED | {t['REJECTED']} |
| REVISE_AND_RERUN | {t['REVISE_AND_RERUN']} |
| ESCALATED | {t['ESCALATED']} |
| Released downstream | {doc['released_downstream']} |

## Dispositions

| Episode | Original status | Validator errors (in trace) | Failure categories (Module 6 count) | Safety route | Decision | Released |
|---|---|---|---|---|---|---|
{rows}

- Episode 3 had **17** validation errors. An earlier report said 18; that was a miscount.
- Episode 1's contract-v1 validator recorded 6 errors, all citations. Its objective-selection disagreement was an
  advisory flag under contract v1, and the Module 6 safety layer counts it as a failure.

**Why REJECTED, for each episode:**
- The LLM-generated interpretation contains deterministic validation failures, so it is not trustworthy enough for
  downstream use.
- No intervention recommendation is approved.
- No implementation is authorized.

The rejection applies **only** to the LLM-generated interpretation and recommendation. It does not affect, and these
remain authoritative: {', '.join(NOT_AFFECTED)}.

## Reviewer notes

{notes}

## How the review was conducted

- No LLM was rerun during human review.
- No prompt was tuned.
- No failed response was automatically repaired.
- All original traces remain available for audit, byte-identical.
- Frozen artifacts verified: {fv['unchanged']} / {fv['pinned']} unchanged.

## Final safety chain

```
LLM Interpretation
        |
Deterministic Validation
        |
Safety Routing
        |
Human Review
        |
Approve / Reject / Revise / Escalate
```

For the three real episodes:

```
LLM Interpretation
        |
Validation Failure
        |
BLOCKED_VALIDATION_FAILURE
        |
Human Review
        |
REJECTED
```

No recommendation was released downstream.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = build()
    texts = {"human_review_records_reviewed.json": json.dumps(doc, indent=2) + "\n", "human_review_summary.md": summary(doc)}
    errors = [f"frozen artifact discrepancy: {d}" for d in doc["frozen_artifacts_verified"]["discrepancies"]]
    for name, text in texts.items():
        path = SAFETY_DIR / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(f"{name} missing or differs from a fresh build")
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote outputs/safety/{name}")
    fv = doc["frozen_artifacts_verified"]
    print(f"reviewed {doc['episodes_reviewed']} | tally {doc['decision_tally']} | released {doc['released_downstream']} | "
          f"frozen {fv['unchanged']} / {fv['pinned']} unchanged")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
