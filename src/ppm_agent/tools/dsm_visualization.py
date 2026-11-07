"""Read-only DSM visualization and explanation package (outputs/dsm_visualization/).

Everything is generated from the frozen DSM outputs in outputs/dsm/ (binary_dsm.csv, weighted_dsm.csv,
dsm_provenance.json, activity_registry.json, dependency_registry.json). Nothing here recomputes or changes
DSM entries, weights or dependencies. Figures are plain SVG written with the standard library (no plotting
package is installed); PNG copies can be rasterized from the SVGs by a headless browser.

Not computed here (next stage): eigenvalues, spectral radius, propagation iterations, scenario simulation.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from html import escape
from pathlib import Path

from ppm_agent.tools.dsm_tools import read_matrix_csv

NODE_LABELS = {
    "D1": "Requirements / KPP Definition",
    "D2": "Air Vehicle Design Maturity",
    "D3": "Weight / Structural Maturity",
    "D4": "Mission-System Software Maturity",
    "D5": "Test-Aircraft Availability",
    "D6": "Flight-Test Execution",
    "D7": "Development / Test Maturity",
    "D8": "Production Commitment / Rework Exposure",
}
TIER_MEANING = {
    0.00: "absent / excluded",
    0.25: "purely synthetic sequencing",
    0.50: "unresolved or fragment-supported relationship",
    0.75: "partially supported or directly stated relationship",
    1.00: "supported relationship",
}
INPUT_FILES = ("binary_dsm.csv", "weighted_dsm.csv", "dsm_provenance.json", "activity_registry.json",
               "dependency_registry.json")
SVG_FILES = ("binary_dsm_heatmap.svg", "weighted_dsm_heatmap.svg", "dsm_dependency_network.svg")

# reference palette (dataviz skill): blue ordinal ramp from step 250 (>= 2:1 on the light surface), neutral zero
SURFACE, INK, INK_2, MUTED, ZERO = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#f0efec"
TIER_FILL = {0.25: "#86b6ef", 0.50: "#3987e5", 0.75: "#1c5cab", 1.00: "#0d366b"}
BINARY_FILL = "#256abf"
FONT = "Segoe UI, Helvetica, Arial, sans-serif"
HALO = f'stroke="{SURFACE}" stroke-width="4" paint-order="stroke"'  # keeps labels legible where arrows cross


# --- loading ------------------------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_dsm(dsm_dir: Path) -> dict:
    ids, b_rows = read_matrix_csv(dsm_dir / "binary_dsm.csv")
    w_ids, w_rows = read_matrix_csv(dsm_dir / "weighted_dsm.csv")
    if ids != w_ids:
        raise ValueError("binary and weighted DSM node orders differ")
    prov = json.loads((dsm_dir / "dsm_provenance.json").read_text(encoding="utf-8"))
    acts = json.loads((dsm_dir / "activity_registry.json").read_text(encoding="utf-8"))
    deps = json.loads((dsm_dir / "dependency_registry.json").read_text(encoding="utf-8"))
    return {
        "ids": ids,
        "binary": [[int(v) for v in r] for r in b_rows],
        "weighted": [[float(v) for v in r] for r in w_rows],
        "cells": {c["cell"]: c for c in prov["cells"]},
        "coupled_blocks": prov["coupled_blocks"],
        "provenance": prov,
        "nodes": acts["nodes"],
        "dependencies": deps["dependencies"],
        "input_sha256": {f"outputs/dsm/{n}": sha256(dsm_dir / n) for n in INPUT_FILES},
    }


# --- derived views (read-only) ------------------------------------------------------------------------

def degrees(m: dict) -> dict[str, tuple[int, int]]:
    """(out-degree = row sum, in-degree = column sum) of the binary DSM, excluding the diagonal."""
    ids, b = m["ids"], m["binary"]
    return {r: (sum(b[i][j] for j in range(len(ids)) if j != i), sum(b[j][i] for j in range(len(ids)) if j != i))
            for i, r in enumerate(ids)}


def sinks_and_sources(m: dict) -> tuple[list[str], list[str]]:
    deg = degrees(m)
    return [n for n, (o, i) in deg.items() if o == 0 and i > 0], [n for n, (o, i) in deg.items() if i == 0 and o > 0]


def partitioned_order(m: dict) -> list[list[str]]:
    """Coupled blocks kept together, blocks in upstream-to-downstream order (topological sort of the condensation)."""
    ids, b = m["ids"], m["binary"]
    group = {n: n for n in ids}
    for block in m["coupled_blocks"]:
        for n in block:
            group[n] = block[0]
    members: dict[str, list[str]] = {}
    for n in ids:
        members.setdefault(group[n], []).append(n)
    edges = {(group[ids[i]], group[ids[j]]) for i in range(len(ids)) for j in range(len(ids))
             if b[i][j] and group[ids[i]] != group[ids[j]]}
    order, remaining = [], list(members)
    while remaining:
        ready = [g for g in remaining if not any(s in remaining and t == g for s, t in edges)]
        g = ready[0]  # remaining keeps the D1..D8 order, so ties resolve deterministically
        order.append(members[g])
        remaining.remove(g)
    return order


def submatrix(m: dict, nodes: list[str], matrix: str = "weighted") -> list[list]:
    idx = [m["ids"].index(n) for n in nodes]
    return [[m[matrix][i][j] for j in idx] for i in idx]


# --- labeled CSVs -------------------------------------------------------------------------------------

def labeled_csv(m: dict, matrix: str) -> str:
    fmt = (lambda v: str(v)) if matrix == "binary" else (lambda v: f"{v:.2f}")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["# row = source / upstream node; column = target / downstream node; cell (Di, Dj) means Di "
                "influences / contributes to Dj" + ("" if matrix == "binary" else
                                                     "; values are ordinal evidence / model weights, not probabilities")])
    w.writerow(["source \\ target", *(f"{n} {NODE_LABELS[n]}" for n in m["ids"])])
    for n, row in zip(m["ids"], m[matrix]):
        w.writerow([f"{n} {NODE_LABELS[n]}", *(fmt(v) for v in row)])
    return buf.getvalue()


# --- SVG figures --------------------------------------------------------------------------------------

def _text(x, y, s, size=13, fill=INK, anchor="start", weight="normal", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {extra}>{escape(s)}</text>')


def _luminance(hex_color: str) -> float:
    c = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def cell_text_color(fill: str) -> str:
    return INK if contrast(fill, INK) >= contrast(fill, "#ffffff") else "#ffffff"


def coupled_cells(m: dict) -> set[tuple[str, str]]:
    """Nonzero cells whose row and column lie in the same coupled block (includes the D6 self-loop)."""
    ids, b = m["ids"], m["binary"]
    out = set()
    for block in m["coupled_blocks"]:
        for r in block:
            for c in block:
                if b[ids.index(r)][ids.index(c)]:
                    out.add((r, c))
    return out


def heatmap_svg(m: dict, matrix: str, title: str | None = None, extra_notes: list[str] | None = None) -> str:
    """Heatmap of the binary or weighted DSM. title / extra_notes let other layers reuse it; the defaults reproduce
    the DSM visualization package exactly."""
    ids, data = m["ids"], m[matrix]
    cs, left, top = 62, 330, 150
    n = len(ids)
    width, height = left + n * cs + 80, top + n * cs + 250
    coupled = coupled_cells(m)
    sinks, _ = sinks_and_sources(m)
    title = title or ("Binary DSM: modeled relationships (1) between the 8 nodes" if matrix == "binary"
                      else "Weighted DSM: ordinal evidence / model weights (not probabilities)")
    if extra_notes:
        height += 20 * len(extra_notes)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
           _text(24, 34, title, 18, weight="600"),
           _text(24, 58, "Row = SOURCE / upstream node.  Column = TARGET / downstream node.  "
                         "Cell [Di, Dj] means Di influences / contributes to Dj.", 13, INK_2),
           _text(left + n * cs / 2, top - 52, "TARGET / downstream (column)  →", 13, INK_2, "middle", "600"),
           _text(24, top - 14, "SOURCE / upstream (row)  ↓", 13, INK_2, weight="600")]
    for j, c in enumerate(ids):
        out.append(_text(left + j * cs + cs / 2, top - 12, c, 14, INK, "middle", "600"))
    for i, r in enumerate(ids):
        label = f"{r}  {NODE_LABELS[r]}" + ("  (sink)" if r in sinks else "")
        out.append(_text(left - 10, top + i * cs + cs / 2 + 5, label, 13, INK, "end"))
        for j, c in enumerate(ids):
            v = data[i][j]
            fill = ZERO if not v else (BINARY_FILL if matrix == "binary" else TIER_FILL[v])
            x, y = left + j * cs, top + i * cs
            tip = f"{r} → {c}: " + (f"{v}" if matrix == "binary" else f"{v:.2f} ({TIER_MEANING[v]})")
            cell = m["cells"].get(f"{r}->{c}")
            if cell:
                tip += " | " + "; ".join(f"{d['dependency_id']} {d['source_activity']}→{d['target_activity']}"
                                         for d in cell["contributing_dependencies"])
            out.append(f'<g><title>{escape(tip)}</title>'
                       f'<rect x="{x + 1}" y="{y + 1}" width="{cs - 2}" height="{cs - 2}" rx="4" fill="{fill}"/>')
            label = str(v) if matrix == "binary" else (f"{v:.2f}" if v else "0")
            out.append(_text(x + cs / 2, y + cs / 2 + 5, label, 14, cell_text_color(fill) if v else MUTED, "middle",
                             "600" if v else "normal") + "</g>")
            if (r, c) in coupled:
                out.append(f'<rect x="{x + 3}" y="{y + 3}" width="{cs - 6}" height="{cs - 6}" rx="3" fill="none" '
                           f'stroke="{INK}" stroke-width="3" stroke-dasharray="7 4"/>')
    # legend and annotations
    ly = top + n * cs + 36
    out.append(_text(24, ly, "Legend", 14, weight="600"))
    swatches = [(ZERO, "0 = no modeled relationship"), (BINARY_FILL, "1 = modeled relationship")] if matrix == "binary" \
        else [(ZERO, "0.00  absent / excluded")] + [(TIER_FILL[w], f"{w:.2f}  {TIER_MEANING[w]}") for w in TIER_FILL]
    for k, (fill, text) in enumerate(swatches):
        y = ly + 14 + k * 24
        out.append(f'<rect x="24" y="{y}" width="18" height="18" rx="3" fill="{fill}"/>')
        out.append(_text(50, y + 14, text, 13, INK_2))
    ax = 520
    out.append(f'<rect x="{ax}" y="{ly + 14}" width="18" height="18" rx="3" fill="none" stroke="{INK}" '
               f'stroke-width="3" stroke-dasharray="7 4"/>')
    out.append(_text(ax + 26, ly + 28, "dashed outline = cell inside a coupled block", 13, INK_2))
    blocks = ", ".join("{" + ", ".join(b) + "}" for b in m["coupled_blocks"])
    notes = [f"Coupled blocks (strongly connected): {blocks}",
             "D2 ↔ D3: design and weight iterate.",
             "D4 ↔ D6: software and flight test iterate.",
             "D6 → D6: rework inside flight test (diagonal exception).",
             f"{', '.join(sinks)} is a terminal sink: its row is all zero."] + (extra_notes or [])
    for k, s in enumerate(notes):
        out.append(_text(ax, ly + 58 + k * 20, s, 13, INK_2))
    out.append("</svg>")
    return "\n".join(out) + "\n"


NETWORK_POS = {"D1": (110, 330), "D2": (330, 150), "D3": (330, 330), "D4": (430, 540), "D5": (580, 210),
               "D6": (720, 430), "D7": (900, 560), "D8": (1010, 270)}
# per-edge bend (perpendicular offset of the curve's control point, px); 0 = straight
NETWORK_BEND = {("D2", "D3"): 36, ("D3", "D2"): 36, ("D4", "D6"): 40, ("D6", "D4"): 40,
                ("D1", "D6"): -110, ("D2", "D8"): 120}
BLOCK_LABEL_POS = {("D2", "D3"): (175, 175), ("D4", "D6"): (575, 600)}
# node-name label placement: (dx, dy, anchor) relative to the node centre, chosen to avoid arrows
NAME_POS = {"D1": (0, 50, "middle"), "D2": (0, -42, "middle"), "D3": (0, 50, "middle"), "D4": (0, 50, "middle"),
            "D5": (0, -42, "middle"), "D6": (40, 52, "start"), "D7": (0, 50, "middle"), "D8": (40, -42, "end")}
NODE_R = 32
EDGE_WIDTH = {0.25: 1.5, 0.50: 2.5, 0.75: 3.5, 1.00: 4.5}


def _edge_geometry(a, b, bend):
    (x1, y1), (x2, y2) = NETWORK_POS[a], NETWORK_POS[b]
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    nx, ny = -dy / length, dx / length  # left-hand normal
    cx, cy = (x1 + x2) / 2 + nx * bend, (y1 + y2) / 2 + ny * bend

    def trim(px, py, qx, qy, r):  # move point p toward q by r
        ddx, ddy = qx - px, qy - py
        d = (ddx * ddx + ddy * ddy) ** 0.5
        return px + ddx / d * r, py + ddy / d * r

    sx, sy = trim(x1, y1, cx, cy, NODE_R + 2)
    ex, ey = trim(x2, y2, cx, cy, NODE_R + 8)
    mx, my = 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey
    return (sx, sy, cx, cy, ex, ey), (mx, my)


def network_svg(m: dict) -> str:
    ids, w = m["ids"], m["weighted"]
    width, height = 1160, 760
    sinks, sources = sinks_and_sources(m)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>',
           "<defs>" + "".join(
               f'<marker id="arrow{int(t * 100)}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" '
               f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{f}"/></marker>'
               for t, f in TIER_FILL.items()) + "</defs>",
           _text(24, 34, "DSM dependency network: arrow = source → target, label = weight", 18, weight="600"),
           _text(24, 58, "Same data as the weighted DSM. Line darkness and width follow the weight tier "
                         "(ordinal, not a probability). Shaded areas are coupled blocks.", 13, INK_2)]
    # coupled-block shading
    for block in m["coupled_blocks"]:
        if len(block) != 2:
            continue  # two-node blocks only in this model; a self-loop alone is drawn as its own arc
        (x1, y1), (x2, y2) = NETWORK_POS[block[0]], NETWORK_POS[block[1]]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        half = math.hypot(x2 - x1, y2 - y1) / 2
        out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{half + 66:.1f}" ry="62" fill="#eef4fd" stroke="#9ec5f4" '
                   f'stroke-dasharray="6 4" transform="rotate({angle:.1f} {cx:.1f} {cy:.1f})"/>')
        lx, ly_ = BLOCK_LABEL_POS[tuple(block)]
        out.append(_text(lx, ly_, "coupled block {" + ", ".join(block) + "}", 12, INK_2, "middle", "600"))
    edges, labels = [], []
    for i, a in enumerate(ids):
        for j, b in enumerate(ids):
            v = w[i][j]
            if not v:
                continue
            color = TIER_FILL[v]
            if a == b:  # self-loop above the node
                x, y = NETWORK_POS[a]
                edges.append(f'<path d="M{x - 14},{y - NODE_R + 2} C{x - 50},{y - 105} {x + 50},{y - 105} {x + 14},'
                             f'{y - NODE_R - 6}" fill="none" stroke="{color}" stroke-width="{EDGE_WIDTH[v]}" '
                             f'marker-end="url(#arrow{int(v * 100)})"><title>{a} → {b}: {v:.2f}</title></path>')
                labels.append((x, y - 86, f"{v:.2f}", f"{a} → {b} (rework)"))
                continue
            (sx, sy, cx, cy, ex, ey), (mx, my) = _edge_geometry(a, b, NETWORK_BEND.get((a, b), 0))
            edges.append(f'<path d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" fill="none" stroke="{color}" '
                         f'stroke-width="{EDGE_WIDTH[v]}" marker-end="url(#arrow{int(v * 100)})">'
                         f'<title>{a} → {b}: {v:.2f} ({TIER_MEANING[v]})</title></path>')
            labels.append((mx, my, f"{v:.2f}", f"{a} → {b}"))
    out += edges
    for x, y, s, tip in labels:
        out.append(f'<g><title>{escape(tip)}</title><rect x="{x - 19:.1f}" y="{y - 11:.1f}" width="38" height="20" rx="4" '
                   f'fill="{SURFACE}" stroke="#d9d8d3"/>' + _text(round(x, 1), round(y + 4, 1), s, 12, INK, "middle") + "</g>")
    for n in ids:
        x, y = NETWORK_POS[n]
        role = " (sink)" if n in sinks else (" (source)" if n in sources else "")
        out.append(f'<g><title>{n} {escape(NODE_LABELS[n])}</title><circle cx="{x}" cy="{y}" r="{NODE_R}" fill="{SURFACE}" '
                   f'stroke="{INK}" stroke-width="2"/>' + _text(x, y + 5, n, 15, INK, "middle", "600") + "</g>")
        dx, dy, anchor = NAME_POS[n]
        out.append(_text(x + dx, y + dy, NODE_LABELS[n] + role, 12, INK_2, anchor, "600", HALO))
    # legend: two columns
    ly = height - 110
    out.append(_text(24, ly, "Weight tier (ordinal, not a probability)", 13, weight="600"))
    for k, (t, f) in enumerate(TIER_FILL.items()):
        x, y = 24 + (k % 2) * 440, ly + 22 + (k // 2) * 24
        out.append(f'<line x1="{x}" y1="{y}" x2="{x + 34}" y2="{y}" stroke="{f}" stroke-width="{EDGE_WIDTH[t]}"/>')
        out.append(_text(x + 42, y + 4, f"{t:.2f}  {TIER_MEANING[t]}", 12, INK_2))
    out.append(_text(24, ly + 84, "D1 is a pure source (column all zero); D8 is a terminal sink (row all zero). "
                                  "Hover any arrow, label or node for details.", 12, INK_2))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# --- explanation document -----------------------------------------------------------------------------

def _md_matrix(m: dict, matrix: str, order: list[str] | None = None) -> str:
    order = order or m["ids"]
    fmt = (lambda v: str(v)) if matrix == "binary" else (lambda v: f"{v:.2f}" if v else "0")
    lines = ["| source \\ target | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
    for r in order:
        i = m["ids"].index(r)
        lines.append(f"| **{r}** | " + " | ".join(fmt(m[matrix][i][m["ids"].index(c)]) for c in order) + " |")
    return "\n".join(lines)


def _deps_text(m: dict, key: str) -> str:
    cell = m["cells"].get(key)
    if not cell:
        return "no approved dependency maps here"
    return "; ".join(f"{d['dependency_id']} {d['source_activity']} → {d['target_activity']} "
                     f"({d['relationship_type']}, {d['source_case']}, {d['weight_tier']} {d['weight']:.2f})"
                     for d in cell["contributing_dependencies"])


def _w(m: dict, r: str, c: str) -> float:
    return m["weighted"][m["ids"].index(r)][m["ids"].index(c)]


def explained_markdown(m: dict) -> str:
    ids = m["ids"]
    deg = degrees(m)
    sinks, sources = sinks_and_sources(m)
    blocks = m["coupled_blocks"]
    order = partitioned_order(m)
    flat = [n for g in order for n in g]
    in_block = {(r, c) for g in order for r in g for c in g}
    below = [(r, c) for a, r in enumerate(flat) for b, c in enumerate(flat)
             if b < a and m["binary"][ids.index(r)][ids.index(c)] and (r, c) not in in_block]
    nonzero = sum(v for row in m["binary"] for v in row)
    off_diag = nonzero - sum(m["binary"][i][i] for i in range(len(ids)))
    scope = m["provenance"]["dependency_scope_counts"]
    agentic = m["provenance"]["agentic_decisions_used"]
    node_rows = "\n".join(f"| {n['node_id']} | {NODE_LABELS[n['node_id']]} | {len(n['activity_ids'])} | "
                          f"{', '.join(n['activity_ids'])} |" for n in m["nodes"])
    deg_rows = "\n".join(f"| {n} | {deg[n][0]} | {deg[n][1]} | "
                         + ("sink" if n in sinks else "source" if n in sources else "") + " |" for n in ids)
    tier_rows = "\n".join(f"| {w:.2f} | {TIER_MEANING[w]} |" for w in TIER_MEANING)
    agentic_rows = "\n".join(f"| {a['source_case']} | {a['source_activity']} → {a['target_activity']} | "
                             f"{a['decision']} |" for a in agentic)
    sub_nodes = ["D4", "D6"]
    sub = submatrix(m, sub_nodes)
    blocks_text = ", ".join("{" + ", ".join(b) + "}" for b in blocks)
    order_text = " → ".join("{" + ", ".join(g) + "}" if len(g) > 1 else g[0] for g in order)
    fingerprints = "\n".join(f"| `{k}` | `{v}` |" for k, v in m["input_sha256"].items())
    return f"""# Understanding the DSM: a visual and mathematical guide

