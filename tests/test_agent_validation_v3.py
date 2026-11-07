"""Tests for agent contract v3: the renamed D1-D7 trajectory field, authoritative structured objective selections,
and deterministic free-text consistency checks. No network calls."""

import hashlib
import json

import pytest

from ppm_agent.agents.llm import REAL_LLM_MODE
from ppm_agent.agents.predictive_intervention import (
    VALIDATED,
    WITH_ERRORS,
    build_catalogue,
    deterministic_effects,
    mock_interpret,
    narrative_check,
    run_episode,
    validate_output,
)
from ppm_agent.config import PROJECT_ROOT
from ppm_agent.models.intervention import InterventionAssessment, PredictiveInterventionOutput

SECOND_TRACE = PROJECT_ROOT / "outputs" / "agentic_traces" / "predictive_intervention_agent_20261106_102300.json"
PRESERVED = {  # second real episode, its summary and the comparison must stay byte-identical (first: test_agent_validation_v2)
    "outputs/agentic_traces/predictive_intervention_agent_20261106_102300.json":
        "5c3d48c6a5c5f3aec4e14c555614c2da512bf9100df65181a9984563ef1c9703",
    "outputs/agentic_traces/predictive_intervention_agent_20261106_102300.md":
        "68deabf49681dd4bc2dbeba0628deabb1f8d7a538b5031b5823d557cea9c8698",
    "outputs/evaluation/predictive_intervention_agent_summary_20261106_102300.md":
        "c87c7c64bbc276696fcd503ad87bc7c958f7cec96890ced6e11342fc8f50c483",
    "outputs/evaluation/predictive_intervention_validation_comparison.md":
        "1576f00795b705637f3841c86824f08df914c982b8586d890c0f836a269b0813",
}
MINIMA = {"preferred_for_total_disturbance": {"CASE_1"}, "preferred_for_flight_test": {"CASE_1", "CASE_2"},
          "preferred_for_production_commitment": {"CASE_1", "CASE_2"}}


@pytest.fixture(scope="module")
def cat():
    return build_catalogue(PROJECT_ROOT)


@pytest.fixture()
def out(cat):
    return mock_interpret(cat)


def errors(out, cat, category):
    return validate_output(out, cat)["errors_by_category"][category]


class FakeClient:
    mode, model = REAL_LLM_MODE, "fake-model"

    def __init__(self, result):
        self.result = result

    def complete(self, system, user, schema):
        return self.result

    def usage_summary(self):
        return {"provider": "fake", "model": self.model, "successful_responses": 1, "input_tokens": 1, "output_tokens": 1}


# --- renamed D1-D7 field -------------------------------------------------------------------------------

def test_field_is_renamed_in_the_schema():
    fields = InterventionAssessment.model_fields
    assert "changes_any_D1_to_D7_trajectory" in fields and "alters_propagation_upstream_of_D8" not in fields


def test_trajectory_field_semantics(cat):
    flags = cat["trajectory_flags"]["changes_any_D1_to_D7_trajectory"]
    assert flags == {"CASE_1": True, "CASE_2": True, "CASE_3": False}  # CASE_1 removes the disturbance: still a change
    assert {c: e["changes_any_D1_to_D7_trajectory"] for c, e in deterministic_effects(cat).items()} == flags
    assert "trajectory_flags" not in json.loads(_user_payload(cat))  # validation truth is not given to the model


def _user_payload(cat):
    from ppm_agent.agents.predictive_intervention import user_message
    return user_message(cat).split("\n\n", 1)[1]


def test_wrong_trajectory_claims_are_rejected(out, cat):
    for a in out.intervention_assessments:
        if a.case_id in ("CASE_1", "CASE_2"):
            a.changes_any_D1_to_D7_trajectory = False  # the second real episode's error
    errs = errors(out, cat, "qualitative")
    assert any("CASE_1.changes_any_D1_to_D7_trajectory: claimed False, deterministic True" in e for e in errs)
    assert any("CASE_2.changes_any_D1_to_D7_trajectory" in e for e in errs)


# --- structured objective selections -------------------------------------------------------------------

def test_structured_selections_match_the_minima(out, cat):
    v = validate_output(out, cat)
    assert v["result"] == "PASS", v["errors"]
    assert {k: set(s["minimum"]) for k, s in v["structured_preference_checks"].items()} == MINIMA
    assert all(s["agreement"] == "MATCH" for s in v["structured_preference_checks"].values())


