# Understanding the DSM: a visual and mathematical guide

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
| D1 | Requirements / KPP Definition | 4 | A100, A105, A110, A115 |
| D2 | Air Vehicle Design Maturity | 3 | A120, A140, A145 |
| D3 | Weight / Structural Maturity | 3 | A125, A130, A135 |
| D4 | Mission-System Software Maturity | 7 | A200, A205, A210, A215, A220, A225, A230 |
| D5 | Test-Aircraft Availability | 6 | A300, A305, A310, A315, A320, A325 |
| D6 | Flight-Test Execution | 6 | A400, A405, A410, A415, A420, A425 |
| D7 | Development / Test Maturity | 1 | A430 |
| D8 | Production Commitment / Rework Exposure | 5 | A500, A505, A510, A515, A520 |

### Why 8 nodes when the IMS has 35 activities

The IMS describes **work**: 35 activities with durations and finish-to-start sequencing. The DSM describes
**structure**: which *areas* of the program depend on which. Each activity belongs to exactly one node, so several
activities collapse into one row and one column. For example, A200-A230 (seven software activities) are all D4.

Eight nodes keep the matrix small enough to read and reason about. They match the dependency themes the evidence
speaks to (software maturity, test-aircraft availability, weight, concurrency), and a later WTM can work on an 8 x 8
matrix instead of 35 x 35. The cost is that detail inside a node disappears. Of the
43 approved dependencies:
- 15 link activities in different nodes and become off-diagonal entries;
- 26 link activities in the same node and are not shown in the matrix (they stay in
  `outputs/dsm/dependency_registry.json`);
- 2 are rework feedback links.

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
   | Q01 | A230 → A405 | PARTIALLY_SUPPORTED |
   | Q04 | A325 → A405 | UNRESOLVED |
   | Q08 | A430 → A510 | UNRESOLVED |

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

1. **[D4, D6] = 0.75.** Mission-System Software Maturity feeds Flight-Test Execution: software must be
   verified before the flight-test readiness review. Source: DEP-027 A230 → A405 (FINISH_TO_START, Q01, MODERATE 0.75).
2. **[D5, D6] = 0.50.** Test-Aircraft Availability feeds Flight-Test Execution. Source:
   DEP-028 A325 → A405 (FINISH_TO_START, Q04, UNRESOLVED_RETAINED 0.50). The passages state this explicitly, but the agentic decision was UNRESOLVED, and that
   decision governs the weight. This is uncertainty kept, not dropped.
3. **[D3, D8] = 0.75.** Weight / Structural Maturity feeds Production Commitment / Rework Exposure:
   weight-driven redesign adds downstream cost and schedule exposure. Source: DEP-040 A135 → A515 (FINISH_TO_START, Q07, MODERATE 0.75).
4. **[D8, D7] = 0.** Reading the other way round gives zero. Production commitment does not feed
   back into development / test maturity in this model (no approved dependency maps here).

## 4. Binary DSM

0 = no modeled relationship; 1 = modeled relationship. There are 16 nonzero cells: 15 off-diagonal plus
1 on the diagonal.

| source \ target | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 |
|---|---|---|---|---|---|---|---|---|
| **D1** | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 0 |
| **D2** | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 |
| **D3** | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| **D4** | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| **D5** | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| **D6** | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 |
| **D7** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **D8** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 5. Weighted DSM

The same cells, but each carries a weight that says how well the relationship is supported. **These are ordinal
evidence / model weights, not probabilities.** 0.75 means "better supported than 0.50". It does not mean "75% likely",
and the values should not be multiplied or summed as if they were probabilities without an explicit modelling
decision.

| Weight | Meaning |
|---|---|
| 0.00 | absent / excluded |
| 0.25 | purely synthetic sequencing |
| 0.50 | unresolved or fragment-supported relationship |
| 0.75 | partially supported or directly stated relationship |
| 1.00 | supported relationship |

| source \ target | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 |
|---|---|---|---|---|---|---|---|---|
| **D1** | 0 | 0.25 | 0.50 | 0.25 | 0 | 0.25 | 0 | 0 |
| **D2** | 0 | 0 | 0.25 | 0 | 0.50 | 0 | 0 | 0.25 |
| **D3** | 0 | 0.25 | 0 | 0 | 0 | 0 | 0 | 0.75 |
| **D4** | 0 | 0 | 0 | 0 | 0 | 0.75 | 0 | 0 |
| **D5** | 0 | 0 | 0 | 0 | 0 | 0.50 | 0 | 0 |
| **D6** | 0 | 0 | 0 | 0.50 | 0 | 0.50 | 0.25 | 0.50 |
| **D7** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.50 |
| **D8** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

