"""Predictive Simulation and Intervention Agent (Module 5, Agent 2): interprets the frozen deterministic comparison.

Responsibility boundary:
  - Python builds a catalogue of FACTS (ids and exact values) from the frozen simulation outputs, plus ASSUMPTIONS
    and LIMITATIONS, and is authoritative for every number.
  - The model (REAL_LLM_MODE, one structured call) or a rule-based stand-in (MOCK_AGENT_MODE) returns a
    PredictiveInterventionOutput. The schema has no numeric fields. Key qualitative claims are structured (effect
    enums, booleans, comparison claims, objective preferences, secondary options) and cite catalogue ids.
  - Python validates the output deterministically, with no model involved:
      citations   every cited id exists; required claims cite at least one FACT id; nothing is repaired;
      numbers     digits must equal a catalogue value; spelled-out quantities (number words, decimals, fractions,
                  percentages in words, approximations) are rejected;
      qualitative each structured effect / boolean / comparison is recomputed from the facts; a backup prose rule
                  rejects D8 "unchanged" statements that contradict the facts;
      objectives  preferred cases must attain the minimum of the objective's single metric (ties allowed);
                  secondary options must state their effect and minimum status truthfully;
      coverage    every LIMITATION id is covered; human_review_required must be true;
      narrative   (contract v3) the structured preferred_for_* fields are the only authoritative objective
                  selections; free text (overall recommendation, rationales, trade-offs) is explanatory and is
                  checked deterministically for contradictions with those fields and the minima.
  - Status: VALIDATED (usable downstream), COMPLETED_WITH_VALIDATION_ERRORS (raw response kept, errors recorded,
    human review required) or FAILED (no response; nothing invented). A configuration error is fatal (raised).
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from datetime import datetime
from pathlib import Path

from ppm_agent.agents.llm import LLMCallError, MOCK_AGENT_MODE, agent_mode
from ppm_agent.models.intervention import PredictiveInterventionOutput

PROMPT = (Path(__file__).parent / "prompts" / "predictive_intervention.md").read_text(encoding="utf-8")
INPUTS = ("outputs/simulation/intervention_comparison.json", "outputs/simulation/predictive_trajectories.csv",
          "outputs/simulation/scenario_mapping.json", "outputs/wtm/structural_analysis.json")
VALIDATED, WITH_ERRORS, FAILED = "VALIDATED", "COMPLETED_WITH_VALIDATION_ERRORS", "FAILED"
CASES = ("CASE_0", "CASE_1", "CASE_2", "CASE_3")
CASE_INTERVENTION = {"CASE_1": "INTERVENTION_1", "CASE_2": "INTERVENTION_2", "CASE_3": "INTERVENTION_3"}
METRIC_DESC = {
    "TOTAL_DISTURBANCE": "cumulative total disturbance (t0..t12)",
    "D6_EXPOSURE": "cumulative effective D6 disturbance (after any absorption)",
    "D8_ENTERING": "cumulative disturbance entering D8",
    "D8_COMMITTED": "cumulative D8 exposure committed before maturity (all of it for cases without staging)",
    "PEAK_DISTURBANCE": "peak total disturbance",
}
OBJECTIVE_METRIC = {"MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE": "TOTAL_DISTURBANCE",
                    "PROTECT_FLIGHT_TEST_EXECUTION": "D6_EXPOSURE",
                    "LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE": "D8_COMMITTED"}
EFFECT_FIELDS = {"effect_on_total_disturbance": "TOTAL_DISTURBANCE", "effect_on_D6_exposure": "D6_EXPOSURE",
                 "effect_on_D8_entering": "D8_ENTERING", "effect_on_D8_committed": "D8_COMMITTED"}
CONTRACT_VERSION = 3
STRUCTURED_PREFERENCES = {  # authoritative field -> objective
    "preferred_for_total_disturbance": "MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE",
    "preferred_for_flight_test": "PROTECT_FLIGHT_TEST_EXECUTION",
    "preferred_for_production_commitment": "LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE",
}
# deterministic narrative-consistency rule: a clause that uses a preference verb, names exactly one objective and
# names case(s) must name only cases in that objective's structured field and its deterministic minimum.
NARRATIVE_OBJECTIVE = {
    "preferred_for_total_disturbance": re.compile(r"\btotal\b|propagated\s+disturbance|overall\s+disturbance|"
                                                  r"eliminat\w*\s+(?:of\s+)?(?:all\s+)?disturbance", re.I),
    "preferred_for_flight_test": re.compile(r"flight[\s-]+test|\bD6\b", re.I),
    "preferred_for_production_commitment": re.compile(r"production|commit\w*|pre-maturity|\bD8\b", re.I),
}
PREFERENCE_VERB = re.compile(r"\b(?:favou?rs?|favou?red|prefer(?:s|red|able)?|recommend(?:s|ed)?|best|optimal|choose|"
                             r"chosen|choice|minimi[sz]e[sd]?|minimi[sz]ing|should\s+(?:be\s+)?(?:use|used|select|"
                             r"selected|choose|chosen|adopt|adopted))\b", re.I)
HEDGE = re.compile(r"\b(?:not|never|rather\s+than|instead\s+of|secondary|although|though|unless|except)\b|n't\b", re.I)
CASE_REF = re.compile(r"\b(?:CASE|INTERVENTION)_([0-3])\b")
TOL = 1e-9
ASSUMPTIONS = {
    "ASSUMPTION.synthetic_baseline": "The IMP/IMS (v1.1) is a synthetic, evidence-calibrated schedule, not an actual or "
                                     "reconstructed F-35 contractor schedule. SYNTHETIC.",
    "ASSUMPTION.provenance_model": "Public GAO / DOT&E passages are OBSERVED; dependency concepts inferred from them are "
                                   "DERIVED; every activity-level link, duration and scenario magnitude is SYNTHETIC. "
                                   "Agentic decisions set three weights (Q01 PARTIALLY_SUPPORTED, Q04 and Q08 UNRESOLVED).",
    "ASSUMPTION.ordinal_weights_as_coefficients": "Ordinal DSM evidence tiers are used directly as multiplicative "
                                                  "propagation coefficients in x(t+1) = W^T x(t).",
    "ASSUMPTION.float_absorbs_first": "Schedule float absorbs a slip before it enters the propagation model "
                                      "(exposed delay = slip - recovery - float, floored at zero).",
    "ASSUMPTION.normalization_4_days": "4 exposed workdays = 1.0 normalized unit (SYNTHETIC normalization constant).",
    "ASSUMPTION.resequencing_cumulative_capacity": "INTERVENTION_2 absorbs D6 disturbance from a cumulative capacity of "
                                                   "1.0 normalized unit that never resets (SYNTHETIC).",
    "ASSUMPTION.staged_commitment_split": "INTERVENTION_3 commits 40% of D8 exposure before maturity and gates 60% "
                                          "(SYNTHETIC; not historical policy). NO ACTION commits all of it before maturity.",
}
LIMITATIONS = {
    "LIMITATION.synthetic_imp_ims": "The IMP/IMS and all activity-level links are synthetic.",
    "LIMITATION.ordinal_weights": "Weights are ordinal evidence tiers, not calibrated probabilities or rework fractions.",
    "LIMITATION.normalization_4_day": "The 4-day normalization is a synthetic constant, not a calibration.",
    "LIMITATION.single_deterministic_scenario": "One deterministic initiating scenario (DISTURBANCE_1); no stochastic "
                                                "variation or sensitivity analysis.",
    "LIMITATION.synthetic_intervention_magnitudes": "Recovery days, resequencing capacity and commitment fractions are "
                                                    "synthetic policy values.",
    "LIMITATION.horizon_t12_truncation": "Cumulative metrics are truncated at t12; NO ACTION has not fully decayed by t12.",
    "LIMITATION.no_intervention_combinations": "Interventions are evaluated one at a time, never in combination.",
    "LIMITATION.no_historical_calibration": "Nothing is calibrated to historical F-35 outcomes; results do not predict them.",
}
# identifiers that legitimately contain digits; removed before the numeral check
IDENTIFIER = re.compile(r"\b[A-Z][A-Z0-9_]*\.[A-Za-z0-9_.]*[A-Za-z0-9_]|\b(?:CASE|INTERVENTION|DISTURBANCE)_\d+\b|\bD[1-8]\b"
                        r"|\bA\d{3}\b|\bt\d{1,2}\b|\bQ\d{2}\b|\bIMP-\d{2}\b|\bF-35\b|\bv\d+(?:\.\d+)*\b"
                        r"|\b(?:Module|Agent)\s+\d+\b")
NUMERAL = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(\s*(?:%|percent))?")
_UNITS = ("zero|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
          "eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|dozen")
SPELLED = [  # (kind, pattern); "one" alone is excluded (too common in prose) but caught in decimals and fractions
    ("decimal in words", re.compile(rf"\b(?:one|{_UNITS})\s+point\s+\w+", re.I)),
    ("number word", re.compile(rf"\b(?:{_UNITS})(?:-\w+)?\b", re.I)),
    ("fraction in words", re.compile(r"\b(?:half|halves|quarters?|thirds?|fifths?|sixths?|eighths?|tenths?)\b", re.I)),
    ("percentage in words", re.compile(r"\b(?:percent|per\s+cent|percentage\s+points?)\b", re.I)),
    ("multiplier in words", re.compile(r"\b(?:twice|double|doubled|triple|tripled|threefold|twofold)\b", re.I)),
]
UNCHANGED_WORDS = re.compile(r"\b(?:unchanged|remains?\s+the\s+same|does\s+not\s+change|not\s+change|no\s+change|"
                             r"does\s+not\s+(?:reduce|affect|alter)|remains?\s+unaltered)\b", re.I)


# --- deterministic inputs ------------------------------------------------------------------------------

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_catalogue(project_root: Path) -> dict:
    comp = json.loads((project_root / INPUTS[0]).read_text(encoding="utf-8"))
    mapping = json.loads((project_root / INPUTS[2]).read_text(encoding="utf-8"))
    structure = json.loads((project_root / INPUTS[3]).read_text(encoding="utf-8"))
    with (project_root / INPUTS[1]).open(encoding="utf-8", newline="") as f:
        trajectories = list(csv.DictReader(f))
    case2 = [r for r in trajectories if r["case_id"] == "CASE_2"]
    first = next(r for r in case2 if float(r["D6_before_absorption"]) > 0)
    by_case = {c: {r["t"]: r for r in trajectories if r["case_id"] == c} for c in CASES}
    # validation truth for changes_any_D1_to_D7_trajectory (step-by-step trajectories; not sent to the model)
    trajectory_flags = {c: any(abs(float(by_case[c][t][f"D{n}"]) - float(by_case["CASE_0"][t][f"D{n}"])) > TOL
                               for t in by_case["CASE_0"] for n in range(1, 8)) for c in CASE_INTERVENTION}
    scen = {s["scenario_id"]: s for s in mapping["scenarios"]}
    facts: dict[str, float] = {}
    for c in comp["cases"]:
        for k, v in c["metrics"].items():
            if v is not None:
                facts[f"{c['case_id']}.{k}"] = float(v)
        for k, ch in c.get("change_vs_no_action", {}).items():
            for kind, v in ch.items():
                if v is not None:
                    facts[f"{c['case_id']}.change.{k}.{kind}"] = float(v)
    d1, i1 = scen["DISTURBANCE_1"], scen["INTERVENTION_1"]
    i2, i3 = scen["INTERVENTION_2"]["intervention_semantics"][0], scen["INTERVENTION_3"]["intervention_semantics"][0]
    facts.update({
        "DISTURBANCE_1.gross_slip_days": d1["gross_slip_days"], "DISTURBANCE_1.available_float_days": d1["available_float_days"],
        "DISTURBANCE_1.exposed_delay_days": d1["exposed_delay_days"],
        "DISTURBANCE_1.initial_D4": d1["initial_wtm_state"]["D4"],
        "MAPPING.reference_exposed_delay_days": mapping["reference_exposed_delay_days"],
        "INTERVENTION_1.recovery_days": i1["recovery_days"], "INTERVENTION_1.exposed_delay_days": i1["exposed_delay_days"],
        "INTERVENTION_2.capacity_days": float(i2["max_absorption_days"]),
        "INTERVENTION_2.capacity_normalized": float(i2["max_absorption_normalized"]),
        "CASE_2.D6_first_arrival": float(first["D6_before_absorption"]), "CASE_2.D6_first_arrival_step": float(first["t"]),
        "INTERVENTION_3.pre_maturity_commitment_fraction": float(i3["pre_maturity_commitment_fraction"]),
        "INTERVENTION_3.post_maturity_commitment_fraction": float(i3["post_maturity_commitment_fraction"]),
        "SIMULATION.horizon_last_step": float(len(case2) - 1),
        "WTM.spectral_radius": float(structure["spectral_radius"]),
    })
    cases = [{"case_id": c["case_id"], "label": c["label"], "intervention_id": CASE_INTERVENTION.get(c["case_id"]),
              "initial_state_from": c["initial_state_from"], "policy": c["policy"]} for c in comp["cases"]]
    return {
        "statement": comp["statement"],
        "common_initiating_disturbance": comp["common_initiating_disturbance"],
        "equation": comp["equation"], "horizon": comp["horizon"],
        "intervention_2_rule": comp["intervention_2_rule"], "intervention_3_rule": comp["intervention_3_rule"],
        "intervention_3_note": comp["intervention_3_note"],
        "cases": cases, "facts": {k: facts[k] for k in sorted(facts)},
        "trajectory_flags": {"changes_any_D1_to_D7_trajectory": trajectory_flags},
        "assumptions": ASSUMPTIONS, "limitations": LIMITATIONS,
        "inputs_sha256": {p: _sha(project_root / p) for p in INPUTS},
    }


def valid_ids(cat: dict) -> set[str]:
    return set(cat["facts"]) | set(cat["assumptions"]) | set(cat["limitations"]) | \
        {c["case_id"] for c in cat["cases"]} | {"DISTURBANCE_1", *CASE_INTERVENTION.values()}


def metric_value(cat: dict, case: str, metric: str) -> float:
    f = cat["facts"]
    key = {"TOTAL_DISTURBANCE": "cumulative_total", "D6_EXPOSURE": "cumulative_D6", "D8_ENTERING": "cumulative_D8",
           "PEAK_DISTURBANCE": "peak_total"}.get(metric)
    if key:
        return f[f"{case}.{key}"]
    return f.get(f"{case}.cumulative_D8_committed_pre_maturity", f[f"{case}.cumulative_D8"])  # D8_COMMITTED


def classify_effect(base: float, value: float) -> str:
    if abs(base) <= TOL:
        return "UNCHANGED" if abs(value) <= TOL else "INCREASED"
    if abs(value) <= TOL:
        return "ELIMINATED"
    if abs(value - base) <= TOL:
        return "UNCHANGED"
    return "REDUCED" if value < base else "INCREASED"


def deterministic_effects(cat: dict) -> dict:
    """Per intervention case, the Python-computed truth for every structured claim (relative to CASE_0)."""
    out = {}
    for case in CASE_INTERVENTION:
        e = {fld: classify_effect(metric_value(cat, "CASE_0", m), metric_value(cat, case, m))
             for fld, m in EFFECT_FIELDS.items()}
        e["disturbance_reaches_D8"] = metric_value(cat, case, "D8_ENTERING") > TOL
        # TRUE if any D1-D7 value differs from NO ACTION at any step t0..t12; FALSE only if all are identical
        e["changes_any_D1_to_D7_trajectory"] = cat["trajectory_flags"]["changes_any_D1_to_D7_trajectory"][case]
        out[case] = e
    return out


def objective_facts(cat: dict) -> dict:
    """Per objective: each case's value of that objective's single metric and the case(s) attaining the minimum."""
    out = {}
    for obj, metric in OBJECTIVE_METRIC.items():
        values = {c: metric_value(cat, c, metric) for c in CASES}
        low = min(values.values())
        out[obj] = {"metric": METRIC_DESC[metric], "values": values,
                    "lowest_cases": [c for c, v in values.items() if abs(v - low) <= TOL]}
    return out


def user_message(cat: dict) -> str:
    payload = {k: cat[k] for k in ("statement", "common_initiating_disturbance", "equation", "horizon",
                                   "intervention_2_rule", "intervention_3_rule", "intervention_3_note", "cases",
                                   "assumptions", "limitations")}
    payload["facts"] = {k: round(v, 4) for k, v in cat["facts"].items()}
    return ("Interpret these frozen deterministic results. Cite ids exactly as listed; do not state numbers in any form "
            "(do not write numerals or number words).\n\n" + json.dumps(payload, indent=2))


# --- mock stand-in -------------------------------------------------------------------------------------

def mock_interpret(cat: dict) -> PredictiveInterventionOutput:
    """MOCK_AGENT_MODE: rule-based output built from Python's own effects (no model call, no numbers in prose).
    Never presented as LLM output."""
    eff, obj = deterministic_effects(cat), objective_facts(cat)
    text = {
        "CASE_1": ("[MOCK] Prevent exposure from entering the propagation model.",
                   "[MOCK] The recovered slip fits inside the float, so no disturbance propagates.",
                   "[MOCK] The dependency structure itself."),
        "CASE_2": ("[MOCK] Absorb downstream disturbance at flight test.",
                   "[MOCK] The capacity absorbs the whole disturbance reaching flight test, with capacity left unused; "
                   "this depends on the synthetic scenario magnitude.",
                   "[MOCK] The initial software disturbance and the readiness gate."),
        "CASE_3": ("[MOCK] Limit pre-maturity production commitment.",
                   "[MOCK] The committed share of production exposure is reduced.",
                   "[MOCK] Upstream propagation and the disturbance entering D8."),
    }
    cites = {"CASE_1": ["INTERVENTION_1.exposed_delay_days", "CASE_1.cumulative_total"],
             "CASE_2": ["CASE_2.D6_first_arrival", "CASE_2.intervention_used", "CASE_2.intervention_unused"],
             "CASE_3": ["CASE_3.cumulative_D8_committed_pre_maturity", "CASE_3.change.cumulative_D8.absolute_reduction"]}
    secondary = []
    for o, v in obj.items():
        metric = OBJECTIVE_METRIC[o]
        for c in CASE_INTERVENTION:
            effect = classify_effect(metric_value(cat, "CASE_0", metric), metric_value(cat, c, metric))
            if c not in v["lowest_cases"] and effect in ("REDUCED", "ELIMINATED"):
                secondary.append({"case_id": c, "objective": o, "condition": "[MOCK] Improves on NO ACTION but is not "
                                  "the minimum.", "effect_vs_no_action": effect, "is_minimum_for_objective": False,
                                  "cited_ids": [f"{c}.cumulative_D8_committed_pre_maturity"
                                                if f"{c}.cumulative_D8_committed_pre_maturity" in cat["facts"]
                                                else f"{c}.cumulative_total"]})
    return PredictiveInterventionOutput.model_validate({
        "no_action_assessment": {"statement": "[MOCK] Under NO ACTION the software disturbance propagates to flight test, "
                                              "development maturity and production, peaks early and decays slowly.",
                                 "cited_ids": ["CASE_0.peak_total", "CASE_0.peak_step", "CASE_0.final_total",
                                               "WTM.spectral_radius"]},
        "intervention_assessments": [
            {"case_id": c, "intervention_id": CASE_INTERVENTION[c], **eff[c], "management_objective": text[c][0],
             "effect_on_trajectory": text[c][1], "what_it_does_not_change": text[c][2], "cited_ids": cites[c]}
            for c in CASE_INTERVENTION],
        "comparative_claims": [{"metric": "TOTAL_DISTURBANCE", "left_case": "CASE_1", "relation": "LOWER_THAN",
                                "right_case": "CASE_2", "cited_ids": ["CASE_1.cumulative_total", "CASE_2.cumulative_total"]},
                               {"metric": "D8_ENTERING", "left_case": "CASE_3", "relation": "EQUAL_TO",
                                "right_case": "CASE_0", "cited_ids": ["CASE_3.cumulative_D8", "CASE_0.cumulative_D8"]}],
        "management_tradeoffs": [{"statement": "[MOCK] The interventions act at different points: before propagation, at "
                                               "flight test, and at production commitment.",
                                  "cited_ids": ["CASE_1.cumulative_total", "CASE_2.intervention_used",
                                                "CASE_3.cumulative_D8_committed_pre_maturity"]}],
        **{fld: obj[o]["lowest_cases"] for fld, o in STRUCTURED_PREFERENCES.items()},
        "preferred_intervention_by_objective": [
            {"objective": o, "preferred_case_ids": v["lowest_cases"], "rationale": f"[MOCK] Lowest value of: {v['metric']}.",
             "conditions_and_caveats": "[MOCK] Single synthetic scenario.",
             "cited_ids": ["CASE_1.cumulative_total", "CASE_2.cumulative_total"]}
            for o, v in obj.items()],
        "secondary_options": secondary,
        "key_assumptions": [{"statement": "[MOCK] See the assumption catalogue.", "cited_ids": list(ASSUMPTIONS)}],
        "uncertainties": [{"statement": f"[MOCK] {LIMITATIONS[i]}", "cited_ids": [i]} for i in LIMITATIONS],
        "human_review_required": True,
        "human_review_reason": "[MOCK] Decision support from a synthetic model; a human must decide.",
        "overall_recommendation": {"statement": "[MOCK] The choice depends on the objective; see the preferences by "
                                                "objective.", "cited_ids": ["CASE_0.cumulative_total"]},
        "confidence_or_support_summary": "[MOCK] Deterministic facts; interpretation is rule-based.",
    })


# --- text extraction -----------------------------------------------------------------------------------

def _texts(out: PredictiveInterventionOutput) -> list[tuple[str, str]]:
    """(field path, text) for every free-text field, with the case it belongs to encoded in the path prefix."""
    items = [("no_action_assessment", out.no_action_assessment.statement), ("human_review_reason", out.human_review_reason),
             ("overall_recommendation", out.overall_recommendation.statement),
             ("confidence_or_support_summary", out.confidence_or_support_summary)]
    for a in out.intervention_assessments:
        items += [(f"{a.case_id}.{k}", getattr(a, k)) for k in ("management_objective", "effect_on_trajectory",
                                                               "what_it_does_not_change")]
    for p in out.preferred_intervention_by_objective:
        items += [(f"{p.objective}.rationale", p.rationale), (f"{p.objective}.conditions", p.conditions_and_caveats)]
    for i, s in enumerate(out.secondary_options):
        items.append((f"secondary_options[{i}].{s.case_id}.condition", s.condition))
    for name in ("management_tradeoffs", "key_assumptions", "uncertainties"):
        items += [(f"{name}[{i}]", s.statement) for i, s in enumerate(getattr(out, name))]
    return items


def numeric_check(out: PredictiveInterventionOutput, cat: dict) -> dict:
    """Every digit-numeral in free text (identifiers excluded) must equal a catalogue value at its displayed precision."""
    return _numeric_check_texts(_texts(out), cat)


def _numeric_check_texts(texts: list[tuple[str, str]], cat: dict) -> dict:
    values = list(cat["facts"].values())
    percents = values + [v * 100 for k, v in cat["facts"].items() if "fraction" in k]
    found, unsupported = [], []
    for field, text in texts:
        for m in NUMERAL.finditer(IDENTIFIER.sub(" ", text)):
            token, pct = m.group(1), bool(m.group(2))
            x = float(token)
            tol = 0.5 * 10 ** -(len(token.split(".")[1]) if "." in token else 0) + 1e-12
            ok = any(abs(x - v) <= tol for v in (percents if pct else values))
            found.append({"field": field, "numeral": m.group(0).strip(), "supported": ok})
            if not ok:
                unsupported.append({"field": field, "numeral": m.group(0).strip()})
    return {"numerals_found": found, "unsupported": unsupported, "result": "PASS" if not unsupported else "FAIL"}


def spelled_number_check(texts: list[tuple[str, str]]) -> dict:
    """Reject numerical quantities written in words. Identifiers are removed first."""
    hits = []
    for field, text in texts:
        clean = IDENTIFIER.sub(" ", text)
        seen = set()
        for kind, pattern in SPELLED:
            for m in pattern.finditer(clean):
                if any(m.start() < e and s < m.end() for s, e in seen):
                    continue  # already reported as part of a longer match
                seen.add((m.start(), m.end()))
                hits.append({"field": field, "kind": kind, "text": m.group(0)})
    return {"spelled_quantities": hits, "result": "PASS" if not hits else "FAIL"}


def narrative_check(texts: list[tuple[str, str]], structured: dict[str, set], minima: dict[str, set]) -> dict:
    """Deterministic check that free text does not contradict the authoritative objective selections.

    Text is split into sentences (. ;) and clauses (, while whereas but); a clause that names no objective inherits
    the objective named earlier in the same sentence. A clause is checked when it contains a preference verb
    (favors, preferred, best, minimizes, ...), has exactly one objective and names at least one case / intervention.
    Hedged clauses
    (not, rather than, secondary, although, ...) and clauses naming several objectives are recorded as unchecked
    rather than guessed. A checked clause contradicts when it names a case outside that objective's structured
    field or its deterministic minimum."""
    contradictions, consistent, unchecked = [], [], []
    for field, text in texts:
        for sentence in re.split(r"(?<=[.;])\s+|[.;]$", text):
            inherited: list[str] = []  # "For limiting production commitment, INTERVENTION_3 is best": the objective
            for clause in re.split(r",|\bwhile\b|\bwhereas\b|\bbut\b", sentence):  # carries over within a sentence
                objectives = [o for o, rx in NARRATIVE_OBJECTIVE.items() if rx.search(clause)]
                if objectives:
                    inherited = objectives
                else:
                    objectives = inherited
                if not PREFERENCE_VERB.search(clause):
                    continue
                cases = {f"CASE_{n}" for n in CASE_REF.findall(clause)}
                if not cases or not objectives:
                    continue
                _check_clause(field, clause, cases, objectives, structured, minima, contradictions, consistent, unchecked)
    return {"contradictions": contradictions, "consistent": consistent, "unchecked": unchecked,
            "result": "PASS" if not contradictions else "FAIL"}


def _check_clause(field, clause, cases, objectives, structured, minima, contradictions, consistent, unchecked) -> None:
    record = {"field": field, "clause": clause.strip(), "cases": sorted(cases)}
    if HEDGE.search(clause) or len(objectives) != 1:
        unchecked.append({**record, "reason": "hedged" if HEDGE.search(clause) else "several objectives"})
        return
    o = objectives[0]
    outside = sorted(cases - (structured[o] & minima[o]))
    record.update({"objective_field": o, "structured": sorted(structured[o]), "minimum": sorted(minima[o])})
    if outside:
        contradictions.append({**record, "outside": outside})
    else:
        consistent.append(record)


def prose_d8_check(texts: list[tuple[str, str]], effects: dict) -> list[dict]:
    """Backup rule for case-scoped prose: a sentence that says D8 (entering) is unchanged / not reduced must agree
    with the deterministic D8-entering effect. Sentences about commitment are skipped (a different metric)."""
    findings = []
    for field, text in texts:
        case = next((c for c in CASE_INTERVENTION if field.startswith(c) or f".{c}." in field), None)
        if not case:
            continue
        for sentence in re.split(r"(?<=[.;])\s+", text):
            if "D8" in sentence and not re.search(r"commit", sentence, re.I) and UNCHANGED_WORDS.search(sentence):
                actual = effects[case]["effect_on_D8_entering"]
                if actual != "UNCHANGED":
                    findings.append({"field": field, "sentence": sentence.strip(), "deterministic_D8_entering": actual})
    return findings


# --- deterministic validation --------------------------------------------------------------------------

def validate_output(out: PredictiveInterventionOutput, cat: dict) -> dict:
    cats = {k: [] for k in ("structure", "citation", "numeric", "qualitative", "objective", "narrative", "coverage",
                            "human_review")}
    ids, fact_ids = valid_ids(cat), set(cat["facts"])
    effects, obj = deterministic_effects(cat), objective_facts(cat)

    # structure
    cases = [a.case_id for a in out.intervention_assessments]
    if sorted(cases) != ["CASE_1", "CASE_2", "CASE_3"]:
        cats["structure"].append(f"intervention_assessments must cover CASE_1, CASE_2, CASE_3 exactly once, got {cases}")
    for a in out.intervention_assessments:
        if CASE_INTERVENTION[a.case_id] != a.intervention_id:
            cats["structure"].append(f"{a.case_id} paired with {a.intervention_id}")
    objectives = [p.objective for p in out.preferred_intervention_by_objective]
    if sorted(objectives) != sorted(OBJECTIVE_METRIC):
        cats["structure"].append(f"preferred_intervention_by_objective must cover each objective once, got {objectives}")

    # citations: every id exists; required claims cite at least one FACT id; never repaired
    need_fact = [("no_action_assessment", out.no_action_assessment.cited_ids),
                 ("overall_recommendation", out.overall_recommendation.cited_ids)]
    need_fact += [(a.case_id, a.cited_ids) for a in out.intervention_assessments]
    need_fact += [(f"comparative_claims[{i}]", c.cited_ids) for i, c in enumerate(out.comparative_claims)]
    need_fact += [(p.objective, p.cited_ids) for p in out.preferred_intervention_by_objective]
    need_fact += [(f"secondary_options[{i}]", s.cited_ids) for i, s in enumerate(out.secondary_options)]
    need_fact += [(f"management_tradeoffs[{i}]", s.cited_ids) for i, s in enumerate(out.management_tradeoffs)]
    other = [(f"key_assumptions[{i}]", s.cited_ids) for i, s in enumerate(out.key_assumptions)]
    other += [(f"uncertainties[{i}]", s.cited_ids) for i, s in enumerate(out.uncertainties)]
    for where, cids in need_fact + other:
        if not cids:
            cats["citation"].append(f"{where}: no citation")
        for c in cids:
            if c not in ids:
                cats["citation"].append(f"{where}: unknown id {c!r}")
    for where, cids in need_fact:
        if cids and not any(c in fact_ids for c in cids):
            cats["citation"].append(f"{where}: must cite at least one FACT id")
    for a in out.intervention_assessments:
        if not any(c.startswith((f"{a.case_id}.", f"{a.intervention_id}.")) for c in a.cited_ids):
            cats["citation"].append(f"{a.case_id}: must cite at least one fact of its own case")
    if not any(c.startswith("CASE_0.") for c in out.no_action_assessment.cited_ids):
        cats["citation"].append("no_action_assessment must cite CASE_0 facts")

    # numbers: digits must match facts; no spelled-out quantities
    texts = _texts(out)
    nums, words = _numeric_check_texts(texts, cat), spelled_number_check(texts)
    cats["numeric"] += [f"unsupported numeral {u['numeral']!r} in {u['field']}" for u in nums["unsupported"]]
    cats["numeric"] += [f"spelled-out quantity ({h['kind']}) {h['text']!r} in {h['field']}" for h in words["spelled_quantities"]]

    # qualitative: structured claims against the facts, plus the backup prose rule
    claim_checks = []
    for a in out.intervention_assessments:
        truth = effects[a.case_id]
        for fld in (*EFFECT_FIELDS, "disturbance_reaches_D8", "changes_any_D1_to_D7_trajectory"):
            claimed, actual = getattr(a, fld), truth[fld]
            claim_checks.append({"case_id": a.case_id, "claim": fld, "claimed": claimed, "deterministic": actual,
                                 "match": claimed == actual})
            if claimed != actual:
                cats["qualitative"].append(f"{a.case_id}.{fld}: claimed {claimed}, deterministic {actual}")
    for i, c in enumerate(out.comparative_claims):
        lv, rv = metric_value(cat, c.left_case, c.metric), metric_value(cat, c.right_case, c.metric)
        actual = "EQUAL_TO" if abs(lv - rv) <= TOL else ("LOWER_THAN" if lv < rv else "HIGHER_THAN")
        claim_checks.append({"claim": f"comparative_claims[{i}]", "claimed": f"{c.left_case} {c.relation} {c.right_case} "
                             f"on {c.metric}", "deterministic": actual, "match": actual == c.relation})
        if actual != c.relation:
            cats["qualitative"].append(f"comparative_claims[{i}]: {c.left_case} {c.relation} {c.right_case} on {c.metric}; "
                                       f"deterministic {actual}")
    prose = prose_d8_check(texts, effects)
    cats["qualitative"] += [f"prose contradicts D8 entering ({p['deterministic_D8_entering']}) in {p['field']}: "
                            f"{p['sentence']!r}" for p in prose]

    # objectives: preferred cases must attain the minimum; secondary options must be truthful
    alignment = {}
    for p in out.preferred_intervention_by_objective:
        low, pref = set(obj[p.objective]["lowest_cases"]), set(p.preferred_case_ids)
        beaten = sorted(pref - low)
        alignment[p.objective] = {"agent_preferred": sorted(pref), "lowest_metric_cases": sorted(low),
                                  "metric": obj[p.objective]["metric"],
                                  "agreement": "MATCH" if pref == low else ("SUBSET_OF_TIE" if pref and pref <= low
                                                                            else "DIFFERS")}
        if not pref:
            cats["objective"].append(f"{p.objective}: no preferred case")
        for c in beaten:
            cats["objective"].append(f"{p.objective}: prefers {c}, but {sorted(low)} attain(s) a strictly lower "
                                     f"{obj[p.objective]['metric']}")
    for i, s in enumerate(out.secondary_options):
        metric = OBJECTIVE_METRIC[s.objective]
        effect = classify_effect(metric_value(cat, "CASE_0", metric), metric_value(cat, s.case_id, metric))
        is_min = s.case_id in obj[s.objective]["lowest_cases"]
        if s.effect_vs_no_action != effect:
            cats["objective"].append(f"secondary_options[{i}] {s.case_id}: effect claimed {s.effect_vs_no_action}, "
                                     f"deterministic {effect}")
        if s.is_minimum_for_objective != is_min:
            cats["objective"].append(f"secondary_options[{i}] {s.case_id}: is_minimum_for_objective "
                                     f"{s.is_minimum_for_objective}, deterministic {is_min}")

    # authoritative structured selections (v3): must attain the deterministic minimum; ties allowed
    structured = {fld: set(getattr(out, fld)) for fld in STRUCTURED_PREFERENCES}
    minima = {fld: set(obj[o]["lowest_cases"]) for fld, o in STRUCTURED_PREFERENCES.items()}
    structured_checks = {}
    for fld, o in STRUCTURED_PREFERENCES.items():
        sel, low = structured[fld], minima[fld]
        structured_checks[fld] = {"selected": sorted(sel), "minimum": sorted(low), "metric": obj[o]["metric"],
                                  "agreement": "MATCH" if sel == low else ("SUBSET_OF_TIE" if sel and sel <= low
                                                                           else "DIFFERS")}
        if not sel:
            cats["objective"].append(f"{fld}: no case selected")
        for c in sorted(sel - low):
            cats["objective"].append(f"{fld}: selects {c}, but {sorted(low)} attain(s) a strictly lower {obj[o]['metric']}")

    # narrative (non-authoritative) must agree with the structured selections; raw text is never repaired
    for p in out.preferred_intervention_by_objective:
        fld = next(f for f, o in STRUCTURED_PREFERENCES.items() if o == p.objective)
        if set(p.preferred_case_ids) != structured[fld]:
            cats["narrative"].append(f"preferred_intervention_by_objective[{p.objective}] lists "
                                     f"{sorted(set(p.preferred_case_ids))}, but {fld} is {sorted(structured[fld])}")
    narrative = narrative_check(texts, structured, minima)
    cats["narrative"] += [f"free text contradicts {c['objective_field']} in {c['field']}: names {c['outside']} "
                          f"({c['clause']!r})" for c in narrative["contradictions"]]

    # coverage and the human-review field
    covered = {c for s in out.uncertainties for c in s.cited_ids}
    cats["coverage"] += [f"uncertainties do not cover {lim}" for lim in LIMITATIONS if lim not in covered]
    if not out.human_review_required:
        cats["human_review"].append("human_review_required must be true for the synthetic capstone scenario")
    if not out.human_review_reason.strip():
        cats["human_review"].append("human_review_reason is empty")

    errors = [e for v in cats.values() for e in v]
    reasons = ["synthetic capstone scenario: decision support only"]
    reasons += [f"{k} validation failed" for k in ("citation", "numeric", "qualitative", "objective", "narrative",
                                                    "coverage") if cats[k]]
    cited = sorted({c for _, cids in need_fact + other for c in cids if c in fact_ids})
    return {"result": "PASS" if not errors else "FAIL", "errors": errors,
            "errors_by_category": cats, "error_counts": {k: len(v) for k, v in cats.items()},
            "numeric_check": nums, "spelled_number_check": words, "prose_d8_check": prose, "claim_checks": claim_checks,
            "deterministic_effects": effects, "objective_alignment": alignment, "objective_facts": obj,
            "structured_preference_checks": structured_checks, "narrative_check": narrative,
            "authoritative_preferences": {fld: sorted(v) for fld, v in structured.items()},
            "cited_fact_values": {c: cat["facts"][c] for c in cited},
            "human_review": {"required": True, "reasons": reasons},
            "usable_downstream": not errors}


def legacy_findings(interpretation: dict, cat: dict) -> dict:
    """Re-check a pre-v2 interpretation (older schema, no structured claims) with the new text-level checks only:
    citations, spelled-out quantities and the D8 prose rule. Read-only; the old trace is not modified."""
    texts, cited = [], []
    for k in ("no_action_assessment", "overall_recommendation"):
        texts.append((k, interpretation[k]["statement"]))
        cited += interpretation[k]["cited_ids"]
    for a in interpretation["intervention_assessments"]:
        texts += [(f"{a['case_id']}.{k}", a[k]) for k in ("management_objective", "effect_on_trajectory",
                                                          "what_it_does_not_change")]
        cited += a["cited_ids"]
    for p in interpretation["preferred_intervention_by_objective"]:
        texts += [(f"{p['objective']}.rationale", p["rationale"]), (f"{p['objective']}.conditions", p["conditions_and_caveats"])]
        cited += p["cited_ids"]
    for name in ("management_tradeoffs", "key_assumptions", "uncertainties"):
        for i, s in enumerate(interpretation[name]):
            texts.append((f"{name}[{i}]", s["statement"]))
            cited += s["cited_ids"]
    obj = objective_facts(cat)
    beaten = [(p["objective"], c) for p in interpretation["preferred_intervention_by_objective"]
              for c in p["preferred_case_ids"] if c not in obj[p["objective"]]["lowest_cases"]]
    return {"unknown_citations": sorted(c for c in cited if c not in valid_ids(cat)),
            "unknown_citation_count": sum(c not in valid_ids(cat) for c in cited),
            "spelled_quantities": spelled_number_check(texts)["spelled_quantities"],
            "prose_d8_contradictions": prose_d8_check(texts, deterministic_effects(cat)),
            "objective_preferences_strictly_beaten": beaten}


# --- episode -------------------------------------------------------------------------------------------

def run_episode(client, project_root: Path, trace_dir: Path, eval_path: Path | None = None) -> dict:
    """One interpretation: one structured call (REAL_LLM_MODE) or the mock stand-in. Returns meta incl. trace paths.
    eval_path may contain "{stamp}", replaced by the trace timestamp."""
    start = time.time()
    cat = build_catalogue(project_root)
    snapshot = json.dumps(cat, sort_keys=True)
    mode = agent_mode(client)
    output, failure = None, None
    if client is None:
        output = mock_interpret(cat)
    else:
        try:
            output = client.complete(PROMPT, user_message(cat), PredictiveInterventionOutput)
        except LLMCallError as exc:  # recorded, not retried, nothing invented
            failure = str(exc)
    if json.dumps(cat, sort_keys=True) != snapshot:
        raise RuntimeError("deterministic inputs were modified during the episode")
    validation = validate_output(output, cat) if output else None
    status = FAILED if failure else (VALIDATED if validation["result"] == "PASS" else WITH_ERRORS)
    meta = {"agent": "Predictive Simulation and Intervention Agent (Module 5, Agent 2)",
            "contract_version": CONTRACT_VERSION, "agent_mode": mode, "model": getattr(client, "model", None),
            "status": status, "usable_downstream": status == VALIDATED, "human_review_required": True,
            # downstream may use only the structured selections, and only from a VALIDATED episode
            "authoritative_preferences": validation["authoritative_preferences"] if status == VALIDATED else None,
            "overall_recommendation_is_authoritative": False, "failure": failure,
            "llm": client.usage_summary() if hasattr(client, "usage_summary") else None,
            "elapsed_seconds": round(time.time() - start, 2), "timestamp": datetime.now().isoformat(timespec="seconds")}
    trace = {"meta": meta, "input_catalogue": cat, "interpretation": output.model_dump() if output else None,
             "validation": validation}
    trace_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = trace_dir / f"predictive_intervention_agent_{stamp}{'' if client else '_MOCK'}"
    json_path, md_path = base.with_suffix(".json"), base.with_suffix(".md")
    if json_path.exists():
        raise FileExistsError(f"refusing to overwrite an existing trace: {json_path}")
    json_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8", newline="\n")
    md_path.write_text(trace_markdown(trace), encoding="utf-8", newline="\n")
    meta.update({"trace_json": str(json_path), "trace_md": str(md_path)})
    if eval_path is not None:
        eval_path = Path(str(eval_path).format(stamp=stamp))
        eval_path.parent.mkdir(parents=True, exist_ok=True)
        eval_path.write_text(evaluation_markdown(trace, json_path, project_root), encoding="utf-8", newline="\n")
        meta["evaluation_summary"] = str(eval_path)
    return meta


# --- rendering -----------------------------------------------------------------------------------------

def _cite(ids: list[str], facts: dict) -> str:
    return ", ".join(f"`{i}` = {facts[i]:.4g}" if i in facts else f"`{i}`" for i in ids)


def trace_markdown(trace: dict) -> str:
    meta, cat, out, val = trace["meta"], trace["input_catalogue"], trace["interpretation"], trace["validation"]
    f = cat["facts"]
    banner = ("**MOCK_AGENT_MODE: rule-based stand-in, not LLM reasoning.**" if meta["agent_mode"] == MOCK_AGENT_MODE
              else f"REAL_LLM_MODE, model `{meta['model']}`")
    lines = [f"# Predictive Simulation and Intervention Agent: trace (validation contract v{meta.get('contract_version', 2)})",
             "", f"> {cat['statement']}",
             "", banner, "",
             f"- Status: **{meta['status']}**; usable downstream: **{meta['usable_downstream']}**; human review required: "
             f"**{meta['human_review_required']}**",
             f"- Elapsed {meta['elapsed_seconds']} s; {meta['timestamp']}",
             f"- Token usage: {meta['llm']}" if meta["llm"] else "- Token usage: n/a",
             f"- Initiating disturbance: {cat['common_initiating_disturbance']}", "",
             "## Deterministic facts supplied (Python-authoritative)", "", "| Fact id | Value |", "|---|---|"]
    lines += [f"| `{k}` | {v:.10g} |" for k, v in f.items()]
    if meta["failure"]:
        lines += ["", "## Model call failed", "", f"`{meta['failure']}`. No interpretation was produced or invented."]
        return "\n".join(lines) + "\n"
    lines += ["", "## Deterministic validation", "", f"- Result: **{val['result']}**; error counts: {val['error_counts']}"]
    lines += [f"- Error: {e}" for e in val["errors"]]
    lines += [f"- Human review reasons: {', '.join(val['human_review']['reasons'])}", "",
              "## Structured claims vs deterministic truth", "", "| Case | Claim | Agent | Python | Match |", "|---|---|---|---|---|"]
    lines += [f"| {c.get('case_id', '')} | {c['claim']} | {c['claimed']} | {c['deterministic']} | "
              f"{'yes' if c['match'] else '**NO**'} |" for c in val["claim_checks"]]
    lines += ["", "## Authoritative objective selections (structured) vs deterministic minimum", "",
              "| Field | Agent selects | Minimum (Python) | Agreement |", "|---|---|---|---|"]
    lines += [f"| {fld} | {', '.join(s['selected'])} | {', '.join(s['minimum'])} | {s['agreement']} |"
              for fld, s in val["structured_preference_checks"].items()]
    nc = val["narrative_check"]
    lines += ["", "## Narrative consistency (free text is explanatory only)", "",
              f"- Result: **{nc['result']}**; {len(nc['contradictions'])} contradiction(s), {len(nc['consistent'])} "
              f"consistent preference clause(s), {len(nc['unchecked'])} unchecked (hedged or several objectives)"]
    lines += [f"- Contradiction in {c['field']}: {c['clause']!r} names {c['outside']}; {c['objective_field']} is "
              f"{c['structured']}, minimum {c['minimum']}" for c in nc["contradictions"]]
    lines += [f"- Unchecked in {u['field']} ({u['reason']}): {u['clause']!r}" for u in nc["unchecked"]]
    lines += ["", "## Interpretation (raw model text; cited values attached by Python; not repaired)", "",
              f"**No action.** {out['no_action_assessment']['statement']}  ",
              f"Cites: {_cite(out['no_action_assessment']['cited_ids'], f)}", ""]
    for a in out["intervention_assessments"]:
        lines += [f"### {a['case_id']} / {a['intervention_id']}", "",
                  f"- **Objective addressed:** {a['management_objective']}",
                  f"- **Effect on trajectory:** {a['effect_on_trajectory']}",
                  f"- **Does not change:** {a['what_it_does_not_change']}",
                  f"- Cites: {_cite(a['cited_ids'], f)}", ""]
    lines += ["## Management trade-offs", ""]
    lines += [f"- {s['statement']} (cites {_cite(s['cited_ids'], f)})" for s in out["management_tradeoffs"]]
    lines += ["", "## Preferred intervention by objective (explanation)", "",
              "| Objective | Agent prefers | Minimum (Python) | Agreement | Rationale | Caveats |", "|---|---|---|---|---|---|"]
    for p in out["preferred_intervention_by_objective"]:
        al = val["objective_alignment"][p["objective"]]
        lines.append(f"| {p['objective']} | {', '.join(p['preferred_case_ids'])} | {', '.join(al['lowest_metric_cases'])} | "
                     f"{al['agreement']} | {p['rationale']} | {p['conditions_and_caveats']} |")
    lines += ["", "## Secondary options (useful under a narrower condition)", ""]
    lines += [f"- {s['case_id']} for {s['objective']}: {s['condition']} (effect vs NO ACTION {s['effect_vs_no_action']}; "
              f"minimum: {s['is_minimum_for_objective']}; cites {_cite(s['cited_ids'], f)})" for s in out["secondary_options"]]
    lines += ["", "## Overall recommendation (explanatory only; not an authoritative choice)", "",
              out["overall_recommendation"]["statement"],
              f"(cites {_cite(out['overall_recommendation']['cited_ids'], f)})", "",
              f"**Agent's human review flag:** {out['human_review_required']}. {out['human_review_reason']}", "",
              f"**Confidence / support:** {out['confidence_or_support_summary']}", "", "## Key assumptions", ""]
    lines += [f"- {s['statement']} (cites {', '.join(s['cited_ids'])})" for s in out["key_assumptions"]]
    lines += ["", "## Uncertainties", ""]
    lines += [f"- {s['statement']} (cites {', '.join(s['cited_ids'])})" for s in out["uncertainties"]]
    return "\n".join(lines) + "\n"


def evaluation_markdown(trace: dict, json_path: Path, project_root: Path) -> str:
    meta, out, val = trace["meta"], trace["interpretation"], trace["validation"]
    path = json_path.resolve()
    rel = path.relative_to(project_root.resolve()).as_posix() if path.is_relative_to(project_root.resolve()) \
        else path.as_posix()
    head = [f"# Predictive Simulation and Intervention Agent: episode summary (validation contract "
            f"v{meta.get('contract_version', 2)})", "",
            f"> {trace['input_catalogue']['statement']}", "",
            f"- Trace: `{rel}` (and `.md`)", f"- Mode: {meta['agent_mode']}; model: {meta['model']}; status: **{meta['status']}**;"
            f" usable downstream: **{meta['usable_downstream']}**",
            f"- Tokens: {meta['llm']}; elapsed {meta['elapsed_seconds']} s", "- One run; not repeated or tuned.", ""]
    if not out:
        return "\n".join(head + [f"Model call failed: `{meta['failure']}`. No interpretation produced."]) + "\n"
    rows = "\n".join(f"| {fld} | {', '.join(s['selected'])} | {', '.join(s['minimum'])} | {s['agreement']} |"
                     for fld, s in val["structured_preference_checks"].items())
    nc = val["narrative_check"]
    return "\n".join(head + [
        "## Validation", "", f"- Result: **{val['result']}**; error counts: {val['error_counts']}",
        *[f"- Error: {e}" for e in val["errors"]], f"- Human review reasons: {', '.join(val['human_review']['reasons'])}", "",
        "## Authoritative objective selections vs deterministic minimum", "",
        "| Field | Agent selects | Minimum | Agreement |", "|---|---|---|---|", rows, "",
        f"Authoritative for downstream use: {meta['authoritative_preferences'] or 'none (episode not VALIDATED)'}", "",
        f"## Narrative consistency: {nc['result']} ({len(nc['contradictions'])} contradiction(s), "
        f"{len(nc['unchecked'])} unchecked clause(s))", "",
        "## Overall recommendation (raw model text; explanatory only)", "", out["overall_recommendation"]["statement"], "",
        "See the trace for structured claim checks, citations with Python-attached values, and the full interpretation.",
    ]) + "\n"
