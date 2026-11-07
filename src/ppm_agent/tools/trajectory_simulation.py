"""Deterministic predictive trajectories and intervention comparison on the frozen WTM (illustrative test harness).

Reuses the frozen pieces rather than re-implementing them:
  - wtm_tools.load_frozen_weighted / step:   W (row = source, column = target) and x(t+1) = W^T x(t);
  - scenario_mapping.build_mapping:          initial states (4 exposed workdays = 1.0) and the policy parameters.

Per-step procedure for every case, t = 0..HORIZON:
  1. x(t) is the incoming state (x(0) from the scenario mapping; afterwards x(t) = W^T x(t-1)).
  2. INTERVENTION_2 only: absorb a = min(x_D6(t), remaining capacity) at D6; x_D6(t) -= a; remaining -= a.
     The capacity (1.0 normalized = 4 workdays) is cumulative over the whole trajectory and never resets.
  3. Record x(t) (after any absorption); it is what propagates to t+1.
  4. INTERVENTION_3 only: split the D8 value recorded at t into committed (0.40) and gated (0.60) exposure.
     Propagation is untouched (D8 is a sink, and the split happens after the state is recorded).

Python computes facts only; there is no composite score or ranking.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from html import escape
from pathlib import Path

import numpy as np

from ppm_agent.tools.dsm_visualization import FONT, HALO, INK, INK_2, MUTED, SURFACE
from ppm_agent.tools.scenario_mapping import build_mapping
from ppm_agent.tools.wtm_tools import load_frozen_weighted, propagate, step

STATEMENT = ("The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative "
             "management policies affect a synthetic, evidence-calibrated dependency model; it does not predict "
             "historical or actual F-35 outcomes.")
HORIZON = 12
CASES = [  # (case id, label, mapping scenario providing x(0), policy)
    ("CASE_0", "NO ACTION (DISTURBANCE_1)", "DISTURBANCE_1", None),
    ("CASE_1", "INTERVENTION_1 software recovery", "INTERVENTION_1", None),
    ("CASE_2", "INTERVENTION_2 flight-test resequencing", "INTERVENTION_2", "ABSORB_AT_D6"),
    ("CASE_3", "INTERVENTION_3 staged production commitment", "DISTURBANCE_1", "SPLIT_AT_D8"),
]
RESEQUENCING_RULE = ("Cumulative capacity of 1.0 normalized unit (4 workdays) over the whole trajectory. At each step, "
                     "absorb min(D6 value, remaining capacity) from D6 before it propagates; track the cumulative amount; "
                     "never reset. Once exhausted, D6 propagates normally. The A405 gate and W are unchanged. SYNTHETIC.")
STAGING_RULE = ("Upstream propagation unchanged. Each step's D8 value is split into 40% committed pre-maturity exposure "
                "and 60% gated / deferred until A430 maturity. NO ACTION (baseline concurrency) commits 100% "
                "pre-maturity. Fractions SYNTHETIC; not historical F-35 policy.")
INPUTS = ("outputs/dsm/weighted_dsm.csv", "outputs/wtm/wtm_matrix.csv", "outputs/simulation/scenario_mapping.json",
          "data/synthetic/synthetic_scenarios.json", "data/synthetic/synthetic_ims.csv")
DECIMALS = 10


def _r(v: float) -> float:
    return round(float(v), DECIMALS) + 0.0


# --- engine -------------------------------------------------------------------------------------------

def simulate(ids: list[str], W: np.ndarray, x0: np.ndarray, horizon: int = HORIZON, absorb_capacity: float = 0.0,
             d8_split: tuple[float, float] | None = None) -> list[dict]:
    """Generic trajectory with an optional cumulative D6 absorption capacity and an optional D8 exposure split."""
    d6, d8 = ids.index("D6"), ids.index("D8")
    remaining, cumulative_absorbed, rows, x = absorb_capacity, 0.0, [], x0.astype(float).copy()
    for t in range(horizon + 1):
        if t:
            x = step(W, x)
        before = x[d6]
        absorbed = min(before, remaining) if remaining > 0 else 0.0
        x[d6] -= absorbed
        remaining -= absorbed
        cumulative_absorbed += absorbed
        row = {"t": t, **{n: _r(v) for n, v in zip(ids, x)}, "total": _r(np.abs(x).sum()),
               "D6_before_absorption": _r(before), "absorbed": _r(absorbed),
               "cumulative_absorbed": _r(cumulative_absorbed), "remaining_capacity": _r(remaining)}
        if d8_split:
            row["D8_committed"], row["D8_gated"] = _r(x[d8] * d8_split[0]), _r(x[d8] * d8_split[1])
        rows.append(row)
    return rows


def metrics(ids: list[str], rows: list[dict], capacity: float, split: tuple[float, float] | None) -> dict:
    totals = [r["total"] for r in rows]
    peak = max(totals)
    out = {"peak_total": _r(peak), "peak_step": totals.index(peak) if peak > 0 else None,
           "cumulative_total": _r(sum(totals)), "final_total": _r(totals[-1]),
           **{f"cumulative_{n}": _r(sum(r[n] for r in rows)) for n in ("D4", "D6", "D7", "D8")},
           "cumulative_D6_arrived_before_absorption": _r(sum(r["D6_before_absorption"] for r in rows)),
           "intervention_capacity": _r(capacity) if capacity else None,
           "intervention_used": _r(rows[-1]["cumulative_absorbed"]) if capacity else None,
           "intervention_unused": _r(rows[-1]["remaining_capacity"]) if capacity else None}
    if split:  # from the cumulative D8 total, so committed + gated equals it exactly
        out["cumulative_D8_committed_pre_maturity"] = _r(out["cumulative_D8"] * split[0])
        out["cumulative_D8_gated_deferred"] = _r(out["cumulative_D8"] * split[1])
    return out


def _change(base: float, value: float) -> dict:
    # percentages are rounded to 6 decimals: a ratio of two 10-decimal values cannot carry more precision
    return {"absolute_reduction": _r(base - value),
            "percent_reduction": round(100 * (base - value) / base, 6) + 0.0 if base > 0 else None}


def compare(case0: dict, case: dict) -> dict:
    out = {k: _change(case0[k], case[k]) for k in ("peak_total", "cumulative_total", "cumulative_D6", "cumulative_D8")}
    committed0 = case0["cumulative_D8"]  # NO ACTION commits all D8 exposure pre-maturity (baseline concurrency)
    committed = case.get("cumulative_D8_committed_pre_maturity", case["cumulative_D8"])
    out["cumulative_D8_committed_pre_maturity"] = _change(committed0, committed)
    return out


def run(project_root: Path) -> dict:
    ids, W = load_frozen_weighted(project_root / "outputs" / "dsm")
    mapping = build_mapping(project_root)
    by_id = {s["scenario_id"]: s for s in mapping["scenarios"]}
    i2 = by_id["INTERVENTION_2"]["intervention_semantics"][0]
    i3 = by_id["INTERVENTION_3"]["intervention_semantics"][0]
    capacity = float(i2["max_absorption_normalized"])
    split = (float(i3["pre_maturity_commitment_fraction"]), float(i3["post_maturity_commitment_fraction"]))
    cases = []
    for cid, label, sid, policy in CASES:
        x0 = np.array([by_id[sid]["initial_wtm_state"][n] for n in ids])
        cap = capacity if policy == "ABSORB_AT_D6" else 0.0
        sp = split if policy == "SPLIT_AT_D8" else None
        rows = simulate(ids, W, x0, absorb_capacity=cap, d8_split=sp)
        cases.append({"case_id": cid, "label": label, "initial_state_from": sid, "policy": policy,
                      "initial_state": {n: _r(v) for n, v in zip(ids, x0)}, "trajectory": rows,
                      "metrics": metrics(ids, rows, cap, sp)})
    base = cases[0]["metrics"]
    for c in cases[1:]:
        c["change_vs_no_action"] = compare(base, c["metrics"])
    return {"ids": ids, "W": W, "mapping": mapping, "capacity": capacity, "split": split, "cases": cases,
            "secondary_disturbance_available": "DISTURBANCE_2" in by_id,
            "inputs_sha256": {p: hashlib.sha256((project_root / p).read_bytes()).hexdigest() for p in INPUTS}}


# --- validation ---------------------------------------------------------------------------------------

def validate(res: dict, project_root: Path) -> list[str]:
    errors: list[str] = []
    ids, W, cases = res["ids"], res["W"], {c["case_id"]: c for c in res["cases"]}
    frozen_ids, frozen_W = load_frozen_weighted(project_root / "outputs" / "dsm")
    if frozen_ids != ids or not np.array_equal(frozen_W, W):
        errors.append("simulation W differs from the frozen weighted DSM / WTM")
    if res["inputs_sha256"] != {p: hashlib.sha256((project_root / p).read_bytes()).hexdigest() for p in INPUTS}:
        errors.append("frozen inputs changed")
    d1 = {n: 1.0 if n == "D4" else 0.0 for n in ids}
    expected_x0 = {"CASE_0": d1, "CASE_1": {n: 0.0 for n in ids}, "CASE_2": d1, "CASE_3": d1}
    for cid, x0 in expected_x0.items():
        if cases[cid]["initial_state"] != x0:
            errors.append(f"{cid}: wrong initial state {cases[cid]['initial_state']}")
    if res["capacity"] != 1.0 or res["split"] != (0.40, 0.60) or abs(sum(res["split"]) - 1.0) > 1e-12:
        errors.append("policy parameters differ from the frozen values (capacity 1.0, split 0.40 / 0.60)")
    for c in res["cases"]:
        rows = c["trajectory"]
        if [r["t"] for r in rows] != list(range(HORIZON + 1)):
            errors.append(f"{c['case_id']}: horizon must be t0..t{HORIZON}")
        values = [v for r in rows for v in r.values() if isinstance(v, float)]
        if not all(math.isfinite(v) for v in values):
            errors.append(f"{c['case_id']}: non-finite values")
        if any(r[n] < 0 for r in rows for n in ids):
            errors.append(f"{c['case_id']}: negative disturbance")
    # NO ACTION reproduces the frozen WTM propagation (and its own step rule to t12)
    c0 = cases["CASE_0"]["trajectory"]
    wtm_rows = propagate(ids, W, np.array([c0[0][n] for n in ids]))
    if any(abs(a[n] - b[n]) > 1e-9 for a, b in zip(wtm_rows, c0) for n in ids):
        errors.append("CASE_0 does not reproduce the frozen WTM propagation")
    x = np.array([c0[0][n] for n in ids])
    for r in c0[1:]:
        x = step(W, x)
        if any(abs(_r(v) - r[n]) > 1e-9 for n, v in zip(ids, x)):
            errors.append(f"CASE_0 t{r['t']}: not x(t+1) = W^T x(t)")
            break
    if any(r[n] for r in cases["CASE_1"]["trajectory"] for n in ids):
        errors.append("CASE_1 must start at, and remain at, zero disturbance")
    # INTERVENTION_2 capacity: bounded, cumulative, never reset
    c2 = cases["CASE_2"]["trajectory"]
    used = [r["cumulative_absorbed"] for r in c2]
    remaining = [r["remaining_capacity"] for r in c2]
    if used[-1] > res["capacity"] + 1e-12 or used != sorted(used) or remaining != sorted(remaining, reverse=True):
        errors.append("CASE_2 absorption exceeds the capacity or the capacity reset")
    if any(abs(u + rem - res["capacity"]) > 1e-9 for u, rem in zip(used, remaining)):
        errors.append("CASE_2 used + remaining capacity must equal 1.0 at every step")
    if any(r["absorbed"] > r["D6_before_absorption"] + 1e-12 for r in c2):
        errors.append("CASE_2 absorbed more than the D6 disturbance present")
    # INTERVENTION_3 leaves propagation untouched; split is exact
    c3 = cases["CASE_3"]["trajectory"]
    if any(a[n] != b[n] for a, b in zip(c0, c3) for n in ids):
        errors.append("CASE_3 altered upstream propagation")
    if any(abs(r["D8_committed"] + r["D8_gated"] - r["D8"]) > 1e-9 for r in c3):
        errors.append("CASE_3 committed + gated must equal D8 at every step")
    return errors


# --- outputs ------------------------------------------------------------------------------------------

def _fmt(v) -> str:
    if v is None:
        return ""
    return f"{v:.{DECIMALS}f}" if isinstance(v, float) else str(v)


def _csv(header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


METRIC_KEYS = ("peak_total", "peak_step", "cumulative_total", "final_total", "cumulative_D4", "cumulative_D6",
               "cumulative_D6_arrived_before_absorption", "cumulative_D7", "cumulative_D8", "intervention_capacity", "intervention_used", "intervention_unused",
               "cumulative_D8_committed_pre_maturity", "cumulative_D8_gated_deferred")
CHANGE_KEYS = ("peak_total", "cumulative_total", "cumulative_D6", "cumulative_D8", "cumulative_D8_committed_pre_maturity")


def render_text_outputs(res: dict) -> dict[str, str]:
    ids = res["ids"]
    traj_header = ["case_id", "t", *ids, "total", "D6_before_absorption", "absorbed", "cumulative_absorbed",
                   "remaining_capacity", "D8_committed", "D8_gated"]
    traj_rows = [[c["case_id"], *(_fmt(r.get(k)) for k in traj_header[1:])] for c in res["cases"] for r in c["trajectory"]]
    comp_header = ["case_id", "label", *METRIC_KEYS,
                   *(f"{k}_{x}_vs_no_action" for k in CHANGE_KEYS for x in ("reduction", "pct_reduction"))]
    comp_rows = []
    for c in res["cases"]:
        ch = c.get("change_vs_no_action", {})
        comp_rows.append([c["case_id"], c["label"], *(_fmt(c["metrics"].get(k)) for k in METRIC_KEYS),
                          *(_fmt(ch[k][x] if k in ch else None) for k in CHANGE_KEYS
                            for x in ("absolute_reduction", "percent_reduction"))])
    doc = {
        "statement": STATEMENT,
        "computed_by": "ppm_agent.tools.trajectory_simulation (deterministic Python / numpy; no LLM; no composite score)",
        "inputs_sha256": res["inputs_sha256"],
        "equation": "x(t+1) = W^T x(t) (frozen WTM; row = source, column = target)",
        "horizon": f"t0..t{HORIZON}, identical for every case; no early stopping",
        "common_initiating_disturbance": ("DISTURBANCE_1: A210 +8 workdays, A230 float 4, exposed 4 workdays, "
                                          "normalized D4 = 1.0 (reference 4 workdays = 1.0)"),
        "intervention_2_rule": RESEQUENCING_RULE, "intervention_3_rule": STAGING_RULE,
        "data_classification": "SYNTHETIC",
        "cases": [{k: c[k] for k in ("case_id", "label", "initial_state_from", "policy", "initial_state", "metrics")}
                  | ({"change_vs_no_action": c["change_vs_no_action"]} if "change_vs_no_action" in c else {})
                  for c in res["cases"]],
        "percent_reduction_note": "percent_reduction is null where the NO ACTION value is 0 (not meaningful).",
        "intervention_3_note": ("INTERVENTION_3 does not reduce the D8 disturbance entering the node (cumulative_D8 is "
                                "unchanged); it reduces the share committed before maturity."),
        "not_done": ["composite ranking", "agentic interpretation", "DISTURBANCE_2 comparison", "cost conversion"],
    }
    return {
        "predictive_trajectories.csv": _csv(traj_header, traj_rows),
        "intervention_comparison.csv": _csv(comp_header, comp_rows),
        "intervention_comparison.json": json.dumps(doc, indent=2) + "\n",
        "predictive_simulation_summary.md": summary_markdown(res),
        "trajectory_comparison.svg": comparison_svg(res),
    }


def summary_markdown(res: dict) -> str:
    cases = {c["case_id"]: c for c in res["cases"]}
    m = {cid: c["metrics"] for cid, c in cases.items()}

    def f(v, d=4):
        return "n/a" if v is None else (f"{v:.{d}f}" if isinstance(v, float) else str(v))

    metric_rows = "\n".join(
        f"| {c['case_id']} {c['label']} | {f(c['metrics']['peak_total'])} | {f(c['metrics']['peak_step'])} | "
        f"{f(c['metrics']['cumulative_total'])} | {f(c['metrics']['cumulative_D4'])} | {f(c['metrics']['cumulative_D6'])} | "
        f"{f(c['metrics']['cumulative_D7'])} | {f(c['metrics']['cumulative_D8'])} | {f(c['metrics']['final_total'])} | "
        f"{f(c['metrics']['intervention_used'])} / {f(c['metrics']['intervention_unused'])} |" for c in res["cases"])

    def ch(cid, k):
        x = cases[cid]["change_vs_no_action"][k]
        pct = "n/a" if x["percent_reduction"] is None else f"{x['percent_reduction']:.1f}%"
        return f"{x['absolute_reduction']:.4f} ({pct})"

    change_rows = "\n".join(
        f"| {cid} {cases[cid]['label']} | {ch(cid, 'peak_total')} | {ch(cid, 'cumulative_total')} | "
        f"{ch(cid, 'cumulative_D6')} | {ch(cid, 'cumulative_D8')} | {ch(cid, 'cumulative_D8_committed_pre_maturity')} |"
        for cid in ("CASE_1", "CASE_2", "CASE_3"))
    c2 = cases["CASE_2"]["trajectory"]
    absorbed_steps = ", ".join(f"t{r['t']} {r['absorbed']:.4f}" for r in c2 if r["absorbed"])
    tail = cases["CASE_0"]["trajectory"][-1]
    return f"""# Predictive trajectories and intervention comparison

