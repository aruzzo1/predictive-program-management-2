"""Tests for the strengthened agent validation (contract v2): spelled-out numbers, structured qualitative claims,
objective minima, secondary options, citations and human-review triggers. No network calls."""

import hashlib
import json

import pytest

from ppm_agent.agents.llm import REAL_LLM_MODE
from ppm_agent.agents.predictive_intervention import (
    WITH_ERRORS,
    build_catalogue,
    deterministic_effects,
    legacy_findings,
    mock_interpret,
    run_episode,
    spelled_number_check,
    validate_output,
)
from ppm_agent.config import PROJECT_ROOT
from ppm_agent.models.intervention import SecondaryOption

FIRST_TRACE = PROJECT_ROOT / "outputs" / "agentic_traces" / "predictive_intervention_agent_20261106_101319.json"
PRESERVED = {  # first real episode and its reviewed summary must stay byte-identical
    "outputs/agentic_traces/predictive_intervention_agent_20261106_101319.json":
        "357ea4155c81dc03ed06f5f948fc529ceedde826d1fff75bdff78998c13e04bf",
    "outputs/agentic_traces/predictive_intervention_agent_20261106_101319.md":
        "b0576e97a2ad27576d6665a9f9dff5dc38cab37ac435da49333bffa2c77b3864",
    "outputs/evaluation/predictive_intervention_agent_summary.md":
        "56fb10e26bbb8c86d85a8653b386bef16738f42135043623ebeb341980bf08ce",
}


@pytest.fixture(scope="module")
def cat():
    return build_catalogue(PROJECT_ROOT)


@pytest.fixture()
def out(cat):
    return mock_interpret(cat)


def assessment(out, case):
    return next(a for a in out.intervention_assessments if a.case_id == case)


def preference(out, objective):
    return next(p for p in out.preferred_intervention_by_objective if p.objective == objective)


def errors(out, cat, category):
    return validate_output(out, cat)["errors_by_category"][category]


# --- numeric guardrail ---------------------------------------------------------------------------------

@pytest.mark.parametrize("text, kind", [
    ("cumulative disturbance of about ten point four units", "decimal in words"),
    ("uses about three quarters of its capacity", "fraction in words"),
    ("reduces committed exposure by sixty percent", "number word"),
    ("the four-day normalization", "number word"),
    ("falls to zero", "number word"),
    ("roughly half of the disturbance", "fraction in words"),
    ("a reduction of forty per cent", "number word"),
    ("D6 receives twice as much", "multiplier in words"),
])
def test_spelled_out_quantities_are_rejected(text, kind):
    hits = spelled_number_check([("f", text)])["spelled_quantities"]
    assert hits and any(h["kind"] == kind for h in hits)


def test_ordinary_prose_and_identifiers_pass():
    text = ("CASE_2 absorbs the disturbance at D6 one step after A210 slips; INTERVENTION_3 acts at D8 by t12. "
            "No one intervention dominates every objective.")
    assert spelled_number_check([("f", text)])["result"] == "PASS"


def test_spelled_quantity_in_agent_output_fails_validation(out, cat):
    out.no_action_assessment.statement = "Under NO ACTION the cumulative disturbance is about ten point four."
    assert any("decimal in words" in e for e in errors(out, cat, "numeric"))


# --- structured qualitative claims ---------------------------------------------------------------------

def test_deterministic_effects_for_the_frozen_results(cat):
    e = deterministic_effects(cat)
    assert [e["CASE_1"][k] for k in ("effect_on_total_disturbance", "effect_on_D8_entering")] == ["ELIMINATED", "ELIMINATED"]
    assert (e["CASE_2"]["effect_on_total_disturbance"], e["CASE_2"]["effect_on_D6_exposure"],
            e["CASE_2"]["effect_on_D8_entering"], e["CASE_2"]["disturbance_reaches_D8"]) == ("REDUCED", "ELIMINATED",
                                                                                            "ELIMINATED", False)
    assert (e["CASE_3"]["effect_on_D8_entering"], e["CASE_3"]["effect_on_D8_committed"], e["CASE_3"]["disturbance_reaches_D8"],
            e["CASE_3"]["changes_any_D1_to_D7_trajectory"]) == ("UNCHANGED", "REDUCED", True, False)


