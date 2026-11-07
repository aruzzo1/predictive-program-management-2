"""Deterministic validation of the synthetic IMP / IMS files in data/synthetic/.

validate_dataset() returns a list of error strings (empty = valid). It works on the loaded, in-memory
dataset so tests can break one rule at a time. No network, no model calls.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from ppm_agent.synthetic.baseline import (
    DELAY_ABSORPTION_DAYS,
    DERIVED,
    EXPECTED_DSM_COUNT,
    EXPECTED_IMP_COUNT,
    EXPECTED_IMS_COUNT,
    FEEDBACK_REWORK,
    FILES,
    NODE_ASSIGNMENT_CHECKS,
    REWORK_FEEDBACKS,
    FINISH_ACTIVITY,
    FINISH_TO_START,
    NO_CASE,
    NOT_APPLICABLE,
    OBSERVED,
    POST_MATURITY_COMMITMENT_FRACTION,
    PRE_MATURITY_COMMITMENT_FRACTION,
    PROVENANCE_CLASSES,
    READINESS_GATE,
    READINESS_GATE_PREDECESSORS,
    RELATIONSHIP_TYPES,
    RESEQUENCING_POLICY,
    REWORK_FEEDBACK,
    REWORK_INDICATORS,
    REWORK_LOOP,
    RISK_STATES,
    SOFTWARE_PATH_END,
    SOURCE_CASES,
    STAGED_COMMITMENT_POLICY,
    START_ACTIVITY,
    STATEMENT,
    SUPPORT_LABELS,
    SYNTHETIC,
    TARGET_SOFTWARE_FLOAT,
    WORKSTREAMS,
    forward_pass,
    total_float,
)

IMS_REQUIRED = ("activity_id", "activity_name", "workstream", "imp_event", "baseline_duration_days", "predecessor_ids",
                "dsm_node", "data_classification", "evidence_basis", "source_case", "synthetic_assumption")
DEP_REQUIRED = ("source_activity", "target_activity", "relationship_type", "data_classification", "evidence_basis",
                "source_case", "confidence_or_support", "synthetic_implementation_note")
SCENARIO_IDS = ("BASELINE", "DISTURBANCE_1", "DISTURBANCE_2", "INTERVENTION_1", "INTERVENTION_2", "INTERVENTION_3")
# frozen magnitudes from the v1.0 specification: scenario -> (activity, delta)
FROZEN_DELTAS = {"DISTURBANCE_1": ("A210", 8), "DISTURBANCE_2": ("A305", 4), "INTERVENTION_1": ("A210", -4)}
# frozen scenario policies: scenario -> required fields of its single POLICY change
FROZEN_POLICIES = {
    "INTERVENTION_2": {"policy": RESEQUENCING_POLICY, "readiness_gate_activity": READINESS_GATE,
                       "applies_to_activity": "A410", "delay_absorption_days": DELAY_ABSORPTION_DAYS},
    "INTERVENTION_3": {"policy": STAGED_COMMITMENT_POLICY, "commitment_activity": "A505", "maturity_gate_activity": "A430",
                       "pre_maturity_commitment_fraction": PRE_MATURITY_COMMITMENT_FRACTION,
                       "post_maturity_commitment_fraction": POST_MATURITY_COMMITMENT_FRACTION},
}
# policies are simulator parameters; changes that edit the precedence network are not allowed
CHANGE_TYPES = ("DURATION_DELTA", "POLICY")


def _split(value: str) -> list[str]:
    return [v for v in (value or "").split(";") if v]


def _int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_dataset(directory: Path) -> dict:
    return {
        "imp": _read_csv(directory / FILES["imp"]),
        "ims": _read_csv(directory / FILES["ims"]),
        "dependencies": _read_csv(directory / FILES["dependencies"]),
        "scenarios": json.loads((directory / FILES["scenarios"]).read_text(encoding="utf-8")),
        "provenance": json.loads((directory / FILES["provenance"]).read_text(encoding="utf-8")),
    }


def _reachable(start: str, adjacency: dict[str, list[str]]) -> set[str]:
    seen, stack = {start}, [start]
    while stack:
        for nxt in adjacency.get(stack.pop(), []):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def validate_dataset(ds: dict) -> list[str]:
    errors: list[str] = []
    ims, imp, deps = ds["ims"], ds["imp"], ds["dependencies"]
    scenarios, prov = ds["scenarios"], ds["provenance"]
    dsm_nodes = prov.get("dsm_nodes", [])

    # counts and unique ids
    if len(ims) != EXPECTED_IMS_COUNT:
        errors.append(f"expected {EXPECTED_IMS_COUNT} IMS activities, found {len(ims)}")
    if len(imp) != EXPECTED_IMP_COUNT:
        errors.append(f"expected {EXPECTED_IMP_COUNT} IMP events, found {len(imp)}")
    if len(dsm_nodes) != EXPECTED_DSM_COUNT:
        errors.append(f"expected {EXPECTED_DSM_COUNT} DSM nodes, found {len(dsm_nodes)}")
    for label, ids in (("activity", [r.get("activity_id") for r in ims]), ("IMP event", [r.get("imp_event_id") for r in imp]),
                       ("DSM node", [n.get("node_id") for n in dsm_nodes]),
                       ("dependency", [d.get("dependency_id") for d in deps])):
        for dup, n in Counter(ids).items():
            if n > 1:
                errors.append(f"duplicate {label} id {dup!r} ({n} times)")

    activity_ids = {r["activity_id"] for r in ims}
    imp_ids = {r["imp_event_id"] for r in imp}
    dsm_ids = {n["node_id"] for n in dsm_nodes}
    by_id = {r["activity_id"]: r for r in ims}

    # IMS rows
    durations: dict[str, int] = {}
    for r in ims:
        aid = r.get("activity_id")
        for field in IMS_REQUIRED:
            if field not in r or (field != "predecessor_ids" and not str(r[field]).strip()):
                errors.append(f"{aid}: missing {field}")
        dur = _int(r.get("baseline_duration_days"))
        if dur is None or dur <= 0:
            errors.append(f"{aid}: baseline_duration_days must be a positive integer")
        else:
            durations[aid] = dur
        preds = _split(r.get("predecessor_ids", ""))
        if len(preds) != len(set(preds)):
            errors.append(f"{aid}: duplicate predecessor ids")
        for p in preds:
            if p == aid:
                errors.append(f"{aid}: lists itself as predecessor")
            elif p not in activity_ids:
                errors.append(f"{aid}: unknown predecessor {p!r}")
        if r.get("imp_event") not in imp_ids:
            errors.append(f"{aid}: unknown IMP event {r.get('imp_event')!r}")
        if r.get("dsm_node") not in dsm_ids:
            errors.append(f"{aid}: unknown DSM node {r.get('dsm_node')!r}")
        if r.get("workstream") not in WORKSTREAMS:
            errors.append(f"{aid}: unknown workstream {r.get('workstream')!r}")
        if r.get("data_classification") != SYNTHETIC:
            errors.append(f"{aid}: activity data_classification must be SYNTHETIC, got {r.get('data_classification')!r}")
        for case in _split(r.get("source_case", "")):
            if case not in SOURCE_CASES and case != NO_CASE:
                errors.append(f"{aid}: unknown source_case {case!r}")
        if r.get("risk_state") not in RISK_STATES:
            errors.append(f"{aid}: invalid risk_state {r.get('risk_state')!r}")
        if r.get("rework_indicator") not in REWORK_INDICATORS:
            errors.append(f"{aid}: invalid rework_indicator {r.get('rework_indicator')!r}")
        pct = _int(r.get("percent_complete"))
        if pct is None or not 0 <= pct <= 100:
            errors.append(f"{aid}: percent_complete must be 0-100")
    for label, used, known in (("IMP event", {r.get("imp_event") for r in ims}, imp_ids),
                               ("DSM node", {r.get("dsm_node") for r in ims}, dsm_ids),
                               ("workstream", {r.get("workstream") for r in ims}, set(WORKSTREAMS))):
        for unused in sorted(known - used):
            errors.append(f"{label} {unused!r} has no activities")

    # precedence network: FS edges must equal the IMS predecessor lists
    pred_edges = {(p, r["activity_id"]) for r in ims for p in _split(r.get("predecessor_ids", ""))}
    successors = defaultdict(list)
    for p, a in sorted(pred_edges):
        successors[p].append(a)
    for r in ims:
        if set(_split(r.get("successor_ids", ""))) != set(successors[r["activity_id"]]):
            errors.append(f"{r['activity_id']}: successor_ids inconsistent with predecessor lists")

    # orphans: single start, single finish, everything on a start -> finish path
    for r in ims:
        aid = r["activity_id"]
        if aid != START_ACTIVITY and not _split(r.get("predecessor_ids", "")):
            errors.append(f"{aid}: orphan (no predecessors and not the start activity)")
        if aid != FINISH_ACTIVITY and not successors[aid]:
            errors.append(f"{aid}: orphan (no successors and not the finish activity)")
    if START_ACTIVITY in activity_ids and FINISH_ACTIVITY in activity_ids:
        backwards = defaultdict(list)
        for p, a in pred_edges:
            backwards[a].append(p)
        on_path = _reachable(START_ACTIVITY, successors) & _reachable(FINISH_ACTIVITY, backwards)
        for aid in sorted(activity_ids - on_path):
            errors.append(f"{aid}: not on any {START_ACTIVITY} -> {FINISH_ACTIVITY} path")
    else:
        errors.append("start or finish activity missing")

    # dependency rows
    fs_edges, feedback = set(), []
    pair_counts = Counter((d.get("source_activity"), d.get("target_activity")) for d in deps)
    for (src, tgt), n in pair_counts.items():
        if n > 1:
            errors.append(f"duplicate dependency {src} -> {tgt} ({n} times)")
    for d in deps:
        did = d.get("dependency_id")
        for field in DEP_REQUIRED:
            if not str(d.get(field, "")).strip():
                errors.append(f"{did}: missing {field}")
        src, tgt, rel = d.get("source_activity"), d.get("target_activity"), d.get("relationship_type")
        if src not in activity_ids or tgt not in activity_ids:
            errors.append(f"{did}: unknown activity in {src} -> {tgt}")
            continue
        if rel not in RELATIONSHIP_TYPES:
            errors.append(f"{did}: invalid relationship_type {rel!r}")
        elif rel == FINISH_TO_START:
            fs_edges.add((src, tgt))
        else:
            feedback.append((src, tgt))
        if _int(d.get("lag_workdays")) is None:
            errors.append(f"{did}: lag_workdays must be an integer")
        for end, node_field in ((src, "source_dsm_node"), (tgt, "target_dsm_node")):
            if node_field in d and d[node_field] != by_id[end].get("dsm_node"):
                errors.append(f"{did}: {node_field} does not match {end}'s dsm_node")
        cls, case, support = d.get("data_classification"), d.get("source_case"), d.get("confidence_or_support")
        if cls not in PROVENANCE_CLASSES:
            errors.append(f"{did}: invalid data_classification {cls!r}")
        elif cls == OBSERVED:
            errors.append(f"{did}: a schedule dependency cannot be OBSERVED (the link is synthetic)")
        elif cls == DERIVED:
            if case not in SOURCE_CASES:
                errors.append(f"{did}: DERIVED dependency needs a source case in {SOURCE_CASES}, got {case!r}")
            if support not in SUPPORT_LABELS or support == NOT_APPLICABLE:
                errors.append(f"{did}: DERIVED dependency needs an evidence support label, got {support!r}")
        elif case != NO_CASE or support != NOT_APPLICABLE:
            errors.append(f"{did}: SYNTHETIC dependency must have source_case NONE and support NOT_APPLICABLE")
        if d.get("implementation_classification", SYNTHETIC) != SYNTHETIC:
            errors.append(f"{did}: implementation_classification must be SYNTHETIC")
    for src, tgt in sorted(pred_edges - fs_edges):
        errors.append(f"predecessor link {src} -> {tgt} missing from dependencies")
    for src, tgt in sorted(fs_edges - pred_edges):
        errors.append(f"dependency {src} -> {tgt} not reflected in predecessor_ids")

    # intentional rework feedback: exactly the approved feedback edges, never scheduling predecessors
    if sorted(feedback) != sorted(REWORK_FEEDBACKS):
        errors.append(f"expected exactly the {FEEDBACK_REWORK} dependencies {list(REWORK_FEEDBACKS)}, found {feedback}")
    if REWORK_FEEDBACK not in feedback:
        errors.append(f"flight-test rework feedback {REWORK_FEEDBACK} missing")
    for src, tgt in zip(REWORK_LOOP, REWORK_LOOP[1:]):
        if (src, tgt) not in fs_edges:
            errors.append(f"rework loop forward link {src} -> {tgt} missing")
    for edge in REWORK_FEEDBACKS:
        if edge in pred_edges or edge in fs_edges:
            errors.append(f"rework feedback {edge} must not be a scheduling predecessor")

    # v1.1 abstraction boundary: A430 stays in D7, A510 is in D8, so A430 -> A510 crosses D7 -> D8
    for aid, node in NODE_ASSIGNMENT_CHECKS.items():
        if aid in by_id and by_id[aid].get("dsm_node") != node:
            errors.append(f"{aid}: must map to DSM node {node}, got {by_id[aid].get('dsm_node')!r}")
    q08 = [d for d in deps if (d.get("source_activity"), d.get("target_activity")) == ("A430", "A510")]
    if len(q08) != 1 or (q08[0].get("source_dsm_node"), q08[0].get("target_dsm_node")) != ("D7", "D8"):
        errors.append("A430 -> A510 must be a single dependency mapping to D7 -> D8")
    for aid in REWORK_LOOP:
        if aid in by_id and by_id[aid].get("rework_indicator") != "LOOP":
            errors.append(f"{aid}: rework-loop member must have rework_indicator LOOP")

    # schedule: acyclic and consistent with a forward pass over the synthetic durations
    if len(durations) == len(ims) and not any("unknown predecessor" in e for e in errors):
        edges = [(p, a, 0) for p, a in sorted(pred_edges)]
        try:
            schedule = forward_pass(durations, edges)
        except ValueError as exc:
            errors.append(f"precedence network is not acyclic: {exc}")
        else:
            floats = total_float(durations, edges)
            for r in ims:
                start, finish = schedule[r["activity_id"]]
                if (_int(r.get("baseline_start")), _int(r.get("baseline_finish"))) != (start, finish):
                    errors.append(f"{r['activity_id']}: baseline start/finish differ from forward pass ({start}, {finish})")
                if _int(r.get("baseline_total_float")) != floats[r["activity_id"]]:
                    errors.append(f"{r['activity_id']}: baseline_total_float differs from backward pass "
                                  f"({floats[r['activity_id']]})")
                if (r.get("forecast_start"), r.get("forecast_finish")) != (r.get("baseline_start"), r.get("baseline_finish")):
                    errors.append(f"{r['activity_id']}: forecast must equal baseline in the baseline file")
            for e in imp:
                members = [r for r in ims if r.get("imp_event") == e["imp_event_id"]]
                if set(_split(e.get("activity_ids", ""))) != {r["activity_id"] for r in members}:
                    errors.append(f"{e['imp_event_id']}: activity_ids inconsistent with IMS")
                if members and _int(e.get("baseline_complete_workday")) != max(schedule[r["activity_id"]][1] for r in members):
                    errors.append(f"{e['imp_event_id']}: baseline_complete_workday inconsistent with IMS")
            # synthetic float calibration: software path near-critical, test-aircraft path controls the readiness gate
            if floats.get(SOFTWARE_PATH_END) != TARGET_SOFTWARE_FLOAT:
                errors.append(f"{SOFTWARE_PATH_END}: total float must be {TARGET_SOFTWARE_FLOAT} (synthetic calibration), "
                              f"got {floats.get(SOFTWARE_PATH_END)}")
            if floats.get("A325") != 0:
                errors.append(f"A325: expected to control {READINESS_GATE} at baseline (float 0), got {floats.get('A325')}")
            # the frozen v1.0 record must describe the files as they are
            freeze = prov.get("freeze", {})
            actual = {"imp_events": len(imp), "ims_activities": len(ims), "dsm_nodes": len(dsm_nodes),
                      "dependencies": len(deps), "scenarios": len(scenarios.get("scenarios", [])),
                      "A230_total_float": floats.get("A230"), "A325_total_float": floats.get("A325"),
                      "baseline_program_duration_workdays": max(f for _, f in schedule.values())}
            if freeze.get("status") != "FROZEN" or freeze.get("preserved") != actual:
                errors.append(f"freeze record does not match the dataset: recorded {freeze.get('preserved')}, actual {actual}")

    # readiness gate keeps its normal predecessors; baseline keeps development-production concurrency
    if READINESS_GATE in by_id and set(_split(by_id[READINESS_GATE].get("predecessor_ids", ""))) != set(READINESS_GATE_PREDECESSORS):
        errors.append(f"{READINESS_GATE}: readiness gate must keep predecessors {list(READINESS_GATE_PREDECESSORS)}")
    ancestors_of_a505 = _reachable("A505", {a: [p for p, b in pred_edges if b == a] for a in activity_ids})
    if "A430" in ancestors_of_a505:
        errors.append("A505 must not depend on A430 in the baseline (development-production concurrency is intentional)")

    for e in imp:
        if e.get("data_classification") != SYNTHETIC:
            errors.append(f"{e.get('imp_event_id')}: IMP event data_classification must be SYNTHETIC")

    errors += validate_scenarios(scenarios, durations)
    errors += validate_provenance(prov, deps)
    return errors


def validate_scenarios(doc: dict, durations: dict[str, int]) -> list[str]:
    errors: list[str] = []
    if doc.get("data_classification") != SYNTHETIC:
        errors.append("scenarios document must be SYNTHETIC")
    scenarios = doc.get("scenarios", [])
    by_id = {s.get("scenario_id"): s for s in scenarios}
    if sorted(by_id) != sorted(SCENARIO_IDS) or len(scenarios) != len(SCENARIO_IDS):
        errors.append(f"scenarios must be exactly {list(SCENARIO_IDS)}, found {[s.get('scenario_id') for s in scenarios]}")
    for s in scenarios:
        sid = s.get("scenario_id", "?")
        if s.get("data_classification") != SYNTHETIC:
            errors.append(f"{sid}: scenario must be SYNTHETIC")
        if s.get("outcome") != "NOT_COMPUTED":
            errors.append(f"{sid}: outcome must be NOT_COMPUTED until forward simulation exists")
        expected_type = sid.split("_")[0] if sid != "BASELINE" else "BASELINE"
        if s.get("scenario_type") != expected_type:
            errors.append(f"{sid}: scenario_type should be {expected_type}")
        if sid == "BASELINE":
            if s.get("base_scenario") is not None or s.get("changes"):
                errors.append("BASELINE must have no base_scenario and no changes")
            continue
        if s.get("base_scenario") not in by_id or s.get("base_scenario") == sid:
            errors.append(f"{sid}: invalid base_scenario {s.get('base_scenario')!r}")
            continue
        if not s.get("changes"):
            errors.append(f"{sid}: no changes")
        # apply the base chain to check effective durations and edges
        chain, cur = [], s
        while cur is not None and cur.get("scenario_id") not in [c.get("scenario_id") for c in chain]:
            chain.append(cur)
            cur = by_id.get(cur.get("base_scenario"))
        if cur is not None:
            errors.append(f"{sid}: base_scenario chain has a cycle")
            continue
        eff_dur = dict(durations)
        for step in reversed(chain):
            for c in step.get("changes", []):
                ctype = c.get("change_type")
                if c.get("data_classification") != SYNTHETIC:
                    errors.append(f"{sid}: change magnitudes must be SYNTHETIC")
                if ctype not in CHANGE_TYPES:
                    errors.append(f"{sid}: unknown change_type {ctype!r} (scenarios may not edit the precedence network)")
                elif ctype == "DURATION_DELTA":
                    aid, delta = c.get("activity_id"), _int(c.get("delta_workdays"))
                    if aid not in eff_dur or delta is None:
                        errors.append(f"{sid}: invalid DURATION_DELTA {c}")
                    else:
                        eff_dur[aid] += delta
                        if eff_dur[aid] <= 0:
                            errors.append(f"{sid}: {aid} duration becomes non-positive")
                elif step is s:
                    errors += _validate_policy(sid, c, set(durations))
        if sid in FROZEN_POLICIES:
            policies = [c for c in s.get("changes", []) if c.get("change_type") == "POLICY"]
            expected = FROZEN_POLICIES[sid]
            if len(policies) != 1 or any(policies[0].get(k) != v for k, v in expected.items()):
                errors.append(f"{sid}: expected the frozen policy {expected}, found {policies}")
        if sid in FROZEN_DELTAS:
            aid, delta = FROZEN_DELTAS[sid]
            got = [(c.get("activity_id"), _int(c.get("delta_workdays"))) for c in s.get("changes", [])
                   if c.get("change_type") == "DURATION_DELTA"]
            if got != [(aid, delta)]:
                errors.append(f"{sid}: expected the frozen change {aid} {delta:+d} workdays, found {got}")
    return errors


def _validate_policy(sid: str, c: dict, activity_ids: set[str]) -> list[str]:
    errors: list[str] = []
    policy = c.get("policy")
    if policy == RESEQUENCING_POLICY:
        for field in ("readiness_gate_activity", "applies_to_activity"):
            if c.get(field) not in activity_ids:
                errors.append(f"{sid}: {field} {c.get(field)!r} is not an activity")
        days = c.get("delay_absorption_days")
        if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
            errors.append(f"{sid}: delay_absorption_days must be a positive integer")
    elif policy == STAGED_COMMITMENT_POLICY:
        for field in ("commitment_activity", "maturity_gate_activity"):
            if c.get(field) not in activity_ids:
                errors.append(f"{sid}: {field} {c.get(field)!r} is not an activity")
        pre, post = c.get("pre_maturity_commitment_fraction"), c.get("post_maturity_commitment_fraction")
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and 0 <= x <= 1 for x in (pre, post)):
            errors.append(f"{sid}: commitment fractions must be numbers in [0, 1]")
        elif abs(pre + post - 1.0) > 1e-9:
            errors.append(f"{sid}: commitment fractions must sum to 1, got {pre} + {post}")
    else:
        errors.append(f"{sid}: unknown policy {policy!r}")
    if not str(c.get("intended_simulator_semantics", "")).strip():
        errors.append(f"{sid}: policy {policy!r} needs intended_simulator_semantics")
    return errors


def validate_provenance(prov: dict, deps: list[dict]) -> list[str]:
    errors: list[str] = []
    if prov.get("statement") != STATEMENT:
        errors.append("provenance statement missing or altered")
    if sorted(prov.get("provenance_classes", {})) != sorted(PROVENANCE_CLASSES):
        errors.append(f"provenance_classes must be exactly {list(PROVENANCE_CLASSES)}")
    if sorted(prov.get("source_cases", {})) != sorted(SOURCE_CASES):
        errors.append(f"source_cases must document exactly {list(SOURCE_CASES)}")
    for n in prov.get("dsm_nodes", []):
        if n.get("concept_classification") != DERIVED:
            errors.append(f"DSM node {n.get('node_id')}: concept_classification must be DERIVED")
    observed = prov.get("observed_evidence", [])
    if not observed:
        errors.append("observed_evidence register is empty")
    for o in observed:
        if o.get("data_classification") != OBSERVED:
            errors.append(f"{o.get('evidence_id')}: observed_evidence entries must be OBSERVED")
        if o.get("source_case") not in SOURCE_CASES:
            errors.append(f"{o.get('evidence_id')}: unknown source_case {o.get('source_case')!r}")
    observed_cases = {o.get("source_case") for o in observed}
    for d in deps:
        if d.get("data_classification") == DERIVED and d.get("source_case") not in observed_cases:
            errors.append(f"{d.get('dependency_id')}: DERIVED from {d.get('source_case')} with no observed evidence recorded")
    return errors
