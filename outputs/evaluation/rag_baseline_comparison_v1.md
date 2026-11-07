# RAG Retrieval Comparison: BASELINE_V1_ORIGINAL vs RAG_HYGIENE_V1

| | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 |
|---|---|---|
| Results file | `rag_baseline_5doc.json` | `rag_baseline_5doc_hygiene_v1.json` |
| Run | 2026-10-25T14:56:19+00:00 | 2026-10-25T16:28:00+00:00 |
| Store | 541 chunks | 461 chunks |
| Corpus | same 5 documents | same 5 documents |
| Embedding / chunking / retrieval | sentence-transformers/all-MiniLM-L6-v2, 220/35 tokens, top_k 5, candidate_k 15 | identical |
| Questions | `rag_evaluation_questions.json` eval_v1 (13) | identical, unedited |

The only change between the runs is the retrieval-hygiene rules in `src/ppm_agent/ingestion/hygiene.py`, plus the DOT&E contractor-line rule in `page_extraction.py`. These are deterministic text-quality rules. None is based on similarity, frequency or evaluation-question wording. Every removal is logged in `data/processed/prototype_filtered_text.jsonl`.

**How to read this.** Columns 2-7 are computed objectively from the saved results. *Boilerplate* means a result containing a contact, distribution or letter-furniture pattern. *Table residue* means a result with three or more standalone table-cell paragraphs. The last two columns are Claude's preliminary reading of the passage texts. **They are not human judgments**, and they make no claim of improvement based on similarity scores.

## Aggregate

| Metric | Original | Hygiene V1 |
|---|---|---|
| Results with obvious boilerplate | 1 | 0 |
| Results with table residue | 4 | 0 |
| Results from the DoD comments appendix (tagged `agency_comments` in V1) | (untagged) | 10 |
| Appearances of the generic DOT&E description chunk `DOTE-FY2010-F35-p030-c00` | 6 | 3 |
| Mean distinct documents per question | 2.46 | 2.46 |
| Duplicate-suppression events | 6 | 6 |
| GAO Highlights chunks retrieved | 0 | 1 |
| Mean top similarity (not a quality measure) | 0.6169 | 0.6164 |

| Source share of results (store share) | Original | Hygiene V1 |
|---|---|---|
| DOTE-FY2010-F35 | 43.1% (6.5%) | 43.1% (7.4%) |
| GAO-06-356 | 7.7% (14.8%) | 9.2% (16.7%) |
| GAO-09-303 | 4.6% (26.6%) | 4.6% (26.0%) |
| GAO-10-382 | 18.5% (22.4%) | 20.0% (24.3%) |
| GAO-11-325 | 26.2% (29.8%) | 23.1% (25.6%) |

## Per-question comparison