> **{STATEMENT}**

Generated by `scripts/build_trajectory_simulation.py`. It is deterministic Python / numpy on the frozen baseline v1.1, DSM
v1.1, WTM and scenario mapping. No LLM was involved and **no composite score or ranking** was produced: Python reports
facts, and interpreting the trade-offs is left to the later Predictive Simulation and Intervention Agent.

## Common initiating disturbance

DISTURBANCE_1. A210 software integration slips 8 workdays. A230 has 4 workdays of float, so the exposed delay is
max(0, 8 - 4) = **4 workdays**. With the synthetic reference of 4 workdays = 1.0, that gives **x(0): D4 = 1.0**, all
other nodes 0.

## The four cases

| Case | Initial state | Policy |
|---|---|---|
| CASE_0 NO ACTION | D4 = 1.0 | none: the frozen WTM, x(t+1) = W^T x(t) |
| CASE_1 INTERVENTION_1 software recovery | D4 = 0.0 (8 - 4 recovered - 4 float = 0 exposed) | none needed: nothing enters the WTM |
| CASE_2 INTERVENTION_2 flight-test resequencing | D4 = 1.0 | cumulative D6 absorption, capacity 1.0 (4 workdays) |
| CASE_3 INTERVENTION_3 staged production commitment | D4 = 1.0 | D8 exposure split 40% committed / 60% gated |

