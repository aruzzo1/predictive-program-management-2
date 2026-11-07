"""Illustrative Work Transformation / Weighted Propagation Matrix built on the frozen weighted DSM v1.1.

Deterministic Python (numpy) only; no model calls. The matrix is the frozen weighted DSM, read as-is.

Orientation (unchanged from the DSM): W[i, j] = weight of the influence of source node i on target node j
(row = source, column = target). A node's next-step disturbance is the weighted sum of what its sources
held at the current step:

    x_j(t+1) = sum_i W[i, j] * x_i(t)        i.e.   x(t+1) = W^T x(t)

W^T appears only inside that update; no transposed matrix is stored, and W is never scaled, normalized
or otherwise altered. Treating the ordinal DSM weights as multiplicative propagation coefficients is the
explicit modelling assumption of this layer.

Not done here: scenario disturbances (A210 +8, A305 +4), interventions, calibration.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from html import escape
from pathlib import Path

import numpy as np

from ppm_agent.tools.dsm_tools import read_matrix_csv
from ppm_agent.tools.dsm_visualization import FONT, HALO, INK, INK_2, MUTED, SURFACE, heatmap_svg, load_frozen_dsm

TERM = "Illustrative Work Transformation / Weighted Propagation Matrix"
STATEMENT = ("The WTM/propagation model is an illustrative test harness for evaluating the Predictive Program Management "
             "2.0 architecture. Its weights are evidence-calibrated ordinal values and synthetic assumptions, not "
             "historically calibrated probabilities.")
EQUATION = "x(t+1) = W^T x(t), i.e. x_j(t+1) = sum_i W[i, j] * x_i(t)"
ORIENTATION = "W[i, j]: row i = source / upstream node, column j = target / downstream node (DSM convention, unchanged)"
TRANSFORMATIONS = [
    "W is the frozen weighted DSM (outputs/dsm/weighted_dsm.csv), read element by element with no scaling, "
    "normalization, thresholding or reordering.",
    "W^T is used only inside the state update x(t+1) = W^T x(t), so that each target column sums its sources. It is "
    "not written to any file.",
]
HORIZON = 6
STOPPING_RULE = (f"Fixed horizon: iterate from t0 to t{HORIZON} as specified, with no early stopping. The long-run "
                 "behaviour beyond the horizon is characterised analytically by the spectral radius and, because it is "
                 "below 1, by the closed-form cumulative total (I - W^T)^-1 x(0).")
BEHAVIOUR_TOL = 0.05  # step ratio within 1 +/- 0.05 counts as persistent
INITIAL_NODE = "D4"
DECIMALS = 10
INPUT_FILES = ("weighted_dsm.csv", "binary_dsm.csv", "dsm_provenance.json")
OUTPUT_FILES = ("wtm_matrix.csv", "wtm_provenance.json", "eigenvalues.json", "structural_analysis.json",
                "software_disturbance_propagation.csv", "wtm_summary.md")


def _r(v: float) -> float:
    """Fixed rounding for reproducible text output (and no negative zero)."""
    return round(float(v), DECIMALS) + 0.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- loading and structure ----------------------------------------------------------------------------

def load_frozen_weighted(dsm_dir: Path) -> tuple[list[str], np.ndarray]:
    ids, rows = read_matrix_csv(dsm_dir / "weighted_dsm.csv")
    return ids, np.array([[float(v) for v in r] for r in rows])


def step(W: np.ndarray, x: np.ndarray) -> np.ndarray:
    """One propagation step: x(t+1) = W^T x(t) (row = source, column = target)."""
    return W.T @ x


def strongly_connected_components(ids: list[str], W: np.ndarray) -> list[list[str]]:
    """All SCCs (including singletons), each in D-order, listed by first member. Reachability via Warshall."""
    n = len(ids)
    reach = (W > 0) | np.eye(n, dtype=bool)
    for k in range(n):
        reach = reach | (reach[:, [k]] & reach[[k], :])
    comps, seen = [], set()
    for i in range(n):
        if i in seen:
            continue
        comp = [j for j in range(n) if reach[i, j] and reach[j, i]]
        seen.update(comp)
        comps.append([ids[j] for j in comp])
    return comps


def coupled(ids: list[str], W: np.ndarray, comp: list[str]) -> bool:
    return len(comp) > 1 or W[ids.index(comp[0]), ids.index(comp[0])] > 0


def eigen_by_blocks(ids: list[str], W: np.ndarray) -> list[dict]:
    """Eigenvalues as the union of the SCC diagonal blocks' eigenvalues (exact for a block-triangularizable matrix,
    and numerically robust for the zero eigenvalues of the acyclic part)."""
    out = []
    for comp in strongly_connected_components(ids, W):
        idx = [ids.index(n) for n in comp]
        for lam in np.linalg.eigvals(W[np.ix_(idx, idx)]):
            out.append({"block": comp, "real": _r(lam.real), "imag": _r(lam.imag), "modulus": _r(abs(lam))})
    return sorted(out, key=lambda e: (-e["modulus"], -e["real"], e["imag"], e["block"]))


def dominant_mode(W: np.ndarray, ids: list[str]) -> tuple[float, dict[str, float]]:
    """Dominant eigenvalue of W^T and its eigenvector, scaled to sum to 1: the long-run shape of a disturbance."""
    vals, vecs = np.linalg.eig(W.T)
    k = int(np.argmax(np.abs(vals)))
    v = np.real(vecs[:, k])
    v = v / v.sum()
    return float(np.real(vals[k])), {n: _r(x) for n, x in zip(ids, v)}


def d4_d6_closed_form(ids: list[str], W: np.ndarray) -> dict:
    a, b, c, d = (W[ids.index(r), ids.index(s)] for r, s in (("D4", "D4"), ("D4", "D6"), ("D6", "D4"), ("D6", "D6")))
    trace, det = a + d, a * d - b * c
    disc = (trace * trace - 4 * det) ** 0.5
    return {"w44": _r(a), "w46": _r(b), "w64": _r(c), "w66": _r(d), "loop_gain_w46_x_w64": _r(b * c),
            "characteristic_polynomial": f"lambda^2 - {_r(trace)} lambda + ({_r(det)}) = 0",
            "eigenvalues": [_r((trace + disc) / 2), _r((trace - disc) / 2)]}


# --- propagation --------------------------------------------------------------------------------------

def classify(ratio: float | None) -> str:
    if ratio is None:
        return "INITIAL"
    if ratio > 1 + BEHAVIOUR_TOL:
        return "AMPLIFYING"
    if ratio < 1 - BEHAVIOUR_TOL:
        return "DECAYING"
    return "PERSISTENT"


def propagate(ids: list[str], W: np.ndarray, x0: np.ndarray, horizon: int = HORIZON) -> list[dict]:
    rows, x, cumulative, prev = [], x0.copy(), np.zeros(len(ids)), None
    d8 = ids.index("D8")
    for t in range(horizon + 1):
        cumulative = cumulative + x
        total = float(np.abs(x).sum())
        ratio = None if prev in (None, 0.0) else total / prev
        rows.append({"t": t, **{n: _r(v) for n, v in zip(ids, x)}, "total_magnitude": _r(total),
                     "magnitude_excluding_D8": _r(total - abs(x[d8])),
                     "dominant_node": "/".join(n for n, v in zip(ids, x) if abs(v - x.max()) < 1e-12),  # ties shown
                     "step_ratio": None if ratio is None else _r(ratio),
                     "behaviour": classify(ratio), "cumulative_D8": _r(cumulative[d8])})
        prev, x = total, step(W, x)
    return rows


def analyse(dsm_dir: Path) -> dict:
    ids, W = load_frozen_weighted(dsm_dir)
    eig = eigen_by_blocks(ids, W)
    full = sorted(np.linalg.eigvals(W), key=lambda z: (-abs(z), -z.real))
    rho = max(e["modulus"] for e in eig)
    dom_val, dom_vec = dominant_mode(W, ids)
    comps = strongly_connected_components(ids, W)
    x0 = np.zeros(len(ids))
    x0[ids.index(INITIAL_NODE)] = 1.0
    rows = propagate(ids, W, x0)
    cumulative_inf = np.linalg.solve(np.eye(len(ids)) - W.T, x0) if rho < 1 else None
    out_strength = W.sum(axis=1)
    return {
        "ids": ids, "W": W, "eigenvalues": eig,
        "full_matrix_eigenvalues": [{"real": _r(z.real), "imag": _r(z.imag)} for z in full],
        "max_block_vs_full_eigen_gap": _r(max(abs(abs(complex(e["real"], e["imag"])) - abs(z))
                                              for e, z in zip(eig, full))),
        "spectral_radius": _r(rho),
        "dominant_eigenvalue": _r(dom_val), "dominant_mode": dom_vec,
        "raw_behaviour": "DECAY" if rho < 1 - 1e-9 else ("PERSIST" if rho <= 1 + 1e-9 else "AMPLIFY"),
        "components": comps, "coupled_blocks": [c for c in comps if coupled(ids, W, c)],
        "d4_d6": d4_d6_closed_form(ids, W),
        "out_strength": {n: _r(v) for n, v in zip(ids, out_strength)},
        "in_strength": {n: _r(v) for n, v in zip(ids, W.sum(axis=0))},
        "max_out_strength": _r(out_strength.max()),
        "propagation": rows,
        "cumulative_infinite": None if cumulative_inf is None else {n: _r(v) for n, v in zip(ids, cumulative_inf)},
        "input_sha256": {f"outputs/dsm/{n}": sha256(dsm_dir / n) for n in INPUT_FILES},
    }


# --- validation ---------------------------------------------------------------------------------------

def validate(res: dict, dsm_dir: Path) -> list[str]:
    errors: list[str] = []
    ids, W = res["ids"], res["W"]
    if len(ids) != 8 or W.shape != (8, 8):
        errors.append(f"expected 8 nodes and an 8x8 matrix, got {len(ids)} and {W.shape}")
        return errors
    frozen_ids, frozen = load_frozen_weighted(dsm_dir)
    if frozen_ids != ids or not np.array_equal(frozen, W):
        errors.append("WTM differs from the frozen weighted DSM (unexplained transformation)")
    if res["input_sha256"] != {f"outputs/dsm/{n}": sha256(dsm_dir / n) for n in INPUT_FILES}:
        errors.append("frozen DSM inputs changed")
    if not np.all(np.isfinite(W)) or not ((W >= 0) & (W <= 1)).all():
        errors.append("WTM entries must be finite and within [0, 1]")
    d4, d6, d8 = ids.index("D4"), ids.index("D6"), ids.index("D8")
    if not (W[d4, d6] > 0 and W[d6, d4] > 0 and ["D4", "D6"] in res["coupled_blocks"]):
        errors.append("D4 -> D6 -> D4 feedback not preserved")
    if W[d8].any() or not W[:, d8].any():
        errors.append("D8 must remain a sink (zero row, nonzero column)")
    if res["max_block_vs_full_eigen_gap"] > 1e-6:
        errors.append("block eigenvalues disagree with the full-matrix eigenvalues")
    cf = res["d4_d6"]["eigenvalues"]
    block = sorted(e["real"] for e in res["eigenvalues"] if e["block"] == ["D4", "D6"])
    if any(abs(a - b) > 1e-9 for a, b in zip(sorted(cf), block)):
        errors.append("D4/D6 block eigenvalues disagree with the closed form")
    if abs(res["spectral_radius"] - max(abs(e["real"]) for e in res["eigenvalues"])) > 1e-9:
        errors.append("spectral radius is not the largest eigenvalue modulus")
    rows = res["propagation"]
    if [r["t"] for r in rows] != list(range(HORIZON + 1)):
        errors.append(f"propagation must cover t0..t{HORIZON} (documented stopping rule)")
    if rows and (rows[0][INITIAL_NODE] != 1.0 or any(rows[0][n] for n in ids if n != INITIAL_NODE)):
        errors.append("initial state must be D4 = 1.0, all others 0")
    x = np.array([rows[0][n] for n in ids])
    for r in rows[1:]:
        x = step(W, x)
        if any(abs(_r(v) - r[n]) > 1e-9 for n, v in zip(ids, x)):
            errors.append(f"t{r['t']}: propagation is not reproducible from x(t+1) = W^T x(t)")
            break
    values = [v for r in rows for k, v in r.items() if isinstance(v, float)]
    if not all(np.isfinite(values)):
        errors.append("non-finite propagation values")
    return errors


# --- outputs ------------------------------------------------------------------------------------------

def _csv(header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def _fmt(v) -> str:
    if v is None:
        return ""
    return f"{v:.{DECIMALS}f}" if isinstance(v, float) else str(v)


def _json(doc) -> str:
    return json.dumps(doc, indent=2) + "\n"


def structural_document(res: dict) -> dict:
    ids = res["ids"]
    return {
        "term": TERM, "statement": STATEMENT, "orientation": ORIENTATION, "equation": EQUATION,
        "spectral_radius": res["spectral_radius"], "dominant_eigenvalue": res["dominant_eigenvalue"],
        "raw_behaviour": res["raw_behaviour"],
        "raw_behaviour_explanation": (
            "Spectral radius < 1: under repeated application of W^T, any initial disturbance eventually decays "
            "geometrically, at a long-run rate of about the spectral radius per step. Short-run growth is still possible, "
            "because the largest out-strength (row sum of W) exceeds 1."),
        "max_out_strength": res["max_out_strength"],
        "max_out_strength_note": "= ||W^T||_1, the largest possible one-step growth of the total (L1) disturbance.",
        "out_strength": res["out_strength"], "in_strength": res["in_strength"],
        "strongly_connected_components": res["components"],
        "coupled_blocks": res["coupled_blocks"],
        "coupled_block_eigenvalues": {",".join(b): [e["real"] for e in res["eigenvalues"] if e["block"] == b]
                                      for b in res["coupled_blocks"]},
        "d4_d6_block": res["d4_d6"],
        "dominant_mode_shape": res["dominant_mode"],
        "dominant_mode_note": "Eigenvector of W^T for the dominant eigenvalue, scaled to sum to 1: the long-run shape of a "
                              "decaying disturbance that reaches the D4/D6 loop.",
        "sink_nodes": [n for i, n in enumerate(ids) if not res["W"][i].any() and res["W"][:, i].any()],
        "source_nodes": [n for i, n in enumerate(ids) if not res["W"][:, i].any() and res["W"][i].any()],
    }


def render_text_outputs(res: dict) -> dict[str, str]:
    ids, W = res["ids"], res["W"]
    rows = res["propagation"]
    prop_header = ["t", *ids, "total_magnitude", "magnitude_excluding_D8", "dominant_node", "step_ratio", "behaviour",
                   "cumulative_D8"]
    texts = {
        "wtm_matrix.csv": _csv(["source\\target", *ids], [[n, *(f"{v:.2f}" for v in row)] for n, row in zip(ids, W)]),
        "eigenvalues.json": _json({
            "method": "Union of the eigenvalues of the strongly connected diagonal blocks (numpy.linalg.eigvals per "
                      "block), cross-checked against numpy.linalg.eigvals on the full matrix.",
            "matrix": "W (eigenvalues of W and W^T are identical)",
            "eigenvalues": res["eigenvalues"],
            "full_matrix_eigenvalues": res["full_matrix_eigenvalues"],
            "max_block_vs_full_modulus_gap": res["max_block_vs_full_eigen_gap"],
            "spectral_radius": res["spectral_radius"], "dominant_eigenvalue": res["dominant_eigenvalue"]}),
        "structural_analysis.json": _json(structural_document(res)),
        "software_disturbance_propagation.csv": _csv(prop_header, [[_fmt(r[k]) for k in prop_header] for r in rows]),
        "wtm_provenance.json": _json({
            "term": TERM, "statement": STATEMENT,
            "computed_by": "ppm_agent.tools.wtm_tools (deterministic Python / numpy; no LLM involvement)",
            "inputs_sha256": res["input_sha256"], "source_matrix": "outputs/dsm/weighted_dsm.csv (frozen DSM v1.1)",
            "orientation": ORIENTATION, "equation": EQUATION, "transformations": TRANSFORMATIONS,
            "modelling_assumption": "Ordinal DSM weights are used directly as multiplicative propagation coefficients.",
            "initial_state": {n: (1.0 if n == INITIAL_NODE else 0.0) for n in ids},
            "initial_state_note": "Normalized analytical disturbance; not a probability or a historical measurement.",
            "stopping_rule": STOPPING_RULE, "behaviour_tolerance": BEHAVIOUR_TOL,
            "behaviour_rule": f"step ratio = total(t) / total(t-1); > 1 + {BEHAVIOUR_TOL} AMPLIFYING, < 1 - {BEHAVIOUR_TOL} "
                              "DECAYING, otherwise PERSISTENT.",
            "numeric_precision": f"values rounded to {DECIMALS} decimals in outputs",
            "not_done": ["A210 +8 disturbance", "A305 +4 disturbance", "intervention comparison", "calibration"]}),
    }
    texts["wtm_summary.md"] = summary_markdown(res)
    return texts


def summary_markdown(res: dict) -> str:
    ids, W, rows = res["ids"], res["W"], res["propagation"]
    s = structural_document(res)
    cf = res["d4_d6"]
    eig_rows = "\n".join(f"| {e['real']:.4f} | {e['imag']:.4f} | {e['modulus']:.4f} | {{{', '.join(e['block'])}}} |"
                         for e in res["eigenvalues"])
    w_rows = "\n".join(f"| **{n}** | " + " | ".join(f"{v:.2f}" if v else "0" for v in row) + " |" for n, row in zip(ids, W))
    p_rows = "\n".join(
        f"| t{r['t']} | " + " | ".join(f"{r[n]:.4f}" for n in ids) + f" | {r['total_magnitude']:.4f} | "
        f"{r['magnitude_excluding_D8']:.4f} | {r['dominant_node']} | "
        + ("" if r["step_ratio"] is None else f"{r['step_ratio']:.3f}") + f" | {r['behaviour']} | {r['cumulative_D8']:.4f} |"
        for r in rows)
    inf = res["cumulative_infinite"]
    inf_text = ", ".join(f"{n} {v:.2f}" for n, v in inf.items() if abs(v) > 1e-12) if inf else "not defined (rho >= 1)"
    inf_total = sum(inf.values()) if inf else float("nan")
    mode = ", ".join(f"{n} {v:.3f}" for n, v in res["dominant_mode"].items() if abs(v) > 1e-9)
    blocks = ", ".join("{" + ", ".join(b) + "}" for b in res["coupled_blocks"])
    peak = max(rows[1:], key=lambda r: r["total_magnitude"])
    behaviours = ", ".join(f"t{r['t']} {r['behaviour'].lower()}" for r in rows[1:])
    return f"""# {TERM}

