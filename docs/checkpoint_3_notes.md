# Checkpoint 3 Notes

> **Historical checkpoint document.** It records the project at Checkpoint 3 (RAG prototype and Agentic Phase 1).
> Items listed as not done were completed or superseded later; see [`technical_freeze.md`](technical_freeze.md) for the
> final implementation. The corpus-review records referenced below (`corpus_inventory.csv`, `corpus_summary.md`,
> `corpus_decisions.csv`) are kept locally and are not distributed with the public repository.

## Goal
Semantic RAG prototype over the F-35 / JSF historical corpus.

## Completed
- [x] Project scaffold (repository structure, configuration, placeholders)
- [x] Corpus inventory and ingestion-readiness assessment (`data/metadata/corpus_inventory.csv`, `corpus_summary.md`)
- [x] Per-file corpus decisions (`data/metadata/corpus_decisions.csv`) and source-link provenance
- [x] Five-document prototype corpus with hand-entered metadata and SHA-256 verification (`prototype_corpus.json`)
- [x] Document loading: read-only discovery, exact-duplicate detection, pypdf page extraction
- [x] Page cleaning and filtering, with every drop and skip logged
- [x] Token-aware, structure-aware chunking (220-token target / 35-token overlap, hard ceiling)
- [x] Local embeddings (all-MiniLM-L6-v2) and persistent Chroma vector store (541 chunks in BASELINE_V1_ORIGINAL; 461 after retrieval hygiene)
- [x] Semantic top-k retrieval with near-duplicate suppression
- [x] Retrieval trace logging
- [x] Grounded prompt construction (evidence blocks, citation and labeling rules, dependency verdict)
- [x] Rule-based grounding verifier (evidence coverage, citations, causal language), unit-tested
- [x] Test suite (94 tests)
- [x] Agentic Phase 1: Pydantic domain models, generator / critic / deterministic validation, bounded ToT controller (plain Python and LangGraph), traces in `outputs/agentic_traces/`; Q01 demo run in MOCK_AGENT_MODE (no LLM configured)
- [x] RAG_RANKING_V2_1: BM25, RRF hybrid and cross-encoder reranking benchmark; temporal eligibility and `analysis_date` retrieval (`outputs/evaluation/rag_ranking_v2_1_comparison.md`)
- [x] RAG_EXPANDED_V2: 10-document corpus (848 chunks) with temporal metadata, re-evaluated on the same 13 questions (`outputs/evaluation/rag_v1_v2_comparison.md`)
- [x] Retrieval evaluation: 13-question set, BASELINE_V1_ORIGINAL with human review (`docs/rag_baseline_v1_findings.md`)
- [x] Retrieval hygiene (RAG_HYGIENE_V1) and re-evaluation (`outputs/evaluation/rag_baseline_comparison_v1.md`)
- [x] Cleanup pass: page schema standardized on `pdf_page`; requirements reconciled; docs and corpus metadata updated

## Not yet done
- [ ] Grounded answer generation with an LLM (no LLM client installed, no API key configured)
- [ ] Initial evaluation question set and metrics (hit rate @k, citation correctness, unsupported-claim rate)

## Decisions
- Chunk sizes are measured in embedding-model tokens, not characters (replaced the original 1,200/175-character design).
- The chunker is implemented in-house rather than with `langchain-text-splitters`, so chunks stay page-bounded and Highlights-aware.
- The DOT&E FY2010 Annual Report is indexed for its F-35 chapter only (PDF pp. 29–34).
- Unreliable pypdf table/figure text is dropped rather than indexed.
- Exact duplicates are detected by SHA-256 at ingestion; near-duplicates are excluded by recorded decision.
- `pdf_page` is the project-wide page field; `printed_page` is kept only when it can be read reliably.

## Open questions
- Which LLM provider to use for grounded generation.
- How to keep a small, dense source (DOT&E chapter) from dominating results as the corpus grows.
- Whether PyMuPDF fixes the letter-spaced files well enough to avoid OCR.

## Observations
- Benchmark query ("What evidence indicates that F-35 software maturity affected flight-test execution?"): 4 of the top 5 results come from the DOT&E FY2010 chapter and 1 from GAO-06-356. 2 near-duplicates were suppressed. Latest trace: `outputs/retrieval_traces/trace_20261023_103616.json`.
- 15 of 188 considered PDF pages were skipped (contents pages and image-only pages). GAO-10-382 pp. 25–26 are flagged as degraded extraction.
- Two prototype documents have date review flags: GAO-10-382 (Highlights page date conflict) and DOT&E FY2010 (no printed publication date).