No cell is 1.00, because none of the three agentic decisions was SUPPORTED.

## 6. The math, simply

**The matrix.** With nodes numbered 1 to 8, the DSM is an 8 x 8 matrix

$$D = [d_{ij}], \quad i, j \in \{1, \dots, 8\}$$

In plain English: a table with one row and one column per node. $d_{ij}$ is the entry in row $i$, column $j$, and
it describes the influence of node $i$ (source) on node $j$ (target).

**Which dependencies feed a cell.** Let $K_{ij}$ be the set of approved dependencies whose source activity is in
node $i$ and whose target activity is in node $j$. In plain English: all the activity-level arrows that go from
inside area $i$ to inside area $j$.

**Binary DSM.**

$$b_{ij} = \begin{cases} 1 & \text{if } K_{ij} \text{ contains at least one dependency with weight} > 0 \\ 0 & \text{otherwise} \end{cases}$$

In plain English: put a 1 wherever at least one real (non-excluded) arrow crosses from area $i$ to area $j$.

**Weighted DSM.** Each dependency $k$ has a tier weight $w_k \in \{0, 0.25, 0.5, 0.75, 1\}$, and

$$w_{ij} = \max_{k \in K_{ij}} w_k \quad (w_{ij} = 0 \text{ if } K_{ij} \text{ is empty})$$

In plain English: a cell is as strong as its best-supported arrow. Max is used, not a sum, so many weak synthetic
links cannot add up to look like strong evidence. By construction, $b_{ij} = 1$ exactly when $w_{ij} > 0$.

**Off-diagonal cells** ($i \neq j$) are the interfaces between areas. A nonzero $d_{ij}$ says that a change or
delay in area $i$ can reach area $j$. These are the paths a later propagation model will follow, so each one needs
provenance.

**Diagonal cells** ($i = j$) would mean an area influences itself. They are 0 by policy, because a node's own internal
sequencing is hidden. The one exception is $d_{66}$: the rework feedback A425 → A410 makes Flight-Test
Execution loop back on itself (re-flying after regression testing).

**Out-degree and in-degree** (binary, diagonal excluded). The row sum $\sum_j b_{ij}$ counts how many areas a node
feeds. The column sum $\sum_i b_{ij}$ counts how many areas feed it.

| Node | Out-degree (row sum) | In-degree (column sum) | Role |
|---|---|---|---|
| D1 | 4 | 0 | source |
| D2 | 3 | 2 |  |
| D3 | 2 | 2 |  |
| D4 | 1 | 2 |  |
| D5 | 1 | 1 |  |
| D6 | 3 | 3 |  |
| D7 | 1 | 1 |  |
| D8 | 0 | 4 | sink |

**Coupling and strongly connected blocks.** Two nodes are *coupled* when each can reach the other by following
arrows: $i \to \dots \to j$ and $j \to \dots \to i$. A set of nodes in which every node can reach every other is a
*strongly connected block*. This model has the blocks {D2, D3}, {D4, D6}.

Why it matters: outside a block, work flows one way and can be sequenced, upstream first. Inside a block there is no
"first" node; each waits on the other, so the work has to **iterate** until it converges. Iteration is where rework,
schedule growth and propagated delay come from, so these blocks are where a WTM will focus.

**A one-way order with the blocks grouped.** Grouping each block into one unit and sorting upstream to downstream
gives:

D1 → {D2, D3} → D5 → {D4, D6} → D7 → D8

The weighted DSM in that order:

| source \ target | D1 | D2 | D3 | D5 | D4 | D6 | D7 | D8 |
|---|---|---|---|---|---|---|---|---|
| **D1** | 0 | 0.25 | 0.50 | 0 | 0.25 | 0.25 | 0 | 0 |
| **D2** | 0 | 0 | 0.25 | 0.50 | 0 | 0 | 0 | 0.25 |
| **D3** | 0 | 0.25 | 0 | 0 | 0 | 0 | 0 | 0.75 |
| **D5** | 0 | 0 | 0 | 0 | 0 | 0.50 | 0 | 0 |
| **D4** | 0 | 0 | 0 | 0 | 0 | 0.75 | 0 | 0 |
| **D6** | 0 | 0 | 0 | 0 | 0.50 | 0.50 | 0.25 | 0.50 |
| **D7** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.50 |
| **D8** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

With this ordering, every nonzero entry outside the coupled blocks lies above the diagonal. The only marks below the diagonal sit
inside the blocks. That is what "the structure is sequential except for the coupled blocks" means. This is a reordered
*view* only; the frozen files keep the D1-D8 order.