def test_mock_structured_claims_validate(out, cat):
    v = validate_output(out, cat)
    assert v["result"] == "PASS", v["errors"]
    assert all(c["match"] for c in v["claim_checks"])


def test_d8_unchanged_for_case_2_fails(out, cat):
    assessment(out, "CASE_2").effect_on_D8_entering = "UNCHANGED"
    assert any("CASE_2.effect_on_D8_entering: claimed UNCHANGED, deterministic ELIMINATED" in e
               for e in errors(out, cat, "qualitative"))


def test_case_3_unchanged_entering_and_reduced_commitment_pass_but_contradiction_fails(out, cat):
    a = assessment(out, "CASE_3")
    assert (a.effect_on_D8_entering, a.effect_on_D8_committed) == ("UNCHANGED", "REDUCED")
    assert errors(out, cat, "qualitative") == []
    a.effect_on_D8_committed = "UNCHANGED"
    assert any("CASE_3.effect_on_D8_committed" in e for e in errors(out, cat, "qualitative"))


def test_eliminated_versus_reduced(out, cat):
    assessment(out, "CASE_2").effect_on_D6_exposure = "REDUCED"  # actual: effective D6 is zero
    assessment(out, "CASE_1").effect_on_total_disturbance = "REDUCED"
    errs = errors(out, cat, "qualitative")
    assert any("CASE_2.effect_on_D6_exposure: claimed REDUCED, deterministic ELIMINATED" in e for e in errs)
    assert any("CASE_1.effect_on_total_disturbance" in e for e in errs)


def test_reaches_d8_and_upstream_flags_are_checked(out, cat):
    assessment(out, "CASE_2").disturbance_reaches_D8 = True
    assessment(out, "CASE_3").changes_any_D1_to_D7_trajectory = True
    errs = errors(out, cat, "qualitative")
    assert any("CASE_2.disturbance_reaches_D8" in e for e in errs)
    assert any("CASE_3.changes_any_D1_to_D7_trajectory" in e for e in errs)


def test_comparative_claims_are_checked(out, cat):
    out.comparative_claims[1].relation = "LOWER_THAN"  # CASE_3 D8 entering actually equals CASE_0
    assert any("comparative_claims[1]" in e and "deterministic EQUAL_TO" in e for e in errors(out, cat, "qualitative"))


def test_prose_contradiction_on_d8_is_caught(out, cat):
    assessment(out, "CASE_2").what_it_does_not_change = "It does not change the disturbance entering D8."
    assessment(out, "CASE_3").what_it_does_not_change = "It does not reduce the disturbance entering D8."
    errs = errors(out, cat, "qualitative")
    assert any("prose contradicts D8 entering (ELIMINATED) in CASE_2" in e for e in errs)
    assert not any("in CASE_3" in e for e in errs)


# --- objectives ----------------------------------------------------------------------------------------

def test_tied_objectives_allow_the_tie_or_a_member(out, cat):
    v = validate_output(out, cat)["objective_alignment"]
    assert v["PROTECT_FLIGHT_TEST_EXECUTION"]["lowest_metric_cases"] == ["CASE_1", "CASE_2"]
    assert v["LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE"]["lowest_metric_cases"] == ["CASE_1", "CASE_2"]
    assert v["MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE"]["lowest_metric_cases"] == ["CASE_1"]
    preference(out, "PROTECT_FLIGHT_TEST_EXECUTION").preferred_case_ids = ["CASE_2"]
    result = validate_output(out, cat)
    assert result["errors_by_category"]["objective"] == []
    assert result["objective_alignment"]["PROTECT_FLIGHT_TEST_EXECUTION"]["agreement"] == "SUBSET_OF_TIE"