> **{STATEMENT}**

Generated by `scripts/build_wtm.py` from the frozen weighted DSM v1.1 (`outputs/dsm/weighted_dsm.csv`). It is deterministic
Python / numpy, with no LLM involvement.

## 1. DSM and WTM

The DSM records **which** nodes influence which, and how well each link is supported. This layer reuses the same 8 x 8
weighted matrix $W$ as a **propagation operator**: a disturbance at one node is passed to its targets in proportion
to the weights, step by step.

**Why "illustrative".** A Work Transformation Matrix in the strict sense (Smith and Eppinger) has entries that are
calibrated fractions of rework each task creates for another, plus task durations, estimated from project data. These
weights are ordinal evidence tiers (0.25 / 0.50 / 0.75 / 1.00) and synthetic assumptions, not measured rework
fractions. **The one modelling assumption of this layer** is that those ordinal weights are used directly as
multiplicative propagation coefficients. The results show how the *structure* behaves; they are not calibrated
magnitudes.

## 2. Orientation and the exact equation

{ORIENTATION}. So $w_{{ij}}$ is the influence of node $i$ on node $j$.

A node's disturbance at the next step is the weighted sum of what its **sources** hold now. Its sources are found down its
**column**:

$$x_j(t+1) = \\sum_{{i=1}}^{{8}} w_{{ij}} \\, x_i(t) \\qquad \\Longleftrightarrow \\qquad x(t+1) = W^{{\\mathsf T}} x(t)$$

