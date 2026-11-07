"""Deterministic translation from schedule disturbances (workdays) to the dimensionless WTM initial state.

Reads the frozen synthetic baseline v1.1 (scenarios, IMS floats, activity -> DSM node) and the WTM node order.
Nothing in the baseline, DSM or WTM is changed, and no trajectory is propagated here.

    net_slip_days        = gross_slip_days - recovery_days            (forecast slip after any recovery)
    exposed_delay_days   = max(0, net_slip_days - available_total_float_days)
    normalized           = exposed_delay_days / REFERENCE_EXPOSED_DELAY_DAYS
    x(0)[target node]    = normalized; every other node 0

Float absorbs a slip before it can enter the propagation model. The float used is the disturbed activity's own
baseline total float (standard CPM: a slip consumes that activity's float); it is checked against the float at the
end of the same path, at the A405 convergence point (A230 for software, A325 for test aircraft).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from ppm_agent.synthetic.validation import load_dataset
from ppm_agent.tools.dsm_tools import read_matrix_csv

REFERENCE_EXPOSED_DELAY_DAYS = 4.0  # SYNTHETIC normalization constant for the proof-of-concept harness only
REFERENCE_NOTE = ("SYNTHETIC normalization constant for the capstone proof-of-concept test harness. Not a probability, "
                  "not a historical F-35 calibration and not a universal program-management constant. Chosen so that the "
                  "exposed delay of each frozen disturbance (4 workdays) maps to the normalized unit disturbance 1.0 used "
                  "in the WTM analysis.")
STATEMENT = ("Scenario mapping for the illustrative WTM test harness. Slips, recoveries, floats and the normalization "
             "constant are SYNTHETIC; the resulting initial states are normalized analytical disturbances, not "
             "probabilities or historical measurements.")
FORMULA = ("exposed_delay_days = max(0, (gross_slip_days - recovery_days) - available_total_float_days); "
           "normalized_disturbance = exposed_delay_days / reference_exposed_delay_days")
PATH_END = {"A210": "A230", "A305": "A325"}  # convergence-point reference for each disturbed path (into A405)
INPUTS = ("data/synthetic/synthetic_scenarios.json", "data/synthetic/synthetic_ims.csv", "outputs/wtm/wtm_matrix.csv")


def exposed_delay(gross_slip_days: float, available_float_days: float, recovery_days: float = 0.0) -> float:
    if min(gross_slip_days, available_float_days, recovery_days) < 0:
        raise ValueError("slip, float and recovery must be non-negative")
    return max(0.0, (gross_slip_days - recovery_days) - available_float_days)


def normalize(exposed_delay_days: float, reference: float = REFERENCE_EXPOSED_DELAY_DAYS) -> float:
    if reference <= 0:
        raise ValueError("reference must be positive")
    return exposed_delay_days / reference


def activity_nodes(ds: dict) -> dict[str, str]:
    return {a["activity_id"]: a["dsm_node"] for a in ds["ims"]}


def _chain(scenarios: dict, sid: str) -> list[dict]:
    """Base-first list of scenarios from BASELINE to sid."""
    chain, cur = [], scenarios[sid]
    while cur is not None:
        chain.append(cur)
        cur = scenarios.get(cur["base_scenario"]) if cur["base_scenario"] else None
    return list(reversed(chain))


def _semantics(change: dict) -> dict:
    """Where and how each intervention policy acts; documented here, applied by the later simulator."""
    if change["policy"] == "FLIGHT_TEST_RESEQUENCING_AFTER_READINESS":
        days = change["delay_absorption_days"]
        return {"policy": change["policy"], "acts_at_node": "D6", "acts_at_activity": change["applies_to_activity"],
                "type": "DOWNSTREAM_DELAY_ABSORPTION", "changes_initial_state": False,
                "max_absorption_days": days,
                "max_absorption_normalized": normalize(days),
                "description": ("Not applied to the initial D4 disturbance. Acts only after the disturbance reaches D6 "
                                "Flight-Test Execution: up to 4 workdays (1.0 normalized units) of the delay arriving at "
                                "the A410 flight-test block are absorbed by resequencing, reducing the effective D6 "
                                "consequence. The A405 readiness gate is unchanged."),
                "open_design_choice": ("How the cap is applied inside the step-wise propagation (to D6's first arrival, "
                                       "per step, or as a cumulative cap) is not yet decided; it must be fixed before the "
                                       "intervention comparison."),
                "data_classification": "SYNTHETIC"}
    if change["policy"] == "STAGED_PRODUCTION_COMMITMENT":
        return {"policy": change["policy"], "acts_at_node": "D8", "acts_at_activity": change["commitment_activity"],
                "maturity_gate": change["maturity_gate_activity"], "type": "EXPOSURE_MANAGEMENT",
                "changes_initial_state": False, "changes_upstream_propagation": False,
                "pre_maturity_commitment_fraction": change["pre_maturity_commitment_fraction"],
                "post_maturity_commitment_fraction": change["post_maturity_commitment_fraction"],
                "description": ("Exposure-management, not disturbance-reduction: propagation into D8 is unchanged; only "
                                "the share of the long-lead commitment exposed to disturbance arriving before A430 "
                                "maturity is limited to 40%, the remaining 60% being committed after A430. No rework cost "
                                "is computed."),
                "data_classification": "SYNTHETIC"}
    raise ValueError(f"unknown policy {change['policy']!r}")


def map_scenario(sid: str, scenarios: dict, ims: dict, nodes: dict, node_order: list[str]) -> dict:
    """Initial WTM state and semantics for one scenario, derived from its frozen definition and base chain."""
    gross, recovery, activity, semantics = 0.0, 0.0, None, []
    for step in _chain(scenarios, sid):
        for c in step["changes"]:
            if c["change_type"] == "DURATION_DELTA":
                if activity not in (None, c["activity_id"]):
                    raise ValueError(f"{sid}: more than one disturbed activity")
                activity = c["activity_id"]
                if c["delta_workdays"] >= 0:
                    gross += c["delta_workdays"]
                else:
                    recovery += -c["delta_workdays"]
            elif c["change_type"] == "POLICY" and step["scenario_id"] == sid:
                semantics.append(_semantics(c))
    state = {n: 0.0 for n in node_order}
    record = {"scenario_id": sid, "scenario_type": scenarios[sid]["scenario_type"],
              "base_scenario": scenarios[sid]["base_scenario"], "data_classification": "SYNTHETIC"}
    if activity is None:
        record.update({"disturbed_activity": None, "gross_slip_days": 0.0, "recovery_days": 0.0, "net_slip_days": 0.0,
                       "available_float_days": None, "exposed_delay_days": 0.0,
                       "reference_exposed_delay_days": REFERENCE_EXPOSED_DELAY_DAYS, "normalized_disturbance": 0.0,
                       "target_DSM_node": None})
    else:
        float_days = float(ims[activity]["baseline_total_float"])
        exposed = exposed_delay(gross, float_days, recovery)
        norm = normalize(exposed)
        target = nodes[activity]
        state[target] = norm
        end = PATH_END.get(activity)
        record.update({"disturbed_activity": activity, "gross_slip_days": gross, "recovery_days": recovery,
                       "net_slip_days": gross - recovery, "available_float_days": float_days,
                       "float_source": f"{activity} baseline_total_float",
                       "path_end_activity": end, "path_end_float_days": float(ims[end]["baseline_total_float"]) if end else None,
                       "exposed_delay_days": exposed, "reference_exposed_delay_days": REFERENCE_EXPOSED_DELAY_DAYS,
                       "normalized_disturbance": norm, "target_DSM_node": target})
    record["initial_wtm_state"] = state
    record["intervention_semantics"] = semantics
    if sid == "INTERVENTION_3":
        record["note"] = ("Frozen base scenario is BASELINE (no slip), so the initial state is zero; the policy acts on D8 "
                          "exposure and only shows an effect when combined with a disturbance that reaches D8.")
    return record


def build_mapping(project_root: Path) -> dict:
    ds = load_dataset(project_root / "data" / "synthetic")
    scenarios = {s["scenario_id"]: s for s in ds["scenarios"]["scenarios"]}
    ims = {a["activity_id"]: a for a in ds["ims"]}
    nodes = activity_nodes(ds)
    node_order, _ = read_matrix_csv(project_root / "outputs" / "wtm" / "wtm_matrix.csv")
    return {
        "statement": STATEMENT,
        "computed_by": "ppm_agent.tools.scenario_mapping (deterministic Python; no LLM involvement)",
        "inputs_sha256": {p: hashlib.sha256((project_root / p).read_bytes()).hexdigest() for p in INPUTS},
        "formula": FORMULA,
        "reference_exposed_delay_days": REFERENCE_EXPOSED_DELAY_DAYS,
        "reference_note": REFERENCE_NOTE,
        "float_rule": ("available_total_float_days = the disturbed activity's baseline_total_float (frozen IMS v1.1); "
                       "checked against the path-end float at the A405 convergence point."),
        "wtm_node_order": node_order,
        "activity_to_dsm_node": nodes,
        "scenarios": [map_scenario(sid, scenarios, ims, nodes, node_order) for sid in scenarios],
        "not_done": ["trajectory comparison", "applying intervention policies inside propagation", "rework cost"],
    }


def validate_mapping(m: dict) -> list[str]:
    errors: list[str] = []
    by_id = {s["scenario_id"]: s for s in m["scenarios"]}
    order = m["wtm_node_order"]
    expected = {  # scenario: (gross, float, recovery, exposed, node, value)
        "DISTURBANCE_1": (8.0, 4.0, 0.0, 4.0, "D4", 1.0),
        "DISTURBANCE_2": (4.0, 0.0, 0.0, 4.0, "D5", 1.0),
        "INTERVENTION_1": (8.0, 4.0, 4.0, 0.0, "D4", 0.0),
    }
    for sid, (gross, flt, rec, exp, node, value) in expected.items():
        s = by_id.get(sid)
        if not s:
            errors.append(f"{sid} missing")
            continue
        got = (s["gross_slip_days"], s["available_float_days"], s["recovery_days"], s["exposed_delay_days"],
               s["target_DSM_node"], s["initial_wtm_state"][node])
        if got != (gross, flt, rec, exp, node, value):
            errors.append(f"{sid}: expected {(gross, flt, rec, exp, node, value)}, got {got}")
    for s in m["scenarios"]:
        sid, state = s["scenario_id"], s["initial_wtm_state"]
        if list(state) != order or len(order) != 8:
            errors.append(f"{sid}: initial state must cover the 8 WTM nodes in order")
        values = [v for v in state.values()] + [s["exposed_delay_days"], s["normalized_disturbance"]]
        if not all(isinstance(v, float) and math.isfinite(v) for v in values):
            errors.append(f"{sid}: non-finite or non-float values")
        if any(v < 0 for v in values):
            errors.append(f"{sid}: negative disturbance")
        if s["normalized_disturbance"] != s["exposed_delay_days"] / m["reference_exposed_delay_days"]:
            errors.append(f"{sid}: normalized disturbance inconsistent with the formula")
        nonzero = [n for n, v in state.items() if v]
        if nonzero not in ([], [s["target_DSM_node"]]):
            errors.append(f"{sid}: only the target node may be nonzero, got {nonzero}")
        if s.get("path_end_float_days") is not None and s["path_end_float_days"] != s["available_float_days"]:
            errors.append(f"{sid}: activity float differs from the path-end float at A405")
        if s["data_classification"] != "SYNTHETIC":
            errors.append(f"{sid}: must be SYNTHETIC")
        for sem in s["intervention_semantics"]:
            if sem["changes_initial_state"]:
                errors.append(f"{sid}: intervention policies must not change the initial state")
    i2, i3 = by_id.get("INTERVENTION_2"), by_id.get("INTERVENTION_3")
    if i2 and (i2["initial_wtm_state"] != by_id["DISTURBANCE_1"]["initial_wtm_state"]
               or [x["acts_at_node"] for x in i2["intervention_semantics"]] != ["D6"]
               or i2["intervention_semantics"][0]["max_absorption_days"] != 4):
        errors.append("INTERVENTION_2 must keep the DISTURBANCE_1 initial state and act at D6 with 4 days absorption")
    if i3 and ([x["acts_at_node"] for x in i3["intervention_semantics"]] != ["D8"]
               or i3["intervention_semantics"][0]["type"] != "EXPOSURE_MANAGEMENT"
               or (i3["intervention_semantics"][0]["pre_maturity_commitment_fraction"],
                   i3["intervention_semantics"][0]["post_maturity_commitment_fraction"]) != (0.40, 0.60)):
        errors.append("INTERVENTION_3 must be exposure management at D8 with 0.40 / 0.60")
    return errors


def render_outputs(m: dict) -> dict[str, str]:
    return {"scenario_mapping.json": json.dumps(m, indent=2) + "\n", "scenario_mapping_summary.md": summary_markdown(m)}


def summary_markdown(m: dict) -> str:
    def f(v):
        return "n/a" if v is None else (f"{v:g}" if isinstance(v, float) else str(v))

    rows = "\n".join(
        f"| {s['scenario_id']} | {f(s['base_scenario'])} | {f(s['disturbed_activity'])} | {f(s['gross_slip_days'])} | "
        f"{f(s['recovery_days'])} | {f(s['available_float_days'])} | {f(s['exposed_delay_days'])} | "
        f"{f(s['reference_exposed_delay_days'])} | {f(s['normalized_disturbance'])} | {f(s['target_DSM_node'])} | "
        f"{', '.join(f'{n}={v:g}' for n, v in s['initial_wtm_state'].items() if v) or 'all 0'} | {s['data_classification']} |"
        for s in m["scenarios"])
    by_id = {s["scenario_id"]: s for s in m["scenarios"]}
    i2, i3 = by_id["INTERVENTION_2"]["intervention_semantics"][0], by_id["INTERVENTION_3"]["intervention_semantics"][0]
    return f"""# Schedule-to-WTM scenario mapping

