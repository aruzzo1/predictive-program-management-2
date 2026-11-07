# Architecture

> **Scope.** This document details the evidence layers: ingestion, RAG and the Evidence and Dependency Agent. The
> downstream layers (synthetic baseline, DSM, WTM, mapping, simulation, interpretation agent, Module 6 safety) are
> summarized under "Downstream layers" below and documented in [`technical_freeze.md`](technical_freeze.md). LangGraph
> orchestrates the Evidence and Dependency reasoning workflow; later stages are coordinated by deterministic scripts
> and structured artifacts. A unified cross-agent supervisor is not implemented.

## Layers

| Layer | Package / file | Status |
|---|---|---|
| Configuration | `ppm_agent.config` | Implemented — settings from `.env` (paths, model, chunking, retrieval) |
| Corpus selection | `ppm_agent.ingestion.corpus_selection` | Implemented — manifest + `corpus_decisions.csv` (local corpus-review record, not distributed) + SHA-256 check |
| Discovery / dedup | `ppm_agent.ingestion.loaders` | Implemented — read-only discovery, exact-duplicate detection by SHA-256 |
| Page extraction / cleaning | `ppm_agent.ingestion.page_extraction` | Implemented — pypdf; layout-specific cleaning for GAO and DOT&E documents |
| Chunking | `ppm_agent.ingestion.chunking` | Implemented — token-aware, page- and section-bounded |
| Metadata helpers | `ppm_agent.ingestion.metadata` | Implemented — hashing, PDF title, conservative organization rules |
| Embeddings | `ppm_agent.retrieval.embeddings` | Implemented — local sentence-transformers model |
| Vector store | `ppm_agent.retrieval.vector_store` | Implemented — persistent Chroma, cosine distance |
| Retriever | `ppm_agent.retrieval.retriever` | Implemented — top-k search + near-duplicate suppression; optional `analysis_date` (date-bounded retrieval) |
| Temporal controls | `ppm_agent.retrieval.temporal` | Implemented — temporal_status and ELIGIBLE / INELIGIBLE / REQUIRES_REVIEW eligibility |
| Lexical retrieval | `ppm_agent.retrieval.lexical` | Implemented — in-house Okapi BM25 (k1 1.5, b 0.75), no dependency |
| Retrieval strategies | `ppm_agent.retrieval.strategies` | Implemented — semantic / BM25 / RRF hybrid / cross-encoder reranked hybrid benchmark API (RAG_RANKING_V2_1) |
| Retrieval agent | `ppm_agent.agents.retrieval_agent` | Written — single-shot grounded prompt / answer path; the final evidence-grounded LLM reasoning runs through the agentic layer below |
| Verifier | `ppm_agent.agents.verifier` | Implemented and unit-tested — rule-based coverage, citation and causal-language checks |
| Supervisor | `ppm_agent.agents.supervisor` | Placeholder only — proposed architecturally, not implemented within the capstone |
| Domain models | `ppm_agent.models` | Implemented — Pydantic Evidence, Activity, CandidateDependency, DependencyHypothesis, CriticAssessment, ReasoningState, DependencyDecision |
| Agentic dependency reasoning | `ppm_agent.agents.{evidence,generator,critic,validation,scoring,tot,graph,episode,llm}` | Implemented — MOCK_AGENT_MODE for tests; real REAL_LLM_MODE runs for Q01, Q04 and Q08 — see below |
| Tools | `ppm_agent.tools.{retrieval_tools,dsm_tools,dsm_visualization,wtm_tools,scenario_mapping,trajectory_simulation}` | Deterministic tools: retrieval wrapper, DSM, visualization, WTM, schedule-to-WTM mapping, trajectory simulation |
| Synthetic baseline | `ppm_agent.synthetic` | Implemented — synthetic IMP/IMS v1.1 definitions and validator |
| Interpretation agent | `ppm_agent.agents.predictive_intervention` | Implemented — Predictive Simulation and Intervention Agent, validation contract v3 |
| Safety | `ppm_agent.safety` | Implemented — Module 6 routing, guardrails G1–G10, human-review records, multi-metric evaluation |
| Utilities | `ppm_agent.utils.logging_utils` | Logger and JSON trace writer |

