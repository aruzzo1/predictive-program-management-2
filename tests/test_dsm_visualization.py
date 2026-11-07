"""Tests for the read-only DSM visualization package (outputs/dsm_visualization/)."""

import csv
import json

import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.dsm_tools import read_matrix_csv
from ppm_agent.tools.dsm_visualization import (
    INPUT_FILES,
    coupled_cells,
    load_frozen_dsm,
    partitioned_order,
    render_package,
    sha256,
    sinks_and_sources,
    submatrix,
)

DSM_DIR = PROJECT_ROOT / "outputs" / "dsm"
VIS_DIR = PROJECT_ROOT / "outputs" / "dsm_visualization"


@pytest.fixture(scope="module")
def frozen():
    return load_frozen_dsm(DSM_DIR)


def test_rendering_does_not_alter_the_frozen_dsm():
    before = {n: sha256(DSM_DIR / n) for n in INPUT_FILES}
    render_package(DSM_DIR)
    assert {n: sha256(DSM_DIR / n) for n in INPUT_FILES} == before


def test_package_matches_a_fresh_build():
    for name, text in render_package(DSM_DIR).items():
        assert (VIS_DIR / name).read_text(encoding="utf-8") == text, f"{name} is out of date; rebuild it"


def test_manifest_fingerprints_match_the_frozen_inputs():
    manifest = json.loads((VIS_DIR / "visualization_manifest.json").read_text(encoding="utf-8"))
    assert manifest["inputs_sha256"] == {f"outputs/dsm/{n}": sha256(DSM_DIR / n) for n in INPUT_FILES}


@pytest.mark.parametrize("matrix", ["binary", "weighted"])
def test_labeled_matrices_equal_the_frozen_matrices(matrix):
    _, frozen_rows = read_matrix_csv(DSM_DIR / f"{matrix}_dsm.csv")
    with (VIS_DIR / f"{matrix}_dsm_labeled.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0][0].startswith("# row = source / upstream node")
    assert rows[1][1] == "D1 Requirements / KPP Definition"
    assert [r[0].split()[0] for r in rows[2:]] == ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
    assert [[float(v) for v in r[1:]] for r in rows[2:]] == [[float(v) for v in r] for r in frozen_rows]


def test_coupled_cells_sink_and_source(frozen):
    assert coupled_cells(frozen) == {("D2", "D3"), ("D3", "D2"), ("D4", "D6"), ("D6", "D4"), ("D6", "D6")}
    assert sinks_and_sources(frozen) == (["D8"], ["D1"])


def test_d4_d6_submatrix(frozen):
    assert submatrix(frozen, ["D4", "D6"]) == [[0.0, 0.75], [0.50, 0.50]]


def test_partitioned_view_is_sequential_outside_blocks(frozen):
    order = partitioned_order(frozen)
    assert order == [["D1"], ["D2", "D3"], ["D5"], ["D4", "D6"], ["D7"], ["D8"]]
    flat = [n for g in order for n in g]
    group = {n: k for k, g in enumerate(order) for n in g}
    ids, b = frozen["ids"], frozen["binary"]
    for a, r in enumerate(flat):
        for c in flat[:a]:
            if b[ids.index(r)][ids.index(c)]:
                assert group[r] == group[c], f"{r}->{c} lies below the diagonal outside a block"


def test_explanation_states_the_key_points():
    text = (VIS_DIR / "dsm_explained.md").read_text(encoding="utf-8")
    for phrase in ("ROW = SOURCE / UPSTREAM node. COLUMN = TARGET / DOWNSTREAM node.", "not probabilities",
                   "0.00 & 0.75 \\\\ 0.50 & 0.50", "a historical F-35 DSM", "It is not calculated here.",
                   "D8 Production Commitment / Rework Exposure** has out-degree 0"):
        assert phrase in text, phrase


def test_png_copies_exist_when_built():
    pngs = [VIS_DIR / n for n in ("binary_dsm_heatmap.png", "weighted_dsm_heatmap.png", "dsm_dependency_network.png")]
    if not all(p.is_file() for p in pngs):
        pytest.skip("PNG copies not built (no headless browser)")
    assert all(p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for p in pngs)
