"""Deterministic node-level DSM built from the frozen synthetic dependency registry (data/synthetic/).

No model calls: every entry is computed in Python from the approved dependencies, and every nonzero
entry lists the dependencies behind it.

Orientation (used everywhere): row = source / upstream node, column = target / downstream node.
dsm[i][j] != 0 means node i feeds node j (some activity in i must finish before an activity in j).

Binary DSM: 1 if at least one approved dependency with non-zero weight maps to the cell.
Weighted DSM: the maximum weight of the dependencies mapped to the cell (illustrative, not a probability).
Diagonal: 0, except where the cell is produced by an approved FEEDBACK_REWORK dependency (the rework loop).
Intra-node precedence links are not shown in the matrix; they are kept in the dependency registry.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path

from ppm_agent.synthetic.baseline import FEEDBACK_REWORK, FILES, STATEMENT

DSM_VERSION = "1.1"  # built from Synthetic Baseline v1.1
ORIENTATION = ("row = source / upstream node, column = target / downstream node; entry (i, j) != 0 means node i feeds "
               "node j")

# illustrative weight tiers (not calibrated probabilities)
STRONG, MODERATE, UNRESOLVED_RETAINED, SYNTHETIC_SEQUENCING, EXCLUDED = (
    "STRONG", "MODERATE", "UNRESOLVED_RETAINED", "SYNTHETIC_SEQUENCING", "EXCLUDED")
WEIGHT_POLICY = {
    STRONG: (1.00, "Evidence-derived and SUPPORTED by an agentic decision."),
    MODERATE: (0.75, "Evidence-derived and PARTIALLY_SUPPORTED by an agentic decision, or (no agentic decision) "
                     "stated directly by a recorded passage (EXPLICIT_PASSAGE)."),
    UNRESOLVED_RETAINED: (0.50, "Evidence-derived but UNRESOLVED by an agentic decision, or (no agentic decision) "
                                "assembled only from fragments (FRAGMENTARY). Retained in the experimental model."),
    SYNTHETIC_SEQUENCING: (0.25, "Purely synthetic sequencing dependency (data_classification SYNTHETIC)."),
    EXCLUDED: (0.00, "Evidence-derived but NOT_SUPPORTED by an agentic decision. Kept in the registry, not in the matrix."),
}
DECISION_TIER = {"SUPPORTED": STRONG, "PARTIALLY_SUPPORTED": MODERATE, "UNRESOLVED": UNRESOLVED_RETAINED,
                 "NOT_SUPPORTED": EXCLUDED}
SUPPORT_TIER = {"EXPLICIT_PASSAGE": MODERATE, "FRAGMENTARY": UNRESOLVED_RETAINED}

# Agentic Phase 1 decisions (REAL_LLM_MODE, single runs) and the synthetic dependency that implements each tested pair.
# Where one exists it takes precedence over the passage support label.
AGENTIC_DECISIONS = {
    ("A230", "A405"): {"source_case": "Q01", "mvp_pair": "A1 -> A2", "decision": "PARTIALLY_SUPPORTED",
                       "trace": "outputs/agentic_traces/episode_20261030_140841_A1_A2.json"},
    ("A325", "A405"): {"source_case": "Q04", "mvp_pair": "A3 -> A4", "decision": "UNRESOLVED",
                       "trace": "outputs/agentic_traces/episode_20261030_141449_Q04_REAL_LLM_MODE_A3_A4.json"},
    ("A430", "A510"): {"source_case": "Q08", "mvp_pair": "A5 -> A6", "decision": "UNRESOLVED",
                       "trace": "outputs/agentic_traces/episode_20261030_141531_Q08_REAL_LLM_MODE_A5_A6.json"},
}

INTER_NODE, INTRA_NODE, FEEDBACK = "INTER_NODE", "INTRA_NODE", "FEEDBACK"
EXPECTED_NODE_COUNT = 8
OUTPUT_FILES = ("activity_registry.json", "dependency_registry.json", "binary_dsm.csv", "weighted_dsm.csv",
                "dsm_provenance.json", "dsm_summary.md")


def cell_key(row: str, col: str) -> str:
    return f"{row}->{col}"


# --- registries ---------------------------------------------------------------------------------------

def load_node_registry(ds: dict) -> list[dict]:
    """The DSM nodes, in provenance-file order (D1..D8), with their member activities."""
    members = defaultdict(list)
    for a in ds["ims"]:
        members[a["dsm_node"]].append(a["activity_id"])
    return [{"node_id": n["node_id"], "name": n["name"], "concept_classification": n["concept_classification"],
             "source_cases": n["source_cases"], "activity_ids": members[n["node_id"]]}
            for n in ds["provenance"]["dsm_nodes"]]


def activity_registry(ds: dict) -> list[dict]:
    keep = ("activity_id", "activity_name", "workstream", "imp_event", "dsm_node", "rework_indicator", "source_case",
            "data_classification")
    return [{k: a[k] for k in keep} for a in ds["ims"]]


def classify_dependency(dep: dict) -> tuple[str, dict | None, str]:
    """(weight tier, agentic decision or None, human-readable basis) for one approved dependency."""
    agentic = AGENTIC_DECISIONS.get((dep["source_activity"], dep["target_activity"]))
    if agentic:
        tier = DECISION_TIER[agentic["decision"]]
        return tier, agentic, (f"Agentic Phase 1 decision {agentic['decision']} for {agentic['source_case']} "
                               f"({agentic['mvp_pair']}); takes precedence over support label "
                               f"{dep['confidence_or_support']}.")
    if dep["data_classification"] == "DERIVED":
        tier = SUPPORT_TIER[dep["confidence_or_support"]]
        return tier, None, f"DERIVED ({dep['source_case']}), no agentic decision; support label {dep['confidence_or_support']}."
    return SYNTHETIC_SEQUENCING, None, "SYNTHETIC sequencing; no evidence claimed."


def dependency_registry(ds: dict) -> list[dict]:
    """Every approved dependency with its node mapping, scope, weight and the matrix cell it feeds (if any)."""
    rows = []
    for d in ds["dependencies"]:
        src_node, tgt_node = d["source_dsm_node"], d["target_dsm_node"]
        if d["relationship_type"] == FEEDBACK_REWORK:
            scope = FEEDBACK
        else:
            scope = INTRA_NODE if src_node == tgt_node else INTER_NODE
        tier, agentic, basis = classify_dependency(d)
        weight = WEIGHT_POLICY[tier][0]
        in_matrix = scope in (INTER_NODE, FEEDBACK) and weight > 0
        rows.append({
            "dependency_id": d["dependency_id"], "source_activity": d["source_activity"],
            "target_activity": d["target_activity"], "relationship_type": d["relationship_type"],
            "source_node": src_node, "target_node": tgt_node, "scope": scope,
            "data_classification": d["data_classification"], "source_case": d["source_case"],
            "confidence_or_support": d["confidence_or_support"],
            "agentic_decision": agentic["decision"] if agentic else None,
            "agentic_trace": agentic["trace"] if agentic else None,
            "weight_tier": tier, "weight": weight, "weight_basis": basis,
            "included_in_matrix": in_matrix, "matrix_cell": cell_key(src_node, tgt_node) if in_matrix else None,
        })
    return rows


# --- matrices -----------------------------------------------------------------------------------------

def aggregate(registry: list[dict]) -> dict[str, list[dict]]:
    """Matrix cell -> the dependencies mapped to it."""
    cells = defaultdict(list)
    for d in registry:
        if d["included_in_matrix"]:
            cells[d["matrix_cell"]].append(d)
    return dict(cells)


def coupled_blocks(nodes: list[str], binary: list[list[int]]) -> list[list[str]]:
    """Strongly connected components of the binary DSM with more than one node or a self-loop (Tarjan)."""
    index, low, on_stack, stack, comps, counter = {}, {}, set(), [], [], [0]

    def visit(i: int) -> None:
        index[i] = low[i] = counter[0]
        counter[0] += 1
        stack.append(i)
        on_stack.add(i)
        for j in range(len(nodes)):
            if not binary[i][j]:
                continue
            if j not in index:
                visit(j)
                low[i] = min(low[i], low[j])
            elif j in on_stack:
                low[i] = min(low[i], index[j])
        if low[i] == index[i]:
            comp = []
            while True:
                j = stack.pop()
                on_stack.discard(j)
                comp.append(j)
                if j == i:
                    break
            if len(comp) > 1 or binary[i][i]:
                comps.append(sorted(comp))

    for i in range(len(nodes)):
        if i not in index:
            visit(i)
    return sorted([[nodes[i] for i in c] for c in comps])


def build_dsm(ds: dict) -> dict:
    nodes = load_node_registry(ds)
    ids = [n["node_id"] for n in nodes]
    registry = dependency_registry(ds)
    cells = aggregate(registry)
    binary = [[0] * len(ids) for _ in ids]
    weighted = [[0.0] * len(ids) for _ in ids]
    cell_records = []
    for i, r in enumerate(ids):
        for j, c in enumerate(ids):
            deps = cells.get(cell_key(r, c), [])
            if not deps:
                continue
            binary[i][j] = 1
            weighted[i][j] = max(d["weight"] for d in deps)
            cell_records.append({
                "cell": cell_key(r, c), "row": r, "column": c, "binary": 1, "weight": weighted[i][j],
                "aggregation": "max", "entry_type": FEEDBACK if all(d["scope"] == FEEDBACK for d in deps) else "FORWARD",
                "contributing_dependencies": [{k: d[k] for k in ("dependency_id", "source_activity", "target_activity",
                                                                 "relationship_type", "source_case", "weight_tier", "weight")}
                                              for d in deps],
            })
    return {"nodes": nodes, "node_ids": ids, "registry": registry, "binary": binary, "weighted": weighted,
            "cells": cell_records, "coupled_blocks": coupled_blocks(ids, binary),
            "activities": activity_registry(ds)}


# --- validation ---------------------------------------------------------------------------------------

def validate_dsm(dsm: dict) -> list[str]:
    errors: list[str] = []
    ids, binary, weighted = dsm["node_ids"], dsm["binary"], dsm["weighted"]
    n = len(ids)
    if n != EXPECTED_NODE_COUNT or len(set(ids)) != n:
        errors.append(f"expected {EXPECTED_NODE_COUNT} unique DSM nodes, found {ids}")
    for name, m in (("binary", binary), ("weighted", weighted)):
        if len(m) != n or any(len(row) != n for row in m):
            errors.append(f"{name} DSM is not {n}x{n}")
            return errors
    valid_weights = {w for w, _ in WEIGHT_POLICY.values()}
    by_cell = {c["cell"]: c for c in dsm["cells"]}
    registry = {d["dependency_id"]: d for d in dsm["registry"]}
    for i, r in enumerate(ids):
        for j, c in enumerate(ids):
            b, w, key = binary[i][j], weighted[i][j], cell_key(r, c)
            if b not in (0, 1) or isinstance(b, bool):
                errors.append(f"{key}: binary value {b!r} is not 0/1")
            if not isinstance(w, float) or not 0.0 <= w <= 1.0:
                errors.append(f"{key}: weight {w!r} outside 0.0-1.0")
            elif w not in valid_weights:
                errors.append(f"{key}: weight {w} is not a policy value")
            if (b == 1) != (w > 0):
                errors.append(f"{key}: binary and weighted DSM disagree ({b}, {w})")
            cell = by_cell.get(key)
            if b and not cell:
                errors.append(f"{key}: nonzero entry has no provenance")
                continue
            if not b:
                if cell:
                    errors.append(f"{key}: provenance recorded for a zero entry")
                continue
            deps = cell["contributing_dependencies"]
            if not deps:
                errors.append(f"{key}: nonzero entry has no contributing dependency")
            for d in deps:
                reg = registry.get(d["dependency_id"])
                if reg is None:
                    errors.append(f"{key}: unknown dependency {d['dependency_id']}")
                elif (reg["source_node"], reg["target_node"]) != (r, c) or not reg["included_in_matrix"]:
                    errors.append(f"{key}: {d['dependency_id']} does not map to this cell")
            if deps and w != max(d["weight"] for d in deps):
                errors.append(f"{key}: weight is not the max of its contributing dependencies")
            if i == j and cell.get("entry_type") != FEEDBACK:
                errors.append(f"{key}: diagonal entry allowed only for FEEDBACK_REWORK dependencies")
    # no unexplained entries: every included dependency appears in its cell, and nothing else does
    for d in dsm["registry"]:
        expected_in = d["scope"] in (INTER_NODE, FEEDBACK) and d["weight"] > 0
        if d["included_in_matrix"] != expected_in:
            errors.append(f"{d['dependency_id']}: included_in_matrix inconsistent with scope / weight")
        if d["weight"] != WEIGHT_POLICY[d["weight_tier"]][0]:
            errors.append(f"{d['dependency_id']}: weight does not match tier {d['weight_tier']}")
        if expected_in:
            listed = {x["dependency_id"] for x in by_cell.get(d["matrix_cell"], {}).get("contributing_dependencies", [])}
            if d["dependency_id"] not in listed:
                errors.append(f"{d['dependency_id']}: missing from cell {d['matrix_cell']} provenance")
    # the rework feedback must survive aggregation
    feedback = [d for d in dsm["registry"] if d["scope"] == FEEDBACK]
    if not feedback:
        errors.append("no FEEDBACK_REWORK dependency in the registry")
    for d in feedback:
        i, j = ids.index(d["source_node"]), ids.index(d["target_node"])
        if binary[i][j] != 1:
            errors.append(f"feedback {d['dependency_id']} ({d['matrix_cell']}) is not present in the DSM")
    if not dsm["coupled_blocks"]:
        errors.append("DSM has no coupled (iterative) block")
    return errors


def validate_structure(dsm: dict) -> list[str]:
    """Approved v1.1 structural expectations (kept apart from the generic matrix rules in validate_dsm)."""
    errors: list[str] = []
    by_cell = {c["cell"]: c for c in dsm["cells"]}
    reg = {(d["source_activity"], d["target_activity"]): d for d in dsm["registry"]}
    nodes = {a["activity_id"]: a["dsm_node"] for a in dsm["activities"]}
    if len(dsm["activities"]) != 35:
        errors.append(f"expected 35 activities, found {len(dsm['activities'])}")
    if (nodes.get("A430"), nodes.get("A510")) != ("D7", "D8"):
        errors.append(f"A430 / A510 must map to D7 / D8, got {nodes.get('A430')} / {nodes.get('A510')}")
    d64 = by_cell.get("D6->D4")
    if not d64 or d64["entry_type"] != FEEDBACK or any(d["relationship_type"] != FEEDBACK_REWORK
                                                       for d in d64["contributing_dependencies"]):
        errors.append("D6->D4 must exist and be produced only by FEEDBACK_REWORK dependencies")
    d46 = by_cell.get("D4->D6")
    if not d46 or d46["entry_type"] != "FORWARD":
        errors.append("D4->D6 must exist as a forward dependency")
    d78 = by_cell.get("D7->D8")
    if not d78 or "A430" not in {d["source_activity"] for d in d78["contributing_dependencies"]
                                 if d["target_activity"] == "A510"}:
        errors.append("D7->D8 must carry A430 -> A510")
    q04 = reg.get(("A325", "A405"))
    if not q04 or q04["agentic_decision"] != "UNRESOLVED" or q04["weight"] != 0.50:
        errors.append("Q04 (A325 -> A405) must stay UNRESOLVED at weight 0.50")
    if not any({"D4", "D6"} <= set(b) for b in dsm["coupled_blocks"]):
        errors.append("D4 and D6 must form a coupled block (D4 -> D6 -> D4)")
    return errors


# --- outputs ------------------------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_csv(ids: list[str], matrix: list[list], fmt) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["source\\target", *ids])
    for r, row in zip(ids, matrix):
        writer.writerow([r, *(fmt(v) for v in row)])
    return buf.getvalue()


def _json(doc) -> str:
    return json.dumps(doc, indent=2) + "\n"


def provenance_document(dsm: dict, synthetic_dir: Path) -> dict:
    counts = defaultdict(int)
    for d in dsm["registry"]:
        counts[d["scope"]] += 1
    return {
        "statement": ("Illustrative capstone DSM derived from the Evidence-Calibrated Synthetic F-35 Development Baseline "
                      "v1.1. It is not a historical F-35 DSM. " + STATEMENT),
        "dsm_version": DSM_VERSION,
        "computed_by": "ppm_agent.tools.dsm_tools (deterministic Python; no LLM involvement)",
        "inputs": {f"data/synthetic/{name}": _sha256(synthetic_dir / name) for name in FILES.values()},
        "orientation": ORIENTATION,
        "diagonal_policy": "0, except where the cell is produced only by an approved FEEDBACK_REWORK dependency.",
        "intra_node_policy": "Intra-node precedence links are not shown in the matrix; they stay in dependency_registry.json.",
        "aggregation": "Binary: 1 if any included dependency maps to the cell. Weighted: max weight of those dependencies.",
        "weight_policy": {tier: {"weight": w, "rule": rule} for tier, (w, rule) in WEIGHT_POLICY.items()},
        "weight_precedence": ("Agentic decision if one exists for the dependency, else the passage support label for "
                              "DERIVED dependencies, else SYNTHETIC_SEQUENCING."),
        "weights_are_not_probabilities": True,
        "agentic_decisions_used": [{"source_activity": s, "target_activity": t, **v}
                                   for (s, t), v in AGENTIC_DECISIONS.items()],
        "dependency_scope_counts": dict(sorted(counts.items())),
        "nonzero_entries": len(dsm["cells"]),
        "coupled_blocks": dsm["coupled_blocks"],
        "cells": dsm["cells"],
        "not_built": ["WTM", "propagation simulation", "intervention simulation"],
    }


def _md_matrix(ids: list[str], matrix: list[list], fmt) -> str:
    lines = ["| source \\ target | " + " | ".join(ids) + " |", "|---|" + "---|" * len(ids)]
    for r, row in zip(ids, matrix):
        lines.append(f"| **{r}** | " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(lines)


def summary_markdown(dsm: dict, prov: dict) -> str:
    ids = dsm["node_ids"]
    node_rows = "\n".join(f"| {n['node_id']} | {n['name']} | {', '.join(n['activity_ids'])} |" for n in dsm["nodes"])
    policy_rows = "\n".join(f"| {tier} | {w:.2f} | {rule} |" for tier, (w, rule) in WEIGHT_POLICY.items())
    cell_rows = "\n".join(
        f"| {c['cell']} | {c['entry_type']} | {c['weight']:.2f} | "
        + "; ".join(f"{d['dependency_id']} {d['source_activity']}->{d['target_activity']} ({d['weight_tier']}, {d['weight']:.2f})"
                    for d in c["contributing_dependencies"]) + " |"
        for c in dsm["cells"])
    counts = prov["dependency_scope_counts"]
    unresolved = [d for d in dsm["registry"] if d["agentic_decision"] == "UNRESOLVED"]
    unresolved_text = "\n".join(
        f"- {d['dependency_id']} {d['source_activity']} -> {d['target_activity']} ({d['source_case']}): weight "
        f"{d['weight']:.2f}, " + (f"shown in cell {d['matrix_cell']}." if d["included_in_matrix"]
                                  else f"intra-node ({d['source_node']}), so it is kept in the registry, not shown in the matrix.")
        for d in unresolved)
    blocks = "; ".join("{" + ", ".join(b) + "}" for b in dsm["coupled_blocks"])
    return f"""# Node-level DSM (illustrative capstone model)