**Horizon:** t0 to t{HORIZON} for every case, with no early stopping.

**Resequencing cap (SYNTHETIC):** {RESEQUENCING_RULE}

**Staged commitment (SYNTHETIC):** {STAGING_RULE}

**Step procedure:** x(t) = W^T x(t-1). CASE_2 then absorbs at D6 before x(t) propagates. CASE_3 splits D8 after
recording it, which cannot affect propagation because D8 is a sink.

## Results (normalized units; not days, dollars or probabilities)

| Case | Peak total | Peak step | Cumulative total | Cum. D4 | Cum. D6 (effective) | Cum. D7 | Cum. D8 | Final total (t{HORIZON}) | Capacity used / unused |
|---|---|---|---|---|---|---|---|---|---|
{metric_rows}

CASE_3 D8 split: cumulative total D8 {f(m['CASE_3']['cumulative_D8'])}. Of that, **committed pre-maturity
{f(m['CASE_3']['cumulative_D8_committed_pre_maturity'])}** (40%) and **gated / deferred
{f(m['CASE_3']['cumulative_D8_gated_deferred'])}** (60%). Under NO ACTION, all {f(m['CASE_0']['cumulative_D8'])} is
committed pre-maturity, because of the baseline concurrency.

## Change versus NO ACTION (absolute reduction, with percentage where NO ACTION is nonzero)