> Illustrative capstone model built on the Evidence-Calibrated Synthetic F-35 Development Baseline v1.1. It is **not**
> a historical F-35 DSM and not an actual or reconstructed F-35 contractor schedule.

Everything in this folder is generated **read-only** from the frozen DSM outputs in `outputs/dsm/` by
`scripts/build_dsm_visualization.py`. No DSM entry, weight, dependency or agentic decision is recomputed or changed.
The input fingerprints are at the end of this document.

| File | What it shows |
|---|---|
| `binary_dsm_labeled.csv` / `weighted_dsm_labeled.csv` | The two matrices with full node names on rows and columns |
| `binary_dsm_heatmap.svg` / `.png` | The binary DSM, with coupled-block cells outlined |
| `weighted_dsm_heatmap.svg` / `.png` | The weighted DSM, shaded by weight tier |
| `dsm_dependency_network.svg` / `.png` | The same weighted relationships drawn as a directed network |

The SVG files are the source figures; open them in a browser and hover any cell or arrow to see the contributing
dependencies. The PNG files are rasterized copies.

## 1. The 8 nodes

| Node | Name | Activities | IMS activities mapped to it |
|---|---|---|---|
{node_rows}

### Why 8 nodes when the IMS has 35 activities

The IMS describes **work**: 35 activities with durations and finish-to-start sequencing. The DSM describes
**structure**: which *areas* of the program depend on which. Each activity belongs to exactly one node, so several
activities collapse into one row and one column. For example, A200-A230 (seven software activities) are all D4.

