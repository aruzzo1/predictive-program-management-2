# Predictive Program Management 2.0: technical freeze

> **Technical feature development for the capstone is complete. Subsequent work is limited to documentation,
> requirements traceability, repository cleanup, presentation preparation and submission packaging.**

Frozen on 2026-11-06. Environment: `.venv`, Python 3.12.14. 22 artifacts are SHA-256 pinned in
`src/ppm_agent/safety/safety_guardrails.py` (`FROZEN_BASELINE_SHA256`) and verified byte-identical at freeze:
**22 / 22 unchanged.**

This is an illustrative capstone. Its program data are a synthetic, evidence-calibrated IMP/IMS, not an actual or
reconstructed F-35 contractor schedule. Its results do not predict historical or actual F-35 outcomes.

## A. RAG / evidence layer

- **Public evidence corpus:**
  - 10 public documents: 8 GAO reports (GAO-02-39, 05-271, 06-356, 07-360, 08-388, 09-303, 10-382, 11-325) and 2 DOT&E
    F-35 chapters (FY2010, FY2024);
  - manifest: `data/metadata/expanded_corpus_v2.json`. The per-file corpus-review decision records are kept locally
    and are not distributed with the public repository.
- **Index:**
  - 848 chunks in Chroma, embedded with all-MiniLM-L6-v2;
  - 220-token chunks with 35-token overlap;
  - frozen as RAG_EXPANDED_V2 (`data/metadata/rag_expanded_v2_freeze.json`, with a content hash).
- **Provenance:**
  - every chunk carries document id, organization, PDF page, printed page and section type;
  - publication date / reporting period metadata;
  - temporal eligibility so that a date-bounded query excludes later sources.
- **Retrieval and evaluation:**
  - 13 evaluation questions (`data/metadata/rag_evaluation_questions.json`);
  - baseline, hygiene and expanded-corpus evaluations, plus a semantic / BM25 / hybrid / hybrid-reranked comparison
    (`outputs/evaluation/rag_*`, `docs/rag_evaluation_plan.md`, `docs/retrieval_ranking_experiment.md`);
  - HYBRID_RERANKED_V2_1 is used by the agents.
- **Status:** frozen.

## B. Evidence and Dependency Agent

- **Evidence-grounded dependency reasoning:**
  - a bounded Tree-of-Thought controller (successors 3, beam 3, depth 3, threshold 70, budget 20) with a generator and
    an individual critic (weights 30/30/20/20);
  - one advisory comparative review of the survivors;
  - LangGraph orchestration with a shared structured state (`ReasoningState`).
- **Validation:** deterministic Python owns the hard constraints. Critic claims are advisory, and any disagreement with
  Python is recorded.
- **Real episodes:** three, with gpt-4o-mini at temperature 0:
  - Q01: PARTIALLY_SUPPORTED;
  - Q04: UNRESOLVED (69.5, threshold 70);
  - Q08: UNRESOLVED.
- **Traces:** `outputs/agentic_traces/episode_*`; summary in `outputs/evaluation/agentic_phase1_three_case_summary.md`.
- **Status:** frozen.

## C. Synthetic program baseline (v1.1)

- **Size:** 8 IMP events, 35 IMS activities, 8 DSM nodes, 43 dependencies (41 finish-to-start and 2 rework feedback),
  6 scenarios / policies.
- **Schedule:** 355-workday baseline; A230 total float 4, A325 total float 0.
- **Provenance:** OBSERVED (evidence register), DERIVED (11 dependency concepts and the DSM node groupings) and SYNTHETIC
  (all activities, durations, links, scenarios and policy values).
- **Versioning:** v1.0 archived unchanged in `data/synthetic/archive/v1.0/`. v1.1 is a structural revision: the A415 ->
  A225 rework feedback, and A510 moved to D8.
- **Documents:** `docs/synthetic_program_baseline.md`, `data/synthetic/`.
- **Status:** frozen.

## D. DSM

- **Matrices:** binary and weighted, 8 x 8. Row = source, column = target. 16 nonzero cells. Weights are ordinal
  evidence tiers (0.25 / 0.50 / 0.75 / 1.00); an agentic decision, where one exists, governs the weight.
- **Coupled blocks:** {D2, D3} and {D4, D6}, including the D6 self-loop. D8 is a terminal sink.
- **Outputs:**
  - `outputs/dsm/`, with full provenance per cell;
  - visualization package in `outputs/dsm_visualization/` (heatmaps, network, `dsm_explained.md`).
- **Status:** frozen.

## E. WTM / weighted propagation

- **Illustrative Work Transformation / Weighted Propagation Matrix:** W is the frozen weighted DSM, unchanged.
- **Propagation equation:** x(t+1) = Wᵀ x(t).
- **Eigenvalues:** 0.9114 and -0.4114 (the D4/D6 block), ±0.25 (the D2/D3 block), and four zeros.
- **Spectral radius:** 0.9114, so propagation decays in the long run. There is a short-run rise at t2, because D6's
  out-strength is 1.75.