| Case | Peak total | Cumulative total | Cumulative D6 | Cumulative D8 entering | D8 committed pre-maturity |
|---|---|---|---|---|---|
{change_rows}

## What differs among the interventions

- **INTERVENTION_1 (software recovery)** acts *before* the WTM. The recovered 4 workdays exactly use up A230's 4 days
  of float, so the exposed delay is 0 and nothing propagates. Every metric is 0.
- **INTERVENTION_2 (resequencing)** acts *at D6*. The first disturbance reaching D6 is 0.75 at t1. It is entirely
  inside the 1.0 capacity, so it is fully absorbed ({absorbed_steps}). The cumulative D6 in the table is the
  *effective* D6 after absorption (0); the D6 that arrived before absorption totals
  {f(m['CASE_2']['cumulative_D6_arrived_before_absorption'])}. Nothing propagates after t1, and
  {f(m['CASE_2']['intervention_unused'])} of the capacity is left unused. **Under these frozen magnitudes the cap never
  binds.** The only disturbance left is D4 = 1.0 at t0, before the disturbance reaches flight test.
- **INTERVENTION_3 (staged commitment)** acts *at D8* and changes nothing upstream. Its peak, cumulative total, D6 and
  the D8 disturbance *entering* the node are identical to NO ACTION, so those reductions are 0. **It does not reduce
  the D8 disturbance; it reduces the share of D8 exposure committed before maturity**, by 60%.
