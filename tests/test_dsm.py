"""Tests for the deterministic node-level DSM (ppm_agent.tools.dsm_tools, outputs/dsm/)."""

import copy
import json

import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.synthetic.validation import load_dataset
from ppm_agent.tools import dsm_tools
from ppm_agent.tools.dsm_tools import (
    AGENTIC_DECISIONS,
    OUTPUT_FILES,
    build_dsm,
    read_matrix_csv,
    render_outputs,
    validate_dsm,
    validate_structure,
)

SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"
DSM_DIR = PROJECT_ROOT / "outputs" / "dsm"
NODES = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]


@pytest.fixture(scope="module")
def ds():
    return load_dataset(SYNTHETIC_DIR)


@pytest.fixture(scope="module")
def dsm(ds):
    return build_dsm(ds)


def at(dsm, matrix, row, col):
    return dsm[matrix][NODES.index(row)][NODES.index(col)]


def broken(dsm, mutate):
    d = copy.deepcopy(dsm)
    mutate(d)
    return validate_dsm(d)


# --- structure ---------------------------------------------------------------------------------------

def test_dsm_validates(dsm):
    assert validate_dsm(dsm) == []


def test_eight_nodes_and_square_matrices(dsm):
    assert dsm["node_ids"] == NODES
    for m in ("binary", "weighted"):
        assert len(dsm[m]) == 8 and all(len(row) == 8 for row in dsm[m])
    assert {v for row in dsm["binary"] for v in row} <= {0, 1}
    assert all(0.0 <= v <= 1.0 for row in dsm["weighted"] for v in row)


def test_orientation_row_is_source(dsm):
    assert at(dsm, "binary", "D5", "D6") == 1  # test-aircraft availability feeds flight test
    assert at(dsm, "binary", "D6", "D5") == 0
    assert at(dsm, "binary", "D7", "D8") == 1 and at(dsm, "binary", "D8", "D7") == 0


def test_diagonal_is_zero_except_the_rework_feedback(dsm):
    assert [at(dsm, "binary", n, n) for n in NODES] == [0, 0, 0, 0, 0, 1, 0, 0]
    (cell,) = [c for c in dsm["cells"] if c["row"] == c["column"]]
    assert cell["entry_type"] == "FEEDBACK"
    assert [(d["source_activity"], d["target_activity"]) for d in cell["contributing_dependencies"]] == [("A425", "A410")]


def test_coupled_blocks(dsm):
    assert dsm["coupled_blocks"] == [["D2", "D3"], ["D4", "D6"]]


# --- weights and uncertainty -------------------------------------------------------------------------

def test_weights_follow_the_documented_policy(dsm):
    assert at(dsm, "weighted", "D4", "D6") == 0.75  # Q01 PARTIALLY_SUPPORTED
    assert at(dsm, "weighted", "D5", "D6") == 0.50  # Q04 UNRESOLVED, retained
    assert at(dsm, "weighted", "D3", "D8") == 0.75  # Q07 EXPLICIT_PASSAGE, no agentic decision
    assert at(dsm, "weighted", "D1", "D3") == 0.50  # Q07 FRAGMENTARY
    assert at(dsm, "weighted", "D1", "D2") == 0.25  # synthetic sequencing
    assert at(dsm, "weighted", "D2", "D5") == 0.50  # max of synthetic 0.25 and Q07 fragmentary 0.50


def test_unresolved_dependency_is_retained_not_dropped(dsm):
    reg = {(d["source_activity"], d["target_activity"]): d for d in dsm["registry"]}
    q04 = reg[("A325", "A405")]
    assert q04["agentic_decision"] == "UNRESOLVED" and q04["weight"] == 0.50 and q04["included_in_matrix"]
    assert at(dsm, "binary", "D5", "D6") == 1


def test_not_supported_decision_is_excluded(ds, monkeypatch):
    monkeypatch.setitem(AGENTIC_DECISIONS, ("A325", "A405"), {**AGENTIC_DECISIONS[("A325", "A405")],
                                                               "decision": "NOT_SUPPORTED"})
    dsm = build_dsm(ds)
    reg = {(d["source_activity"], d["target_activity"]): d for d in dsm["registry"]}
    assert reg[("A325", "A405")]["weight"] == 0.0 and not reg[("A325", "A405")]["included_in_matrix"]
    assert at(dsm, "binary", "D5", "D6") == 0
    assert validate_dsm(dsm) == []


def test_recorded_agentic_decisions_match_the_traces():
    for (src, tgt), info in AGENTIC_DECISIONS.items():
        path = PROJECT_ROOT / info["trace"]
        if not path.is_file():
            pytest.skip(f"trace not present: {info['trace']}")
        trace = json.loads(path.read_text(encoding="utf-8"))
        assert trace["state"]["decision"]["decision"] == info["decision"], info["trace"]
        assert trace["agent_mode"] == "REAL_LLM_MODE"


# --- traceability and validation rules ----------------------------------------------------------------

