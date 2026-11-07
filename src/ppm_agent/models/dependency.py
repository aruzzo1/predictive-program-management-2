"""Pydantic models for evidence, activities, dependency hypotheses, critic assessments and reasoning state.

Kept deliberately small. These are the objects the agents construct and validate; downstream
DSM / WTM tooling (not yet built) will consume DependencyDecision objects, not free text.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

ActivityType = Literal["software", "design", "integration", "test", "production", "requirements", "management", "other"]
RelationshipType = Literal["DIRECT", "INDIRECT", "RECIPROCAL", "NONE", "UNCERTAIN"]
Decision = Literal["SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "UNRESOLVED"]
Status = Literal["RUNNING", "DOMINANT_CANDIDATE", "NO_VIABLE_CANDIDATE", "NO_NEW_CANDIDATES", "DEPTH_LIMIT", "BUDGET_EXHAUSTED"]

POSITIVE_RELATIONSHIPS = {"DIRECT", "INDIRECT", "RECIPROCAL"}
# critic's advisory label: is the relationship stated by the source, or inferred from it?
EvidenceSupportLabel = Literal["DIRECTLY_STATED", "STRONGLY_SUPPORTED", "INFERRED", "WEAKLY_SUPPORTED", "UNSUPPORTED"]
ReviewStatus = Literal["COMPLETED", "NO_SURVIVORS", "SINGLE_SURVIVOR", "SKIPPED_BUDGET", "NOT_AVAILABLE", "FAILED"]


class Evidence(BaseModel):
    """One retrieved passage with full provenance."""

    evidence_id: str = Field(min_length=1)
    source_document: str = Field(min_length=1)
    source_organization: str | None = None
    pdf_page: int = Field(ge=1)
    printed_page: str | None = None
    chunk_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    section_type: str | None = None
    publication_date: str | None = None
    retrieval_method: str
    retrieval_rank: int = Field(ge=1)
    retrieval_score: float | None = None


class Activity(BaseModel):
    activity_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = ""
    activity_type: ActivityType


class CandidateDependency(BaseModel):
    """The dependency question posed to the agents (before any hypothesis is formed)."""

    source_activity: str
    target_activity: str
    proposed_relationship: str
    relationship_type: RelationshipType = "UNCERTAIN"
    evidence_ids: list[str] = Field(default_factory=list)


class DependencyHypothesis(BaseModel):
    hypothesis_id: str = Field(min_length=1)
    parent_id: str | None = None  # the hypothesis this one refines (None at depth 1)
    depth: int = Field(default=1, ge=1)
    source_activity: str
    target_activity: str
    relationship_type: RelationshipType
    intermediate_activity: str | None = None  # named mediator for INDIRECT hypotheses
    reasoning_summary: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class CriticAssessment(BaseModel):
    """Scores are 0-100. overall_score is computed in Python from the weighted sub-scores.

    Responsibility boundary: hard_constraint_pass / hard_constraint_failures are what pruning uses. In
    REAL_LLM_MODE they are set by deterministic Python validation only; whatever the critic claims
    about hard constraints is kept in the advisory critic_claimed_* fields, and a mismatch with Python
    is recorded as critic_validation_disagreement (never silently dropped, never acted on).
    """

    hypothesis_id: str
    documentary_evidence_score: float = Field(ge=0, le=100)
    engineering_consistency_score: float = Field(ge=0, le=100)
    model_consistency_score: float = Field(ge=0, le=100)
    predictive_usefulness_score: float = Field(ge=0, le=100)
    hard_constraint_pass: bool
    hard_constraint_failures: list[str] = Field(default_factory=list)
    critic_summary: str
    overall_score: float = Field(ge=0, le=100)
    # deterministic (Python-owned) validation; None when not recorded (scripted test critics)
    deterministic_validation_result: Literal["PASS", "FAIL"] | None = None
    deterministic_validation_errors: list[str] = Field(default_factory=list)
    # qualitative (critic-owned) findings
    evidence_support_label: EvidenceSupportLabel | None = None  # advisory; None for the mock and scripted critics
    evidence_strength_summary: str = ""
    contradictions: list[str] = Field(default_factory=list)
    unsupported_assumptions: list[str] = Field(default_factory=list)
    critic_concerns: list[str] = Field(default_factory=list)
    # advisory critic claim about hard constraints, and its comparison with Python
    critic_claimed_hard_failure: bool = False
    critic_claimed_hard_failure_reasons: list[str] = Field(default_factory=list)
    critic_validation_disagreement: bool = False
    disagreement_reason: str | None = None


# --- structured-output schemas for REAL_LLM_MODE ---------------------------------------------------
# The fields a model is allowed to fill, named exactly as in DependencyHypothesis / CriticAssessment.
# Ids, parent/depth, activities, overall_score and hard_constraint_pass are set in Python; every
# field is required (no defaults) so the schemas are valid for strict structured output. Score bounds
# are not encoded here: out-of-range scores are clamped and every output is re-validated
# deterministically. The critic cannot set hard_constraint_pass; it can only make an advisory claim.


class GeneratedHypothesis(BaseModel):
    relationship_type: RelationshipType
    intermediate_activity: str | None
    reasoning_summary: str
    supporting_evidence_ids: list[str]
    contradicting_evidence_ids: list[str]
    assumptions: list[str]


class GeneratorOutput(BaseModel):
    hypotheses: list[GeneratedHypothesis]


class CriticOutput(BaseModel):
    documentary_evidence_score: float
    engineering_consistency_score: float
    model_consistency_score: float
    predictive_usefulness_score: float
    evidence_support_label: EvidenceSupportLabel
    evidence_strength_summary: str
    contradictions: list[str]
    unsupported_assumptions: list[str]
    critic_concerns: list[str]
    critic_claimed_hard_failure: bool
    critic_claimed_hard_failure_reasons: list[str]
    critic_summary: str


class ComparativeReviewOutput(BaseModel):
    """One comparison of the surviving hypotheses. Advisory: it cannot rescore, revive or validate."""

    preferred_hypothesis_id: str
    near_tie: bool
    assumption_comparison: str
    uncertainty_assessment: str
    comparative_reasoning_summary: str


class ComparativeReview(BaseModel):
    """Trace record of the comparative critic review (run once, on the final survivors, before the decision)."""

    status: ReviewStatus
    mode: str = ""
    reviewed_hypothesis_ids: list[str] = Field(default_factory=list)  # survivors only, in score order
    deterministic_near_tie: bool | None = None  # Python: top two totals within the near-tie margin
    preferred_hypothesis_id: str | None = None   # None if not reviewed, or if the critic named a non-survivor
    near_tie: bool | None = None                 # the critic's view of whether the tie is genuine
    agrees_with_score_ranking: bool | None = None
    assumption_comparison: str = ""
    uncertainty_assessment: str = ""
    comparative_reasoning_summary: str = ""
    validation_notes: list[str] = Field(default_factory=list)


class DependencyDecision(BaseModel):
    source_activity: str
    target_activity: str
    decision: Decision
    selected_relationship_type: RelationshipType | None = None
    selected_hypothesis_id: str | None = None
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    critic_score: float | None = Field(default=None, ge=0, le=100)
    decision_summary: str


class ReasoningState(BaseModel):
    """Everything a reasoning episode knows; serialized as the trace."""

    query: str
    source_activity: str
    target_activity: str
    activities: dict[str, Activity] = Field(default_factory=dict)
    candidate: CandidateDependency | None = None
    retrieved_evidence: list[Evidence] = Field(default_factory=list)
    pending_hypotheses: list[DependencyHypothesis] = Field(default_factory=list)  # generated, not yet judged
    active_hypotheses: list[DependencyHypothesis] = Field(default_factory=list)   # retained beam
    rejected_hypotheses: list[DependencyHypothesis] = Field(default_factory=list)
    all_hypotheses: list[DependencyHypothesis] = Field(default_factory=list)
    expanded_ids: list[str] = Field(default_factory=list)  # hypotheses already expanded (each is expanded once)
    assessments: dict[str, CriticAssessment] = Field(default_factory=dict)
    validation_errors: dict[str, list[str]] = Field(default_factory=dict)
    critic_disagreements: list[dict] = Field(default_factory=list)  # critic vs Python validation, for audit
    pruning_log: list[dict] = Field(default_factory=list)
    accepted_hypothesis: DependencyHypothesis | None = None
    comparative_review: ComparativeReview | None = None
    decision: DependencyDecision | None = None
    depth: int = 0
    model_calls: int = 0
    comparative_model_call_count: int = 0  # included in model_calls
    status: Status = "RUNNING"
    agent_mode: str = "MOCK_AGENT_MODE"
    events: list[str] = Field(default_factory=list)

    @field_validator("model_calls")
    @classmethod
    def _non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("model_calls cannot be negative")
        return v

    def evidence_by_id(self) -> dict[str, Evidence]:
        return {e.evidence_id: e for e in self.retrieved_evidence}