def test_strictly_beaten_best_recommendation_is_rejected(out, cat):
    preference(out, "LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE").preferred_case_ids = ["CASE_3"]
    preference(out, "MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE").preferred_case_ids = ["CASE_1", "CASE_2"]
    errs = errors(out, cat, "objective")
    assert any("LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: prefers CASE_3" in e for e in errs)
    assert any("MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE: prefers CASE_2" in e for e in errs)


def test_intervention_3_exposure_management_framing(out, cat):
    sec = [s for s in out.secondary_options if s.case_id == "CASE_3"]
    assert sec and sec[0].objective == "LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE"
    assert (sec[0].effect_vs_no_action, sec[0].is_minimum_for_objective) == ("REDUCED", False)
    assert errors(out, cat, "objective") == []
    out.secondary_options = [SecondaryOption(case_id="CASE_3", objective="LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE",
                                             condition="Reduce production commitment while upstream development continues.",
                                             effect_vs_no_action="REDUCED", is_minimum_for_objective=True,
                                             cited_ids=["CASE_3.cumulative_D8_committed_pre_maturity"])]
    assert any("is_minimum_for_objective True, deterministic False" in e for e in errors(out, cat, "objective"))


# --- citations -----------------------------------------------------------------------------------------

def test_unknown_and_non_fact_citations_are_rejected(out, cat):
    out.overall_recommendation.cited_ids = ["CASE_1.change.cumulative_total"]  # the id the first episode invented
    assessment(out, "CASE_1").cited_ids = ["ASSUMPTION.synthetic_baseline"]
    errs = errors(out, cat, "citation")
    assert any("unknown id 'CASE_1.change.cumulative_total'" in e for e in errs)
    assert any("CASE_1: must cite at least one FACT id" in e for e in errs)
    assert any("CASE_1: must cite at least one fact of its own case" in e for e in errs)


# --- outcome and human review --------------------------------------------------------------------------

class FakeClient:
    mode, model = REAL_LLM_MODE, "fake-model"

    def __init__(self, result):
        self.result = result

    def complete(self, system, user, schema):
        return self.result

    def usage_summary(self):
        return {"provider": "fake", "model": self.model, "successful_responses": 1, "input_tokens": 1, "output_tokens": 1}


def test_validation_failure_requires_human_review_and_is_not_usable(out, tmp_path):
    preference(out, "LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE").preferred_case_ids = ["CASE_3"]
    out.uncertainties = out.uncertainties[:-1]
    raw = out.model_dump()
    meta = run_episode(FakeClient(out), PROJECT_ROOT, tmp_path)
    assert meta["status"] == WITH_ERRORS and meta["usable_downstream"] is False and meta["human_review_required"] is True
    trace = json.loads(open(meta["trace_json"], encoding="utf-8").read())
    assert trace["interpretation"] == raw  # raw response preserved, not repaired
    reasons = trace["validation"]["human_review"]["reasons"]
    assert "objective validation failed" in reasons and "coverage validation failed" in reasons


def test_agent_setting_human_review_false_is_an_error(out, cat):
    out.human_review_required = False
    assert errors(out, cat, "human_review")


# --- the preserved first episode -----------------------------------------------------------------------

def test_first_episode_files_are_unchanged():
    for rel, digest in PRESERVED.items():
        assert hashlib.sha256((PROJECT_ROOT / rel).read_bytes()).hexdigest() == digest, rel


def test_new_checks_detect_the_first_episode_failure_modes(cat):
    first = json.loads(FIRST_TRACE.read_text(encoding="utf-8"))
    found = legacy_findings(first["interpretation"], cat)
    assert found["unknown_citation_count"] == 6
    assert {h["text"].lower() for h in found["spelled_quantities"]} >= {"ten point four", "quarters"}
    assert any(p["field"].startswith("CASE_2") for p in found["prose_d8_contradictions"])
    assert ("LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE", "CASE_3") in found["objective_preferences_strictly_beaten"]
