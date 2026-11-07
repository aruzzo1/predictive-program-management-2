"""Tests for the Illustrative Work Transformation / Weighted Propagation Matrix layer (outputs/wtm/)."""

import copy
import importlib.util
import json
import math

import numpy as np
import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.wtm_tools import (
    HORIZON,
    INPUT_FILES,
    STATEMENT,
    analyse,
    sha256,
    step,
    validate,
)

DSM_DIR = PROJECT_ROOT / "outputs" / "dsm"
WTM_DIR = PROJECT_ROOT / "outputs" / "wtm"
NODES = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
RHO = (0.5 + math.sqrt(0.25 + 4 * 0.375)) / 2  # closed form for the D4/D6 block: 0.9114...


@pytest.fixture(scope="module")
def res():
    return analyse(DSM_DIR)


def unit(node):
    x = np.zeros(8)
    x[NODES.index(node)] = 1.0
    return x


def test_wtm_validates(res):
    assert validate(res, DSM_DIR) == []


def test_analysis_does_not_alter_the_frozen_dsm():
    before = {n: sha256(DSM_DIR / n) for n in INPUT_FILES}
    analyse(DSM_DIR)
    assert {n: sha256(DSM_DIR / n) for n in INPUT_FILES} == before


def test_outputs_are_reproducible(res):
    spec = importlib.util.spec_from_file_location("build_wtm", PROJECT_ROOT / "scripts" / "build_wtm.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    for name, text in build.build_texts(res).items():
        assert (WTM_DIR / name).read_text(encoding="utf-8") == text, f"outputs/wtm/{name} is out of date; rebuild it"


# --- orientation ---------------------------------------------------------------------------------------

def test_update_sums_each_column_of_sources(res):
    W = res["W"]
    assert np.array_equal(step(W, unit("D4")), W[NODES.index("D4")])  # D4's row = what D4 sends
    x = step(W, unit("D5"))
    assert x[NODES.index("D6")] == 0.50 and x.sum() == 0.50  # D5 -> D6 only


def test_d8_is_a_sink(res):
    assert not step(res["W"], unit("D8")).any()
    assert res["W"][:, NODES.index("D8")].any()


# --- eigenstructure ------------------------------------------------------------------------------------

def test_eigenvalues_match_the_closed_form(res):
    got = sorted(e["real"] for e in res["eigenvalues"])
    expected = sorted([RHO, 0.5 - RHO, 0.25, -0.25, 0.0, 0.0, 0.0, 0.0])
    assert all(abs(a - b) < 1e-9 for a, b in zip(got, expected))
    assert all(e["imag"] == 0.0 for e in res["eigenvalues"])
    assert abs(res["spectral_radius"] - RHO) < 1e-9 and abs(res["dominant_eigenvalue"] - RHO) < 1e-9
    assert res["raw_behaviour"] == "DECAY"
    assert res["max_block_vs_full_eigen_gap"] < 1e-6


def test_coupled_blocks_and_feedback(res):
    assert res["coupled_blocks"] == [["D2", "D3"], ["D4", "D6"]]
    cf = res["d4_d6"]
    assert (cf["w46"], cf["w64"], cf["w66"], cf["loop_gain_w46_x_w64"]) == (0.75, 0.5, 0.5, 0.375)


# --- D4 propagation ------------------------------------------------------------------------------------

def test_d4_propagation_matches_hand_calculation(res):
    rows = res["propagation"]
    assert [r["t"] for r in rows] == list(range(HORIZON + 1))
    assert [rows[1][n] for n in NODES] == [0, 0, 0, 0, 0, 0.75, 0, 0]
    assert [rows[2][n] for n in NODES] == [0, 0, 0, 0.375, 0, 0.375, 0.1875, 0.375]
    assert [rows[3][n] for n in NODES] == [0, 0, 0, 0.1875, 0, 0.46875, 0.09375, 0.28125]
    assert [r["total_magnitude"] for r in rows[:3]] == [1.0, 0.75, 1.3125]
    assert [r["behaviour"] for r in rows] == ["INITIAL", "DECAYING", "AMPLIFYING", "DECAYING", "PERSISTENT",
                                              "DECAYING", "DECAYING"]
    assert rows[2]["dominant_node"] == "D4/D6/D8"  # tie shown, not hidden
    assert all(rows[t][n] == 0 for t in range(HORIZON + 1) for n in ("D1", "D2", "D3", "D5"))


def test_cumulative_total_is_finite_and_accumulates_at_d8(res):
    inf = res["cumulative_infinite"]
    assert (inf["D4"], inf["D6"], inf["D7"], inf["D8"]) == (4.0, 6.0, 1.5, 3.75)
    cum = [r["cumulative_D8"] for r in res["propagation"]]
    assert cum == sorted(cum) and cum[-1] < inf["D8"]


# --- validation rules ----------------------------------------------------------------------------------

def test_unexplained_transformation_is_rejected(res):
    bad = copy.deepcopy(res)
    bad["W"] = bad["W"] * 0.9  # e.g. a silent rescale to force faster convergence
    assert any("unexplained transformation" in e for e in validate(bad, DSM_DIR))


def test_transposed_matrix_is_rejected(res):
    bad = copy.deepcopy(res)
    bad["W"] = bad["W"].T.copy()
    assert any("unexplained transformation" in e for e in validate(bad, DSM_DIR))


def test_truncated_propagation_is_rejected(res):
    bad = copy.deepcopy(res)
    bad["propagation"] = bad["propagation"][:4]
    assert any("stopping rule" in e for e in validate(bad, DSM_DIR))


def test_provenance_and_summary_document_the_model():
    prov = json.loads((WTM_DIR / "wtm_provenance.json").read_text(encoding="utf-8"))
    assert prov["statement"] == STATEMENT and prov["equation"].startswith("x(t+1) = W^T x(t)")
    assert "no LLM" in prov["computed_by"] and prov["stopping_rule"].startswith("Fixed horizon")
    assert len(prov["transformations"]) == 2
    summary = (WTM_DIR / "wtm_summary.md").read_text(encoding="utf-8")
    assert STATEMENT in summary and "Illustrative Work Transformation / Weighted Propagation Matrix" in summary