In plain English: to update D6, look down column D6, multiply each source's current disturbance by its weight into
D6, and add them up. Writing that for all nodes at once is exactly "multiply by $W$ transposed". The transpose is not a
hidden change of the data. It is what "row = source" means when the state is a column vector. $W$ itself is stored and
used unchanged, and the transpose appears only in this update. (An equivalent form is the row-vector update
$x(t+1)^{{\\mathsf T}} = x(t)^{{\\mathsf T}} W$.)

## 3. The matrix

| source \\ target | {' | '.join(ids)} |
|---|{'---|' * len(ids)}
{w_rows}

The weights mean the same as in the DSM: 0.25 synthetic sequencing, 0.50 unresolved or fragment-supported, 0.75
partially supported or directly stated, 1.00 supported (none). They are ordinal, not probabilities.

## 4. Eigenvalues and spectral radius

The eigenvalues of $W$ and $W^{{\\mathsf T}}$ are the same. Because the network splits into strongly connected
components with one-way links between them, the eigenvalues are exactly those of the components' diagonal blocks.
They were computed block by block and cross-checked against the full matrix (largest gap
{res['max_block_vs_full_eigen_gap']:.1e}).

| Real | Imag | Modulus | From block |
|---|---|---|---|
{eig_rows}

- **Dominant eigenvalue:** {res['dominant_eigenvalue']:.4f}, from the {{D4, D6}} block.
- **Spectral radius:** $\\rho(W) = \\max |\\lambda| =$ **{res['spectral_radius']:.4f}**.
- All acyclic single nodes contribute 0. {{D2, D3}} contributes $\\pm\\sqrt{{w_{{23}} w_{{32}}}} = \\pm 0.25$.

