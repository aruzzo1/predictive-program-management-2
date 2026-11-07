# RAG Retrieval Evaluation Plan

> **Historical document from the RAG development phase.** Its findings remain valid for that phase. The final, frozen
> implementation is described in [`technical_freeze.md`](technical_freeze.md).

## Purpose

To measure whether retrieval surfaces the evidence the Predictive Program Management methodology
will need, such as dependencies, rework, information flow and cost/schedule propagation, rather
than general F-35 facts. The same question set is re-run after each corpus or retrieval change,
so changes can be compared against a fixed baseline.

This evaluates **retrieval only**. No LLM generates or grades anything.

## Question set

File: `data/metadata/rag_evaluation_questions.json` (version `eval_v1`, 13 questions).

There is one question for each of the 12 methodology categories, plus one deliberate gap probe:

| ID | Category | Prior expectation |
|---|---|---|
| Q01 | software_integration (benchmark) | YES |
| Q02 | requirements | PARTIAL |
| Q03 | design_engineering_activities | PARTIAL |
| Q04 | test_sequencing | YES |
| Q05 | schedule_dependencies | PARTIAL |
| Q06 | technical_deficiencies | PARTIAL |
| Q07 | rework_redesign | UNKNOWN |
| Q08 | concurrency | YES |
| Q09 | milestone_effects | YES |
| Q10 | subsystem_dependencies | PARTIAL |
| Q11 | information_flow | PARTIAL |
| Q12 | downstream_cost_schedule | PARTIAL |
| Q13 | software_integration (temporal-gap probe: Block 4 / TR-3) | NO |

Each record has `question_id`, `category`, `question`, `why_it_matters`,
`expected_evidence_type`, `current_corpus_answer_expected` (YES / PARTIAL / NO / UNKNOWN), and
`expectation_basis`.

Expectations are **prior estimates**, made before looking at retrieval results. They are based
only on document titles, dates and inventory topic notes. They name no expected documents or
pages and are not answer keys. The set intentionally includes questions the current corpus
probably cannot answer.

## Procedure

```powershell
python scripts/run_baseline_evaluation.py                     # writes rag_baseline_5doc.*
python scripts/run_baseline_evaluation.py --name <run_name>   # later runs
```

- Uses the existing vector store and the current `.env` retrieval settings: top_k 5,
  candidate_k 15, near-duplicate suppression. Nothing is re-ingested or tuned.
- Outputs go to `outputs/evaluation/<name>.json` (full results, including chunk text) and
  `<name>.md` (a review sheet with excerpts and blank judgment lines).

## Objective metrics (computed automatically)

Per question:
- results returned
- distinct source documents
- duplicate-suppression events
- candidates considered
- top, mean and minimum top-5 similarity
- number of Highlights chunks

Across the set:
- mean top similarity and mean of the per-question mean similarities
- source concentration: each document's share of all results vs. its share of the store, as a
  representation ratio
- how often each document is ranked first
- chunks returned for more than one question

Similarity is embedding closeness. **It is not relevance**, and these metrics do not measure
answer quality.

## Human judgment (manual, not automated)

Each result has a `human_judgment` field (initially `null`) and `reviewer_notes`. Each question
also has a `question_level_human_judgment` field. Allowed values:

| Value | Meaning |
|---|---|
| `RELEVANT` | The passage directly supplies the evidence type the question asks for |
| `PARTIALLY_RELEVANT` | On topic, but supplies only part of it (e.g., one side of a dependency, or no consequence stated) |
| `NOT_RELEVANT` | Off topic, boilerplate, or generic background |
| `NEEDS_REVIEW` | Cannot be judged from the chunk alone; read the source page |

Judge from the full `text` in the JSON or from the source PDF page, not only from the 400-character
excerpt. From the judgments, compute precision@5 per question and the share of questions with at
least one `RELEVANT` result. Then compare each question's outcome with its prior expectation.

## Designated baseline: BASELINE_V1_ORIGINAL

The run in `outputs/evaluation/rag_baseline_5doc.json` and `rag_baseline_5doc.md`
(2026-10-25T14:56:19Z) is designated **BASELINE_V1_ORIGINAL**. It represents the uncorrected
five-document retrieval system **before retrieval-hygiene improvements**: no boilerplate
filtering, no hub-chunk handling, and no changes to table handling.

| File | SHA-256 |
|---|---|
| `rag_baseline_5doc.json` | `9AB207FB98C4FB1987E7526B34E74EF40FAC5150147845A54869F93E4797348F` |
| `rag_baseline_5doc.md` | `DCAC913697D601203991CE661D88A00042578702C21FEA04B677A343494D45A5` |

These files must not be overwritten or edited. Later runs use a new `--name`. Human judgments
are recorded separately in `outputs/evaluation/rag_baseline_5doc_human_review.md`, which only
presents the baseline results.

## Subsequent run: RAG_HYGIENE_V1

`outputs/evaluation/rag_baseline_5doc_hygiene_v1.json` / `.md` uses the same 5 documents, model,
chunking, retrieval settings and questions as BASELINE_V1_ORIGINAL. It differs only in the
deterministic retrieval-hygiene rules (see `docs/retrieval_design.md`). The store went from 541 to
461 chunks. Comparison: `outputs/evaluation/rag_baseline_comparison_v1.md`. Human findings for the
baseline: `docs/rag_baseline_v1_findings.md`.