## 7. Coupled blocks and feedback

- **D2 ↔ D3 (design ↔ weight).** [D2, D3] = 0.25 (DEP-005 A120 → A125 (FINISH_TO_START, NONE, SYNTHETIC_SEQUENCING 0.25)) and
  [D3, D2] = 0.25 (DEP-009 A135 → A140 (FINISH_TO_START, NONE, SYNTHETIC_SEQUENCING 0.25)). The preliminary design is assessed for weight, and the
  weight corrections return to the design-maturity review. The activity schedule is a single pass with no cycle; the
  loop appears only when activities are grouped into nodes. Both links are synthetic sequencing (0.25).
- **D4 ↔ D6 (software ↔ flight test).** This is the loop the capstone demonstration centres on (Section 8).
- **D6 → D6 (rework inside flight test).** [D6, D6] = 0.50 (DEP-042 A425 → A410 (FEEDBACK_REWORK, Q01, UNRESOLVED_RETAINED 0.50)).
  Regression results can send flight test back for more test points.

The baseline IMS has no cycles. The two FEEDBACK_REWORK dependencies are kept out of the schedule's predecessor lists,
so the plan stays a valid single pass. They exist in the registry and the DSM so the WTM can model iteration.

## 8. The D4 / D6 block, mathematically

Extracting rows and columns D4 and D6 from the weighted DSM:

$$W_{\{4,6\}} = \begin{pmatrix} w_{44} & w_{46} \\ w_{64} & w_{66} \end{pmatrix} = \begin{pmatrix} 0.00 & 0.75 \\ 0.50 & 0.50 \end{pmatrix}$$

| source \ target | D4 Mission-System Software Maturity | D6 Flight-Test Execution |
|---|---|---|
| **D4** | 0.00 | 0.75 |
| **D6** | 0.50 | 0.50 |

What each entry means:

- **$w_{46}$ = 0.75: software maturity → flight test (forward).** Flight test cannot pass its readiness
  gate until the mission-system integration baseline is verified. Source: DEP-027 A230 → A405 (FINISH_TO_START, Q01, MODERATE 0.75). The weight is
  0.75 because the Q01 agentic decision was PARTIALLY_SUPPORTED.
- **$w_{64}$ = 0.50: flight test → software maturity (feedback).** Deficiencies discovered in flight
  test send work back to software / integration correction. Source: DEP-043 A415 → A225 (FEEDBACK_REWORK, Q01, UNRESOLVED_RETAINED 0.50). The weight is 0.50
  because the concept rests on fragmentary evidence and has no agentic decision. The exact activity pair is synthetic.
- **$w_{66}$ = 0.50: flight test → flight test (self-loop).** Regression testing can lead to further
  flight test within D6.
- **$w_{44}$ = 0.00.** There is no self-loop on software; its internal sequencing is hidden in the node.

In plain English: software feeds flight test, and flight test can push work back into software. A delay or deficiency
on either side can therefore circulate around the loop instead of passing through once. The forward link is better
supported (0.75) than the return link (0.50). How strongly a disturbance is amplified or damped around this loop is
the WTM's question. **It is not calculated here.**

## 9. D8 is a terminal sink; D1 is a source

- **D8 Production Commitment / Rework Exposure** has out-degree 0 and in-degree 4. Its row
  is all zero, so it receives effects from D2, D3, D6 and D7 but passes nothing back. In this model, production exposure
  is where consequences accumulate. Since v1.1 there is no production → test feedback.
- **D1 Requirements / KPP Definition** has in-degree 0: nothing feeds it. Changes start here and flow
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
| `outputs/dsm/binary_dsm.csv` | `cb28379e77d9c9a4926019b34f0ac0d7f6238cd67924b54ef16b6f67998fc7d2` |
| `outputs/dsm/weighted_dsm.csv` | `733e3597e1f6899d519be6979a99450ae73ea1e0599a8fc1c60d93d2e9328c93` |
| `outputs/dsm/dsm_provenance.json` | `030a1ab1f8468cfb099d1e60efbd2dfa1f1d0bfd320cacacaf9b29b16cfb9c54` |
| `outputs/dsm/activity_registry.json` | `bcc6d866f98e744a28d0922f61eb2a595e2fb9bcc3a377b09e44c9f0fb07bfaa` |
| `outputs/dsm/dependency_registry.json` | `982b5275f593a10597f670bd1913bd6b8c26de60b5ea57d24818030a237e47c4` |
