# Predictive Program Management 2.0

A capstone research prototype that combines retrieval-augmented generation (RAG), bounded agentic reasoning,
Design Structure Matrix (DSM) / Work Transformation Matrix (WTM) analysis and deterministic simulation for predictive
analysis of complex engineering programs. The case study is the F-35 / Joint Strike Fighter development program,
using public GAO and DOT&E reports.

## Overview

The capstone explores whether modern RAG, agentic AI, DSM/WTM analysis and deterministic simulation can reduce the
manual knowledge-engineering effort that predictive analysis of a complex engineering program normally requires.

> **The LLM does not predict the program. The agents construct, interrogate, and adapt the predictive model.**

Language models retrieve and interpret evidence and propose dependency hypotheses. Deterministic Python validates
those outputs, builds the matrices, runs the propagation and simulation, and decides what may be exposed downstream.
Humans keep authority over consequential decisions.

## Problem Statement

The dependencies that drive cost, schedule and technical outcomes in large engineering programs are rarely recorded
in one place. They are scattered across audit reports, test reports and program documentation, are often stated
indirectly, and change over time. Turning that heterogeneous evidence into an explicit dependency model, and then
into forward-looking analysis, is slow manual work that depends on scarce expertise.

## Capstone Objective

The goal is preemptive: identify structural vulnerabilities in a program, simulate how a disturbance propagates
through its dependency structure, and evaluate management interventions before downstream cost, schedule or
technical failures occur.

## Architecture

```
Public Program Evidence (GAO / DOT&E reports)
  → RAG (hybrid / reranked retrieval with page-level provenance)
  → Evidence & Dependency Agent (bounded Tree-of-Thought: generator, critic, deterministic validation)
  → Validated Dependency Registry
  → DSM / Weighted DSM
  → Illustrative WTM / Weighted Propagation Model
  → Synthetic Program State (evidence-calibrated synthetic IMP/IMS)
  → Deterministic Predictive Simulation
  → Intervention Comparison
  → Predictive Simulation & Intervention Agent
  → Deterministic Validation
  → Safety Routing (Module 6)
  → Human Review
```

- **LangGraph** is used within the Evidence and Dependency reasoning workflow (`src/ppm_agent/agents/graph.py`).
- **Later stages** are coordinated by deterministic Python scripts and structured artifacts (`scripts/`, `outputs/`).
- **A unified cross-agent supervisor is not implemented** and remains future work (`agents/supervisor.py` is a
  documented placeholder).

## Implemented Capabilities

**Evidence and reasoning**
- **Public-source RAG with provenance:** 10 documents, 848 chunks, page-level citations and temporal metadata.
- **Retrieval:** hybrid / reranked (BM25 + semantic, reciprocal rank fusion, cross-encoder reranking), with date-bounded
  retrieval.
- **Bounded agentic reasoning** (Tree-of-Thought with beam, depth, threshold and budget limits) with a generator /
  critic structure.
- **Deterministic validation** of every agent output; Python owns the hard constraints.

**Program model and prediction**
- Synthetic IMP/IMS baseline (v1.1), versioned and hash-pinned.
- Binary and weighted DSM with per-cell provenance.
- WTM / weighted propagation with eigenvalue and spectral-radius analysis.
- Disturbance propagation and deterministic intervention comparison.

**Interpretation and safety**
- Agentic interpretation under explicit validation contracts (v1–v3).
- Module 6 safety routing with guardrails G1–G10, human review and multi-metric evaluation.

**Engineering practice**
- Reproducible automated tests and byte-identical rebuild checks.

## Synthetic Data and Provenance

The public record contains no contractor IMP/IMS, so the program state is synthetic. Every element carries one of three
provenance classes:

| Class | Meaning |
|---|---|
| **OBSERVED** | Directly supported by public F-35 source documentation (the evidence register). |
| **DERIVED** | An analytical dependency or relationship inferred from observed evidence. |
| **SYNTHETIC** | A duration, schedule position, activity structure, disturbance, intervention or simulated outcome created for the capstone demonstration. |

> **The synthetic IMP/IMS is not intended to recreate historical F-35 program data. It functions as a test harness for
> demonstrating how RAG, LLM, and agentic AI capabilities can construct, interrogate, and adapt a predictive
> program-management model when complete proprietary program data are unavailable.**

