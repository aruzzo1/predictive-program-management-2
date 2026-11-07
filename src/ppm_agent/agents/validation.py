"""Deterministic validation (Python, never the LLM).

Checks that hypotheses and assessments are structurally valid and traceable to the retrieved
evidence. A hypothesis that fails any check never reaches the critic.

Responsibility boundary: Python owns every objectively verifiable hard constraint (citations exist
and were retrieved, activities, relationship type, named mediator, schema, score range, duplicates).
The LLM critic owns qualitative evaluation (evidence strength, causal plausibility, contradictions,
assumptions, usefulness) and expresses it through scores. A critic claim about a hard constraint is
advisory: it is compared with Python's result and any mismatch is recorded, not acted on.
"""

from __future__ import annotations

from pydantic import ValidationError

from ppm_agent.agents.scoring import weighted_score
from ppm_agent.models import CriticAssessment, DependencyHypothesis, ReasoningState
from ppm_agent.models.dependency import RelationshipType

VALID_RELATIONSHIPS = set(RelationshipType.__args__)
SCORE_TOLERANCE = 0.01


def parse_hypothesis(raw: dict) -> tuple[DependencyHypothesis | None, list[str]]:
    """Build a hypothesis from untrusted (e.g. LLM) output; schema problems become validation errors."""
    if raw.get("relationship_type") not in VALID_RELATIONSHIPS:
        return None, [f"invalid relationship_type {raw.get('relationship_type')!r}"]
    try:
        return DependencyHypothesis(**raw), []
    except ValidationError as exc:
        return None, [f"schema: {e['loc'][0] if e['loc'] else ''} {e['msg']}" for e in exc.errors()]


def signature(h: DependencyHypothesis) -> tuple:
    """What makes two hypotheses the same claim: type, mediator and cited evidence."""
    return h.relationship_type, h.intermediate_activity, tuple(sorted(h.supporting_evidence_ids))


def validate_hypothesis(h: DependencyHypothesis, state: ReasoningState, retrieval_chunk_ids: list[str]) -> list[str]:
    """Errors that make a hypothesis invalid (empty list = valid)."""
    errors = []
    ids = [o.hypothesis_id for o in state.all_hypotheses]
    earlier = state.all_hypotheses[: ids.index(h.hypothesis_id)] if h.hypothesis_id in ids else state.all_hypotheses
    duplicate = next((o for o in earlier if signature(o) == signature(h)), None)
    if duplicate is not None:
        errors.append(f"duplicate of {duplicate.hypothesis_id} (same type, mediator and citations)")
    evidence = state.evidence_by_id()
    if not h.supporting_evidence_ids:
        errors.append("no supporting evidence cited")
    for eid in h.supporting_evidence_ids + h.contradicting_evidence_ids:
        if eid not in evidence:
            errors.append(f"cited evidence id {eid!r} does not exist")
        elif evidence[eid].chunk_id not in retrieval_chunk_ids:
            errors.append(f"evidence {eid!r} chunk {evidence[eid].chunk_id!r} was not returned by retrieval")
    for role, activity_id, expected in (("source", h.source_activity, state.source_activity),
                                        ("target", h.target_activity, state.target_activity)):
        if activity_id not in state.activities:
            errors.append(f"{role} activity {activity_id!r} does not exist")
        elif activity_id != expected:
            errors.append(f"{role} activity {activity_id!r} is not the activity under analysis ({expected!r})")
    if h.relationship_type not in VALID_RELATIONSHIPS:
        errors.append(f"invalid relationship_type {h.relationship_type!r}")
    if h.relationship_type == "INDIRECT" and not h.intermediate_activity:
        errors.append("INDIRECT hypothesis does not name an intermediate activity")
    if not h.reasoning_summary.strip():
        errors.append("missing reasoning_summary")
    return errors


def deterministic_check(h: DependencyHypothesis, state: ReasoningState) -> list[str]:
    """Python's authoritative hard-constraint result for a hypothesis, against the episode's retrieved evidence.

    Retrieved evidence is verified against the retrieval output when it is attached (episode.attach_evidence),
    so its chunk ids are the retrieval chunk ids.
    """
    return validate_hypothesis(h, state, [e.chunk_id for e in state.retrieved_evidence])


def critic_disagreement(h: DependencyHypothesis, python_errors: list[str], claimed: bool, claimed_reasons: list[str]) -> str | None:
    """Why the critic's advisory hard-constraint claim contradicts Python's result, or None if they agree."""
    if not python_errors and claimed:
        mediator = f"; INDIRECT mediator named ({h.intermediate_activity!r})" if h.relationship_type == "INDIRECT" else ""
        return (f"Critic claimed a hard-constraint failure ({'; '.join(claimed_reasons) or 'no reason given'}), but Python deterministic "
                f"validation PASSED: cited evidence {h.supporting_evidence_ids + h.contradicting_evidence_ids} exists in the retrieved "
                f"evidence and was returned by retrieval; activities {h.source_activity}->{h.target_activity} match the episode; "
                f"relationship type {h.relationship_type} is valid{mediator}. The claim is advisory; the branch is not rejected on it.")
    if python_errors and not claimed:
        return (f"Python deterministic validation FAILED ({'; '.join(python_errors)}), but the critic did not claim a hard-constraint "
                "failure. The Python result applies.")
    return None


def validate_assessment(a: CriticAssessment, hypothesis_ids: set[str]) -> list[str]:
    errors = []
    if a.hypothesis_id not in hypothesis_ids:
        errors.append(f"assessment refers to unknown hypothesis {a.hypothesis_id!r}")
    if a.deterministic_validation_result == "FAIL" and a.hard_constraint_pass:
        errors.append("hard_constraint_pass is true although deterministic validation failed")
    if a.critic_validation_disagreement and not a.disagreement_reason:
        errors.append("critic/Python disagreement recorded without a reason")
    for name in ("documentary_evidence_score", "engineering_consistency_score", "model_consistency_score",
                 "predictive_usefulness_score", "overall_score"):
        if not 0 <= getattr(a, name) <= 100:
            errors.append(f"{name} outside 0-100")
    expected = weighted_score(a.documentary_evidence_score, a.engineering_consistency_score,
                              a.model_consistency_score, a.predictive_usefulness_score)
    if abs(expected - a.overall_score) > SCORE_TOLERANCE:
        errors.append(f"overall_score {a.overall_score} does not equal the weighted sub-scores ({expected})")
    if not a.critic_summary.strip():
        errors.append("missing critic_summary")
    return errors


def validate_evidence(state: ReasoningState, retrieval_chunk_ids: list[str]) -> list[str]:
    errors = []
    ids = [e.evidence_id for e in state.retrieved_evidence]
    if len(ids) != len(set(ids)):
        errors.append("duplicate evidence ids")
    for e in state.retrieved_evidence:
        if e.chunk_id not in retrieval_chunk_ids:
            errors.append(f"evidence {e.evidence_id} chunk {e.chunk_id} not in retrieval output")
    return errors