def test_every_nonzero_entry_traces_to_approved_dependencies(dsm, ds):
    approved = {d["dependency_id"] for d in ds["dependencies"]}
    nonzero = {f"{r}->{c}" for r in NODES for c in NODES if at(dsm, "binary", r, c)}
    assert nonzero == {c["cell"] for c in dsm["cells"]}
    for c in dsm["cells"]:
        assert c["contributing_dependencies"]
        assert {d["dependency_id"] for d in c["contributing_dependencies"]} <= approved


def test_registry_covers_all_43_dependencies(dsm):
    scopes = [d["scope"] for d in dsm["registry"]]
    assert len(scopes) == 43
    assert (scopes.count("INTER_NODE"), scopes.count("INTRA_NODE"), scopes.count("FEEDBACK")) == (15, 26, 2)


def test_unexplained_entry_is_rejected(dsm):
    def mutate(d):
        d["binary"][NODES.index("D8")][NODES.index("D1")] = 1
        d["weighted"][NODES.index("D8")][NODES.index("D1")] = 0.25
    assert any("D8->D1: nonzero entry has no provenance" in e for e in broken(dsm, mutate))


def test_invalid_values_are_rejected(dsm):
    def mutate(d):
        d["binary"][0][1] = 2
        d["weighted"][0][2] = 1.5
    errors = broken(dsm, mutate)
    assert any("D1->D2: binary value 2 is not 0/1" in e for e in errors)
    assert any("D1->D3: weight 1.5 outside 0.0-1.0" in e for e in errors)


def test_non_feedback_diagonal_is_rejected(dsm):
    def mutate(d):
        cell = next(c for c in d["cells"] if c["cell"] == "D6->D6")
        cell["entry_type"] = "FORWARD"
    assert any("diagonal entry allowed only for FEEDBACK_REWORK" in e for e in broken(dsm, mutate))


def test_dropped_feedback_is_rejected(dsm):
    def mutate(d):
        i = NODES.index("D6")
        d["binary"][i][i], d["weighted"][i][i] = 0, 0.0
        d["cells"] = [c for c in d["cells"] if c["cell"] != "D6->D6"]
    errors = broken(dsm, mutate)
    assert any("is not present in the DSM" in e for e in errors)


# --- v1.1 structural corrections ---------------------------------------------------------------------

def cell(dsm, key):
    return next(c for c in dsm["cells"] if c["cell"] == key)


def test_v1_1_structure_validates(dsm):
    assert validate_structure(dsm) == []


def test_software_flight_test_loop(dsm):
    fwd, back = cell(dsm, "D4->D6"), cell(dsm, "D6->D4")
    assert fwd["entry_type"] == "FORWARD" and fwd["weight"] == 0.75
    assert [(d["source_activity"], d["target_activity"]) for d in fwd["contributing_dependencies"]] == [("A230", "A405")]
    assert back["entry_type"] == "FEEDBACK" and back["weight"] == 0.50
    assert [(d["source_activity"], d["target_activity"], d["relationship_type"])
            for d in back["contributing_dependencies"]] == [("A415", "A225", "FEEDBACK_REWORK")]


def test_q08_now_crosses_d7_to_d8(dsm):
    c = cell(dsm, "D7->D8")
    assert [(d["source_activity"], d["target_activity"]) for d in c["contributing_dependencies"]] == [("A430", "A510")]
    assert c["weight"] == 0.50  # Q08 agentic decision UNRESOLVED governs


def test_structure_rejects_raised_q04_weight(dsm):
    d = copy.deepcopy(dsm)
    next(r for r in d["registry"] if (r["source_activity"], r["target_activity"]) == ("A325", "A405"))["weight"] = 0.75
    assert any("Q04" in e for e in validate_structure(d))


def test_structure_rejects_forward_d6_to_d4(dsm):
    d = copy.deepcopy(dsm)
    cell(d, "D6->D4")["entry_type"] = "FORWARD"
    assert any("D6->D4" in e for e in validate_structure(d))


# --- outputs -----------------------------------------------------------------------------------------

def test_outputs_are_reproducible(dsm):
    texts = render_outputs(dsm, SYNTHETIC_DIR)
    assert sorted(texts) == sorted(OUTPUT_FILES)
    for name, text in texts.items():
        assert (DSM_DIR / name).read_text(encoding="utf-8") == text, f"outputs/dsm/{name} is out of date; rebuild it"


def test_csv_files_match_the_matrices(dsm):
    cols, rows = read_matrix_csv(DSM_DIR / "binary_dsm.csv")
    assert cols == NODES and [[int(v) for v in r] for r in rows] == dsm["binary"]
    cols, rows = read_matrix_csv(DSM_DIR / "weighted_dsm.csv")
    assert cols == NODES and [[float(v) for v in r] for r in rows] == dsm["weighted"]


def test_provenance_states_illustrative_and_deterministic():
    prov = json.loads((DSM_DIR / "dsm_provenance.json").read_text(encoding="utf-8"))
    assert "not a historical F-35 DSM" in prov["statement"]
    assert prov["weights_are_not_probabilities"] is True
    assert "no LLM" in prov["computed_by"]
    assert prov["orientation"] == dsm_tools.ORIENTATION