## 5. Convergence interpretation (raw matrix, no tuning)

$\\rho(W) = {res['spectral_radius']:.4f} < 1$, so repeated propagation **decays**. In the long run, the remaining
disturbance shrinks by a factor of about {res['spectral_radius']:.3f} per step, which is about 9% per step: slow decay,
not fast damping. Because $\\rho < 1$, the total disturbance summed over all steps is finite:
$\\sum_t x(t) = (I - W^{{\\mathsf T}})^{{-1}} x(0)$.

Decay in the long run does not rule out **short-run growth**. The largest out-strength (row sum of $W$) is
{res['max_out_strength']:.2f}, for D6, which feeds D4, D6, D7 and D8. One step can therefore increase the total
disturbance by up to that factor. The D4 example below shows this.

The long-run shape of a decaying disturbance (the dominant eigenvector of $W^{{\\mathsf T}}$, scaled to sum to 1) is:
{mode}.

## 6. The D4 / D6 coupled block

$$W_{{\\{{4,6\\}}}} = \\begin{{pmatrix}} w_{{44}} & w_{{46}} \\\\ w_{{64}} & w_{{66}} \\end{{pmatrix}} = \\begin{{pmatrix}} {cf['w44']:.2f} & {cf['w46']:.2f} \\\\ {cf['w64']:.2f} & {cf['w66']:.2f} \\end{{pmatrix}}$$

