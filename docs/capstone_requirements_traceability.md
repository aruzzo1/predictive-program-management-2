# Capstone requirements traceability

Grading-oriented map from course concepts to implementation and evidence.

- **COMPLETE:** an implementation and an output artifact exist.
- **PACKAGING REMAINS:** depends on the README, the public repository, the final write-up or the video.
- **TBD:** a location in the final write-up / video not yet assigned.

See `docs/technical_freeze.md` for the frozen state.

| Requirement / course concept | Implementation | Evidence / output artifact | Status | Final write-up / video location |
|---|---|---|---|---|
| Basic LLM interaction | OpenAI Responses API adapter at temperature 0; grounded retrieval agent | `src/ppm_agent/agents/llm.py`, `agents/retrieval_agent.py`, `notebooks/rag_prototype.ipynb` | COMPLETE | TBD |
| Tool use | Agents invoke deterministic tools: retrieval, and the frozen DSM / WTM / simulation outputs. No LLM function-calling | `src/ppm_agent/tools/` (retrieval, DSM, WTM, scenario mapping, simulation), `agents/retrieval_agent.py` | COMPLETE (see coverage check: needs clearer documentation) | TBD |
| Structured outputs | Pydantic schemas parsed with strict structured output | `src/ppm_agent/models/dependency.py`, `models/intervention.py`, `tests/test_llm_provider.py` | COMPLETE | TBD |
| RAG / evidence grounding | Chroma index over the public GAO / DOT&E corpus; hybrid reranked retrieval; grounded prompts with page citations | `data/metadata/expanded_corpus_v2.json`, `data/metadata/rag_expanded_v2_freeze.json`, `src/ppm_agent/retrieval/` | COMPLETE | TBD |
| Provenance | Chunk-level provenance; OBSERVED / DERIVED / SYNTHETIC classes; DSM cell provenance; trace input hashes | `data/metadata/JSF_Data_Link_Provenance.csv`, `data/synthetic/synthetic_provenance.json`, `outputs/dsm/dsm_provenance.json` | COMPLETE | TBD |
| Retrieval evaluation | 13 evaluation questions; baseline / hygiene / expanded-corpus and ranking comparisons | `outputs/evaluation/rag_*`, `docs/rag_evaluation_plan.md`, `docs/retrieval_ranking_experiment.md` | COMPLETE | TBD |
| Tree-of-Thought / bounded reasoning | Bounded ToT controller: successors, beam, depth, threshold, budget, stop conditions | `src/ppm_agent/agents/tot.py`, `outputs/agentic_traces/episode_*`, `tests/test_agentic.py` | COMPLETE | TBD |
| Generator / critic reasoning | Generator, individual critic and advisory comparative review; Python-computed totals | `agents/generator.py`, `agents/critic.py`, `outputs/evaluation/agentic_phase1_three_case_summary.md` | COMPLETE | TBD |
| Deterministic validation | Python-owned hard constraints (evidence agent); validation contracts v1–v3 (interpretation agent); validator for every analytical layer | `agents/validation.py`, `agents/predictive_intervention.py`, `synthetic/validation.py`, `tools/dsm_tools.py`, `tools/wtm_tools.py` | COMPLETE | TBD |
| Multi-agent architecture | Role-separated agents: retrieval, generator, critic, Evidence and Dependency Agent, Predictive Simulation and Intervention Agent. The supervisor is a placeholder | `src/ppm_agent/agents/`, `agents/supervisor.py` (placeholder) | COMPLETE (see coverage check: no supervisor routing) | TBD |
| LangGraph coordination | LangGraph graph for the evidence agent's ToT episode (retrieve → generate → validate → critic → prune → decide → trace) | `agents/graph.py`, `tests/test_agentic.py` | COMPLETE (see coverage check: scope is the evidence agent) | TBD |
| Shared structured state | `ReasoningState` Pydantic state carried through the graph and serialized as the trace | `models/dependency.py`, `outputs/agentic_traces/episode_*.json` | COMPLETE | TBD |
| DSM | Deterministic 8 x 8 binary DSM built from the dependency registry | `outputs/dsm/binary_dsm.csv`, `tools/dsm_tools.py`, `tests/test_dsm.py` | COMPLETE | TBD |
| Weighted DSM | Ordinal evidence-tier weights; agentic decisions govern; max aggregation | `outputs/dsm/weighted_dsm.csv`, `outputs/dsm_visualization/` | COMPLETE | TBD |
| WTM / propagation | Illustrative WTM; x(t+1) = Wᵀx(t) | `outputs/wtm/`, `tools/wtm_tools.py`, `tests/test_wtm.py` | COMPLETE | TBD |
| Eigenstructure | Eigenvalues by strongly connected block, cross-checked against the full matrix; dominant mode | `outputs/wtm/eigenvalues.json`, `outputs/wtm/structural_analysis.json` | COMPLETE | TBD |
| Convergence analysis | Spectral radius 0.9114 (decay); transient growth; closed-form cumulative totals | `outputs/wtm/wtm_summary.md`, `outputs/wtm/software_disturbance_propagation.csv` | COMPLETE | TBD |
| Synthetic IMP/IMS | Evidence-calibrated synthetic baseline v1.1 (8 IMP, 35 IMS, 43 dependencies), versioned and frozen | `data/synthetic/`, `docs/synthetic_program_baseline.md` | COMPLETE | TBD |
| Forward-looking prediction | Deterministic trajectories t0 to t12 from a schedule disturbance (illustrative; not an F-35 forecast) | `outputs/simulation/predictive_trajectories.csv`, `predictive_simulation_summary.md` | COMPLETE | TBD |
| Scenario generation | 6 synthetic scenarios / policies; schedule-to-WTM mapping | `data/synthetic/synthetic_scenarios.json`, `outputs/simulation/scenario_mapping.json` | COMPLETE | TBD |
| Intervention comparison | Four cases compared on separate metrics, with no composite score | `outputs/simulation/intervention_comparison.json`, `outputs/simulation/intervention_comparison.csv`, `trajectory_comparison.png` | COMPLETE | TBD |
| Verification / convergence | Layer validators and `--check` rebuilds; spectral-radius convergence; hash-pinned frozen artifacts | `scripts/build_*.py --check`, `FROZEN_BASELINE_SHA256` | COMPLETE | TBD |
| Guardrails | Module 6 guardrails G1–G10 and deterministic routing | `src/ppm_agent/safety/`, `outputs/safety/safety_policy.json` | COMPLETE | TBD |
| Correctness / groundedness evaluation | Citation, numeric, qualitative, objective, narrative and coverage metrics | `outputs/safety/safety_evaluation.json` (correctness_groundedness) | COMPLETE | TBD |
| Calibration / uncertainty evaluation | Confidence logged separately from correctness; unresolved evidence; human-review rate | `safety_evaluation.json` (calibration_uncertainty) | COMPLETE | TBD |
| Robustness evaluation | Three real failure patterns detected and withheld; fault-injection matrix; unsafe_downstream_releases = 0 | `safety_evaluation.json` (robustness), `safety_evaluation_summary.md` | COMPLETE | TBD |
| Efficiency evaluation | Model calls, latency and tokens, reported separately | `safety_evaluation.json` (efficiency) | COMPLETE | TBD |
| Human intervention | Human-review records; 3 episodes reviewed and REJECTED; originals preserved | `outputs/safety/human_review_records_reviewed.json`, `human_review_summary.md` | COMPLETE | TBD |
| Bounded autonomy | Agents read / interpret / recommend only; tool access bounded; deterministic validation and human review govern trust | `authorize_agent_action`, `safety_flow.png`, `human_review_summary.md` | COMPLETE | TBD |
| Safety escalation | ESCALATE_HIGH_IMPACT route for consequential actions; high-impact action catalogue | `src/ppm_agent/safety/safety_guardrails.py`, `outputs/safety/safety_policy.json` | COMPLETE | TBD |
| Synthetic-data transparency | Required statements in every synthetic output; OBSERVED / DERIVED / SYNTHETIC labels | `data/synthetic/synthetic_provenance.json`, all summaries | COMPLETE | TBD |
| Auditability / traces | JSON and Markdown traces for every real agent episode; raw responses preserved, never repaired; hash-pinned | `outputs/agentic_traces/`, `outputs/evaluation/` | COMPLETE | TBD |
| Reproducibility | Deterministic builds with byte-identical `--check`; pinned environment (Python 3.12, `requirements.txt`) | `scripts/*.py --check`, `pyproject.toml`, `requirements.txt` | COMPLETE | TBD |
| Automated testing | 327 pytest tests, no live API calls | `tests/` | COMPLETE | TBD |
| Public GitHub deliverable | Repository prepared but not yet published: README rewritten, `.gitignore` curated, public manifest written; the folder is not yet a git repository | `README.md`, `.gitignore`, `docs/public_repository_manifest.md`, `docs/repository_cleanup_report.md` | PACKAGING REMAINS | TBD |
| Final video / presentation | Not yet produced | (none yet) | PACKAGING REMAINS | TBD |

