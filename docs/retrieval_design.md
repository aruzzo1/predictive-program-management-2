# Retrieval Design

Describes the design of the retrieval (RAG) layer. Settings come from `.env` (defaults in `src/ppm_agent/config.py`).

> **Scope note.** The final, frozen store is RAG_EXPANDED_V2 (10 documents, 848 chunks), used by the agents through
> HYBRID_RERANKED_V2_1 retrieval (see [`retrieval_ranking_experiment.md`](retrieval_ranking_experiment.md)). Sections
> below that describe the five-document BASELINE_V1 prototype are kept for history. The overall implementation is
> described in [`technical_freeze.md`](technical_freeze.md).

## Current settings

| Setting | Value | `.env` key |
|---|---|---|
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` (local, 384-d, L2-normalized) | `EMBEDDING_MODEL` |
| Chunk size target (maximum) | 220 tokens | `CHUNK_SIZE_TOKENS` |
| Chunk overlap | 35 tokens | `CHUNK_OVERLAP_TOKENS` |
| Hard ceiling | 254 content tokens (model max 256 minus [CLS]/[SEP]) | derived from the model |
| top_k | 5 | `TOP_K` |
| candidate_k | 15 | `CANDIDATE_K` |
| Duplicate threshold | 12 consecutive shared words | `DEDUP_MIN_SHARED_WORDS` |
| Vector store | Chroma, persistent, `data/processed/chroma`, collection `jsf_corpus`, cosine distance | `VECTOR_STORE_DIR`, `CHROMA_COLLECTION` |

Token counts use the embedding model's own tokenizer. Current store (RAG_EXPANDED_V2): 848 chunks
from 10 documents, longest model input 248 tokens, 0 chunks over the model limit
(`data/metadata/expanded_v2_ingestion_report.json`). Earlier runs: BASELINE_V1_ORIGINAL had 541
chunks (artifacts in `data/processed/baseline_v1_original/`); RAG_HYGIENE_V1 had 461 chunks
(artifacts in `data/processed/rag_hygiene_v1/`, report `data/metadata/prototype_ingestion_report.json`).

## Corpus

**RAG_EXPANDED_V2** (`data/metadata/expanded_corpus_v2.json`) indexes the five prototype documents
below plus GAO-02-39 (2001, 41 chunks), GAO-05-271 (2005, accessible text, 90), GAO-07-360 (2007,
68), GAO-08-388 (2008, 128) and the DOT&E FY2024 F-35 chapter (60), all as full documents. Chunks
by organization: GAO 754, DOT&E 94. By publication year: 2001: 41, 2005: 90, 2006: 77, 2007: 68,
2008: 128, 2009: 120, 2010: 112, 2011: 118, unknown (the two undated DOT&E chapters): 94.

Five-document prototype corpus, defined in `data/metadata/prototype_corpus.json`:

| document_id | Organization | Pages indexed | Chunks (baseline → hygiene V1) |
|---|---|---|---|
| GAO-06-356 | GAO | 33 of 40 | 80 → 77 |
| GAO-09-303 | GAO (accessible-text version) | 38 of 39 | 144 → 120 |
| GAO-10-382 | GAO | 41 of 53 | 121 → 112 |
| GAO-11-325 | GAO (accessible-text version) | 39 of 50 | 161 → 118 |
| DOTE-FY2010-F35 | DOT&E (PDF pp. 29–34 only) | 6 of 6 | 35 → 34 |

A document is ingested only if it is in the manifest, has a `PROTOTYPE_V1` or
`PROTOTYPE_V1_PAGE_RANGE` decision in `corpus_decisions.csv` (a local corpus-review record, not distributed with the
public repository), exists in `JSF_SOURCE_DIR`, and its
SHA-256 matches the manifest. Otherwise ingestion stops with an error.

## Parsing and cleaning

- `pypdf`, page by page. The source folder is only read.
- Removed and logged per page: GAO footers, browser print headers, DOT&E running heads,
  "Table N:/Figure N:" blocks (caption through "Source:") in original-layout GAO reports,
  numeric-heavy table lines, repetitive column headers, short label runs, word fragments and
  lone footnote markers.
- Skipped pages: table-of-contents pages, image-only pages (<100 usable characters; <50 on pages
  that lost administrative lines), pages where >20% of lines are word fragments, and pages left with
  administrative content only. Details in `data/processed/prototype_page_log.json`.
- No OCR and no table extraction. Content in tables and figures is not indexed.

## Retrieval hygiene (RAG_HYGIENE_V1)

Deterministic rules in `ppm_agent.ingestion.hygiene` remove administrative text that is never
program evidence. No rule uses similarity scores, retrieval frequency or evaluation-question
wording. Every removal is written with its rule name, document and page to
`data/processed/prototype_filtered_text.jsonl`, and the counts go to the ingestion report.

| Rule | Removes | Keeps |
|---|---|---|
| `back_matter` | GAO Contact and Staff Acknowledgments, Related GAO Products, GAO back cover | Endnotes ("Footnotes:"), which follow Related GAO Products in accessible text |
| `front_matter` | Accessible-text preamble and cover lines before "GAO Highlights:" | Highlights onward |
| `contents` | Accessible-text "Contents:" section (headings, table lists, abbreviations) | — |
| `agency_letter_furniture` | DoD comments letter: address block, salutation, signature, "[End of letter]", restated report title | The department's substantive responses, tagged `section_type = "agency_comments"` |
| `admin_sentence` | Contact details, distribution and copyright notices (sentence level, any layout) | All other sentences in the same paragraph |
| `table_cell_fragment` / `table_furniture` | In accessible-text table/figure blocks: short standalone label/value cells, "[Refer to PDF…]", "Source:" | Captions, notes and wrapped prose cells |
| `dote_contractor_line` | DOT&E "major contractor(s)" name/address lines (heading may be split, "» MAJOR / CONTRACTORS:") | All DOT&E text |

General extraction fixes added for the RAG_EXPANDED_V2 sources (tested in `tests/test_hygiene.py`):
- DOT&E running heads of later chapter formats ("Article 47", "44 F-35", "45F-35 45") are page furniture.
- DOT&E layout only: a run of short lines is kept when it reads as wrapped prose (at least 8 words,
  with function words making up at least 15% of them). The FY2024 chapter sets body text in a
  ~30-character column, and 354 lines of prose were being dropped as "short label runs". GAO
  layouts are unchanged.
- Accessible-text Contents without "[End of section]" end at the letter's "Washington, DC 20548:"
  address line, with a 150-line safety cap and a page warning.
- Older GAO back cover ("The General Accounting Office, the investigative arm of Congress…") is back matter.
- "Key contributors to this report…" acknowledgments and street-address lines in DoD letters are removed;
  no sentence split after a single-letter initial.

Known costs of these rules:
- Short cells of intact accessible-text tables (e.g. GAO-11-325 Table 3 status cells, Figure 7
  software-block dates) are removed along with the residue. This is consistent with the policy that
  table content is not indexed until table extraction exists.
- Uncaptioned accessible-text tables are not covered.
- Hub chunks are not filtered: a passage is never suppressed for being retrieved often.

Comparison with the baseline: `outputs/evaluation/rag_baseline_comparison_v1.md`.

## Duplicates

- **Source level:** exact duplicates are detected by SHA-256 across the whole source folder;
  near-duplicates (browser re-saves) are excluded by decision in `corpus_decisions.csv`.
- **Retrieval level:** 15 candidates are retrieved. A candidate is suppressed when it is from the
  same document, within one PDF page of a higher-ranked kept result, and shares a run of ≥12
  identical consecutive words with it (typically the chunk overlap). If fewer than top_k
  distinct results remain, the candidate pool is doubled. Ranking is otherwise unchanged: no
  reranking and no source balancing.

## Chunking

Structure-aware and token-aware (`ppm_agent.ingestion.chunking`):

1. A chunk never spans two pages, so every chunk has exactly one `pdf_page`.
2. GAO Highlights text (`section_type = "highlights"`) is never mixed with other text.
3. Paragraphs are packed up to the 220-token target; long paragraphs are split at sentence
   ends, and single over-long sentences by words.
4. Each subsequent chunk in a segment starts with the last whole sentence(s) of the previous one,
   up to 35 tokens.
5. A small final piece is merged into the previous chunk if the result stays within
   1.15 × target and the hard ceiling.

Chunk IDs are stable and readable, e.g. `GAO-10-382-p031-c01`.

## Provenance

Every chunk stores: `chunk_id`, `document_id`, `filename`, `document_hash`, `title`,
`organization`, `publication_date`, `source_type`, `pdf_page`, `printed_page` (only when it can be
read from the GAO footer or a manual page map; otherwise omitted, and returned as `None`),
`section_type`, `extraction_quality`, `chunk_index`, `char_count`, `token_count`, `ingested_at`.

`pdf_page` is the standard page field throughout the project (retriever results, grounded-prompt
citations, verifier). There is no `page` field.

## Traces

`scripts/run_retrieval.py` writes `outputs/retrieval_traces/trace_YYYYMMDD_HHMMSS.json` with the
query, settings, kept results and suppressed duplicates.

## Grounding

The grounded prompt (`agents.retrieval_agent`) requires citations as `[filename, p. <pdf_page>]`,
DIRECT EVIDENCE / INFERENCE labels, and a dependency verdict. In the final system, evidence-grounded LLM reasoning
runs through the Evidence and Dependency Agent (bounded Tree-of-Thought with generator, critic and deterministic
validation; `agents/tot.py`, `agents/graph.py`). The verifier (`agents.verifier`) checks evidence coverage, citation
validity and uncited causal language with keyword rules; it does not judge truth.

## Known limitations

- In BASELINE_V1_ORIGINAL the DOT&E chapter was 35 of the 541 chunks but filled 4 of the top 5 results for the
  benchmark query. Source balance needs evaluation as the corpus grows.
- Retrieval is evaluated on a 13-question set with human review (`data/metadata/rag_evaluation_questions.json`,
  `docs/rag_evaluation_plan.md`, results in `outputs/evaluation/rag_*`).
- Tables, figures and image-only pages are not indexed.