| Q | Original top result | New top result | Sources | Boilerplate | Table residue | Previously useful evidence disappeared? | Ranking change (preliminary reading) |
|---|---|---|---|---|---|---|---|
| Q01 software_integration | DOT&E p33 DOT&E-p033-c03 (0.6965) | same | 2 → 1 | 0 → 0 | 0 → 0 | Yes: GAO-11-325 p.31 (software delivery ~3-year delay) left the top 5; still indexed | **Degraded (minor).** Ranks 1-4 unchanged, but the second-organization corroboration (GAO) was displaced by the DOT&E program-description chunk, whose boundary shifted (see note on p30-c00). Sources 2 → 1. |
| Q02 requirements | GAO-11-325 p44 GAO-11-325-p044-c01 (0.6525) | same | 3 → 4 | 1 → 0 | 1 → 0 | No | **Improved (modest).** DoD letter furniture (contact, signature, title restatement) is gone. Gained GAO-06-356 Highlights on a 5-year development slip *delaying delivery of capabilities to the warfighter* (indirect requirements evidence) and the DOT&E description chunk (generic). Still dominated by DoD response text; likely still WEAK. |
| Q03 design_engineering_activities | GAO-11-325 p26 GAO-11-325-p026-c01 (0.6321) [TABLE-RESIDUE] | same | 2 → 2 | 0 → 0 | 2 → 0 | No | **Improved (chunk quality).** Same five passages; the rank-1 and one other chunk no longer begin with flattened table cells, so the drawing-release prose now leads. |
| Q04 test_sequencing | DOT&E p33 DOT&E-p033-c03 (0.7094) | same | 3 → 3 | 0 → 0 | 0 → 0 | No | **Unchanged.** |
| Q05 schedule_dependencies | DOT&E p32 DOT&E-p032-c00 (0.6176) | same | 2 → 2 | 0 → 0 | 0 → 0 | Partly: the DOT&E Block 1/2/3 definition left the top 5; still indexed | **Mixed.** Lost the block-definition passage (an expected evidence type); gained DOT&E p.33 on *deferrals to later increments* (block-to-block consequence). Net roughly neutral. |
| Q06 technical_deficiencies | GAO-10-382 p22 GAO-10-382-p022-c02 (0.5814) | same | 2 → 2 | 0 → 0 | 0 → 0 | No | **Unchanged.** |
| Q07 rework_redesign | GAO-10-382 p10 GAO-10-382-p010-c02 (0.5466) | same | 3 → 3 | 0 → 0 | 0 → 0 | No | **Unchanged.** Identical top 5 (see the Q07 section). |
| Q08 concurrency | GAO-10-382 p22 GAO-10-382-p022-c02 (0.5846) | same | 2 → 2 | 0 → 0 | 0 → 0 | No | **Unchanged in substance.** Generic DOT&E description replaced by generic DOT&E flight-test progress; GAO-06-356 still absent (see the Q08 section). |
| Q09 milestone_effects | DOT&E p33 DOT&E-p033-c03 (0.6023) | same | 2 → 3 | 0 → 0 | 0 → 0 | No | **Neutral.** Generic DOT&E description replaced by DoD's response on separate full-rate production decisions (agency_comments): marginal relevance. |
| Q10 subsystem_dependencies | DOT&E p33 DOT&E-p033-c05 (0.6398) | same | 3 → 3 | 0 → 0 | 0 → 0 | No | **Slightly improved.** Generic description replaced by DOT&E p.33 software/test assessment; still marginal for subsystem coupling. |
| Q11 information_flow | GAO-11-325 p44 GAO-11-325-p044-c02 (0.5518) | same | 3 → 3 | 0 → 0 | 0 → 0 | No | **Unchanged.** |
| Q12 downstream_cost_schedule | GAO-11-325 p28 GAO-11-325-p028-c00 (0.6015) [TABLE-RESIDUE] | GAO-10-382 p10 GAO-10-382-p010-c02 (0.5942) | 4 → 3 | 0 → 0 | 1 → 0 | Partly: GAO-11-325 p.28 prose on LRIP contract cost growth and 9-month delivery extensions left the top 5; still indexed (its table-residue prefix was removed) | **Mixed.** The table-residue chunk dropped out, but with it a relevant passage on production cost growth. Gained GAO-10-382 p.22 on engine redesigns and manufacturing problems (relevant to propagation). Net roughly neutral. |
| Q13 software_integration | DOT&E p33 DOT&E-p033-c05 (0.6032) | same | 1 → 1 | 0 → 0 | 0 → 0 | No | **Unchanged (FAILED, as intended).** Still five wrong-era DOT&E FY2010 passages. |

## Changes in each top 5

A result is treated as the same across runs when it comes from the same document and page with at least 85% word overlap. Chunk IDs alone are not compared, because they can shift when a page loses lines. "Still indexed" means the text is in the V1 store but ranked below 5 for that question.

### Q01: software_integration

- **Out:** GAO-11-325 p31 GAO-11-325-p031-c02 (0.6248). still indexed (as `GAO-11-325-p031-c02`, 100% word overlap) - displaced in ranking.  
  > Software development--essential for achieving about 80 percent of the JSF functionality--is significantly behind schedule as it enters its most challenging phase. Software delivery to the test program that is essential to demonstrating full system capability is now expected in late 2014, a 3-year de
- **In:** DOT&E p30 DOT&E-p030-c00 (0.6366)  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped

### Q02: requirements

- **Out:** GAO-11-325 p43 GAO-11-325-p043-c00 (0.6178) [BOILERPLATE, TABLE-RESIDUE]. text partly removed by hygiene (closest new chunk `GAO-11-325-p043-c00`, 64% overlap).  
  > of contact is Colonel Jason Denney, U.S. Air Force. Jason.Denney@%osd.mil, 703-697-3619. Sincerely, Signed by: David G. Ahern: Deputy Assistant Secretary of Defense: GAO Draft Report Dated February 28, 2011: "JOINT STRIKE FIGHTER: RESTRUCTURING PLACES PROGRAM ON FIRMER FOOTING, BUT PROGRESS IS STILL
- **In:** DOT&E p30 DOT&E-p030-c00 (0.6221)  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped
- **In:** GAO-06-356 p2 GAO-06-356-p002-c04 (0.6184)  
  > Development costs have increased 84 percent, planned purchases have decreased by 535 aircraft, and the completion of development has slipped 5 years, delaying delivery of capabilities to the warfighter. With more than 90 percent of the JSF investment remaining, DOD officials have the opportunity to

