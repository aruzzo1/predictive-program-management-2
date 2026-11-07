# Public repository manifest

What the public repository contains, what stays local, and why. `.gitignore` implements this manifest.

## INCLUDE (KEEP IN PUBLIC REPO)

| Category | Paths | Rationale |
|---|---|---|
| Source code | `src/ppm_agent/` | The implementation: ingestion, RAG, agents, prompts, schemas, synthetic baseline, deterministic tools, safety layer. |
| Tests | `tests/` | 327 tests; no live API calls. In a clean public checkout, 324 pass and 3 skip by design (they need local-only data). |
| Scripts | `scripts/*.py` | Build / `--check` entry points for every layer and the agent run scripts. |
| Documentation | `docs/`, `README.md` | Architecture, design notes, agent contract, technical freeze, traceability, cleanup report. Historical documents are labeled. |
| Synthetic baseline | `data/synthetic/` (including `archive/v1.0/`) | The frozen synthetic IMP/IMS v1.1 and the preserved v1.0; small and required for reproduction. |
| Corpus manifests and evaluation inputs | `data/metadata/prototype_corpus.json`, `expanded_corpus_v2.json`, `rag_evaluation_questions.json`, ingestion reports, `rag_expanded_v2_freeze.json`, `JSF_Data_Inventory_Table.*`, `JSF_Data_Link_Provenance.csv` | They define the public evidence corpus and its provenance, and record the frozen RAG configuration. |
| Frozen analytical outputs | `outputs/dsm/` (including `archive/v1.0/`), `outputs/dsm_visualization/`, `outputs/wtm/`, `outputs/simulation/` | Matrices, eigenstructure, mapping, trajectories, comparison and figures. Hash-pinned and checked byte for byte by tests. |
| Safety outputs | `outputs/safety/` | Module 6 policy, evaluation, original and reviewed human-review records, summaries, flow diagram. |
| Agent traces and evaluations | `outputs/agentic_traces/`, `outputs/evaluation/`, `outputs/retrieval_traces/` | The audit record of every real agent episode (raw responses preserved) and the RAG / agent evaluations. The three interpretation-agent traces are hash-pinned. |
| Notebook | `notebooks/rag_prototype.ipynb` | Early RAG prototype; it has no stored outputs. |
| Project configuration | `pyproject.toml`, `requirements.txt`, `.env.example`, `.gitignore`, `.gitattributes`, `.gitkeep` placeholders | The environment definition and an empty configuration template, with no values. `.gitattributes` disables line-ending conversion so the hash-pinned frozen artifacts are checked out byte-identical on every platform. |

Scanned before release:
- for restricted-distribution markings, API-key-like strings and personal paths;
- across all 235 files intended for publication;
- result: no matches.

## EXCLUDE (LOCAL ONLY)

| Category | Paths | Rationale |
|---|---|---|
| Secrets and local configuration | `.env`, `.env.*` (except `.env.example`), `secrets/`, credential and key files | They contain the API key and local paths. Never published. |
| Virtual environment and caches | `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, other tool caches | Machine-specific and regenerable. |
| Editor and OS files | `.vscode/` (including `scripts/.vscode/`), `.idea/`, `desktop.ini`, `Thumbs.db`, `.DS_Store` | Local tooling, not project content. |
| Source documents | `data/raw/**`, every `*.pdf` outside `data/sample/` | The source PDFs are not distributed. The authoritative copies are kept outside the repository and referenced through `JSF_SOURCE_DIR`. |
| Local corpus-review working records | `data/metadata/corpus_decisions.csv`, `data/metadata/corpus_inventory.csv`, `data/metadata/corpus_summary.md` | File-level working records from corpus assembly, kept locally and not part of the published evidence base. The published manifests (`prototype_corpus.json`, `expanded_corpus_v2.json`) define the corpus that was used. Two tests that need these records skip when they are absent. |
| Personal notes | `my_notes.docx` | Personal working notes. |

## OPTIONAL DATA: LOCAL ONLY / EXCLUDED FROM INITIAL PUBLIC RELEASE

| Category | Paths | Size | Classification |
|---|---|---|---|
| Processed corpus data | `data/processed/` (chunk JSONL, filtered text, page logs, per-run copies) | about 6 MB | LOCAL ONLY / EXCLUDED FROM INITIAL PUBLIC RELEASE |
| Vector store | `data/processed/chroma/` | about 12 MB, binary | LOCAL ONLY / EXCLUDED FROM INITIAL PUBLIC RELEASE |

Rationale:
- They are not required for the validated deterministic reproduction / check path.
- Excluding them reduces repository size and avoids publishing duplicated derived data. They are regenerable from the
  source documents by `scripts/ingest_corpus.py`, and `data/metadata/rag_expanded_v2_freeze.json` records content
  hashes for verification.
- They may be published separately in future research if needed.

The one test that queries the vector store skips when it is absent.

The deterministic reproduction path (README, "Reproducing the Demonstration") needs none of the excluded items: no API
key, no source PDFs, no processed data, no vector store.