Eight nodes keep the matrix small enough to read and reason about. They match the dependency themes the evidence
speaks to (software maturity, test-aircraft availability, weight, concurrency), and a later WTM can work on an 8 x 8
matrix instead of 35 x 35. The cost is that detail inside a node disappears. Of the
{sum(scope.values())} approved dependencies:
- {scope.get('INTER_NODE', 0)} link activities in different nodes and become off-diagonal entries;
- {scope.get('INTRA_NODE', 0)} link activities in the same node and are not shown in the matrix (they stay in
  `outputs/dsm/dependency_registry.json`);
- {scope.get('FEEDBACK', 0)} are rework feedback links.

## 2. How the DSM was built

```
real documentary evidence (GAO / DOT&E passages in the RAG corpus)
  -> agentic dependency interpretation (Tree-of-Thought generator + critic; 3 cases run)
  -> deterministic validation (Python owns the hard constraints)
  -> dependency registry (43 approved activity-level dependencies, each labelled OBSERVED / DERIVED / SYNTHETIC)
  -> DSM aggregation (deterministic Python: activity links -> node cells)
```

Each step, honestly:

1. **Evidence.** Retrieved passages are the OBSERVED layer (15 entries in the evidence register).
2. **Agentic interpretation.** Only three dependencies were assessed by the agentic pipeline, each in a single
   REAL_LLM_MODE run:

   | Case | Dependency | Agentic decision |
   |---|---|---|
{chr(10).join('   ' + r for r in agentic_rows.splitlines())}

   The other evidence-derived dependencies carry a passage support label (EXPLICIT_PASSAGE or FRAGMENTARY) from the
   evaluation outputs. The rest are synthetic sequencing.
