"""Tests for the Predictive Simulation and Intervention Agent. No network: real mode uses a fake client."""

import copy
import hashlib
import json
import typing

import pytest
from pydantic import ValidationError

from ppm_agent.agents.llm import MOCK_AGENT_MODE, REAL_LLM_MODE, LLMCallError, LLMConfigurationError
from ppm_agent.agents.predictive_intervention import (
    INPUTS,
    LIMITATIONS,
    build_catalogue,
    mock_interpret,
    numeric_check,
    objective_facts,
    run_episode,
    validate_output,
)
from ppm_agent.config import PROJECT_ROOT
from ppm_agent.models.intervention import PredictiveInterventionOutput


@pytest.fixture(scope="module")
def cat():
    return build_catalogue(PROJECT_ROOT)


@pytest.fixture()
def out(cat):
    return mock_interpret(cat)


class FakeClient:
    mode, model = REAL_LLM_MODE, "fake-model"

    def __init__(self, result):
        self.result, self.calls = result, 0

    def complete(self, system, user, schema):
        self.calls += 1
        assert schema is PredictiveInterventionOutput and "do not write numerals" in user
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    def usage_summary(self):
        return {"provider": "fake", "model": self.model, "successful_responses": self.calls, "input_tokens": 1,
                "output_tokens": 1}


# --- structured output ---------------------------------------------------------------------------------

def _leaf_types(annotation, seen):
    """All concrete types reachable from an annotation, descending into nested Pydantic models."""
    args = typing.get_args(annotation)
    if typing.get_origin(annotation) is typing.Literal:
        yield from (type(a) for a in args)
    elif args:
        for a in args:
            yield from _leaf_types(a, seen)
    elif hasattr(annotation, "model_fields"):
        if annotation not in seen:
            seen.add(annotation)
            for field in annotation.model_fields.values():
                yield from _leaf_types(field.annotation, seen)
    else:
        yield annotation


def test_schema_is_strict_and_has_no_numeric_fields():
    assert all(f.is_required() for f in PredictiveInterventionOutput.model_fields.values())
    leaves = set(_leaf_types(PredictiveInterventionOutput, set()))
    assert leaves == {str, bool}  # the model cannot return numbers as values
    assert "human_review_required" in PredictiveInterventionOutput.model_fields


def test_human_review_field_is_required(out):
    data = out.model_dump()
    del data["human_review_required"]
    with pytest.raises(ValidationError):
        PredictiveInterventionOutput.model_validate(data)


def test_invalid_intervention_id_is_rejected_by_the_schema(out):
    data = out.model_dump()
    data["intervention_assessments"][0]["intervention_id"] = "INTERVENTION_9"
    with pytest.raises(ValidationError):
        PredictiveInterventionOutput.model_validate(data)


# --- deterministic validation --------------------------------------------------------------------------

def test_mock_output_validates(out, cat):
    v = validate_output(out, cat)
    assert v["result"] == "PASS", v["errors"]
    assert v["numeric_check"]["result"] == "PASS"


def test_catalogue_comes_from_frozen_outputs(cat):
    f = cat["facts"]
    assert (f["CASE_0.peak_total"], f["CASE_2.D6_first_arrival"], f["CASE_2.intervention_used"],
            f["CASE_2.intervention_unused"], f["INTERVENTION_2.capacity_normalized"]) == (1.3125, 0.75, 0.75, 0.25, 1.0)
    assert f["CASE_3.change.cumulative_D8_committed_pre_maturity.percent_reduction"] == 60.0
    assert cat["inputs_sha256"] == {p: hashlib.sha256((PROJECT_ROOT / p).read_bytes()).hexdigest() for p in INPUTS}


def test_unsupported_number_is_rejected(out, cat):
    bad = out.model_copy(deep=True)
    bad.no_action_assessment.statement = "Peak disturbance reaches 1.77 and falls by 37% by t12."
    check = numeric_check(bad, cat)
    assert check["result"] == "FAIL" and {u["numeral"] for u in check["unsupported"]} == {"1.77", "37%"}
    assert validate_output(bad, cat)["result"] == "FAIL"


