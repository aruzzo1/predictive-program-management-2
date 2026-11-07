# Synthetic Program Baseline: Evidence-Calibrated Synthetic F-35 Development Baseline v1.1

> **This synthetic IMP/IMS is an evidence-calibrated experimental model created for the Predictive Program
> Management 2.0 capstone. It is not an actual or reconstructed F-35 contractor schedule.**

## Status: v1.1 FROZEN for the capstone MVP (2026-11-01)

v1.1 is frozen with these values:
- 8 IMP events, 35 IMS activities, 8 DSM nodes, 43 dependencies and 6 scenarios / policies;
- A230 total float 4 workdays and A325 total float 0;
- a baseline program duration of 355 workdays.

No further changes are allowed to durations, float, scenario magnitudes, predecessor logic or policy values, unless a
genuine implementation defect is found. Any such fix must be recorded as a new version in `version_history` and
`freeze` in `synthetic_provenance.json`. The validator fails if `freeze` no longer matches the files.

Recorded decisions:
- INTERVENTION_2 stays based on DISTURBANCE_1, the mission-system software delay. Resequencing lets test content that
  does not need the delayed mission-system capability proceed after the A405 readiness gate.
- Q04 keeps weight 0.50 in the DSM. Where an agentic decision exists, it governs the weight. Q04 is an example of
  conservative agentic evaluation (UNRESOLVED at 69.5 despite explicit passages) and of uncertainty kept rather than
  dropped.

## Version history

| Version | Status | What it is |
|---|---|---|
| v1.0 | Superseded; archived unchanged in `data/synthetic/archive/v1.0/` (SHA-256 recorded in `version_history`) | The original frozen synthetic baseline |
| v1.1 | **Current, frozen** | A minor structural-model revision, made after DSM aggregation exposed two abstraction defects |

**v1.1 changes only two things:**

1. **Cross-node rework feedback.** v1.0 represented the flight-test rework loop only inside D6 (A425 -> A410). That
   could not express test-discovered deficiencies feeding back to software. v1.1 adds one `FEEDBACK_REWORK` dependency,
   **A415 Analyze Flight-Test Results and Deficiencies -> A225 Correct Critical Software / Integration Deficiencies**
   (DEP-043, D6 -> D4).
   - The engineering concept is evidence-calibrated: concept classification DERIVED, from Q01, FRAGMENTARY (DOT&E
     FY2010 p.33, discovery in flight test; p.29, software delays affected flight test).
   - The exact activity pair is synthetic: implementation classification SYNTHETIC.
   - It is not a scheduling predecessor, so the IMS stays acyclic.
   - With A230 -> A405 (D4 -> D6), it gives the coupled loop D4 -> D6 -> D4. The original A425 -> A410 feedback is
     kept (regression results -> further flight test).
2. **DSM-node assignment of A510.** A510 Conduct Development / Production Readiness Assessment moved from D7 to D8.
   - The Q08 link A430 -> A510, which v1.0 hid inside D7, now maps to D7 -> D8. No dependency was added for it.
   - A430 stays in D7. D8 now holds A500, A505, A510, A515 and A520.
   - A510's workstream and IMP event are unchanged.

**No baseline schedule calibration changed.** Durations, predecessor logic, baseline dates, total floats, the
355-workday duration, IMP / IMS counts, scenario magnitudes and intervention policies are identical to v1.0. A test
compares v1.1 against the archived v1.0 files.

## Why it exists

The public JSF corpus (GAO and DOT&E reports) describes dependencies between program *themes*, such as software
maturity and flight test, but contains no contractor IMP or IMS. The later DSM, WTM and forward-simulation stages need a
structured schedule to work on. This dataset provides one. Its activity structure, durations and scenarios are
invented; a small number of its dependency *concepts* are calibrated against evidence retrieved for Q01, Q04, Q07 and
Q08. No historical accuracy is claimed.

## Files