Details: [`docs/synthetic_program_baseline.md`](docs/synthetic_program_baseline.md).

## Predictive Demonstration

A mission-system software integration slip (A210, 8 workdays) is reduced to 4 exposed workdays by the available schedule
float, which becomes a normalized disturbance at D4 (Mission-System Software Maturity). It is then propagated for t0 to
t12 through the frozen WTM.

| Case | Mechanism | Result (normalized units) |
|---|---|---|
| No action | — | Peak 1.3125 at t2; cumulative total 10.414; slow decay (0.911 per step) |
| Intervention 1: software recovery | Prevents exposure: recovery fits inside the float | Nothing enters propagation; all metrics 0 |
| Intervention 2: flight-test resequencing | Absorbs disturbance at flight test (D6), cumulative capacity 1.0 | The 0.75 reaching D6 is fully absorbed and 0.25 of capacity is unused; this depends on the synthetic magnitude |
| Intervention 3: staged production commitment | Limits commitment at production (D8): 40% before maturity, 60% gated | Upstream propagation unchanged; committed pre-maturity exposure 60% lower (0.964 vs 2.410) |

The interventions act through different management mechanisms (prevention, downstream absorption, exposure
management). They are compared metric by metric and are **not** collapsed into one composite score. Details:
[`outputs/simulation/predictive_simulation_summary.md`](outputs/simulation/predictive_simulation_summary.md).

## Safety and Reliability

**Deterministic validation**
- Every agent output is checked by Python: provenance (fact-id citations must exist), numerical authority, qualitative
  and objective consistency, narrative consistency and coverage.
- The interpretation agent's schema contains no numeric fields; numbers come only from Python.

**Module 6 guardrails**
- Baseline integrity: 22 hash-pinned frozen artifacts.
- Bounded tool access: agents may only read, interpret and recommend.
- High-impact actions are escalated for explicit human approval.
- Model confidence is logged for evaluation only and never changes a route.

**Human review**
- Required for every result in this synthetic capstone.
- The three preserved real interpretation-agent episodes were all blocked and then REJECTED on human review.
- **0 unsafe downstream releases.**

> **The system did not make the language model reliable; it made unreliable model behavior observable, bounded, and
> preventable from propagating into consequential decisions.**

Details: [`outputs/safety/safety_evaluation_summary.md`](outputs/safety/safety_evaluation_summary.md),
[`outputs/safety/human_review_summary.md`](outputs/safety/human_review_summary.md).

## What Is Not Implemented

These are scoped limitations of the capstone, not defects:
- no unified cross-agent supervisor;
- no single end-to-end LangGraph graph; LangGraph covers the Evidence and Dependency workflow;
- no generalized LLM function-calling / tool loop; agents invoke deterministic Python tools;
- no autonomous program-management actions; the system is advisory;
- no historical F-35 schedule reconstruction;
- no historically calibrated WTM weights; they are ordinal evidence tiers;
- no system-dynamics (stock-and-flow) engine; propagation is a linear WTM model;
- no claim of predictive accuracy for real F-35 outcomes.

## Key Results

| Item | Value |
|---|---|
| Public evidence corpus | 10 documents (8 GAO, 2 DOT&E), 848 chunks |
| Synthetic baseline v1.1 | 8 IMP events, 35 IMS activities, 8 DSM nodes, 43 dependencies, 355-workday baseline |
| DSM | 8 x 8, 16 nonzero cells; coupled blocks {D2, D3} and {D4, D6}; D8 is a terminal sink |
| WTM spectral radius | 0.9114 (long-run decay) |
| Evidence and Dependency Agent (real runs) | Q01 PARTIALLY_SUPPORTED; Q04 UNRESOLVED; Q08 UNRESOLVED |
| Interpretation agent (real runs) | 3 episodes; 6, 5 and 17 validator errors; all withheld; 3 REJECTED on human review |
| Unsafe downstream releases | 0 |
| Automated tests | 327 passing (see Testing) |

## Repository Structure