- These are different kinds of effect: preventing exposure (INTERVENTION_1), absorbing it at a downstream gate
  (INTERVENTION_2), and limiting commitment to it (INTERVENTION_3). One composite score would hide that difference, so
  none is computed.

## Notes on NO ACTION

The disturbance peaks at {f(m['CASE_0']['peak_total'])} at t{m['CASE_0']['peak_step']}. At t{HORIZON} it is still
{f(tail['total'])}, because the decay rate is the spectral radius (0.911 per step), which is slow. Cumulative values
here are truncated at t{HORIZON}. The full infinite-horizon totals from the WTM layer (D4 4.0, D6 6.0, D7 1.5, D8 3.75)
are larger.

## Limitations

- This is an illustrative, linear, deterministic harness. Its magnitudes come from ordinal weights, a synthetic 4-workday
  normalization and synthetic policy values. It does not predict F-35 outcomes and converts nothing into cost.
- The INTERVENTION_2 result depends on capacity (1.0) relative to the first D6 arrival (0.75). A larger exposed delay
  or a smaller capacity would let the cap bind. That was not explored; the frozen values were not tuned.
- INTERVENTION_3 splits by a fixed fraction at each step. It does not model when A430 maturity is reached or what the
  deferred 60% eventually costs.
- Cumulative metrics are truncated at t{HORIZON}, the same for every case. Interventions are compared one at a time,
  not in combination. DISTURBANCE_2 is available in the framework but not compared.