3. **Deterministic validation.** The synthetic baseline validator checks the registry (counts, references, no cycles in
   the schedule, provenance classes, feedback links). The DSM validator checks the matrices.
4. **Registry.** The 43 dependencies are the only input to the DSM.
5. **Aggregation.** Each dependency maps to the cell (node of its source activity, node of its target activity). No LLM
   is involved in any matrix entry.

## 3. Orientation: how to read a cell

**ROW = SOURCE / UPSTREAM node. COLUMN = TARGET / DOWNSTREAM node.**

So the cell in row Di, column Dj means **Di influences / contributes to Dj**. Read across a row to see what a node
feeds, and down a column to see what a node depends on.

Worked examples from the actual matrix:

1. **[D4, D6] = {_w(m, 'D4', 'D6'):.2f}.** Mission-System Software Maturity feeds Flight-Test Execution: software must be
   verified before the flight-test readiness review. Source: {_deps_text(m, 'D4->D6')}.
2. **[D5, D6] = {_w(m, 'D5', 'D6'):.2f}.** Test-Aircraft Availability feeds Flight-Test Execution. Source:
   {_deps_text(m, 'D5->D6')}. The passages state this explicitly, but the agentic decision was UNRESOLVED, and that
   decision governs the weight. This is uncertainty kept, not dropped.