| File | Content |
|---|---|
| `data/synthetic/synthetic_imp.csv` | 8 IMP events, their activities and baseline completion workday |
| `data/synthetic/synthetic_ims.csv` | 35 IMS activities with sequencing, schedule, indicators and provenance |
| `data/synthetic/synthetic_dependencies.csv` | 41 finish-to-start links and 2 rework feedback links, with provenance |
| `data/synthetic/synthetic_scenarios.json` | BASELINE, 2 disturbances, 3 interventions (definitions only) |
| `data/synthetic/synthetic_provenance.json` | Statement, provenance model, DSM node definitions, observed-evidence register, Q-case notes |

The source of truth is `src/ppm_agent/synthetic/baseline.py`. The files are generated, never hand-edited:

```
.\.venv\Scripts\python.exe scripts\build_synthetic_baseline.py          # rebuild and validate
.\.venv\Scripts\python.exe scripts\build_synthetic_baseline.py --check  # validate only
```

The build is deterministic. A test fails if the committed files differ from what the definitions produce.

**Separation from the corpus.** The files live only in `data/synthetic/`. Nothing is placed in `data/raw/jsf/`. RAG
ingestion is driven by the corpus manifests, which do not reference these files, and the vector store and embeddings
were not touched.

## Provenance model

| Class | Meaning | Where it is used |
|---|---|---|
| **OBSERVED** | Directly supported by public F-35 source documentation | Only the `observed_evidence` register in the provenance file (15 entries) |
| **DERIVED** | An analytical dependency or relationship inferred from observed evidence | 11 dependency concepts; the 8 DSM node groupings |
| **SYNTHETIC** | Durations, schedule positions, activity structure, disturbances, interventions, simulated outcomes | Every IMS activity, IMP event, scenario, change and policy value; the float calibration; 32 generic dependencies; the implementation of every dependency |

The rules that keep the classes apart:

- Every IMS activity and IMP event is `SYNTHETIC`. `evidence_basis` names the observed *theme* that motivated it, if
  any; that does not make the activity observed.
- A dependency row carries two classifications. `data_classification` is `DERIVED` when the *concept* is inferred
  from Q01/Q04/Q07/Q08 evidence, otherwise `SYNTHETIC`. `implementation_classification` is always `SYNTHETIC`, because
  the exact activity-to-activity link, its type and its lag are invented.
- No activity or dependency is `OBSERVED`. The validator rejects an `OBSERVED` dependency.

`confidence_or_support` for a DERIVED concept is `EXPLICIT_PASSAGE` (a recorded passage states the concept directly) or
`FRAGMENTARY` (assembled from separate passages). These labels are my reading of the passages recorded in the project's
evaluation outputs, not human-annotated ground truth.

## Structure

### Workstreams, IMP events and DSM nodes

| IMP event | Activities | Workstream(s) | DSM node(s) | Baseline complete (workday) |
|---|---|---|---|---|
| IMP-01 Requirements Baseline Established | A100-A115 | Requirements / KPPs | D1 | 50 |
| IMP-02 Air Vehicle Design Maturity Achieved | A120-A145 | Air Vehicle Design / Weight | D2, D3 | 150 |
| IMP-03 Mission-System Integration Baseline Ready | A200-A230 | Mission-System Software | D4 | 216 |
| IMP-04 Test-Aircraft Readiness Achieved | A300-A325 | Test-Aircraft Availability | D5 | 220 |
| IMP-05 Development Flight-Test Entry Criteria Met | A400, A405 | Flight-Test Execution | D6 | 225 |
| IMP-06 Flight-Test Maturity Demonstrated | A410-A430 | Flight-Test Execution; Rework (A420); Dev / Test Maturity (A430) | D6, D7 | 330 |
| IMP-07 Development / Production Readiness Assessed | A500, A505, A510 | Production Commitment; Dev / Test Maturity (A510) | D8 | 340 |
| IMP-08 Controlled Production Configuration Released | A515, A520 | Rework (A515); Production Commitment | D8 | 355 |

DSM nodes: D1 Requirements / KPP Definition; D2 Air Vehicle Design Maturity; D3 Weight / Structural Maturity
(A125-A135); D4 Mission-System Software Maturity; D5 Test-Aircraft Availability; D6 Flight-Test Execution
(A400-A425); D7 Development / Test Maturity (A430); D8 Production Commitment / Rework Exposure (A500, A505, A510,
A515, A520; A510 moved here in v1.1). The DSM itself is built separately; see `outputs/dsm/dsm_summary.md`.