> {prov['statement']}

Generated by `scripts/build_dsm.py` from the frozen synthetic baseline. Do not edit by hand.

## Nodes

| Node | Name | Activities |
|---|---|---|
{node_rows}

## Orientation

**Row = source / upstream node; column = target / downstream node.** A nonzero entry (i, j) means node i feeds node j: some
activity in i must finish before an activity in j. This convention is used in every file in this folder.

## Binary DSM

1 means at least one approved dependency with non-zero weight maps to the cell. It has {len(dsm['cells'])} nonzero
entries.

{_md_matrix(ids, dsm['binary'], str)}

## Weighted DSM (illustrative)

Each cell takes the **maximum** weight of its contributing dependencies. The weights are **ordinal evidence tiers, not
calibrated probabilities**.

{_md_matrix(ids, dsm['weighted'], lambda v: f"{v:.2f}" if v else "0")}

## Weighting policy

| Tier | Weight | Rule |
|---|---|---|
{policy_rows}

Precedence: {prov['weight_precedence']} The agentic decisions used come from single REAL_LLM_MODE runs:
Q01 PARTIALLY_SUPPORTED, Q04 UNRESOLVED and Q08 UNRESOLVED.

## Uncertainty treatment

UNRESOLVED does not mean there is no relationship. An UNRESOLVED dependency is retained at 0.50 rather than dropped, and
the binary DSM marks it present, because it is intentionally part of the experimental model. The weighted DSM is where
the lower confidence shows. Only an agentic NOT_SUPPORTED decision would give 0.00 (EXCLUDED); none exists.