```
data/
  metadata/      corpus manifests, evaluation questions, provenance tables, RAG freeze records
  synthetic/     synthetic IMP/IMS baseline v1.1 (and archive/v1.0)
  raw/, processed/, sample/   placeholders; source PDFs and the vector store are not distributed
docs/            architecture, design notes, contract, technical freeze, traceability (historical docs are labeled)
outputs/
  agentic_traces/      JSON / Markdown traces of every real agent episode
  evaluation/          RAG and agent evaluation reports
  dsm/, dsm_visualization/, wtm/   matrices, eigenstructure, figures
  simulation/          scenario mapping, trajectories, intervention comparison
  safety/              Module 6 policy, evaluation, human-review records
scripts/         build / check entry points for every layer; agent run scripts
src/ppm_agent/
  ingestion/, retrieval/   corpus processing and RAG
  agents/                  evidence and dependency agent (ToT, LangGraph), interpretation agent, prompts
  models/                  Pydantic schemas
  synthetic/               synthetic baseline definitions and validator
  tools/                   deterministic DSM, WTM, mapping, simulation and visualization tools
  safety/                  Module 6 routing, guardrails, reporting
tests/           pytest suite (no live API calls)
```

## Reproducing the Demonstration

Requirements: Python 3.12 (`requires-python = ">=3.12,<3.13"`; do not use Python 3.14).

```powershell
<path-to-python-3.12>\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

Check every frozen deterministic layer in pipeline order. These need no API key and no source PDFs, and each confirms
its outputs match a fresh build byte for byte:

```powershell
.\.venv\Scripts\python.exe scripts\build_synthetic_baseline.py --check
.\.venv\Scripts\python.exe scripts\build_dsm.py --check
.\.venv\Scripts\python.exe scripts\build_dsm_visualization.py --check
.\.venv\Scripts\python.exe scripts\build_wtm.py --check
.\.venv\Scripts\python.exe scripts\build_scenario_mapping.py --check
.\.venv\Scripts\python.exe scripts\build_trajectory_simulation.py --check
.\.venv\Scripts\python.exe scripts\build_safety_evaluation.py --check
.\.venv\Scripts\python.exe scripts\record_human_review.py --check
```

Optional steps, not part of the required reproduction:
- **Real agent episodes** need an OpenAI API key in `.env` (see `.env.example`). They are not rerun for reproduction:
  the preserved traces are the record, and rerunning would create new traces rather than reproduce the old ones.
- **Rebuilding the RAG index** needs the public source PDFs, which are not distributed (set `JSF_SOURCE_DIR`).

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

In the full local workspace, **327 tests pass**. In a clean public checkout, 324 pass and 3 are skipped:
- two check the real corpus manifests against local corpus-review records that are not distributed;
- one queries the local vector store, which is not distributed.

No test makes a live API call.

## Limitations

- The IMP/IMS is synthetic, including activities, durations, links, scenarios and intervention magnitudes.
- WTM weights are ordinal evidence tiers used as propagation coefficients, not calibrated probabilities.
- There is no historical F-35 calibration, and the results do not predict F-35 outcomes.
- Propagation is simplified: linear, deterministic and time-invariant, with a fixed horizon.
- Real LLM episodes are few (single runs), which is not statistically sufficient to estimate model reliability.
- Validators cannot detect every possible prose error; human review remains necessary.

Full list: [`docs/technical_freeze.md`](docs/technical_freeze.md).

## Future Work

- Unified supervisor / cross-agent orchestration.
- Richer probabilistic weighting of dependencies.
- Additional historical programs.
- Real IMP/IMS and earned-value (EVM) data.
- Expert validation of dependencies and interventions.
- Monte Carlo / probabilistic simulation.
- System-dynamics expansion.
- Broader agent reliability evaluation (more runs and models).

## Academic / Demonstration Use

This repository is a capstone / research prototype. It is **not** an operational acquisition or program-management
decision system, and its outputs must not be used as predictions of real program outcomes.

Further documentation: [`docs/technical_freeze.md`](docs/technical_freeze.md),
[`docs/capstone_requirements_traceability.md`](docs/capstone_requirements_traceability.md),
[`docs/architecture.md`](docs/architecture.md),
[`docs/public_repository_manifest.md`](docs/public_repository_manifest.md).