### Schedule conventions

- Time is in relative workdays from synthetic day 0; `finish = start + duration`. No calendar dates are used.
- All links are finish-to-start with zero lag in the baseline.
- `baseline_start` / `baseline_finish` come from a forward pass over the synthetic durations, and
  `baseline_total_float` from a backward pass against the network finish. The validator recomputes both.
- The schedule is a plan, not a status: `percent_complete` is 0 and forecast equals baseline.
- `risk_state` (LOW / MEDIUM / HIGH) and `maturity_indicator` are synthetic labels.
- The network has one start (A100) and one finish (A520), at workday 355.

**Critical path (baseline):** A100 → A105 → A110 → A115 → A120 → A125 → A130 → A135 → A140 → A145 → A305 → A310 → A315 →
A320 → A325 → A405 → A410 → A415 → A420 → A425 → A430 → A510 → A515 → A520 (355 workdays). The design / weight chain feeds
test-aircraft configuration (A145 → A305), so the **test-aircraft path controls A405** (A325 finishes at 220, float 0).

| Path into A405 | Arrives at | Total float |
|---|---|---|
| Test aircraft (A325) | 220 | 0 (controls A405) |
| Mission-system software (A230) | 216 | **4** (near-critical) |
| Flight-test planning (A400) | 70 | 150 |

Long-lead commitment (A505) finishes at 185, about 145 workdays before the maturity assessment that A510 also waits for
(float 145). This is the deliberate development-production concurrency of the baseline.

## Design rationale (pre-freeze v1.0 calibration)

Three design corrections were made after review, before v1.0 was frozen. **Every numerical value in them is a
SYNTHETIC experimental assumption** selected for the proof of concept. None is historically derived, and none
reproduces F-35 schedule performance. No evidence-derived relationship was changed to make them.

**A. Why the software path is deliberately near-critical.** In the first draft the software chain reached A405 with 30
workdays of float. DISTURBANCE_1 (A210 +8) would have been absorbed with no downstream effect, and INTERVENTION_1 (the
4-workday recovery) could not have shown any value. The primary predictive demonstration is software maturity → flight
test (Q01), so the software path should be close to controlling the gate without already controlling it. The smallest
change was one synthetic duration: **A205 Develop Mission-System Software Increment, 40 → 66 workdays**. No logic
changed. A230 now has **4 workdays of total float**. An 8-workday A210 slip consumes the 4 and then begins to propagate,
and the 4-workday recovery acts on the propagating part. The program finish (355) and critical path are unchanged.

**B. Why flight-test resequencing does not bypass the readiness gate.** A405 Development Test Readiness Review is a gate.
It keeps all its predecessors (A400, A230, A325) in every scenario, and the validator enforces this. The first draft
let A405 start before A325 finished; that is removed. INTERVENTION_2 now acts only *after* readiness. Flight-test
content that does not need the delayed mission-system capability is flown first while the affected content waits.
This is encoded as a simulator parameter, `delay_absorption_days = 4`, on the A410 flight-test block. It absorbs up to 4
workdays of the delay that reaches A410 and does not change any predecessor.

**C. Why staged production commitment preserves concurrency.** The baseline intentionally keeps development-production
concurrency (A505 is not gated on A430), as described by the Q08 evidence. The first draft's INTERVENTION_3 added
A430 → A505, which removed that concurrency. It is replaced by a policy: **40%** of the modeled long-lead commitment
may be made before A430 Development / Test Maturity, and the remaining **60%** is gated on A430. Concurrency remains,
but pre-maturity exposure is reduced. The later simulator can then compare full concurrent commitment (BASELINE, 100%
before maturity) with staged commitment. The 40/60 split is a synthetic policy assumption.

**D. All values are synthetic.** The A205 calibration (66), `delay_absorption_days` (4) and the commitment fractions
(0.40 / 0.60) are marked SYNTHETIC in `synthetic_scenarios.json` and in `design_calibrations` in
`synthetic_provenance.json`, and listed under `synthetic_values`.