Characteristic polynomial: $\\lambda^2 - w_{{66}}\\lambda - w_{{46}}w_{{64}} = \\lambda^2 - {cf['w66']:.2f}\\lambda - {cf['loop_gain_w46_x_w64']:.3f} = 0$, so

$$\\lambda = \\frac{{w_{{66}} \\pm \\sqrt{{w_{{66}}^2 + 4\\,w_{{46}}w_{{64}}}}}}{{2}} = {cf['eigenvalues'][0]:.4f} \\text{{ and }} {cf['eigenvalues'][1]:.4f}$$

In plain English:
- **Round trip.** A disturbance in software passes 0.75 of itself to flight test. Flight test passes 0.50 of what it
  holds back to software, so one round trip returns $0.75 \\times 0.50 = {cf['loop_gain_w46_x_w64']:.3f}$ of the original
  to D4.
- **Self-loop.** Each step, flight test also keeps 0.50 of its own disturbance.
- **Combined.** Together these give the loop a persistence rate of {cf['eigenvalues'][0]:.3f} per step. That is high
  enough that the disturbance circulates for many steps, but below 1, so it dies out. This block alone sets the
  spectral radius of the whole network. {{D2, D3}} is weaker (0.25), and every other node passes disturbance on without
  holding it.
- **What drives the rate.** It rises with either the loop gain $w_{{46}}w_{{64}}$ or the self-loop $w_{{66}}$, and it
  would reach 1 when $w_{{66}} + w_{{46}}w_{{64}} = 1$. At present that sum is
  {cf['w66'] + cf['loop_gain_w46_x_w64']:.3f}. This is the algebra of the frozen weights; nothing was changed to test it.