## Capstone requirement coverage check

**Fully satisfied** (implementation, artifacts and tests):
- **Evidence and reasoning:** basic LLM interaction, structured outputs, RAG / evidence grounding, provenance, retrieval
  evaluation, Tree-of-Thought / bounded reasoning, generator / critic reasoning, deterministic validation, shared
  structured state.
- **Program model and prediction:** DSM, weighted DSM, WTM / propagation, eigenstructure, convergence analysis,
  synthetic IMP/IMS, forward-looking prediction (illustrative), scenario generation, intervention comparison,
  verification / convergence.
- **Safety and evaluation:** guardrails, correctness / groundedness, calibration / uncertainty, robustness and
  efficiency evaluation, human intervention, bounded autonomy, safety escalation.
- **Engineering practice:** synthetic-data transparency, auditability / traces, reproducibility, automated testing.

**Satisfied technically, but needing clearer documentation in the write-up:**
- **Tool use.** Agents invoke deterministic Python tools (retrieval and the frozen analytical outputs); the LLM does
  not call tools through function calling. The write-up should describe tool use in those terms.
- **Multi-agent architecture.** The agents are role-separated (retrieval, generator, critic, evidence agent,
  interpretation agent), but `agents/supervisor.py` is an unimplemented placeholder; its docstring now says so
  explicitly. The write-up should not claim supervisor-based routing.
- **LangGraph coordination.** LangGraph orchestrates the evidence agent's ToT episode. The pipeline from evidence to
  DSM, WTM, simulation, the interpretation agent and the safety layer is linked by deterministic scripts, not one
  LangGraph graph. The write-up should state this scope precisely.
- **Forward-looking prediction.** This must be presented as an illustrative test harness on synthetic data, not an
  F-35 forecast.

**Dependent on final packaging:**
- the public GitHub repository: the folder is not yet under git; repository contents are prepared (README rewritten,
  `.gitignore` curated, cleanup done; see `docs/repository_cleanup_report.md`);
- the final write-up, with every TBD column above to be filled in;
- the final video / presentation.

**Genuine gaps** (reported, not implemented):
- **No implemented supervisor / cross-agent router,** and no single end-to-end LangGraph across all layers. Whether
  this matters depends on how the course defines "multi-agent coordination". The current architecture coordinates
  through structured artifacts and deterministic validation.
- **No VALIDATED real interpretation-agent output.** All three real episodes were withheld. This is presented as
  safety evidence, not as an analytical gap: the deterministic results stand on their own.
- **No LLM function-calling (tool-calling) loop.** If the course requires model-initiated tool calls specifically,
  that is not implemented.