## Input fingerprints

{chr(10).join(f"- `{k}`: `{v}`" for k, v in res['inputs_sha256'].items())}
"""


# --- figure -------------------------------------------------------------------------------------------

CASE_STYLE = {"CASE_0": (INK, "circle", ""), "CASE_1": ("#2a78d6", "square", ""),
              "CASE_2": ("#eb6834", "triangle", ""), "CASE_3": ("#1baf7a", "diamond", ' stroke-dasharray="7 5"')}


def _t(x, y, s, size=12, fill=INK_2, anchor="start", weight="normal", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{escape(s)}</text>')


def _marker(shape, x, y, color):
    ring = f'stroke="{SURFACE}" stroke-width="2"'
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" {ring}/>'
    if shape == "square":
        return f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" fill="{color}" {ring}/>'
    if shape == "triangle":
        return f'<path d="M{x:.1f},{y - 6:.1f} L{x + 6:.1f},{y + 5:.1f} L{x - 6:.1f},{y + 5:.1f} Z" fill="{color}" {ring}/>'
    return f'<path d="M{x:.1f},{y - 6:.1f} L{x + 6:.1f},{y:.1f} L{x:.1f},{y + 6:.1f} L{x - 6:.1f},{y:.1f} Z" fill="{color}" {ring}/>'


def _axes(out, x0, y0, w, h, ymax, ticks, title):
    sy = lambda v: y0 + h - h * v / ymax  # noqa: E731
    sx = lambda t: x0 + w * t / HORIZON  # noqa: E731
    out.append(_t(x0, y0 - 14, title, 13, INK, weight="600"))
    for v in ticks:
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0 + w}" y2="{sy(v):.1f}" stroke="#e6e5e0" stroke-width="1"/>')
        out.append(_t(x0 - 8, sy(v) + 4, f"{v:g}", 11, MUTED, "end"))
    for t in range(HORIZON + 1):
        out.append(_t(sx(t), y0 + h + 18, f"t{t}", 11, MUTED, "middle"))
    return sx, sy


def _line(out, sx, sy, values, color, shape, dash, label):
    pts = " ".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in enumerate(values))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" '
               f'stroke-linecap="round"{dash}/>')
    for t, v in enumerate(values):
        out.append(f'<g><title>{escape(label)}, t{t}: {v:.4f}</title>{_marker(shape, sx(t), sy(v), color)}</g>')


def comparison_svg(res: dict) -> str:
    cases = {c["case_id"]: c for c in res["cases"]}
    width, height = 980, 900
    x0, w = 80, 640
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
           _t(24, 34, "Intervention comparison: common DISTURBANCE_1 (D4 = 1.0), t0 to t12", 18, INK, weight="600"),
           _t(24, 58, "Normalized units of an illustrative, synthetic, evidence-calibrated model; not a prediction of F-35 "
                      "outcomes, days or cost.", 12)]
    # panel A: total disturbance per step
    sx, sy = _axes(out, x0, 110, w, 260, 1.5, [0, 0.5, 1.0, 1.5], "A. Total disturbance per step (sum of D1-D8)")
    for cid in ("CASE_0", "CASE_3", "CASE_2", "CASE_1"):
        color, shape, dash = CASE_STYLE[cid]
        _line(out, sx, sy, [r["total"] for r in cases[cid]["trajectory"]], color, shape, dash, cases[cid]["label"])
    m0 = cases["CASE_0"]["metrics"]
    out.append(_t(sx(m0["peak_step"]) + 10, sy(m0["peak_total"]) - 10,
                  f"CASE_0 peak {m0['peak_total']:.4f} at t{m0['peak_step']}; CASE_3 identical (dashed)", 11, INK_2,
                  extra=HALO))
    out.append(_t(sx(1) + 10, sy(0) - 12, "CASE_2 absorbed at D6 (t1); CASE_1 zero throughout", 11, INK_2, extra=HALO))
    # panel B: cumulative D8 exposure
    acc = lambda vals: [sum(vals[: t + 1]) for t in range(len(vals))]  # noqa: E731
    c3 = cases["CASE_3"]["trajectory"]
    d8_total = acc([r["D8"] for r in cases["CASE_0"]["trajectory"]])
    ymax = math.ceil(d8_total[-1] * 2) / 2
    sx2, sy2 = _axes(out, x0, 470, w, 240, ymax, [k * 0.5 for k in range(int(ymax * 2) + 1)],
                     "B. Cumulative D8 exposure (production)")
    d8_committed = acc([r["D8_committed"] for r in c3])
    _line(out, sx2, sy2, d8_total, INK, "circle", "", "CASE_0 / CASE_3 D8 entering the node (CASE_0: all committed)")
    _line(out, sx2, sy2, d8_committed, "#1baf7a", "diamond", ' stroke-dasharray="7 5"', "CASE_3 committed pre-maturity (40%)")
    _line(out, sx2, sy2, acc([r["D8"] for r in cases["CASE_2"]["trajectory"]]), "#eb6834", "triangle", "", "CASE_2 D8")
    out.append(_t(sx2(HORIZON) + 12, sy2(d8_total[-1]) + 4, f"entering D8 {d8_total[-1]:.3f}", 12, INK))
    out.append(_t(sx2(HORIZON) + 12, sy2(d8_committed[-1]) + 4, f"CASE_3 committed {d8_committed[-1]:.3f}", 12, INK))
    out.append(_t(sx2(HORIZON) + 12, sy2(0) + 4, "CASE_1, CASE_2: 0", 12, INK))
    # legend
    ly = 780
    out.append(_t(24, ly, "Cases", 13, INK, weight="600"))
    for k, cid in enumerate(("CASE_0", "CASE_1", "CASE_2", "CASE_3")):
        color, shape, dash = CASE_STYLE[cid]
        x, y = 24 + (k % 2) * 470, ly + 24 + (k // 2) * 24
        out.append(f'<line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y}" stroke="{color}" stroke-width="2"{dash}/>')
        out.append(_marker(shape, x + 15, y, color))
        out.append(_t(x + 40, y + 4, f"{cid} {cases[cid]['label']}", 12, INK_2))
    out.append(_t(24, ly + 84, "Panel B: CASE_3 changes the committed share only (40%); the D8 disturbance entering the node "
                               "equals CASE_0. Hover any point for its value.", 11))
    out.append("</svg>")
    return "\n".join(out) + "\n"