## 7. D4 software disturbance (normalized example)

$x(0)$: D4 = 1.0, all other nodes 0. This is a normalized analytical disturbance, not a probability or a measurement.
Iterated with $x(t+1) = W^{{\\mathsf T}}x(t)$ for t0 to t{HORIZON}.

**Stopping rule:** {STOPPING_RULE}

**Behaviour per step:** the ratio total(t) / total(t-1). Above {1 + BEHAVIOUR_TOL:.2f} is amplifying, below
{1 - BEHAVIOUR_TOL:.2f} is decaying, and anything in between is persistent. "Total" is the L1 magnitude (the sum of the
eight values), which includes what arrives at D8 that step. "Dominant" is the node or nodes with the largest value; ties
are shown as, for example, D4/D6/D8.

| t | {' | '.join(ids)} | Total | Total excl. D8 | Dominant | Ratio | Behaviour | Cumulative D8 |
|---|{'---|' * (len(ids) + 6)}
{p_rows}

Reading the table:
- **t1.** All of D4's disturbance moves to D6 (×0.75).
- **t2.** D6 fans out to D4, itself, D7 and D8 (out-strength 1.75). The total jumps to
  {rows[2]['total_magnitude']:.4f}: short-run amplification.
- **After that,** the total falls, with step ratios heading towards the spectral radius ({res['spectral_radius']:.3f}).
  The peak total is {peak['total_magnitude']:.4f} at t{peak['t']}.