## Subsequent run: RAG_EXPANDED_V2

`outputs/evaluation/rag_expanded_v2.json` / `.md`: the same model, chunking, retrieval settings and
questions, over the 10-document corpus `data/metadata/expanded_corpus_v2.json` (848 chunks).
Three-way comparison: `outputs/evaluation/rag_v1_v2_comparison.md`.

## Subsequent run: RAG_RANKING_V2_1

The same frozen RAG_EXPANDED_V2 store and questions, run through four retrieval strategies
(`outputs/evaluation/rag_{semantic,bm25,hybrid,hybrid_reranked}_v2_1.*`). Design:
`docs/retrieval_ranking_experiment.md`. Comparison: `outputs/evaluation/rag_ranking_v2_1_comparison.md`.

## Key Capstone Finding: Q07 and Latent Engineering Dependencies

Q07 asked:

> "What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?"

In BASELINE_V1_ORIGINAL the five-document semantic retriever returned no passage that directly
answers this question. Human review rated Q07 **FAILED**: the top five results were budget and
JET-estimate text, DoD response text, background, and a passage on the F-16's incremental approach.

This failure is analytically important. It is not merely a bad RAG result.

**Capstone hypothesis.** Important engineering-program dependencies may be *distributed* across
multiple documents, activities, organizations and time periods, rather than stated explicitly in
any single passage. A chain such as

```
Weight Growth
    ↓
Design Changes / Redesign
    ↓
Subsystem Effects
    ↓
Retest / Requalification
    ↓
Schedule and Cost Consequences
```

may be evidenced only by fragments. One passage may describe a redesign, another a subsystem
problem, another a retest or schedule slip. None of them needs to state the complete dependency,
and none needs to use the words of the question. A semantic retriever ranks passages by their
similarity to the question as a whole. It is therefore poorly suited to finding evidence that
exists only as the composition of several partial statements.

This is one reason the proposed architecture does not stop at RAG:

```
RAG retrieves evidence fragments
        ↓
Agentic reasoning proposes and evaluates candidate dependencies
        ↓
DSM represents cross-activity and cross-subsystem interdependencies
        ↓
WTM represents iteration and rework behavior
        ↓
Predictive models analyze propagation
```

**Important nuance.** Q07 does **not** prove that a weight-growth dependency exists, and a
retrieval failure is not evidence for any dependency. Q07 also does not establish that the
indexed documents contain no weight-related evidence. What it shows is narrower: semantic
retrieval alone cannot be expected to reconstruct every important nonlinear program
relationship. A dependency has to be assembled from fragments, each backed by its own citation,
and then evaluated, rather than looked up.

**Use in later phases.** Retain this finding for the final capstone write-up. It should inform
DSM/WTM construction logic in four ways:
- Candidate dependencies are built from multiple cited fragments.
- Each link in a chain carries its own evidence and confidence.
- A link with no supporting fragment is recorded as unsupported, not inferred.
- Q07 is not to be "fixed" by retrieval tuning specific to weight growth.

**Update after RAG_EXPANDED_V2 (2026-10-25).** The original finding above is kept as written; this
addendum refines it.
- With GAO-08-388 indexed, one passage now states the first-order chain explicitly: *"Redesign
  efforts to address weight growth was the single largest factor causing the $10 billion cost
  increase and 18-month extension in the development schedule"* (GAO-08-388 p.34, rank 1 for Q07).
- The intermediate links exist only as separate fragments across five documents, none retrieved for
  Q07: 2004 rebaseline (GAO-10-382, GAO-11-325); effect on KPPs and on the other variants' designs
  (GAO-05-271); first test aircraft not production-representative (GAO-06-356); bulkhead material
  change (DOT&E FY2010). No passage links weight growth to retest or requalification.
- Two sources give different magnitudes ($10 billion in GAO-08-388; $7 billion and 18 months in
  GAO-11-325). Figures need reconciliation before quantitative use.
- Some weight passages were already indexed in BASELINE_V1_ORIGINAL but not retrieved, so the
  baseline failure was partly a retrieval miss as well as a corpus gap.

The capstone point stands: the complete dependency is not stated in any single passage and has to be
assembled from cited fragments. It is now also clear that some explicit summary statements exist
when the right source is indexed.

## Comparison across runs

Re-run the same question set, unchanged, after corpus expansion and after any retrieval change.
Keep each run under its own name, and do not overwrite `rag_baseline_5doc`. If questions are
added or reworded, increment the question-set version so that runs stay comparable.

## Limitations

- Thirteen questions is a small sample, so results are indicative only.
- The prior expectations are informed guesses, not ground truth.
- Similarity scores from all-MiniLM-L6-v2 sit in a narrow band (about 0.50–0.71 in the baseline)
  and cannot on their own show that evidence is absent.
- `outputs/` is git-ignored. To keep a baseline under version control, commit a copy deliberately
  (e.g., under `docs/evaluation/`) once it has been reviewed.
