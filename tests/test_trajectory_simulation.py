"""Tests for the deterministic trajectory and intervention comparison (outputs/simulation/)."""

import copy
import json

import numpy as np
import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.trajectory_simulation import HORIZON, STATEMENT, render_text_outputs, run, simulate, validate
from ppm_agent.tools.wtm_tools import load_frozen_weighted

OUT_DIR = PROJECT_ROOT / "outputs" / "simulation"
NODES = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]


@pytest.fixture(scope="module")
def res():
    return run(PROJECT_ROOT)


def case(res, cid):
    return next(c for c in res["cases"] if c["case_id"] == cid)


def unit(node, value=1.0):
    x = np.zeros(8)
    x[NODES.index(node)] = value
    return x


def test_simulation_validates(res):
    assert validate(res, PROJECT_ROOT) == []


def test_outputs_are_reproducible(res):
    for name, text in render_text_outputs(res).items():
        assert (OUT_DIR / name).read_text(encoding="utf-8") == text, f"outputs/simulation/{name} is out of date"


def test_same_horizon_for_every_case(res):
    assert all([r["t"] for r in c["trajectory"]] == list(range(HORIZON + 1)) for c in res["cases"])


# --- the four cases ------------------------------------------------------------------------------------

def test_no_action(res):
    m = case(res, "CASE_0")["metrics"]
    assert (m["peak_total"], m["peak_step"]) == (1.3125, 2)
    assert case(res, "CASE_0")["initial_state"]["D4"] == 1.0


def test_intervention_1_starts_and_stays_at_zero(res):
    c = case(res, "CASE_1")
    assert not any(c["initial_state"].values())
    assert c["metrics"]["cumulative_total"] == 0.0 and c["metrics"]["peak_step"] is None


def test_intervention_2_absorbs_first_d6_arrival(res):
    c = case(res, "CASE_2")
    t1 = c["trajectory"][1]
    assert (t1["D6_before_absorption"], t1["absorbed"], t1["D6"]) == (0.75, 0.75, 0.0)
    assert (c["metrics"]["intervention_used"], c["metrics"]["intervention_unused"]) == (0.75, 0.25)
    assert c["metrics"]["cumulative_D6_arrived_before_absorption"] == 0.75
    assert all(r["total"] == 0.0 for r in c["trajectory"][1:])


def test_intervention_2_capacity_is_cumulative_and_binds_when_exceeded():
    ids, W = load_frozen_weighted(PROJECT_ROOT / "outputs" / "dsm")
    rows = simulate(ids, W, unit("D4", 2.0), absorb_capacity=1.0)  # test-only input: D6 receives 1.5 at t1
    assert rows[1]["absorbed"] == 1.0 and rows[1]["D6"] == 0.5
    assert all(r["absorbed"] == 0.0 for r in rows[2:])  # exhausted capacity never resets
    assert max(r["cumulative_absorbed"] for r in rows) == 1.0


def test_intervention_3_changes_commitment_not_propagation(res):
    c0, c3 = case(res, "CASE_0"), case(res, "CASE_3")
    assert all(a[n] == b[n] for a, b in zip(c0["trajectory"], c3["trajectory"]) for n in NODES)
    m = c3["metrics"]
    assert m["cumulative_D8"] == c0["metrics"]["cumulative_D8"]
    assert m["cumulative_D8_committed_pre_maturity"] == round(m["cumulative_D8"] * 0.4, 10)
    assert abs(m["cumulative_D8_committed_pre_maturity"] + m["cumulative_D8_gated_deferred"] - m["cumulative_D8"]) < 1e-9
    ch = c3["change_vs_no_action"]
    assert ch["cumulative_D8"]["absolute_reduction"] == 0.0
    assert ch["cumulative_D8_committed_pre_maturity"]["percent_reduction"] == 60.0


def test_comparison_reports_facts_without_a_composite_score():
    doc = json.loads((OUT_DIR / "intervention_comparison.json").read_text(encoding="utf-8"))
    assert doc["statement"] == STATEMENT
    text = json.dumps(doc).lower()
    assert '"score"' not in text and '"rank"' not in text and "best_intervention" not in text
    assert STATEMENT in (OUT_DIR / "predictive_simulation_summary.md").read_text(encoding="utf-8")


def test_secondary_disturbance_is_accepted():
    ids, W = load_frozen_weighted(PROJECT_ROOT / "outputs" / "dsm")
    rows = simulate(ids, W, unit("D5"))
    assert rows[1]["D6"] == 0.5 and all(np.isfinite(r["total"]) for r in rows)


# --- validation rules ----------------------------------------------------------------------------------

def test_capacity_reset_is_rejected(res):
    bad = copy.deepcopy(res)
    c2 = case(bad, "CASE_2")["trajectory"]
    c2[5]["remaining_capacity"], c2[5]["cumulative_absorbed"] = 1.0, 0.0
    assert any("capacity reset" in e for e in validate(bad, PROJECT_ROOT))


def test_altered_upstream_propagation_in_case_3_is_rejected(res):
    bad = copy.deepcopy(res)
    case(bad, "CASE_3")["trajectory"][3]["D6"] = 0.1
    assert any("CASE_3 altered upstream propagation" in e for e in validate(bad, PROJECT_ROOT))


def test_negative_values_are_rejected(res):
    bad = copy.deepcopy(res)
    case(bad, "CASE_0")["trajectory"][2]["D7"] = -0.1
    assert any("negative disturbance" in e for e in validate(bad, PROJECT_ROOT))