## Current data flow

```
JSF_SOURCE_DIR (read-only, outside repo)
  → ingestion.loaders           discover PDFs, SHA-256, flag exact duplicates
  → ingestion.corpus_selection  manifest documents (decisions allowed by the manifest + hash check):
                                prototype_v1 = 5 documents; rag_expanded_v2 = 10 documents (current)
  → ingestion.page_extraction   per-page text, cleaning, printed page, Highlights tagging
  → ingestion.hygiene           logged removal of administrative text; agency_comments tagging
  → ingestion.chunking          220-token chunks, 35-token overlap, one page per chunk
  → retrieval.embeddings        all-MiniLM-L6-v2 (local, 384-d, normalized)
  → retrieval.vector_store      Chroma collection "jsf_corpus" in data/processed/chroma (848 chunks, RAG_EXPANDED_V2)
  → retrieval.retriever         15 candidates → near-duplicate suppression → top 5
  → outputs/retrieval_traces/   JSON trace per query (scripts/run_retrieval.py)
  → agents.evidence             HYBRID_RERANKED_V2_1 evidence for the Evidence and Dependency Agent (below)
```

Entry points: `scripts/ingest_corpus.py`, `scripts/run_retrieval.py`, `scripts/run_rag_demo.py`.

## Result schema

Every retrieval result carries page-level provenance under these keys (the project-wide
standard; there is no `page` key):

`rank`, `original_rank` (deduplicated retrieval), `chunk_id`, `text`, `document_id`, `title`,
`organization`, `filename`, `pdf_page`, `printed_page` (None when unknown), `section_type`
(`highlights`, `agency_comments` or None), `distance`, `similarity`, `metadata`.

Temporal metadata (in `metadata`): `publication_date`, `publication_year`,
`publication_date_uncertain`, and for undated annual reports `reporting_period` and
`content_not_before` (a dated event in the text: the document cannot predate it). They support date-bounded retrieval
through the retriever's optional `analysis_date` (`ppm_agent.retrieval.temporal`: ELIGIBLE / INELIGIBLE /
REQUIRES_REVIEW).

Citations in the grounded prompt use `[filename, p. <pdf_page>]`, with the printed page shown
alongside when known.

## Agentic Dependency Reasoning Layer

```
User / Analytical Question
        |
        v
RAG Retrieval                    agents.evidence -> retrieval.strategies (HYBRID_RERANKED_V2_1, top 5)
        |
        v
Structured Evidence Objects      models.Evidence (E1..En, full provenance)
        |
        v
Thought Generator                agents.generator + prompts/generator.md (<= 3 hypotheses per expansion)
        |
        v
Candidate Dependency Hypotheses  models.DependencyHypothesis (DIRECT / INDIRECT / RECIPROCAL / NONE / UNCERTAIN)
        |
        v
Deterministic Validation         agents.validation (Python: citations exist and match retrieval,
        |                        activities valid, type valid, no duplicates, score bounds and arithmetic)
        v
Critic                           agents.critic + prompts/critic.md (30/30/20/20 weights; total computed in Python)
        |
        v
Bounded ToT Controller           agents.tot (3 successors, beam 3, depth 3, threshold 70, near tie 5, 20 calls)
        |                        orchestrated by plain Python or LangGraph (agents.graph), same steps
        v
Dependency Decision              models.DependencyDecision: SUPPORTED / PARTIALLY_SUPPORTED / NOT_SUPPORTED / UNRESOLVED
        |                        + trace in outputs/agentic_traces/ (JSON + Markdown)
        v
Validated dependency registry    -> DSM / WTM and downstream layers (implemented; see "Downstream layers")
```

**The LLM does not perform the DSM/WTM mathematics. Agents construct and validate the dependency
model; deterministic analytical tools perform downstream computation.**

- **Role separation.** The generator and critic have separate prompts, classes and LangGraph
  nodes. The critic recomputes its view from the evidence and never receives a score from the
  generator. The weighted total is computed in Python and re-checked by validation.
- **Hard constraints.** These reject a hypothesis regardless of score. Deterministic checks run
  before the critic (citations, retrieval match, activities, type, duplicates). Evidence-level
  checks belong to the critic (contradiction, traceability).
