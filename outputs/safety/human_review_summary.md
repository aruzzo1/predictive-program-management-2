# Human review of the preserved real agent episodes

> **The human reviewer did not reject the deterministic simulation results. The reviewer rejected the LLM-generated interpretations because each failed one or more deterministic validation checks.**
>
> **The preserved episodes demonstrate bounded autonomy: an LLM may generate interpretations and recommendations, but deterministic validation and human review govern whether those recommendations can be trusted.**

Reviewed on 2026-11-06. Reviewer: Capstone human reviewer (project owner); decision recorded at the reviewer's explicit instruction. Scope: LLM-generated interpretation / recommendation only. Records:
`human_review_records_reviewed.json`. The original Module 6 records (`human_review_records.json`, decision PENDING) are
preserved unchanged and referenced by index and hash.

| Measure | Count |
|---|---|
| Episodes reviewed | 3 |
| APPROVED_AS_ADVISORY | 0 |
| REJECTED | 3 |
| REVISE_AND_RERUN | 0 |
| ESCALATED | 0 |
| Released downstream | 0 |

## Dispositions

| Episode | Original status | Validator errors (in trace) | Failure categories (Module 6 count) | Safety route | Decision | Released |
|---|---|---|---|---|---|---|
| Episode 1 (contract v1) | COMPLETED_WITH_VALIDATION_ERRORS | 6 | citation 6, objective 1 | BLOCKED_VALIDATION_FAILURE | **REJECTED** | False |
| Episode 2 (contract v2) | COMPLETED_WITH_VALIDATION_ERRORS | 5 | qualitative 2, objective 3 | BLOCKED_VALIDATION_FAILURE | **REJECTED** | False |
| Episode 3 (contract v3) | COMPLETED_WITH_VALIDATION_ERRORS | 17 | citation 7, qualitative 1, objective 4, narrative 1, coverage 4 | BLOCKED_VALIDATION_FAILURE | **REJECTED** | False |

- Episode 3 had **17** validation errors. An earlier report said 18; that was a miscount.
- Episode 1's contract-v1 validator recorded 6 errors, all citations. Its objective-selection disagreement was an
  advisory flag under contract v1, and the Module 6 safety layer counts it as a failure.

**Why REJECTED, for each episode:**
- The LLM-generated interpretation contains deterministic validation failures, so it is not trustworthy enough for
  downstream use.
- No intervention recommendation is approved.
- No implementation is authorized.

The rejection applies **only** to the LLM-generated interpretation and recommendation. It does not affect, and these
remain authoritative: frozen synthetic baseline v1.1, DSM, WTM, schedule-to-WTM mapping, deterministic trajectory simulation, deterministic intervention comparison.

## Reviewer notes

- **Episode 1 (contract v1):** Validation failures reviewed and confirmed: 6 validation errors recorded by the contract-v1 validator (all citation), plus 1 objective-selection disagreement flagged as advisory under contract v1 and counted as a failure by the Module 6 safety layer. The raw trace remains preserved unchanged. The LLM recommendation remains withheld and no downstream implementation is authorized. The deterministic analytical results remain usable independently. Human oversight prevented an invalid agent interpretation from being trusted.
- **Episode 2 (contract v2):** Validation failures reviewed and confirmed: 5 validation errors (2 qualitative, 3 objective) recorded by the contract-v2 validator. The raw trace remains preserved unchanged. The LLM recommendation remains withheld and no downstream implementation is authorized. The deterministic analytical results remain usable independently. Human oversight prevented an invalid agent interpretation from being trusted.
- **Episode 3 (contract v3):** Validation failures reviewed and confirmed: 17 validation errors (7 citation, 1 qualitative, 4 objective, 1 narrative, 4 coverage) recorded by the contract-v3 validator. The raw trace remains preserved unchanged. The LLM recommendation remains withheld and no downstream implementation is authorized. The deterministic analytical results remain usable independently. Human oversight prevented an invalid agent interpretation from being trusted.

## How the review was conducted

- No LLM was rerun during human review.
- No prompt was tuned.
- No failed response was automatically repaired.
- All original traces remain available for audit, byte-identical.
- Frozen artifacts verified: 22 / 22 unchanged.

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