{unresolved_text}

## Feedback and coupling

There are two approved FEEDBACK_REWORK dependencies. Neither is a scheduling predecessor, so the baseline IMS stays
acyclic; the loops exist only in the dependency registry and the DSM.

- **Software rework feedback (v1.1): A415 -> A225, cell D6->D4.** Deficiencies found in flight test feed corrective
  software / integration work. The concept is DERIVED (Q01); the exact activity pair is SYNTHETIC. Together with the
  forward software-maturity link A230 -> A405 (D4->D6), it forms the coupled loop **D4 -> D6 -> D4**.
- **Flight-test rework feedback: A425 -> A410, cell D6->D6.** Regression results lead to further flight test inside
  Flight-Test Execution. It is the only allowed exception to the zero diagonal.
- **Coupled blocks** (strongly connected components of the binary DSM): {blocks}. {{D4, D6}} is the software /
  flight-test loop, and it contains the D6 self-loop. {{D2, D3}} (design <-> weight) arises from aggregating approved
  forward links; the activity network itself has no cycle.

## Traceability

Every nonzero cell lists its contributing dependencies. Full records are in `dsm_provenance.json` and
`dependency_registry.json`, which also contains the {counts.get(INTRA_NODE, 0)} intra-node links that are not shown.
Dependency scopes: {counts.get(INTER_NODE, 0)} inter-node, {counts.get(INTRA_NODE, 0)} intra-node,
{counts.get(FEEDBACK, 0)} feedback.

