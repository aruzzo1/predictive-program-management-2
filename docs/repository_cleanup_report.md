# Repository cleanup report (submission packaging)

Date: 2026-11-06. Scope: cleanup, documentation alignment and public-repository readiness only. No features were added,
no LLM was run, and no frozen artifact was modified.

## Stale documentation updated

| Document | Change |
|---|---|
| `README.md` | Rewritten for the final, frozen capstone (see below). |
| `docs/architecture.md` | Scope note added. Stale statements corrected: DSM/WTM were "not built", the agents were "not operational", and the date-bounded retrieval was "not implemented". Added a "Downstream layers" section, the tool / synthetic / safety rows and the coordination scope (LangGraph for the evidence workflow, scripts elsewhere, no supervisor, no system-dynamics engine). The dependency table is relabeled as historical. |
| `docs/retrieval_design.md` | Scope note added (the final store is RAG_EXPANDED_V2 with HYBRID_RERANKED_V2_1; BASELINE_V1 sections kept for history). Corrected "LLM generation is not yet operational" and "no evaluation question set yet". |
| `docs/synthetic_program_baseline.md` | Corrected "not implemented yet" / "not built" statements, and recorded how the intervention policies were applied in the frozen comparison. |
| `docs/technical_freeze.md` | Corpus-decision records marked local-only. |
| `docs/capstone_requirements_traceability.md` | README / supervisor notes updated; shorthand artifact paths made explicit. Requirement statuses unchanged: GitHub and video remain PACKAGING REMAINS. |
| `docs/checkpoint_3_notes.md`, `docs/rag_baseline_v1_findings.md`, `docs/rag_evaluation_plan.md`, `docs/retrieval_ranking_experiment.md` | Preserved, with a banner labeling each as a historical development-phase document. |

`docs/methodology.md` and `docs/evaluation.md` do not exist. They were not created; the methodology and evaluation are
covered by `technical_freeze.md`, the layer documents and the evaluation outputs.

Current-facing documentation no longer claims that:
- the project is a scaffold;
- DSM / WTM, the predictive simulation or Module 6 are unimplemented;
- a supervisor exists;
- all agents run in one LangGraph graph;
- a system-dynamics model was implemented.

A check confirmed that every COMPLETE requirement in the traceability document cites at least one file that exists in
the public set.

## README status

Rewritten in research-project style with all requested sections:
- **Framing:** overview with the core principle, problem statement, objective, architecture and its coordination
  scope, implemented capabilities.
- **Data and results:** synthetic data and provenance (with the required statement), predictive demonstration, safety
  and reliability (with the required statement), what is not implemented, key results (verified figures only).
- **Using the repository:** repository structure, reproduction (no API key needed), testing.
- **Context:** limitations, future work, academic / demonstration use.

## Supervisor placeholder status

`src/ppm_agent/agents/supervisor.py` is still a placeholder with no functionality. Its docstring, which had a
character-encoding defect, was rewritten as clean UTF-8. It now states that a unified cross-agent supervisor was
proposed but not implemented within the capstone, and how coordination actually works. No mojibake remains in the
source, tests, scripts or docs.

## .gitignore status

Reviewed and made safe for a public repository:
- **Excludes** secrets (`.env`, `.env.*` except the example, key and credential files), virtual environments, Python
  and tool caches, `*.egg-info`, notebook checkpoints, editor and OS files, vector-store files, raw source documents,
  every PDF outside `data/sample/`, processed corpus data, the local corpus-review records and personal notes.
- **No longer ignores** `outputs/`. The earlier rule excluded the frozen analytical results, traces and evaluations,
  which the tests, hash pins and documentation depend on.

## Secrets scan

- **`.env`** holds the API key and is excluded.
- **`src/ppm_agent/config.py`** only reads the `OPENAI_API_KEY` environment variable.
- **The tests** contain only fake placeholder keys.
- **Files intended for publication** contain no API-key-like strings and no personal paths. Trace files store no
  provider keys or responses beyond the parsed structured outputs.

## Restricted-material scan

All files intended for publication were scanned for restricted-distribution markings,
key-like strings and personal paths: **no matches**. No source PDF is published. Local corpus-review working records
and personal notes are kept local-only (see the manifest).

## Public repository manifest

`docs/public_repository_manifest.md` lists what is included, excluded (local only) and optional, with a rationale for
each. 235 files are intended for publication (including `.gitattributes`, added at publication to disable line-ending conversion so the hash-pinned artifacts stay byte-identical in every checkout).

## Reproducibility path

The deterministic path needs no API key, no source PDFs and no vector store:
- `build_synthetic_baseline` → `build_dsm` → `build_dsm_visualization` → `build_wtm` → `build_scenario_mapping` →
  `build_trajectory_simulation` → `build_safety_evaluation` → `record_human_review`, each with `--check`;
- then `pytest`.

This was verified on a simulated clean public checkout: only the files the `.gitignore` would publish, with no `.env`,
no local-only records and no vector store. **All 8 `--check` rebuilds passed**, and the suite gave **324 passed, 3
skipped**. Git is not installed on the packaging machine, so the public file set was computed by a script that mirrors
the `.gitignore` rules; `git status` should confirm it once the repository is created.

One reproducibility issue was found and fixed: two corpus-selection tests read the local corpus-review records and
failed in a public checkout. They now skip when those records are absent, as the vector-store test already does. They
still run, and pass, in the full local workspace.

## Frozen artifact verification

Checked before and after cleanup: **22 / 22 frozen artifacts unchanged**. No hash was updated.

## Final test count

- Full local workspace: **327 passed**.
- Clean public checkout: 324 passed, 3 skipped by design.
- No live API calls.

## Unresolved packaging items

- Create the git repository, confirm the published set with `git status`, and publish it to GitHub.
- Final write-up: fill in the TBD locations in the traceability document, and state the tool-use, multi-agent and
  LangGraph scope precisely.
- Final presentation / video.
- Resolved: `data/processed/` and the vector store are LOCAL ONLY / EXCLUDED FROM INITIAL PUBLIC RELEASE (see the
  manifest). They may be published separately in future research.