- **Decision rule.** This is an MVP rule, not taken from Checkpoint 4.1.
  - A positive hypothesis (DIRECT, INDIRECT or RECIPROCAL) that clearly leads scores SUPPORTED at
    80 or above and PARTIALLY_SUPPORTED between 70 and 80.
  - A near tie between two positive types is PARTIALLY_SUPPORTED: a dependency exists, but its type
    is unresolved.
  - A near tie between a dependency and NONE is UNRESOLVED.
  - A dominant NONE is NOT_SUPPORTED.
  - If no hypothesis survives, the decision is UNRESOLVED.
- **Stop statuses.** DOMINANT_CANDIDATE, NO_VIABLE_CANDIDATE, NO_NEW_CANDIDATES (every retained
  hypothesis has been expanded once without producing a new claim), DEPTH_LIMIT and
  BUDGET_EXHAUSTED.
- **LLM mode.** A real provider is used only if it is configured (client package installed and key
  set). Otherwise the system runs in **MOCK_AGENT_MODE**: rule-based stand-ins over generic text
  features (`agents.text_features`) that exercise the whole pipeline. Every mock hypothesis,
  assessment, trace and printout is labelled, and the mock output is not model reasoning. With a
  key set, the system runs in **REAL_LLM_MODE** (`agents.llm.OpenAIResponsesClient`): OpenAI
  Responses API, strict structured output into `GeneratorOutput` / `CriticOutput` (the
  model-fillable fields of `DependencyHypothesis` / `CriticAssessment`), temperature 0, responses
  not stored. Configuration errors abort the episode; per-call failures are logged and the
  hypothesis is dropped, never scored. First real run: Q01, `outputs/evaluation/agentic_q01_mock_vs_real.md`.
- **Validation ownership.** Deterministic Python validation owns every objectively verifiable hard
  constraint (citations exist and were retrieved, activities, relationship type, named mediator,
  schema, score range, duplicates) and alone sets `hard_constraint_pass` in REAL_LLM_MODE. The LLM
  critic owns qualitative evaluation (evidence strength, plausibility, contradictions, assumptions,
  usefulness) and expresses it only through scores. A critic's hard-failure claim is advisory
  (`critic_claimed_hard_failure`); any mismatch with Python is recorded as
  `critic_validation_disagreement` in the assessment, `state.critic_disagreements`, the events and the
  trace, and is never acted on. Model consistency is pinned to 50 in Python; the DSM was built afterwards, and the
evidence-agent episodes were not re-run against it. The
  mock critic's own rule-based hard failures remain binding in MOCK_AGENT_MODE.
  See `outputs/evaluation/agentic_q01_real_run1_vs_run2.md`.
- **Critic calibration and comparative review.** The critic scores documentary evidence against
  explicit anchors and returns an advisory `evidence_support_label` (DIRECTLY_STATED …
  UNSUPPORTED). After the search stops, `ToTController.decide` runs one comparative review of the
  surviving hypotheses (`prompts/comparative.md`, at most one model call, counted against the
  budget). It is advisory: Python discards a recommendation of a non-survivor, restores the
  individual assessments if they were touched, and keeps the verdict rule deterministic on the
  scores. Recorded as `state.comparative_review` and `comparative_model_call_count`.
  See `outputs/evaluation/agentic_q01_real_run2_vs_run3.md`.
- **CrewAI.** This is an **OPTIONAL FUTURE ROLE-ORCHESTRATION LAYER**, not used. Generator/critic
  separation is already expressed with separate prompts, classes and graph nodes, and CrewAI would
  add a framework without new capability at MVP scale.

Run: `python scripts/run_dependency_episode.py` (LangGraph) or `--python` (plain loop).

## Downstream layers (implemented after Agentic Phase 1)

