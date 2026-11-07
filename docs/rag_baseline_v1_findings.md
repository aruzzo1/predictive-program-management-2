# RAG Baseline V1 Findings

> **Historical document from the RAG development phase.** Its findings remain valid for that phase. The final, frozen
> implementation is described in [`technical_freeze.md`](technical_freeze.md).

Human assessment of **BASELINE_V1_ORIGINAL**: the uncorrected five-document semantic retriever
(541 chunks, all-MiniLM-L6-v2, top_k 5, candidate_k 15), evaluated on the 13-question set
`data/metadata/rag_evaluation_questions.json`.

- Results: `outputs/evaluation/rag_baseline_5doc.json` / `.md`
- Review worksheet: `outputs/evaluation/rag_baseline_5doc_human_review.md`
- Evaluation design: `docs/rag_evaluation_plan.md`

This assessment covers retrieval only. It makes **no claim that the corpus is sufficient**,
either the five-document prototype or the full corpus.

## Assessment categories

| Category | Meaning |
|---|---|
| **STRONG** | At least one retrieved passage provides clear evidence needed for the analytical question. |
| **PARTIAL** | Some useful evidence is present, but important information is missing. |
| **WEAK** | Results are mostly indirect or generic and do not adequately support the question. |
| **FAILED** | The returned passages provide no meaningful evidence for the question. |

## Working classifications

| Assessment | Questions |
|---|---|
| STRONG (6) | Q01 software integration · Q03 design/engineering activities · Q04 test sequencing · Q05 schedule dependencies · Q06 technical deficiencies · Q12 downstream cost/schedule |
| PARTIAL (3) | Q09 milestone effects · Q10 subsystem dependencies · Q11 information flow |
| WEAK (2) | Q02 requirements · Q08 concurrency |
| FAILED (2) | Q07 rework/redesign (weight growth) · Q13 Block 4 / TR-3 (temporal-gap probe) |

## Key findings

**Q01: explicit evidence for a candidate dependency.** Retrieval returned strong, explicit
evidence for **Mission-System Software Maturity → Flight-Test Execution**. DOT&E FY2010 describes
mission-systems software following "familiar historical patterns of extended development,
discovery in flight test, and deferrals to later increments". GAO-11-325 reports that software
delivery to the test program had slipped about three years. Both state the relationship
directly, and they come from two organizations.

**Q07: a failure that may reflect distributed dependencies.** No passage directly answered the
weight-growth question. This is treated as a substantive finding, not just a retrieval defect.
Important engineering dependencies may be spread across fragments in different documents and
periods rather than stated in one passage. See "Key Capstone Finding: Q07 and Latent Engineering
Dependencies" in `docs/rag_evaluation_plan.md`. The failure is not evidence that the dependency
exists.

**Q08: likely retrieval miss.** Concurrency evidence is expected to exist in GAO-06-356, which
is already indexed and whose title concerns entering production before testing demonstrates
acceptable performance. Yet no GAO-06-356 passage reached the top 5. The results were
engine-manufacturing and generic DOT&E text. This points to retrieval quality rather than a gap
in the corpus.

**Q13: intentional corpus-gap probe.** Block 4 and TR-3 postdate every indexed document. The
retriever still returned five plausible-looking DOT&E FY2010 passages about Block 2/3 software,
with a top similarity of 0.603. That is higher than several questions with genuine evidence. In
other words, semantic similarity can return plausible but wrong-era evidence, and a
similarity score cannot signal that evidence is absent.

## Retrieval-quality problems observed

1. **Agency-comment and administrative boilerplate.** Text from the DoD comments appendix in
   GAO-11-325 (letter header, signature, point-of-contact details) appeared 10 times across the
   set.
2. **Hub chunks.** Three DOT&E FY2010 chunks each appeared in 6 of 13 questions. One of them is
   the generic program description. The DOT&E chapter supplied 43% of all results from 6.5% of
   the chunks.
3. **Accessible-text table residue.** Some chunks begin with flattened table cells (e.g.,
   "Aircraft: BF3; Aircraft: BF4; …"), because table filtering covered only the original GAO
   layout.
4. **No GAO Highlights chunk** was retrieved for any question.
5. **Similarity does not measure relevance.** Scores fall in a narrow band (about 0.50–0.71) and
   overlap between relevant, irrelevant and wrong-era results. They cannot serve as an evidence
   filter.

## Implications

- Retrieval hygiene (problems 1 and 3) can be addressed by deterministic text-quality rules
  without touching embeddings, chunk size or ranking. See the RAG_HYGIENE_V1 comparison.
- Source concentration and hub chunks need monitoring, but they should not be "fixed" by
  frequency-based suppression, which would discard evidence just because it is often relevant.
- Corpus expansion is needed for the time-span gaps (Q13) and should be measured against the
  same question set.
- Distributed dependencies (Q07) need the agentic, DSM and WTM layers. They are not expected
  to be solved by retrieval tuning.