## Evidence-derived dependency concepts

| Link (synthetic) | DSM | Case | Concept (DERIVED) | Support | Key evidence |
|---|---|---|---|---|---|
| A230 → A405 | D4 → D6 | Q01 | Software maturity → flight-test execution | EXPLICIT_PASSAGE | DOT&E FY2010 p.29; GAO-10-382 p.31 |
| A415 → A420 | D6 → D6 | Q01 | Discovery in flight test → corrective changes | FRAGMENTARY | DOT&E FY2010 p.33 |
| A425 → A410 (feedback) | D6 → D6 | Q01 | Regression results → further flight test | FRAGMENTARY | DOT&E FY2010 p.33 |
| A325 → A405 | D5 → D6 | Q04 | Test-aircraft availability → flight-test execution | EXPLICIT_PASSAGE | GAO-11-325 p.17, p.31; GAO-09-303 p.11 |
| A105 → A130 | D1 → D3 | Q07 | KPPs → weight-margin evaluation | FRAGMENTARY | GAO-05-271 p.10 |
| A130 → A135 | D3 → D3 | Q07 | Weight growth → redesign | EXPLICIT_PASSAGE | GAO-08-388 p.34 |
| A145 → A305 | D2 → D5 | Q07 | Redesign → test-aircraft configuration | FRAGMENTARY | GAO-06-356 p.14 |
| A135 → A515 | D3 → D8 | Q07 | Weight / redesign → cost-schedule exposure | EXPLICIT_PASSAGE | GAO-08-388 p.34 (GAO-11-325 p.40 differs) |
| A415 → A225 (feedback, v1.1) | D6 → D4 | Q01 | Test-discovered deficiencies → corrective software / integration work | FRAGMENTARY | DOT&E FY2010 p.33, p.29 |
| A430 → A510 | D7 → D8 (D7 → D7 in v1.0) | Q08 | Test maturity → production commitment | EXPLICIT_PASSAGE | GAO-07-360 p.7, p.22 |
| A420 → A515 | D6 → D8 | Q08 | Late test discovery → rework exposure | FRAGMENTARY | GAO-08-388 p.23 |

For context, the Agentic Phase 1 verdicts were Q01 PARTIALLY_SUPPORTED, Q04 UNRESOLVED (69.5) and Q08 UNRESOLVED
(65.5). Each was a single run near the threshold. Q07 was not run as an agentic case. The support labels above
describe the retrieved passages; they are not agentic verdicts and do not override them.

## Rework loop

Conceptually: flight-test execution → deficiency discovery → engineering / software correction → regression → flight
test. In the schedule, **A410 → A415 → A420 → A425** are all finish-to-start. There are two `FEEDBACK_REWORK` links:
- **A425 → A410** (D6 → D6): regression results lead to further flight test.
- **A415 → A225** (D6 → D4, added in v1.1): deficiencies discovered in flight test feed corrective software /
  integration work.

Both feedback links are recorded in `synthetic_dependencies.csv` but excluded from `predecessor_ids`. The baseline is a
single planned pass, so it stays acyclic and can be validated. Rework iterations are for the later simulation stage.

The validator requires:
- exactly these two feedback links, neither of them a scheduling predecessor;
- the forward path A410 → A415 → A420 → A425;
- `rework_indicator = LOOP` on the four loop members.

## Scenarios

All magnitudes, policy values and effects are **SYNTHETIC**. All outcomes are `NOT_COMPUTED`; no forward simulation
exists yet. There are two change types:
- `DURATION_DELTA` changes a synthetic duration.
- `POLICY` is a parameter for the later deterministic simulator, with its intended semantics written in the file.

No scenario may add, remove or re-lag a precedence link; the validator rejects any other change type.