3. **[D3, D8] = {_w(m, 'D3', 'D8'):.2f}.** Weight / Structural Maturity feeds Production Commitment / Rework Exposure:
   weight-driven redesign adds downstream cost and schedule exposure. Source: {_deps_text(m, 'D3->D8')}.
4. **[D8, D7] = {_w(m, 'D8', 'D7'):.0f}.** Reading the other way round gives zero. Production commitment does not feed
   back into development / test maturity in this model ({_deps_text(m, 'D8->D7')}).

## 4. Binary DSM

0 = no modeled relationship; 1 = modeled relationship. There are {nonzero} nonzero cells: {off_diag} off-diagonal plus
{nonzero - off_diag} on the diagonal.

{_md_matrix(m, 'binary')}

## 5. Weighted DSM

The same cells, but each carries a weight that says how well the relationship is supported. **These are ordinal
evidence / model weights, not probabilities.** 0.75 means "better supported than 0.50". It does not mean "75% likely",
and the values should not be multiplied or summed as if they were probabilities without an explicit modelling
decision.

| Weight | Meaning |
|---|---|
{tier_rows}

{_md_matrix(m, 'weighted')}

No cell is 1.00, because none of the three agentic decisions was SUPPORTED.

## 6. The math, simply

**The matrix.** With nodes numbered 1 to 8, the DSM is an 8 x 8 matrix