### Q05: schedule_dependencies

- **Out:** DOT&E p30 DOT&E-p030-c00 (0.5456). still indexed (as `DOTE-FY2010-F35-p030-c00`, 91% word overlap) - displaced in ranking.  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped
- **In:** DOT&E p33 DOT&E-p033-c03 (0.5364)  
  > F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and oth

### Q08: concurrency

- **Out:** DOT&E p30 DOT&E-p030-c00 (0.5429). still indexed (as `DOTE-FY2010-F35-p030-c00`, 91% word overlap) - displaced in ranking.  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped
- **In:** DOT&E p29 DOT&E-p029-c01 (0.5428)  
  > teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated tes

### Q09: milestone_effects

- **Out:** DOT&E p30 DOT&E-p030-c00 (0.5906). still indexed (as `DOTE-FY2010-F35-p030-c00`, 91% word overlap) - displaced in ranking.  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped
- **In:** GAO-11-325 p44 GAO-11-325-p044-c02 (0.5617) [agency_comments]  
  > The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of mon

### Q10: subsystem_dependencies

- **Out:** DOT&E p30 DOT&E-p030-c00 (0.5644). still indexed (as `DOTE-FY2010-F35-p030-c00`, 91% word overlap) - displaced in ranking.  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped
- **In:** DOT&E p33 DOT&E-p033-c03 (0.5564)  
  > F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and oth

### Q12: downstream_cost_schedule

- **Out:** GAO-11-325 p28 GAO-11-325-p028-c00 (0.6015) [TABLE-RESIDUE]. still indexed (as `GAO-11-325-p028-c00`, 85% word overlap) - displaced in ranking.  
  > Aircraft: BF3; Aircraft: BF4; Aircraft: AF1; Aircraft: AF2; Aircraft: AF3; Aircraft: CF1; Aircraft: CF2; Aircraft: CF3; Aircraft: BF5; Aircraft: AF4; Source: GAO analysis of DOD data. Manufacturing production aircraft is different from building test aircraft, and some gains in learning as more aircr
- **In:** GAO-10-382 p22 GAO-10-382-p022-c02 (0.5618)  
  > Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontr

### Q13: software_integration

- **In:** DOT&E p30 DOT&E-p030-c00 (0.5296)  
  > • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped

Identical top-5 passages (texts may be cleaner): Q03, Q04, Q06, Q07, Q11.

## Note on the DOT&E description chunk (p30-c00)

Removing the two-line contractor address shifted a chunk boundary on DOT&E p.30. Chunk `DOTE-FY2010-F35-p030-c00` now holds the program-description bullets **plus** the following JET II paragraph, which says the SDD flight-test plan lacked resources and assumed unrealistic productivity. Measured against the evaluation questions, its similarity rose for Q01 (0.597 → 0.637) and Q02 (0.614 → 0.622), and fell for Q05, Q09 and Q10. That is why it left four top-5 lists and entered three (Q01, Q02, Q13). The effect comes from chunk packing, not from a rule aimed at this chunk. The new chunk carries more substantive text than before, but its leading bullets are still generic description.

## Q07: weight growth (not tuned)

No rule targets Q07. Its top 5 is **identical** to the baseline: JET budget and estimate text, DoD response text, F-16 incremental-approach background, and report background. It remains FAILED. This is consistent with the capstone finding that a weight-growth dependency, if it exists, would have to be assembled from distributed fragments rather than retrieved as one passage. See "Key Capstone Finding: Q07 and Latent Engineering Dependencies" in `docs/rag_evaluation_plan.md`.

## Q08: concurrency and GAO-06-356

**GAO-06-356 still does not appear in Q08's top 5**, so the hygiene changes did not resolve the suspected retrieval miss. Nothing in GAO-06-356's concurrency discussion was boilerplate competing for rank; its 77 indexed chunks are essentially unchanged from 80. The only change in Q08's top 5 was one generic DOT&E passage replacing another. The miss therefore lies in how the query and passages are matched (vocabulary and embedding), not in noise. No Q08-specific rule was added.

## What hygiene did not change

- DOT&E FY2010 still supplies 43% of all results from 7.4% of the store. Its p.33 assessment chunks now recur in up to 8 of 13 questions.
- DoD response text (now tagged `agency_comments`) is still retrieved, because it is substantive DoD-authored content and was intentionally kept. Whether it should compete with GAO and DOT&E findings is an open design decision.
- Uncaptioned accessible-text tables (the GAO-09-303 Highlights table, the GAO-11-325 Appendix II table) are untouched.