| Scenario | Base | Change |
|---|---|---|
| BASELINE | none | none (full concurrent long-lead commitment) |
| DISTURBANCE_1 (Q01) | BASELINE | A210 duration +8 (projected 8 workdays late) |
| DISTURBANCE_2 (Q04) | BASELINE | A305 duration +4 (projected 4 workdays late) |
| INTERVENTION_1 (Q01) | DISTURBANCE_1 | A210 duration -4 (software recovery recovers 4 workdays) |
| INTERVENTION_2 (Q01) | DISTURBANCE_1 | POLICY `FLIGHT_TEST_RESEQUENCING_AFTER_READINESS`: gate A405 unchanged; on A410, `delay_absorption_days = 4` |
| INTERVENTION_3 (Q08) | BASELINE | POLICY `STAGED_PRODUCTION_COMMITMENT`: A505 commitment, gate A430, `pre_maturity_commitment_fraction = 0.40`, `post_maturity_commitment_fraction = 0.60` |

Intended simulator semantics, as recorded in the scenario file:
- **INTERVENTION_2.** If A410 starts d workdays late, it finishes `max(0, d - 4)` workdays late.
- **INTERVENTION_3.** Rework exposure before A430 applies to 40% of the A505 commitment; the other 60% is committed when
  A430 finishes. Rework and cost effects are not modeled.

How the policies were applied in the frozen intervention comparison (`outputs/simulation/`; decided after this baseline
was frozen, without changing the scenario file):
- **INTERVENTION_2:** a cumulative absorption capacity of 4 workdays (1.0 normalized WTM unit) at D6 over the whole
  trajectory. It never resets.
- **INTERVENTION_3:** evaluated against DISTURBANCE_1. It splits D8 exposure into 40% committed before maturity and 60%
  gated, with upstream propagation unchanged.

## Validation

`ppm_agent.synthetic.validation.validate_dataset` checks, deterministically:

- exactly 35 activities, 8 IMP events and 8 DSM nodes;
- unique activity, IMP, DSM and dependency ids;
- all predecessor, IMP and DSM references exist, and every IMP event, DSM node and workstream is used;
- no orphans: a single start and finish, and every activity on a start → finish path;
- no duplicate dependencies, and the dependency file matches the predecessor and successor lists exactly;
- provenance classes are valid and not blurred (see the rules above);
- an acyclic network whose dates match a forward pass and whose floats match a backward pass, with IMP completion dates
  consistent with the IMS;
- the synthetic calibration: A230 total float 4, and A325 float 0 (it controls A405);
- the readiness gate: A405 keeps predecessors A400, A230 and A325;
- concurrency retained: A505 does not depend on A430, directly or indirectly;
- the rework loop and both feedback links as described above;
- the v1.1 abstraction boundary: A430 in D7, A510 in D8, and A430 → A510 mapped to D7 → D8;
- the `freeze` record matches the files (counts, floats, the 355-workday duration);
- scenarios:
  - exactly the six ids, with valid base chains;
  - only `DURATION_DELTA` and `POLICY` changes, referencing existing activities;
  - positive resulting durations;
  - commitment fractions in [0, 1] that sum to 1;
  - the frozen values: A210 +8, A305 +4, A210 -4, `delay_absorption_days` 4, and 0.40 / 0.60.

`tests/test_synthetic_baseline.py` checks the committed files and breaks each rule once to confirm it is enforced. The
tests make no API calls.

## Limitations

- Observed evidence is summarized from the project's evaluation outputs. Page numbers are as recorded there and were
  not re-checked against the PDFs.
- Durations are illustrative, not calibrated to real program data.
- The 4-workday software float is a synthetic calibration chosen to make the Q01 scenarios decision-relevant. It is not
  an evidence finding.
- The weight re-plan cost differs between GAO-08-388 ($10 billion) and GAO-11-325 ($7 billion). Neither is used
  quantitatively.
- A510 sits in the Development / Test Maturity workstream but in the D8 DSM node. Workstream and DSM node are
  separate classifications, and v1.1 changed only the node.
- This document covers the baseline only. The DSM, WTM, schedule-to-WTM mapping and predictive simulation are built
  from it by separate scripts (`scripts/build_dsm.py`, `build_wtm.py`, `build_scenario_mapping.py`,
  `build_trajectory_simulation.py`); see [`technical_freeze.md`](technical_freeze.md).