> {m['statement']}

Generated by `scripts/build_scenario_mapping.py` from the frozen synthetic baseline v1.1 and the WTM node order. No trajectory
is propagated and no intervention comparison is made here.

## Formula

$$\\text{{exposed delay}} = \\max\\big(0,\\; (\\text{{gross slip}} - \\text{{recovery}}) - \\text{{available total float}}\\big)$$

$$\\text{{normalized disturbance}} = \\frac{{\\text{{exposed delay}}}}{{\\text{{reference exposed delay}}}}, \\qquad \\text{{reference}} = {m['reference_exposed_delay_days']:g} \\text{{ workdays}}$$

In plain English:
- **Float first.** Schedule float absorbs a slip before anything enters the propagation model. Only the part of the
  slip that float cannot absorb, the exposed delay, becomes a disturbance.
- **Then scale.** The exposed delay is divided by a reference of 4 workdays to give a dimensionless number, which is
  placed on the DSM node of the slipped activity. All other nodes start at 0.

**Which float.** The disturbed activity's own baseline total float, as standard critical-path practice says. It is
checked against the float at the end of the same path, at the A405 convergence point: A230 for software and A325 for
test aircraft. In the frozen baseline they are equal.

**The 4-workday reference** is a SYNTHETIC normalization constant for this proof-of-concept harness only. It is not a
probability, not a historical F-35 calibration and not a universal program-management constant. It was chosen so that
each frozen disturbance's exposed delay (4 workdays) maps to the unit disturbance 1.0 already used in the WTM analysis.

