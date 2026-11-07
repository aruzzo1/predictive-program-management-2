"""Structured output of the Predictive Simulation and Intervention Agent (Module 5, Agent 2).

The schema has no numeric fields: the model interprets deterministic results and cites them by fact id. Every
quantitative value in the final trace comes from Python. Qualitative claims that matter are structured (effect
enums, booleans, comparison claims) so Python can validate them against the frozen metrics; free text explains
them but is not authoritative. Contract v3: the objective selections are the structured preferred_for_* fields; the
overall recommendation text is explanatory only. All fields are required (no defaults) for strict structured output.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

CaseId = Literal["CASE_1", "CASE_2", "CASE_3"]
AnyCaseId = Literal["CASE_0", "CASE_1", "CASE_2", "CASE_3"]
InterventionId = Literal["INTERVENTION_1", "INTERVENTION_2", "INTERVENTION_3"]
Objective = Literal["MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE", "PROTECT_FLIGHT_TEST_EXECUTION",
                    "LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE"]
Effect = Literal["ELIMINATED", "REDUCED", "UNCHANGED", "INCREASED"]  # relative to CASE_0 (NO ACTION)
Metric = Literal["TOTAL_DISTURBANCE", "D6_EXPOSURE", "D8_ENTERING", "D8_COMMITTED", "PEAK_DISTURBANCE"]
Relation = Literal["LOWER_THAN", "HIGHER_THAN", "EQUAL_TO"]


class CitedStatement(BaseModel):
    statement: str
    cited_ids: list[str]  # fact, assumption, limitation or case ids from the supplied catalogue


class InterventionAssessment(BaseModel):
    case_id: CaseId
    intervention_id: InterventionId
    # structured, authoritative claims (validated by Python against the deterministic metrics)
    effect_on_total_disturbance: Effect
    effect_on_D6_exposure: Effect
    effect_on_D8_entering: Effect
    effect_on_D8_committed: Effect
    disturbance_reaches_D8: bool
    # TRUE if any D1-D7 trajectory differs from NO ACTION at any step; FALSE only if all are identical
    changes_any_D1_to_D7_trajectory: bool
    # explanation (not authoritative)
    management_objective: str
    effect_on_trajectory: str
    what_it_does_not_change: str
    cited_ids: list[str]


class ComparativeClaim(BaseModel):
    metric: Metric
    left_case: AnyCaseId
    relation: Relation
    right_case: AnyCaseId
    cited_ids: list[str]


class ObjectivePreference(BaseModel):
    objective: Objective
    preferred_case_ids: list[AnyCaseId]  # must be case(s) that attain the minimum of the objective's metric
    rationale: str
    conditions_and_caveats: str
    cited_ids: list[str]


class SecondaryOption(BaseModel):
    """A case that is useful under a narrower condition without being the mathematical minimum for the objective."""

    case_id: CaseId
    objective: Objective
    condition: str
    effect_vs_no_action: Effect
    is_minimum_for_objective: bool
    cited_ids: list[str]


class PredictiveInterventionOutput(BaseModel):
    no_action_assessment: CitedStatement
    intervention_assessments: list[InterventionAssessment]
    comparative_claims: list[ComparativeClaim]
    management_tradeoffs: list[CitedStatement]
    # authoritative objective selections (contract v3); validated against the deterministic minima; ties allowed
    preferred_for_total_disturbance: list[AnyCaseId]
    preferred_for_flight_test: list[AnyCaseId]
    preferred_for_production_commitment: list[AnyCaseId]
    preferred_intervention_by_objective: list[ObjectivePreference]  # explanation; must agree with the fields above
    secondary_options: list[SecondaryOption]
    key_assumptions: list[CitedStatement]
    uncertainties: list[CitedStatement]
    human_review_required: bool
    human_review_reason: str
    overall_recommendation: CitedStatement  # explanatory only; never an authoritative intervention choice
    confidence_or_support_summary: str