- **Step by step:** {behaviours}.
- **Overall:** transient amplification followed by slow decay, which is what the spectral radius predicts.
- **Never reached:** D1, D2, D3 and D5 stay at 0 throughout, because nothing flows from D4 or D6 back upstream to
  them.
- **Over all steps** (closed form, $(I - W^{{\\mathsf T}})^{{-1}}x(0)$): {inf_text}, for a total of {inf_total:.2f}.
  These are relative units of the normalized disturbance, not days or costs.

## 8. D8 is a sink

D8's row in $W$ is all zero, so $x_{{D8}}(t)$ never enters any other node's update. Whatever reaches D8 at a step stops
there. In the state vector, D8 shows what **arrives** each step (from D6 at 0.50 and D7 at 0.50, plus D2 and D3 for
other disturbances). It is not carried forward, because D8 has no self-loop. Its **accumulated** exposure is the
running sum, shown in the "Cumulative D8" column: {rows[-1]['cumulative_D8']:.4f} by t{HORIZON}, and
{(inf or {}).get('D8', float('nan')):.2f} over all steps. In this MVP, consequences collect in production exposure and
do not feed back to development or test.

## 9. Coupled blocks

{blocks}. {{D4, D6}} sets the dominant behaviour. {{D2, D3}} would matter only for disturbances that start upstream (D1,
D2 or D3); the D4 example never reaches it.

## 10. Limitations

- These are ordinal evidence tiers used as propagation coefficients, so magnitudes are illustrative, not calibrated.
  A different but equally defensible tier mapping would change the numbers. It would preserve which links exist, but
  not necessarily the spectral radius.
- This is a linear, time-invariant, deterministic model. It has no durations, no resource limits and no learning, and
  it has a single disturbance channel.
- The behaviour labels depend on a documented tolerance of ±{BEHAVIOUR_TOL}.
- The agentic weights come from single runs (Q01 0.75, Q04 0.50, Q08 0.50), and some links (D2 ↔ D3, D6 → D7) are purely
  synthetic. The D6 → D4 feedback has a synthetic activity pair.
- Not done yet: the A210 +8 and A305 +4 scenario disturbances, and intervention comparisons.

## Input fingerprints