## Scenarios

| Scenario | Base | Activity | Gross slip | Recovery | Float | Exposed | Reference | Normalized | Target node | Initial WTM state | Class |
|---|---|---|---|---|---|---|---|---|---|---|---|
{rows}

- **DISTURBANCE_1:** A210 +8, A230 float 4, so 8 - 4 = **4 exposed**, giving **D4 = 1.0**.
- **DISTURBANCE_2:** A305 +4, A325 float 0, so 4 - 0 = **4 exposed**, giving **D5 = 1.0**.
- **INTERVENTION_1:** gross slip 8, recovery 4, float 4, so 8 - 4 - 4 = **0 exposed**, giving **D4 = 0.0**. The
  recovered slip fits inside the float, so nothing enters propagation.

## Intervention semantics

- **INTERVENTION_2: {i2['policy']}, a downstream delay-absorption intervention at {i2['acts_at_node']}
  ({i2['acts_at_activity']}).**
  - It starts from the DISTURBANCE_1 state (D4 = 1.0). It is **not** applied to the initial D4 disturbance.
  - {i2['description']}
  - Maximum absorption is {i2['max_absorption_days']} workdays, which is {i2['max_absorption_normalized']:g}
    normalized units.
  - Open design choice: {i2['open_design_choice']}
- **INTERVENTION_3: {i3['policy']}, an exposure-management intervention at {i3['acts_at_node']}, gated on
  {i3['maturity_gate']}.**
  - {i3['description']}
  - Pre-maturity fraction {i3['pre_maturity_commitment_fraction']:.2f}, post-maturity fraction
    {i3['post_maturity_commitment_fraction']:.2f}. Both are SYNTHETIC.
  - Note: {by_id['INTERVENTION_3']['note']}

## Limitations

- One linear mapping and one reference constant. The same exposed delay always maps to the same disturbance, whatever
  the activity's size or criticality.
- Only the slipped activity's node is disturbed. Float is treated as fully available, with no other demands on it.
- Workday slips become dimensionless units. Reading WTM outputs back as days (value × 4) is a convention of this
  harness, not a calibration.
- The intervention policies are described here but applied only in the later simulation. The INTERVENTION_2 cap rule
  is still open.

## Input fingerprints

{chr(10).join(f"- `{k}`: `{v}`" for k, v in m['inputs_sha256'].items())}
"""