def test_supported_numbers_and_identifiers_pass(out, cat):
    ok = out.model_copy(deep=True)
    ok.no_action_assessment.statement = ("CASE_0 peaks at 1.3125 at t2 and D6 receives 0.75; CASE_3 cuts committed D8 "
                                         "exposure by 60% (40% committed); see CASE_2.intervention_unused.")
    assert numeric_check(ok, cat)["result"] == "PASS"


def test_unknown_citation_and_missing_coverage_are_rejected(out, cat):
    bad = out.model_copy(deep=True)
    bad.overall_recommendation.cited_ids = ["CASE_9.peak_total"]
    bad.uncertainties = bad.uncertainties[:-1]
    errors = validate_output(bad, cat)["errors"]
    assert any("unknown id 'CASE_9.peak_total'" in e for e in errors)
    assert any(f"do not cover {list(LIMITATIONS)[-1]}" in e for e in errors)


def test_recommendations_must_reference_valid_cases_and_objectives(out, cat):
    bad = out.model_copy(deep=True)
    bad.preferred_intervention_by_objective = bad.preferred_intervention_by_objective[:2]
    bad.intervention_assessments[1].intervention_id = "INTERVENTION_3"
    errors = validate_output(bad, cat)["errors"]
    assert any("each objective once" in e for e in errors)
    assert any("CASE_2 paired with INTERVENTION_3" in e for e in errors)


def test_objective_facts_are_single_metric_minima(cat):
    obj = objective_facts(cat)
    assert obj["MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE"]["lowest_cases"] == ["CASE_1"]
    assert obj["PROTECT_FLIGHT_TEST_EXECUTION"]["lowest_cases"] == ["CASE_1", "CASE_2"]
    assert obj["LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE"]["lowest_cases"] == ["CASE_1", "CASE_2"]


# --- episodes ------------------------------------------------------------------------------------------

def test_mock_episode_writes_labelled_trace(tmp_path):
    meta = run_episode(None, PROJECT_ROOT, tmp_path)
    assert meta["agent_mode"] == MOCK_AGENT_MODE and meta["status"] == "VALIDATED"  # status renamed in contract v2
    trace = json.loads(open(meta["trace_json"], encoding="utf-8").read())
    assert trace["meta"]["model"] is None and "MOCK_AGENT_MODE" in open(meta["trace_md"], encoding="utf-8").read()


def test_real_mode_episode_does_not_modify_inputs(tmp_path, cat, out):
    before = {p: hashlib.sha256((PROJECT_ROOT / p).read_bytes()).hexdigest() for p in INPUTS}
    snapshot = copy.deepcopy(cat)
    meta = run_episode(FakeClient(out), PROJECT_ROOT, tmp_path, tmp_path / "summary.md")
    assert meta["status"] == "VALIDATED" and meta["llm"]["successful_responses"] == 1  # status renamed in contract v2
    assert {p: hashlib.sha256((PROJECT_ROOT / p).read_bytes()).hexdigest() for p in INPUTS} == before
    trace = json.loads(open(meta["trace_json"], encoding="utf-8").read())
    assert trace["input_catalogue"]["facts"] == snapshot["facts"]
    assert all(trace["validation"]["cited_fact_values"][k] == cat["facts"][k] for k in trace["validation"]["cited_fact_values"])
    assert (tmp_path / "summary.md").is_file()


def test_provider_call_failure_is_recorded_not_invented(tmp_path):
    meta = run_episode(FakeClient(LLMCallError("APITimeoutError: timed out")), PROJECT_ROOT, tmp_path)
    assert meta["status"] == "FAILED" and "timed out" in meta["failure"]
    trace = json.loads(open(meta["trace_json"], encoding="utf-8").read())
    assert trace["interpretation"] is None and trace["validation"] is None


def test_provider_configuration_error_is_fatal(tmp_path):
    with pytest.raises(LLMConfigurationError):
        run_episode(FakeClient(LLMConfigurationError("AuthenticationError")), PROJECT_ROOT, tmp_path)
    assert not list(tmp_path.glob("*.json"))