$$D = [d_{{ij}}], \\quad i, j \\in \\{{1, \\dots, 8\\}}$$

In plain English: a table with one row and one column per node. $d_{{ij}}$ is the entry in row $i$, column $j$, and
it describes the influence of node $i$ (source) on node $j$ (target).

**Which dependencies feed a cell.** Let $K_{{ij}}$ be the set of approved dependencies whose source activity is in
node $i$ and whose target activity is in node $j$. In plain English: all the activity-level arrows that go from
inside area $i$ to inside area $j$.

**Binary DSM.**

$$b_{{ij}} = \\begin{{cases}} 1 & \\text{{if }} K_{{ij}} \\text{{ contains at least one dependency with weight}} > 0 \\\\ 0 & \\text{{otherwise}} \\end{{cases}}$$

In plain English: put a 1 wherever at least one real (non-excluded) arrow crosses from area $i$ to area $j$.

**Weighted DSM.** Each dependency $k$ has a tier weight $w_k \\in \\{{0, 0.25, 0.5, 0.75, 1\\}}$, and

$$w_{{ij}} = \\max_{{k \\in K_{{ij}}}} w_k \\quad (w_{{ij}} = 0 \\text{{ if }} K_{{ij}} \\text{{ is empty}})$$

In plain English: a cell is as strong as its best-supported arrow. Max is used, not a sum, so many weak synthetic
links cannot add up to look like strong evidence. By construction, $b_{{ij}} = 1$ exactly when $w_{{ij}} > 0$.