{chr(10).join(f"- `{k}`: `{v}`" for k, v in res['input_sha256'].items())}
"""


# --- figures (SVG, standard library; rasterized to PNG by the build script) ---------------------------

SERIES = {"D4": ("#2a78d6", "circle"), "D6": ("#eb6834", "square"), "D7": ("#1baf7a", "triangle"),
          "D8": ("#eda100", "diamond")}  # reference categorical slots 1-4, in order; marker shape is secondary encoding
SVG_FILES = ("wtm_heatmap.svg", "software_disturbance_propagation.svg")


def wtm_heatmap_svg(res: dict, dsm_dir: Path) -> str:
    return heatmap_svg(load_frozen_dsm(dsm_dir), "weighted",
                       title="WTM / weighted propagation matrix W (same values as the frozen weighted DSM)",
                       extra_notes=[f"Update: x(t+1) = W^T x(t); a node sums its column (its sources).",
                                    f"Spectral radius {res['spectral_radius']:.4f} (from the D4/D6 block): decays."])


def _t(x, y, s, size=12, fill=INK_2, anchor="start", weight="normal", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {extra}>{escape(s)}</text>')


def _marker(shape, x, y, color):
    ring = f'stroke="{SURFACE}" stroke-width="2"'
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" {ring}/>'
    if shape == "square":
        return f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" fill="{color}" {ring}/>'
    if shape == "triangle":
        return f'<path d="M{x:.1f},{y - 6:.1f} L{x + 6:.1f},{y + 5:.1f} L{x - 6:.1f},{y + 5:.1f} Z" fill="{color}" {ring}/>'
    return f'<path d="M{x:.1f},{y - 6:.1f} L{x + 6:.1f},{y:.1f} L{x:.1f},{y + 6:.1f} L{x - 6:.1f},{y:.1f} Z" fill="{color}" {ring}/>'


def _panel(out, x0, y0, w, h, ymax, ticks, ts, series, title):
    """One line panel: series = [(label, values, color, shape, dashed)]."""
    sx = lambda t: x0 + w * t / (len(ts) - 1)  # noqa: E731
    sy = lambda v: y0 + h - h * v / ymax  # noqa: E731
    out.append(_t(x0, y0 - 14, title, 13, INK, weight="600"))
    for v in ticks:
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="#e6e5e0" stroke-width="1"/>')
        out.append(_t(x0 - 8, sy(v) + 4, f"{v:.2f}", 11, MUTED, "end"))
    for t in ts:
        out.append(_t(sx(t), y0 + h + 18, f"t{t}", 11, MUTED, "middle"))
    for label, values, color, shape, dashed in series:
        pts = " ".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in zip(ts, values))
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" '
                   f'stroke-linecap="round"{dash}/>')
        for t, v in zip(ts, values):
            out.append(f'<g><title>{escape(label)}, t{t}: {v:.4f}</title>{_marker(shape, sx(t), sy(v), color)}</g>')
    return sx, sy


def propagation_svg(res: dict) -> str:
    rows, ts = res["propagation"], [r["t"] for r in res["propagation"]]
    width, height = 900, 760
    x0, w = 90, 660
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
           _t(24, 34, "Normalized D4 software disturbance: x(t+1) = W^T x(t), t0 to t6", 18, INK, weight="600"),
           _t(24, 58, "x(0): D4 = 1.0, all others 0. Relative units of a normalized analytical disturbance; "
                      "not a probability or a measurement.", 12)]
    totals = [r["total_magnitude"] for r in rows]
    _, sy = _panel(out, x0, 110, w, 190, 1.5, [0, 0.5, 1.0, 1.5], ts,
                   [("Total magnitude", totals, INK, "circle", False)], "Total disturbance (sum of D1-D8 values)")
    sx = lambda t: x0 + w * t / (len(ts) - 1)  # noqa: E731
    for r in rows:
        label = r["behaviour"].lower() if r["t"] else "initial"
        out.append(_t(sx(r["t"]), sy(r["total_magnitude"]) - 12, f"{r['total_magnitude']:.3f}", 11, INK, "middle",
                      extra=HALO))
        out.append(_t(sx(r["t"]), 110 + 190 + 34, label, 10, MUTED, "middle"))
    series = [(n, [r[n] for r in rows], c, s, False) for n, (c, s) in SERIES.items()]
    _, sy2 = _panel(out, x0, 410, w, 220, 1.0, [0, 0.25, 0.5, 0.75, 1.0], ts, series,
                    "Disturbance at each reached node")
    # direct end labels with leader lines (ends of D4 and D7 / D6 and D8 sit close together)
    ends = sorted(((rows[-1][n], n) for n in SERIES), reverse=True)
    label_y = [410 + 40 + k * 44 for k in range(len(ends))]
    for (v, n), ly in zip(ends, label_y):
        color, shape = SERIES[n]
        ex, ey = sx(ts[-1]), sy2(v)
        out.append(f'<line x1="{ex + 7:.1f}" y1="{ey:.1f}" x2="{ex + 30:.1f}" y2="{ly - 4:.1f}" stroke="{MUTED}" stroke-width="1"/>')
        out.append(_marker(shape, ex + 40, ly - 4, color))
        out.append(_t(ex + 50, ly, f"{n} {v:.3f}", 12, INK))
    out.append(_t(24, 690, "D4 Mission-System Software Maturity, D6 Flight-Test Execution, D7 Development / Test Maturity, "
                           "D8 Production Commitment / Rework Exposure (sink: value = arrivals that step).", 11))
    out.append(_t(24, 708, "D1, D2, D3 and D5 stay at 0 throughout: no path leads from D4 or D6 back upstream to them.", 11))
    out.append(_t(24, 726, f"Long-run decay rate = spectral radius {res['spectral_radius']:.4f} per step; transient "
                           f"growth at t2 because D6's out-strength is {res['out_strength']['D6']:.2f}.", 11))
    out.append("</svg>")
    return "\n".join(out) + "\n"