| Cell | Type | Weight | Contributing dependencies |
|---|---|---|---|
{cell_rows}

## Limitations

- This is an illustrative capstone model built on a synthetic schedule, not a historical F-35 DSM.
- The weights are ordinal tiers. Max-aggregation hides how many links support a cell.
- **Q04 shows conservative agentic evaluation and preserved uncertainty.** Its passages state the dependency explicitly,
  but the agentic decision was UNRESOLVED (best 69.5, threshold 70, single run). Because the agentic decision governs the
  weight, D5->D6 stays at 0.50. That is below untested EXPLICIT_PASSAGE concepts such as Q07 D3->D8 (0.75). The
  dependency is kept, not dropped.
- D6->D4 rests on fragmentary evidence (0.50), and its activity pair (A415 -> A225) is synthetic.
- Not built: WTM, propagation simulation, intervention simulation.

## Version

Built from Synthetic Baseline v1.1. That is a minor structural revision of v1.0: it adds the cross-node feedback A415 ->
A225 and moves A510 from D7 to D8. No schedule calibration changed. The v1.0 DSM outputs are archived unchanged in
`outputs/dsm/archive/v1.0/`.
"""


def render_outputs(dsm: dict, synthetic_dir: Path) -> dict[str, str]:
    """File name -> exact file text. Deterministic for a given synthetic baseline."""
    prov = provenance_document(dsm, synthetic_dir)
    return {
        "activity_registry.json": _json({"nodes": dsm["nodes"], "activities": dsm["activities"]}),
        "dependency_registry.json": _json({"orientation": ORIENTATION, "dependencies": dsm["registry"]}),
        "binary_dsm.csv": _matrix_csv(dsm["node_ids"], dsm["binary"], str),
        "weighted_dsm.csv": _matrix_csv(dsm["node_ids"], dsm["weighted"], lambda v: f"{v:.2f}"),
        "dsm_provenance.json": _json(prov),
        "dsm_summary.md": summary_markdown(dsm, prov),
    }


def write_outputs(texts: dict[str, str], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, text in texts.items():
        path = out_dir / name
        path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def read_matrix_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0][1:], [r[1:] for r in rows[1:]]
