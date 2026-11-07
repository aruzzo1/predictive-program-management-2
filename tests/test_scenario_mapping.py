"""Tests for the schedule-to-WTM scenario mapping (ppm_agent.tools.scenario_mapping, outputs/simulation/)."""

import copy
import hashlib

import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.scenario_mapping import (
    INPUTS,
    REFERENCE_EXPOSED_DELAY_DAYS,
    build_mapping,
    exposed_delay,
    normalize,
    render_outputs,
    validate_mapping,
)

OUT_DIR = PROJECT_ROOT / "outputs" / "simulation"


@pytest.fixture(scope="module")
def mapping():
    return build_mapping(PROJECT_ROOT)


def scenario(mapping, sid):
    return next(s for s in mapping["scenarios"] if s["scenario_id"] == sid)


def test_mapping_validates(mapping):
    assert validate_mapping(mapping) == []


def test_outputs_are_reproducible(mapping):
    for name, text in render_outputs(mapping).items():
        assert (OUT_DIR / name).read_text(encoding="utf-8") == text, f"outputs/simulation/{name} is out of date"


def test_mapping_reads_inputs_without_changing_them():
    before = {p: hashlib.sha256((PROJECT_ROOT / p).read_bytes()).hexdigest() for p in INPUTS}
    build_mapping(PROJECT_ROOT)
    assert {p: hashlib.sha256((PROJECT_ROOT / p).read_bytes()).hexdigest() for p in INPUTS} == before


# --- formula -------------------------------------------------------------------------------------------

def test_exposed_delay_formula():
    assert exposed_delay(8, 4) == 4
    assert exposed_delay(4, 0) == 4
    assert exposed_delay(8, 4, recovery_days=4) == 0
    assert exposed_delay(3, 4) == 0  # float absorbs the whole slip
    with pytest.raises(ValueError):
        exposed_delay(-1, 4)


def test_normalization_uses_the_synthetic_reference(mapping):
    assert REFERENCE_EXPOSED_DELAY_DAYS == 4.0 == mapping["reference_exposed_delay_days"]
    assert normalize(4) == 1.0 and normalize(2) == 0.5 and normalize(0) == 0.0
    assert "Not a probability" in mapping["reference_note"]


def test_activity_to_node_mapping(mapping):
    nodes = mapping["activity_to_dsm_node"]
    assert len(nodes) == 35 and (nodes["A210"], nodes["A305"], nodes["A410"]) == ("D4", "D5", "D6")


# --- scenarios -----------------------------------------------------------------------------------------

def test_disturbance_1(mapping):
    s = scenario(mapping, "DISTURBANCE_1")
    assert (s["gross_slip_days"], s["available_float_days"], s["exposed_delay_days"]) == (8.0, 4.0, 4.0)
    assert (s["path_end_activity"], s["path_end_float_days"]) == ("A230", 4.0)
    assert s["initial_wtm_state"] == {"D1": 0.0, "D2": 0.0, "D3": 0.0, "D4": 1.0, "D5": 0.0, "D6": 0.0, "D7": 0.0,
                                      "D8": 0.0}


def test_disturbance_2(mapping):
    s = scenario(mapping, "DISTURBANCE_2")
    assert (s["gross_slip_days"], s["available_float_days"], s["exposed_delay_days"]) == (4.0, 0.0, 4.0)
    assert (s["path_end_activity"], s["path_end_float_days"]) == ("A325", 0.0)
    assert [n for n, v in s["initial_wtm_state"].items() if v] == ["D5"] and s["initial_wtm_state"]["D5"] == 1.0


def test_intervention_1(mapping):
    s = scenario(mapping, "INTERVENTION_1")
    assert (s["gross_slip_days"], s["recovery_days"], s["available_float_days"]) == (8.0, 4.0, 4.0)
    assert s["exposed_delay_days"] == 0.0 and s["initial_wtm_state"]["D4"] == 0.0
    assert not any(s["initial_wtm_state"].values())


def test_intervention_2_acts_at_d6_not_on_the_initial_state(mapping):
    s = scenario(mapping, "INTERVENTION_2")
    assert s["initial_wtm_state"] == scenario(mapping, "DISTURBANCE_1")["initial_wtm_state"]
    (sem,) = s["intervention_semantics"]
    assert (sem["acts_at_node"], sem["type"], sem["max_absorption_days"], sem["max_absorption_normalized"]) == \
        ("D6", "DOWNSTREAM_DELAY_ABSORPTION", 4, 1.0)
    assert sem["changes_initial_state"] is False


def test_intervention_3_is_exposure_management_at_d8(mapping):
    s = scenario(mapping, "INTERVENTION_3")
    (sem,) = s["intervention_semantics"]
    assert (sem["acts_at_node"], sem["type"]) == ("D8", "EXPOSURE_MANAGEMENT")
    assert (sem["pre_maturity_commitment_fraction"], sem["post_maturity_commitment_fraction"]) == (0.40, 0.60)
    assert sem["changes_upstream_propagation"] is False
    assert not any(s["initial_wtm_state"].values())  # frozen base is BASELINE


def test_wrong_mapping_is_rejected(mapping):
    bad = copy.deepcopy(mapping)
    scenario(bad, "DISTURBANCE_1")["initial_wtm_state"]["D4"] = 2.0
    scenario(bad, "INTERVENTION_1")["exposed_delay_days"] = 4.0
    errors = validate_mapping(bad)
    assert any(e.startswith("DISTURBANCE_1: expected") for e in errors)
    assert any(e.startswith("INTERVENTION_1: expected") for e in errors)


def test_non_finite_values_are_rejected(mapping):
    bad = copy.deepcopy(mapping)
    scenario(bad, "DISTURBANCE_2")["initial_wtm_state"]["D5"] = float("inf")
    assert any("non-finite" in e for e in validate_mapping(bad))