- **Outputs:** `outputs/wtm/`.
- **Status:** frozen.

## F. Schedule-to-WTM mapping

- **Exposed delay:** max(0, gross slip - recovery - total float).
- **Normalization:** synthetic, 4 exposed workdays = 1.0.
- **Mappings:**
  - DISTURBANCE_1 → D4 = 1.0;
  - DISTURBANCE_2 → D5 = 1.0;
  - INTERVENTION_1 → 0.
- **Output:** `outputs/simulation/scenario_mapping.json`.
- **Status:** frozen.

## G. Predictive simulation

- **Setup:** common DISTURBANCE_1 (D4 = 1.0), horizon t0 to t12.
- **No action:** peak 1.3125 at t2; cumulative total 10.414.
- **Interventions:**
  - INTERVENTION_1 (software recovery): eliminates exposure before propagation;
  - INTERVENTION_2 (resequencing): its cumulative 1.0 capacity absorbs the 0.75 arriving at D6, leaving 0.25 unused;
  - INTERVENTION_3 (staged commitment): upstream propagation unchanged; committed pre-maturity D8 exposure 60% lower.
- **Comparison:** deterministic, with no composite score.
- **Outputs:** `outputs/simulation/` (trajectories, comparison, summary, figure).
- **Status:** frozen.

## H. Predictive Simulation and Intervention Agent

- **Design:** interprets the frozen comparison through one structured call. Python supplies and validates every number
  and every structured claim.
- **Real episodes:** three, with gpt-4o-mini at temperature 0, under contracts v1, v2 and v3. Their validators recorded
  **6**, **5** and **17** validation errors. Episode 3 had 17, not 18 as an earlier report said.
- **Outcome:** all three ended COMPLETED_WITH_VALIDATION_ERRORS, so **none was usable downstream**. The traces are
  preserved and hash-pinned.
- **Documents:** `docs/predictive_intervention_agent_contract.md`,
  `outputs/evaluation/predictive_intervention_validation_comparison.md`.
- **Status:** contract v3 frozen; no further runs.

## I. Module 6 safety layer

- **Routing:** deterministic, over five routes (SAFE_ADVISORY, HUMAN_REVIEW_REQUIRED, BLOCKED_VALIDATION_FAILURE,
  ESCALATE_HIGH_IMPACT, FAILED). Model confidence is logged but never read by routing.
- **Guardrails:** G1–G10, covering provenance, numerical authority, qualitative and objective consistency, baseline
  integrity, bounded tool access, coverage, consequence, failed validation and confidence.
- **Multi-metric evaluation:** correctness / groundedness, calibration / uncertainty, robustness and efficiency, with
  no composite score.
- **Result:** all three real episodes were BLOCKED_VALIDATION_FAILURE, so **unsafe_downstream_releases = 0**. In the
  fault-injection matrix every injected fault was blocked.
- **Human review:** required for every episode in this synthetic capstone.
- **Output:** `outputs/safety/`.

## J. Human review

- **Episodes reviewed:** 3. Rejected: **3**. Approved as advisory: 0. Revise and rerun: 0. Escalated: 0.
- **Released downstream:** 0.
- **Scope:** the rejection covers only the LLM-generated interpretations. The deterministic analytical results remain
  authoritative.
- **Records:**
  - `outputs/safety/human_review_records_reviewed.json` and `human_review_summary.md`;
  - the original PENDING records are preserved unchanged.
- **Final safety chain for the real episodes:** LLM interpretation → validation failure → BLOCKED_VALIDATION_FAILURE →
  human review → REJECTED.

## K. Testing

**327 tests, all passing:** the 322 from Module 6 plus 5 human-review-disposition tests. No test calls a live API.
Every analytical layer has a `--check` rebuild that confirms its outputs are reproducible byte for byte:
- `build_synthetic_baseline`;
- `build_dsm` and `build_dsm_visualization`;
- `build_wtm`;
- `build_scenario_mapping`;
- `build_trajectory_simulation`;
- `build_safety_evaluation`;
- `record_human_review`.

## L. Known limitations

- **The IMP/IMS is synthetic.** Activities, durations, links, scenarios and intervention magnitudes are synthetic.
- **WTM weights are ordinal evidence tiers** used as propagation coefficients, not calibrated probabilities or rework
  fractions.
- **There is no historical F-35 calibration,** and the results do not predict F-35 outcomes.
- **Propagation is simplified:** linear, deterministic and time-invariant, with a fixed horizon.
- **Real LLM episodes are few:** three for the interpretation agent and three for the evidence agent, each a single
  run. That is not statistically sufficient to estimate model reliability.
- **The validators cannot detect every possible prose error.** The narrative and prose rules are narrow and
  keyword-based.
- **The 4-day normalization is a synthetic constant.**
- **Agentic evidence decisions** were single runs near the threshold (Q01 partial; Q04 and Q08 unresolved).
- **Coordination is partial:** the supervisor agent is a placeholder, and the layers are linked by scripts rather than
  one end-to-end graph.
- **Human review remains necessary** for every result.