**Off-diagonal cells** ($i \\neq j$) are the interfaces between areas. A nonzero $d_{{ij}}$ says that a change or
delay in area $i$ can reach area $j$. These are the paths a later propagation model will follow, so each one needs
provenance.

**Diagonal cells** ($i = j$) would mean an area influences itself. They are 0 by policy, because a node's own internal
sequencing is hidden. The one exception is $d_{{66}}$: the rework feedback A425 → A410 makes Flight-Test
Execution loop back on itself (re-flying after regression testing).

**Out-degree and in-degree** (binary, diagonal excluded). The row sum $\\sum_j b_{{ij}}$ counts how many areas a node
feeds. The column sum $\\sum_i b_{{ij}}$ counts how many areas feed it.

| Node | Out-degree (row sum) | In-degree (column sum) | Role |
|---|---|---|---|
{deg_rows}

**Coupling and strongly connected blocks.** Two nodes are *coupled* when each can reach the other by following
arrows: $i \\to \\dots \\to j$ and $j \\to \\dots \\to i$. A set of nodes in which every node can reach every other is a
*strongly connected block*. This model has the blocks {blocks_text}.

Why it matters: outside a block, work flows one way and can be sequenced, upstream first. Inside a block there is no
"first" node; each waits on the other, so the work has to **iterate** until it converges. Iteration is where rework,
schedule growth and propagated delay come from, so these blocks are where a WTM will focus.

**A one-way order with the blocks grouped.** Grouping each block into one unit and sorting upstream to downstream
gives:

{order_text}

The weighted DSM in that order:

{_md_matrix(m, 'weighted', flat)}

With this ordering, {('every nonzero entry outside the coupled blocks lies above the diagonal' if not below
else f'{len(below)} entries remain below the diagonal outside the blocks')}. The only marks below the diagonal sit
inside the blocks. That is what "the structure is sequential except for the coupled blocks" means. This is a reordered
*view* only; the frozen files keep the D1-D8 order.

## 7. Coupled blocks and feedback

- **D2 ↔ D3 (design ↔ weight).** [D2, D3] = {_w(m, 'D2', 'D3'):.2f} ({_deps_text(m, 'D2->D3')}) and
  [D3, D2] = {_w(m, 'D3', 'D2'):.2f} ({_deps_text(m, 'D3->D2')}). The preliminary design is assessed for weight, and the
  weight corrections return to the design-maturity review. The activity schedule is a single pass with no cycle; the
  loop appears only when activities are grouped into nodes. Both links are synthetic sequencing (0.25).
- **D4 ↔ D6 (software ↔ flight test).** This is the loop the capstone demonstration centres on (Section 8).
- **D6 → D6 (rework inside flight test).** [D6, D6] = {_w(m, 'D6', 'D6'):.2f} ({_deps_text(m, 'D6->D6')}).
  Regression results can send flight test back for more test points.

The baseline IMS has no cycles. The two FEEDBACK_REWORK dependencies are kept out of the schedule's predecessor lists,
so the plan stays a valid single pass. They exist in the registry and the DSM so the WTM can model iteration.

## 8. The D4 / D6 block, mathematically

Extracting rows and columns D4 and D6 from the weighted DSM:

$$W_{{\\{{4,6\\}}}} = \\begin{{pmatrix}} w_{{44}} & w_{{46}} \\\\ w_{{64}} & w_{{66}} \\end{{pmatrix}} = \\begin{{pmatrix}} {sub[0][0]:.2f} & {sub[0][1]:.2f} \\\\ {sub[1][0]:.2f} & {sub[1][1]:.2f} \\end{{pmatrix}}$$

| source \\ target | D4 Mission-System Software Maturity | D6 Flight-Test Execution |
|---|---|---|
| **D4** | {sub[0][0]:.2f} | {sub[0][1]:.2f} |
| **D6** | {sub[1][0]:.2f} | {sub[1][1]:.2f} |

What each entry means:

