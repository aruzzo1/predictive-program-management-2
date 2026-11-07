"""Pydantic models for the Module 6 safety / human-intervention layer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SafetyRoute = Literal["SAFE_ADVISORY", "HUMAN_REVIEW_REQUIRED", "BLOCKED_VALIDATION_FAILURE", "ESCALATE_HIGH_IMPACT",
                      "FAILED"]
ReviewerDecision = Literal["PENDING", "APPROVED_AS_ADVISORY", "REJECTED", "REVISE_AND_RERUN", "ESCALATED"]
GuardrailStatus = Literal["PASS", "FAIL", "ENFORCED", "NOT_CHECKED", "NOT_APPLICABLE"]
ConfidenceSignal = Literal["HIGH", "HEDGED", "MIXED", "UNSPECIFIED", "NOT_AVAILABLE"]
ImpactLevel = Literal["HIGH", "LOW", "NONE"]


class SafetyInput(BaseModel):
    """Structured facts about one agent episode; the only input to routing (no prose is parsed for routing)."""

    trace_id: str
    trace_path: str
    contract_version: int
    agent_mode: str
    model: str | None
    execution_status: str                       # VALIDATED / COMPLETED_WITH_VALIDATION_ERRORS / FAILED
    output_produced: bool
    usable_downstream: bool
    agent_human_review_flag: bool | None
    checks_performed: list[str]
    failures_by_category: dict[str, int]        # validator results under the contract in force at run time
    supplementary_findings: dict = Field(default_factory=dict)  # read-only re-check with later checks (evaluation only)
    proposed_cases_by_objective: dict[str, list[str]]
    deterministic_minima: dict[str, list[str]]
    impact_actions: list[str]
    inputs_match_frozen: bool                   # trace's input hashes equal the frozen artifacts
    requested_agent_actions: list[str]
    unresolved_evidence: list[str]
    conflicting_evidence: list[str]
    synthetic_inputs: bool
    confidence_text: str | None
    confidence_signal: ConfidenceSignal
    model_calls: int
    elapsed_seconds: float | None
    input_tokens: int | None
    output_tokens: int | None


class GuardrailResult(BaseModel):
    guardrail_id: str
    name: str
    status: GuardrailStatus
    detail: str


class HumanReviewRecord(BaseModel):
    trace_id: str
    trace_path: str
    safety_route: SafetyRoute
    review_required: bool
    authorizes_implementation: bool = False     # never true: the system is advisory
    reasons: list[str]
    episode_stages: dict[str, bool | str]
    validation_summary: dict
    guardrails: list[GuardrailResult]
    proposed_intervention: dict                 # agent's (non-authoritative) selections, as recorded
    deterministic_support: dict
    confidence_signal: dict
    assumptions: list[str]
    limitations: list[str]
    impact_level: ImpactLevel
    impact_actions: list[str]
    reviewer_decision: ReviewerDecision = "PENDING"  # never fabricated; set only by a human reviewer
    reviewer: str | None = None
    reviewer_notes: str | None = None