```
Validated dependency registry (synthetic baseline v1.1: 35 activities, 43 dependencies)   ppm_agent.synthetic
  → DSM / weighted DSM (8 x 8, cell provenance)                                            tools.dsm_tools
  → Illustrative WTM / weighted propagation, x(t+1) = Wᵀ x(t); spectral radius 0.9114       tools.wtm_tools
  → Schedule-to-WTM mapping (exposed delay, synthetic 4-day normalization)                 tools.scenario_mapping
  → Deterministic predictive simulation and intervention comparison (t0..t12)              tools.trajectory_simulation
  → Predictive Simulation and Intervention Agent (one structured call; contract v3)         agents.predictive_intervention
  → Deterministic validation → Module 6 safety routing → human review                      safety.*
```

These stages are coordinated by deterministic scripts (`scripts/build_*.py`, `scripts/run_predictive_intervention_agent.py`,
`scripts/record_human_review.py`) and structured artifacts in `outputs/`. They are not part of a LangGraph graph. No
system-dynamics (stock-and-flow) model was implemented; propagation is the linear WTM model above. Details and results:
[`technical_freeze.md`](technical_freeze.md).

## Design principles

- **Source data is read-only.** The corpus is referenced by path, never modified.
- **Provenance everywhere.** Every chunk carries source file, document hash and page.
- **Controlled corpus.** Only documents with an approved decision and matching hash are indexed.
- **Deterministic where possible.** Numerical analysis (DSM, WTM, propagation, intervention comparison) is done by
  deterministic Python tools, never by the LLM.
- **Incremental.** Each milestone produces a working, testable slice.

## Dependencies

Current runtime requirements are in `requirements.txt` (read by `pyproject.toml`):
python-dotenv, pypdf, sentence-transformers, transformers, chromadb, pydantic, langgraph, openai
(REAL_LLM_MODE only), and pytest for the test suite. torch and numpy are installed as dependencies of sentence-transformers; pydantic as a
dependency of chromadb. None of the three is imported directly by project code.

RAG_RANKING_V2_1 added no package. The optional reranker uses the model
`cross-encoder/ms-marco-MiniLM-L-6-v2` through the already installed sentence-transformers; its
weights are downloaded once from Hugging Face and cached, like the embedding model.

The downstream layers use numpy (WTM eigenstructure and propagation) and the standard library (SVG figures). No
plotting package is required; PNG copies of figures are rasterized from SVG by an already-installed headless browser
when one is available.

## Candidate dependencies considered during development (historical)

These packages were considered at earlier milestones and are **not** runtime requirements. The final implementation
did not need them (numpy sufficed for the WTM; no system-dynamics library was adopted).

| Package | Phase | Purpose | Notes |
|---|---|---|---|
| `pymupdf` | RAG expansion | Test on the five letter-spaced browser re-saves | AGPL license; evaluate before adopting |
| `ocrmypdf` / `pytesseract` (+ Tesseract binary) | Later: OCR | `Ahern-report.pdf`, scanned pages of `CHRG-112hhrg73791.pdf` | OCR is out of scope for now |
| `cryptography` | Not needed | Was needed only to open `BoletinSumarios12.pdf` | That file has been removed from the corpus |
| `pydantic` (direct use) | **Now current** (Agentic Phase 1) | Typed domain objects (`ppm_agent.models`) | In requirements.txt |
| `pandas` | Corpus evaluation, DSM/WTM data handling | Tabular analysis | Removed from requirements; not used by current code |
| `langgraph` | **Now current** (Agentic Phase 1) | ToT graph: explicit state, nodes, routing, stop conditions | In requirements.txt (pulls langchain-core and 8 other packages); `langchain`, `langchain-community` and `langchain-text-splitters` remain unused |
| `crewai` | Optional future role-orchestration layer | Multi-agent roles | Not needed for the MVP |
| `scipy` | WTM eigenstructure | Eigen-decomposition beyond numpy | numpy may suffice |
| `networkx` | DSM | Dependency graphs, partitioning | |
| `matplotlib` | DSM/WTM/system-dynamics outputs | Plots | |
| A system-dynamics library (e.g., `pysd`) or plain numpy/scipy ODE integration | Predictive simulation | Stock-and-flow models | Choice open |
| `mcp` | MCP tool integration | Expose deterministic tools to agents | |
| `ipykernel` / `jupyter` | Optional | Run `notebooks/rag_prototype.ipynb` | Notebook is currently a placeholder |