- **$w_{{46}}$ = {sub[0][1]:.2f}: software maturity → flight test (forward).** Flight test cannot pass its readiness
  gate until the mission-system integration baseline is verified. Source: {_deps_text(m, 'D4->D6')}. The weight is
  0.75 because the Q01 agentic decision was PARTIALLY_SUPPORTED.
- **$w_{{64}}$ = {sub[1][0]:.2f}: flight test → software maturity (feedback).** Deficiencies discovered in flight
  test send work back to software / integration correction. Source: {_deps_text(m, 'D6->D4')}. The weight is 0.50
  because the concept rests on fragmentary evidence and has no agentic decision. The exact activity pair is synthetic.
- **$w_{{66}}$ = {sub[1][1]:.2f}: flight test → flight test (self-loop).** Regression testing can lead to further
  flight test within D6.
- **$w_{{44}}$ = {sub[0][0]:.2f}.** There is no self-loop on software; its internal sequencing is hidden in the node.

In plain English: software feeds flight test, and flight test can push work back into software. A delay or deficiency
on either side can therefore circulate around the loop instead of passing through once. The forward link is better
supported (0.75) than the return link (0.50). How strongly a disturbance is amplified or damped around this loop is
the WTM's question. **It is not calculated here.**

## 9. D8 is a terminal sink; D1 is a source

- **D8 Production Commitment / Rework Exposure** has out-degree {deg['D8'][0]} and in-degree {deg['D8'][1]}. Its row
  is all zero, so it receives effects from D2, D3, D6 and D7 but passes nothing back. In this model, production exposure
  is where consequences accumulate. Since v1.1 there is no production → test feedback.
- **D1 Requirements / KPP Definition** has in-degree {deg['D1'][1]}: nothing feeds it. Changes start here and flow
  downstream.

## 10. Not computed yet

Eigenvalues, spectral radius, propagation iterations, work-transformation (WTM) rates and scenario simulations. Those
belong to the next stage.

## 11. Limitations

- The weights are ordinal tiers chosen by a documented rule, not calibrated probabilities. Max-aggregation hides how
  many dependencies support a cell.
- The three agentic decisions come from single runs within about 0.5 points of the threshold. Q04's 0.50 reflects a
  conservative UNRESOLVED decision despite explicit passages.
- Coupling at node level can come from synthetic sequencing alone (D2 ↔ D3 is 0.25 in both directions); it is a
  model structure, not an evidence finding.
- The feedback link D6 → D4 has a synthetic activity pair and fragmentary support.
- The figures are SVG drawn with the Python standard library, because no plotting package is installed. The PNGs are
  rasterized from the SVGs by a headless browser.

## Input fingerprints (SHA-256 of the frozen DSM files read)

| File | SHA-256 |
|---|---|
{fingerprints}
"""


def render_package(dsm_dir: Path) -> dict[str, str]:
    """File name -> exact text for every text artifact (CSV, Markdown, SVG, manifest). Read-only on dsm_dir."""
    m = load_frozen_dsm(dsm_dir)
    texts = {
        "binary_dsm_labeled.csv": labeled_csv(m, "binary"),
        "weighted_dsm_labeled.csv": labeled_csv(m, "weighted"),
        "dsm_explained.md": explained_markdown(m),
        "binary_dsm_heatmap.svg": heatmap_svg(m, "binary"),
        "weighted_dsm_heatmap.svg": heatmap_svg(m, "weighted"),
        "dsm_dependency_network.svg": network_svg(m),
    }
    texts["visualization_manifest.json"] = json.dumps({
        "purpose": "Read-only visualization of the frozen v1.1 DSM; no DSM data is recomputed or altered.",
        "inputs_sha256": m["input_sha256"],
        "generated_files": sorted(texts),
        "png_copies": [s.replace(".svg", ".png") for s in SVG_FILES],
        "not_computed": ["eigenvalues", "spectral radius", "propagation iterations", "scenario simulations"],
    }, indent=2) + "\n"
    return texts


# --- rasterizing (shared by the DSM visualization and WTM builds) -------------------------------------

BROWSERS = (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def find_browser() -> str | None:
    return next((b for b in BROWSERS if Path(b).is_file()), None)


def rasterize_svg(svg: Path, png: Path, browser: str) -> bool:
    """Screenshot an SVG to PNG with an already-installed headless browser (no plotting dependency)."""
    import re
    import subprocess
    import tempfile

    width, height = re.search(r'width="(\d+)" height="(\d+)"', svg.read_text(encoding="utf-8")).groups()
    png.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([browser, "--headless", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                        f"--window-size={width},{height}", f"--screenshot={png}", svg.resolve().as_uri()],
                       capture_output=True, timeout=120)
    return png.is_file()