def test_ties_allow_the_full_tie_or_one_member(out, cat):
    out.preferred_for_flight_test = ["CASE_2"]
    for p in out.preferred_intervention_by_objective:
        if p.objective == "PROTECT_FLIGHT_TEST_EXECUTION":
            p.preferred_case_ids = ["CASE_2"]
    v = validate_output(out, cat)
    assert v["result"] == "PASS", v["errors"]
    assert v["structured_preference_checks"]["preferred_for_flight_test"]["agreement"] == "SUBSET_OF_TIE"


def test_strictly_beaten_structured_selection_is_rejected(out, cat):
    out.preferred_for_production_commitment = ["CASE_3"]
    out.preferred_for_total_disturbance = []
    errs = errors(out, cat, "objective")
    assert any("preferred_for_production_commitment: selects CASE_3" in e for e in errs)
    assert any("preferred_for_total_disturbance: no case selected" in e for e in errs)


def test_explanatory_list_must_agree_with_structured_fields(out, cat):
    for p in out.preferred_intervention_by_objective:
        if p.objective == "MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE":
            p.preferred_case_ids = ["CASE_1", "CASE_2"]
    assert any("lists ['CASE_1', 'CASE_2'], but preferred_for_total_disturbance is ['CASE_1']" in e
               for e in errors(out, cat, "narrative"))


# --- free-text consistency -----------------------------------------------------------------------------

def test_second_episode_recommendation_text_contradicts_the_minima():
    text = json.loads(SECOND_TRACE.read_text(encoding="utf-8"))["interpretation"]["overall_recommendation"]["statement"]
    result = narrative_check([("overall_recommendation", text)], MINIMA, MINIMA)
    assert result["result"] == "FAIL"
    (c,) = result["contradictions"]
    assert c["objective_field"] == "preferred_for_production_commitment" and c["outside"] == ["CASE_3"]
    assert len(result["consistent"]) == 2  # the total-disturbance and flight-test clauses agree


@pytest.mark.parametrize("text", [
    "INTERVENTION_3 is useful when the objective is to reduce committed exposure while upstream development continues.",
    "INTERVENTION_3 is not the best option for minimizing production commitment.",
    "Production commitment is minimized by INTERVENTION_1 or INTERVENTION_2.",
])
def test_valid_framings_do_not_trigger_contradictions(text):
    assert narrative_check([("f", text)], MINIMA, MINIMA)["contradictions"] == []


def test_contradiction_in_overall_text_fails_validation(out, cat):
    out.overall_recommendation.statement = "For limiting production commitment, INTERVENTION_3 is the best choice."
    assert any("free text contradicts preferred_for_production_commitment" in e for e in errors(out, cat, "narrative"))


def test_contradiction_requires_human_review_and_blocks_validated_status(out, tmp_path):
    out.overall_recommendation.statement = "Limiting production commitment favors INTERVENTION_3."
    raw = out.model_dump()
    meta = run_episode(FakeClient(out), PROJECT_ROOT, tmp_path)
    assert meta["status"] == WITH_ERRORS and meta["usable_downstream"] is False
    assert meta["human_review_required"] is True and meta["authoritative_preferences"] is None
    trace = json.loads(open(meta["trace_json"], encoding="utf-8").read())
    assert trace["interpretation"] == raw  # raw text preserved, not repaired
    assert "narrative validation failed" in trace["validation"]["human_review"]["reasons"]


def test_validated_only_when_structured_and_narrative_agree(out, tmp_path):
    meta = run_episode(FakeClient(out), PROJECT_ROOT, tmp_path)
    assert meta["status"] == VALIDATED and meta["usable_downstream"] is True
    assert {k: set(v) for k, v in meta["authoritative_preferences"].items()} == MINIMA
    assert meta["overall_recommendation_is_authoritative"] is False


def test_schema_requires_the_structured_fields(out):
    data = out.model_dump()
    del data["preferred_for_flight_test"]
    with pytest.raises(Exception):
        PredictiveInterventionOutput.model_validate(data)


# --- preserved earlier episodes ------------------------------------------------------------------------

def test_second_episode_files_are_unchanged():
    for rel, digest in PRESERVED.items():
        assert hashlib.sha256((PROJECT_ROOT / rel).read_bytes()).hexdigest() == digest, rel
