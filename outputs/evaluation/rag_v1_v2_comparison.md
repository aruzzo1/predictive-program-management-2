# RAG Comparison: BASELINE_V1_ORIGINAL vs RAG_HYGIENE_V1 vs RAG_EXPANDED_V2

| | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| Chunks | 541 | 461 | 848 |
| Documents | 5 | 5 | 10 |
| Corpus | 5 prototype docs | same 5 | same 5 + GAO-02-39, GAO-05-271, GAO-07-360, GAO-08-388, DOT&E FY2024 |
| Extraction | pre-hygiene | hygiene rules | hygiene rules + general fixes for new layouts (original 5 docs: 458/461 chunks byte-identical; the 3 changes are admin text) |
| Model / chunking / top_k / candidate_k / dedup | all-MiniLM-L6-v2, 220/35, 5, 15, 12 | identical | identical |
| Questions | eval_v1 (13) | identical | identical, unedited |

**How to read this.** Results, sources, similarities and source diversity are computed from the saved runs. Similarity is embedding closeness, not relevance. The columns *V2 vs hygiene V1* and *Suggests* are Claude's **preliminary reading of the passage texts, not human judgments**. Where the diagnosis cites evidence that is indexed but not retrieved, it comes from a keyword scan of the V2 chunk dump, used as a diagnostic only (it is not part of retrieval).

## Per-question summary

| Q | Sources in top 5 (V1 → hygiene → V2) | Top sim. (V1 / H / V2) | New sources in V2 top 5 | Lost vs hygiene V1 | V2 vs hygiene V1 | Suggests |
|---|---|---|---|---|---|---|
| Q01 software_integration | 2 → 1 → 3 | 0.697 / 0.697 / 0.711 | 2 (DOT&E-24, GAO-05-271) | 2 | **Stronger** | UNCERTAIN |
| Q02 requirements | 3 → 4 → 4 | 0.652 / 0.652 / 0.652 | 0 (-) | 0 | **Unchanged** | RETRIEVAL_MISS |
| Q03 design_engineering_activities | 2 → 2 → 2 | 0.632 / 0.633 / 0.633 | 2 (GAO-07-360) | 2 | **Mixed** | UNCERTAIN |
| Q04 test_sequencing | 3 → 3 → 4 | 0.709 / 0.709 / 0.709 | 2 (DOT&E-24, GAO-07-360) | 2 | **Mixed** | RETRIEVAL_MISS |
| Q05 schedule_dependencies | 2 → 2 → 3 | 0.618 / 0.618 / 0.622 | 3 (DOT&E-24) | 3 | **Mixed** | UNCERTAIN |
| Q06 technical_deficiencies | 2 → 2 → 2 | 0.581 / 0.581 / 0.674 | 4 (DOT&E-24) | 4 | **Mixed** | RETRIEVAL_MISS |
| Q07 rework_redesign | 3 → 3 → 4 | 0.547 / 0.547 / 0.611 | 3 (DOT&E-24, GAO-08-388) | 3 | **Stronger** | BOTH |
| Q08 concurrency | 2 → 2 → 4 | 0.585 / 0.585 / 0.634 | 2 (DOT&E-24, GAO-07-360) | 2 | **Unchanged** | RETRIEVAL_MISS |
| Q09 milestone_effects | 2 → 3 → 3 | 0.602 / 0.602 / 0.646 | 2 (DOT&E-24) | 2 | **Stronger** | UNCERTAIN |
| Q10 subsystem_dependencies | 3 → 3 → 4 | 0.640 / 0.640 / 0.640 | 1 (DOT&E-24) | 1 | **Slightly stronger** | UNCERTAIN |
| Q11 information_flow | 3 → 3 → 4 | 0.552 / 0.552 / 0.573 | 2 (DOT&E-24) | 2 | **Stronger** | UNCERTAIN |
| Q12 downstream_cost_schedule | 4 → 3 → 3 | 0.602 / 0.594 / 0.594 | 1 (GAO-07-360) | 1 | **Unchanged** | BOTH |
| Q13 software_integration | 1 → 1 → 2 | 0.603 / 0.603 / 0.681 | 4 (DOT&E-24) | 4 | **Stronger (gap closed)** | CORPUS_GAP closed |

## Top five by question

### Q01: software_integration

*What evidence indicates that mission-system software maturity affected F-35 flight-test execution?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | DOT&E-10 p33 (0.697) | DOT&E-10 p33 (0.697) | DOT&E-24 p2 (0.711) **new source** |
| 2 | DOT&E-10 p33 (0.692) | DOT&E-10 p33 (0.692) | DOT&E-10 p33 (0.697) |
| 3 | DOT&E-10 p29 (0.691) | DOT&E-10 p29 (0.691) | DOT&E-10 p33 (0.692) |
| 4 | DOT&E-10 p30 (0.628) | DOT&E-10 p30 (0.637) | DOT&E-10 p29 (0.691) |
| 5 | GAO-11-325 p31 (0.625) | DOT&E-10 p30 (0.628) | GAO-05-271 p11 (0.649) **new source** |

**Preliminary reading:** New direct evidence: DOT&E FY2024 (software stop-test halted OT) and GAO-05-271 (software complexity, capabilities deferred). Sources 1 → 3. The GAO-11-325 p.31 three-year software-delivery delay (lost in hygiene V1) is still not back.

Left the top 5 relative to RAG_HYGIENE_V1:
- DOT&E-10 p30 (0.637), still indexed in V2, ranked below 5: "• The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the U…"
- DOT&E-10 p30 (0.628), still indexed in V2, ranked below 5: "However, during the months since the last program review, more problems with STOVL design and mission systems software arose. • The TBR recommended further changes to the parameter…"

### Q02: requirements

*What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-11-325 p44 (0.652) | GAO-11-325 p44 (0.652) | GAO-11-325 p44 (0.652) |
| 2 | GAO-10-382 p10 (0.640) | GAO-10-382 p10 (0.640) | GAO-10-382 p10 (0.640) |
| 3 | GAO-11-325 p45 (0.637) | GAO-11-325 p45 (0.637) | GAO-11-325 p45 (0.637) |
| 4 | GAO-11-325 p43 (0.618) | DOT&E-10 p30 (0.622) | DOT&E-10 p30 (0.622) |
| 5 | DOT&E-10 p30 (0.614) | GAO-06-356 p2 (0.618) | GAO-06-356 p2 (0.618) |

**Preliminary reading:** Identical top 5. Key-performance-parameter evidence is now indexed (GAO-05-271 p.10-11: design not meeting speed, maneuverability and radar-cross-section specifications; GAO-07-360 p.17-18; GAO-08-388 p.15) but not retrieved.

### Q03: design_engineering_activities

*What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-11-325 p26 (0.632) | GAO-11-325 p26 (0.633) | GAO-11-325 p26 (0.633) |
| 2 | GAO-11-325 p44 (0.564) | GAO-11-325 p44 (0.564) | GAO-07-360 p21 (0.582) **new source** |
| 3 | GAO-10-382 p23 (0.557) | GAO-11-325 p18 (0.561) | GAO-11-325 p44 (0.564) |
| 4 | GAO-11-325 p18 (0.552) | GAO-10-382 p23 (0.557) | GAO-07-360 p16 (0.561) **new source** |
| 5 | GAO-11-325 p17 (0.542) | GAO-11-325 p17 (0.542) | GAO-11-325 p18 (0.561) |

**Preliminary reading:** Gained GAO-07-360 p.21 (production before design maturity → costly design changes that cascade). Lost GAO-10-382 p.23 (90%-of-drawings best practice), still indexed.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-10-382 p23 (0.557), still indexed in V2, ranked below 5: "base; increases in the amount of on- and out-of-station work required on aircraft in production; and require costly retrofitting of aircraft already produced and fielded. A best pr…"
- GAO-11-325 p17 (0.542), still indexed in V2, ranked below 5: "improve oversight and budgeting, holding people accountable for meeting interim objectives and, for objectives not met, providing criteria and a forum for evaluating reasons why an…"

### Q04: test_sequencing

*What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | DOT&E-10 p33 (0.709) | DOT&E-10 p33 (0.709) | DOT&E-10 p33 (0.709) |
| 2 | DOT&E-10 p29 (0.660) | DOT&E-10 p29 (0.660) | GAO-07-360 p20 (0.689) **new source** |
| 3 | GAO-06-356 p14 (0.641) | GAO-06-356 p14 (0.641) | DOT&E-24 p2 (0.661) **new source** |
| 4 | GAO-09-303 p6 (0.640) | GAO-09-303 p6 (0.640) | DOT&E-10 p29 (0.660) |
| 5 | GAO-09-303 p11 (0.638) | GAO-09-303 p11 (0.638) | GAO-06-356 p14 (0.641) |

**Preliminary reading:** Gained GAO-07-360 p.20 (15 flight-test aircraft in 5 years: aggressive) and DOT&E FY2024. Lost GAO-09-303 p.11 (late test aircraft will compress test schedules), the most direct passage, still indexed.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-09-303 p6 (0.640), still indexed in V2, ranked below 5: "of production jets on order and is still working to deliver test jets and mature manufacturing processes, plans to accelerate procurement will be difficult to achieve in a cost-eff…"
- GAO-09-303 p11 (0.638), still indexed in V2, ranked below 5: "Continuing delays in delivering test aircraft are expected to hamper and further compress test schedules. In particular, the joint team projects that the two aircraft dedicated to…"

### Q05: schedule_dependencies

*What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | DOT&E-10 p32 (0.618) | DOT&E-10 p32 (0.618) | DOT&E-24 p1 (0.622) **new source** |
| 2 | GAO-11-325 p36 (0.589) | GAO-11-325 p36 (0.589) | DOT&E-10 p32 (0.618) |
| 3 | DOT&E-10 p33 (0.574) | DOT&E-10 p33 (0.574) | DOT&E-24 p7 (0.609) **new source** |
| 4 | DOT&E-10 p30 (0.546) | DOT&E-10 p31 (0.539) | DOT&E-24 p2 (0.603) **new source** |
| 5 | DOT&E-10 p31 (0.539) | DOT&E-10 p33 (0.536) | GAO-11-325 p36 (0.589) |

**Preliminary reading:** DOT&E FY2024 now supplies 3 of 5: Block 4 / TR-3 delays to later capability (relevant) but also generic chapter openings. Lost DOT&E FY2010 Block 0.5/1 slip passages, still indexed. Results now span two eras.

Left the top 5 relative to RAG_HYGIENE_V1:
- DOT&E-10 p33 (0.574), still indexed in V2, ranked below 5: "advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission sy…"
- DOT&E-10 p31 (0.539), still indexed in V2, ranked below 5: "Block 0.5 is the infrastructure increment, which contains communications, navigation, and limited radar functionality. - Aircraft BF-4, loaded with Block 0.5, accomplished first fl…"
- DOT&E-10 p33 (0.536), still indexed in V2, ranked below 5: "F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increme…"

### Q06: technical_deficiencies

*What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-10-382 p22 (0.581) | GAO-10-382 p22 (0.581) | DOT&E-24 p2 (0.674) **new source** |
| 2 | DOT&E-10 p33 (0.568) | DOT&E-10 p33 (0.568) | DOT&E-24 p8 (0.597) **new source** |
| 3 | DOT&E-10 p33 (0.567) | DOT&E-10 p33 (0.567) | GAO-10-382 p22 (0.581) |
| 4 | GAO-10-382 p32 (0.543) | GAO-10-382 p32 (0.543) | DOT&E-24 p10 (0.578) **new source** |
| 5 | DOT&E-10 p29 (0.542) | DOT&E-10 p29 (0.542) | DOT&E-24 p13 (0.576) **new source** |

**Preliminary reading:** Gained DOT&E FY2024 Category 1 deficiencies and regression testing (retest evidence). Lost GAO-10-382 p.32 (lift-fan redesign after test damage, i.e. redesign evidence), still indexed. Two FY2024 results are generic (reliability metrics, recommendations).

Left the top 5 relative to RAG_HYGIENE_V1:
- DOT&E-10 p33 (0.568), still indexed in V2, ranked below 5: "The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Schedule Re-Planning and Implementation of Changes • The year-long proce…"
- DOT&E-10 p33 (0.567), still indexed in V2, ranked below 5: "advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission sy…"
- GAO-10-382 p32 (0.543), still indexed in V2, ranked below 5: "Nonetheless, completing the design modifications will likely result in carrier suitability test delays of at least 4 months, according to an official from DOT&E. • JSF engine. The…"
- DOT&E-10 p29 (0.542), still indexed in V2, ranked below 5: "teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 progra…"

### Q07: rework_redesign

*What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-10-382 p10 (0.547) | GAO-10-382 p10 (0.547) | GAO-08-388 p34 (0.611) **new source** |
| 2 | GAO-11-325 p44 (0.539) | GAO-11-325 p44 (0.539) | DOT&E-24 p10 (0.556) **new source** |
| 3 | GAO-11-325 p45 (0.510) | GAO-11-325 p45 (0.510) | DOT&E-24 p8 (0.548) **new source** |
| 4 | GAO-06-356 p21 (0.502) | GAO-06-356 p21 (0.502) | GAO-10-382 p10 (0.547) |
| 5 | GAO-11-325 p5 (0.501) | GAO-11-325 p5 (0.501) | GAO-11-325 p44 (0.539) |

**Preliminary reading:** GAO-08-388 p.34 at rank 1: weight-growth redesign was 'the single largest factor causing the $10 billion cost increase and 18-month extension'. In V1, weight-related passages were already indexed (GAO-10-382 p.7, GAO-11-325 p.5) but not retrieved, so the baseline failure was partly a retrieval miss.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-11-325 p45 (0.510), still indexed in V2, ranked below 5: "metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test point…"
- GAO-06-356 p21 (0.502), still indexed in V2, ranked below 5: "Structuring the program into separate and manageable increments based on what is achievable now and in the future would allow more predictable cost and delivery estimates. Over the…"
- GAO-11-325 p5 (0.501), still indexed in V2, ranked below 5: "We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on our audit objectives. Background: The F-35 program is a joint, multinati…"

### Q08: concurrency

*What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-10-382 p22 (0.585) | GAO-10-382 p22 (0.585) | DOT&E-24 p2 (0.634) **new source** |
| 2 | DOT&E-10 p33 (0.556) | DOT&E-10 p33 (0.556) | GAO-10-382 p22 (0.585) |
| 3 | DOT&E-10 p33 (0.554) | DOT&E-10 p33 (0.554) | GAO-07-360 p21 (0.564) **new source** |
| 4 | GAO-10-382 p9 (0.547) | GAO-10-382 p9 (0.547) | DOT&E-10 p33 (0.556) |
| 5 | DOT&E-10 p30 (0.543) | DOT&E-10 p29 (0.543) | DOT&E-10 p33 (0.554) |

**Preliminary reading:** GAO-06-356 (8 explicit concurrency chunks) and GAO-05-271 (8) are still absent. GAO-07-360 p.21 (production before design maturity) is partially relevant. Rank 1 is the generic FY2024 hub chunk.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-10-382 p9 (0.547), still indexed in V2, ranked below 5: "contractor capabilities and plans for ramping-up and sustaining production at maximum rates, and the Joint Assessment Team (JAT) reviewed F135 engine costs and affordability projec…"
- DOT&E-10 p29 (0.543), still indexed in V2, ranked below 5: "teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 progra…"

### Q09: milestone_effects

*What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | DOT&E-10 p33 (0.602) | DOT&E-10 p33 (0.602) | DOT&E-24 p2 (0.646) **new source** |
| 2 | DOT&E-10 p30 (0.591) | DOT&E-10 p29 (0.587) | DOT&E-24 p1 (0.622) **new source** |
| 3 | DOT&E-10 p29 (0.587) | GAO-10-382 p10 (0.586) | DOT&E-10 p33 (0.602) |
| 4 | GAO-10-382 p10 (0.586) | GAO-10-382 p22 (0.580) | DOT&E-10 p29 (0.587) |
| 5 | GAO-10-382 p22 (0.580) | GAO-11-325 p44 (0.562) | GAO-10-382 p10 (0.586) |

**Preliminary reading:** DOT&E FY2024: full-rate production decision (March 2024) taken during a year-long TR-3 acceptance pause, i.e. milestone-effect evidence, but from a later era than the other results.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-10-382 p22 (0.580), still indexed in V2, ranked below 5: "Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced m…"
- GAO-11-325 p44 (0.562), still indexed in V2, ranked below 5: "The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Se…"

### Q10: subsystem_dependencies

*What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | DOT&E-10 p33 (0.640) | DOT&E-10 p33 (0.640) | DOT&E-10 p33 (0.640) |
| 2 | GAO-10-382 p33 (0.582) | GAO-10-382 p33 (0.582) | GAO-10-382 p33 (0.582) |
| 3 | GAO-11-325 p45 (0.577) | GAO-11-325 p45 (0.577) | GAO-11-325 p45 (0.577) |
| 4 | GAO-11-325 p44 (0.574) | GAO-11-325 p44 (0.574) | GAO-11-325 p44 (0.574) |
| 5 | DOT&E-10 p30 (0.564) | DOT&E-10 p33 (0.556) | DOT&E-24 p7 (0.573) **new source** |

**Preliminary reading:** DOT&E FY2024 p.7 (TR-3 hardware challenges delayed TR-2 software capabilities) is hardware-software coupling evidence; its chunk opens with generic text. Otherwise unchanged.

Left the top 5 relative to RAG_HYGIENE_V1:
- DOT&E-10 p33 (0.556), still indexed in V2, ranked below 5: "F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increme…"

### Q11: information_flow

*What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-11-325 p44 (0.552) | GAO-11-325 p44 (0.552) | DOT&E-24 p1 (0.573) **new source** |
| 2 | DOT&E-10 p33 (0.544) | DOT&E-10 p33 (0.544) | GAO-11-325 p44 (0.552) |
| 3 | GAO-06-356 p28 (0.542) | GAO-06-356 p28 (0.542) | DOT&E-10 p33 (0.544) |
| 4 | GAO-11-325 p45 (0.528) | GAO-11-325 p45 (0.528) | GAO-06-356 p28 (0.542) |
| 5 | GAO-06-356 p6 (0.522) | GAO-06-356 p6 (0.522) | DOT&E-24 p2 (0.539) **new source** |

**Preliminary reading:** DOT&E FY2024: TR-3 aircraft delivered to the field ~2 years before dedicated OT (fielding ahead of test knowledge), and the OT report supporting the full-rate production decision. Direct information-timing evidence.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-11-325 p45 (0.528), still indexed in V2, ranked below 5: "metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test point…"
- GAO-06-356 p6 (0.522), still indexed in V2, ranked below 5: "case be accompanied by a knowledge-based acquisition approach approach that ensures attainment and use of demonstrated product knowledge before making future investments. In commen…"

### Q12: downstream_cost_schedule

*What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | GAO-11-325 p28 (0.602) | GAO-10-382 p10 (0.594) | GAO-10-382 p10 (0.594) |
| 2 | GAO-10-382 p10 (0.594) | GAO-06-356 p19 (0.585) | GAO-06-356 p19 (0.585) |
| 3 | GAO-06-356 p19 (0.585) | GAO-10-382 p8 (0.565) | GAO-07-360 p2 (0.567) **new source** |
| 4 | GAO-09-303 p9 (0.568) | GAO-10-382 p22 (0.562) | GAO-10-382 p8 (0.565) |
| 5 | GAO-10-382 p8 (0.565) | GAO-09-303 p9 (0.561) | GAO-10-382 p22 (0.562) |

**Preliminary reading:** Similar aggregate cost-growth passages. Retrofit statements are indexed (10 chunks, e.g. GAO-08-388 p.23, GAO-05-271 p.15) but not retrieved, and only qualitative: no quantified retrofit or concurrency cost observed.

Left the top 5 relative to RAG_HYGIENE_V1:
- GAO-09-303 p9 (0.561), still indexed in V2, ranked below 5: "New Estimates Project Rising Costs and Further Delays to Complete JSF Development: Development costs are projected to increase between $2.4 billion and $7.4 billion and the schedul…"

### Q13: software_integration

*What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?*

| Rank | BASELINE_V1_ORIGINAL | RAG_HYGIENE_V1 | RAG_EXPANDED_V2 |
|---|---|---|---|
| 1 | DOT&E-10 p33 (0.603) | DOT&E-10 p33 (0.603) | DOT&E-24 p2 (0.681) **new source** |
| 2 | DOT&E-10 p33 (0.582) | DOT&E-10 p33 (0.582) | DOT&E-24 p7 (0.677) **new source** |
| 3 | DOT&E-10 p30 (0.546) | DOT&E-10 p30 (0.546) | DOT&E-24 p1 (0.618) **new source** |
| 4 | DOT&E-10 p30 (0.532) | DOT&E-10 p30 (0.530) | DOT&E-10 p33 (0.603) |
| 5 | DOT&E-10 p32 (0.524) | DOT&E-10 p32 (0.524) | DOT&E-24 p2 (0.598) **new source** |

**Preliminary reading:** 4 of 5 from DOT&E FY2024 with on-era Block 4 / TR-3 evidence (TR-3 software failing on new hardware delayed Lot 15 delivery; TR-3 challenges delayed Block 4 capabilities). The baseline result was a deliberate corpus gap, not a retrieval failure.

Left the top 5 relative to RAG_HYGIENE_V1:
- DOT&E-10 p33 (0.582), still indexed in V2, ranked below 5: "F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increme…"
- DOT&E-10 p30 (0.546), still indexed in V2, ranked below 5: "F-35 Flight Test STOVL Flight Sciences, Flight Test with BF-1, BF-2, and BF-3 Test Aircraft • BF-3 ferried to Patuxent River NAS, Maryland, in February 2010; it is the last of thre…"
- DOT&E-10 p30 (0.530), still indexed in V2, ranked below 5: "• The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the U…"
- DOT&E-10 p32 (0.524), still indexed in V2, ranked below 5: "training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.…"

## Special analyses

### Q02: requirements / KPP evidence
The V2 top 5 is **identical** to RAG_HYGIENE_V1. Two passages are DoD response text, one is JET budget text, one is the generic DOT&E description, and one is a GAO-06-356 Highlights passage on delayed capability delivery. Direct requirements evidence **is now indexed** but not retrieved. GAO-05-271 p.10-11 says design changes resulted from STOVL weight growth and its impact on key performance parameters, and that the design was still not meeting several speed, maneuverability and radar-cross-section specifications. GAO-07-360 p.17-18 and GAO-08-388 p.15 report KPP projections. This suggests a RETRIEVAL_MISS. No requirements documents themselves (ORD/JORD/CDD) are in the corpus.

### Q07: weight growth → redesign → downstream effects (no tuning applied)
GAO-08-388 p.34 now ranks first: *"Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase and 18-month extension in the development schedule since the start of system development."* This **one passage states the first-order chain explicitly** (weight growth → redesign → cost and schedule). The other four results are not about weight.

The intermediate links of the hypothesized chain appear only as **separate fragments** in other indexed passages, none of them retrieved for Q07. They were found by the diagnostic keyword scan:
- weight problems found during system integration and design review led to the 2004 rebaseline and schedule extension (GAO-10-382 p.7; GAO-11-325 p.5);
- design changes driven by STOVL weight affected key performance parameters, and *the other JSF variants' designs were affected as well* (GAO-05-271 p.10): cross-variant propagation;
- the first flight-test aircraft would not include the weight-reduction design changes and so would not represent the production configuration (GAO-06-356 p.14): a test consequence;
- STOVL bulkhead material differs because of earlier weight-reduction actions (DOT&E FY2010 p.32): a design/manufacturing consequence;
- the re-plan to address weight *added $7 billion and 18 months* (GAO-11-325 p.40, prior-reports table). This **differs** from GAO-08-388's "$10 billion", so figures need reconciliation (different bases or dates) before any quantitative use.

No passage was observed that links weight growth to **retest or requalification** explicitly. The full chain is therefore not stated in any single passage; it would have to be assembled from fragments across five documents and roughly 2004-2011. This refines the capstone finding rather than overturning it. Part of the baseline failure was a corpus gap (GAO-08-388 was not indexed) and part was a retrieval miss (GAO-10-382 p.7 and GAO-11-325 p.5 were indexed but not retrieved). The full dependency remains latent and distributed. Retrieval tuning was not, and should not be, used to "fix" this.

### Q08: development-test-production concurrency
**Still not surfaced.** No GAO-06-356 or GAO-05-271 passage reaches the top 5, although the V2 index holds 46 chunks that use the word concurrency, including explicit statements such as GAO-06-356 p.6 (*"a highly concurrent approach that makes significant investments in manufacturing capabilities and production aircraft before flight testing demonstrates the JSF's performance"*). The closest V2 result is GAO-07-360 p.21 (production before design maturity → costly design changes that cascade), which is partial. The diagnosis is a **RETRIEVAL_MISS**: the evidence exists and the embedding ranking does not surface it. No Q08-specific rule was added.

### Q12: downstream cost / schedule, retrofit, rework cost
No retrofit, concurrency-cost or rework-cost passage entered the top 5. The index now contains qualitative retrofit statements from five documents, e.g. GAO-08-388 p.23 (*"problems found may require redesign, production line changes, and retrofit expenses for aircraft already built"*) and GAO-05-271 p.15. No **quantified** retrofit or concurrency cost was observed. Suggested: **BOTH** (retrieval miss for the qualitative evidence; gap for the quantified evidence). The quantitative tables of these reports are not indexed.

### Q13: Block 4 / TR-3 (temporal)
In V1 this was a **deliberate corpus gap**: five wrong-era FY2010 passages. In V2, **4 of 5 results come from DOT&E FY2024 and are on-era, valid evidence**. TR-3 mission-systems software did not function on the new hardware, so Lot 15 deliveries were refused until July 2024. TR-3 challenges delayed Block 4 capabilities, and dedicated OT of TR-3 aircraft is not expected until FY26. The fifth result is still the FY2010 passage. The change comes from adding the source, not from better retrieval.

**Temporal caution.** The same FY2024 passages now also rank in Q01, Q04, Q05, Q06, Q08, Q09, Q10 and Q11, whose evidence is otherwise from 2001-2011. In historical backtesting, a prediction made at an analysis date such as 2010 must not see this evidence. Every V2 chunk now carries `publication_date`, `publication_year`, `publication_date_uncertain`, and, for undated annual reports, `reporting_period` and `content_not_before`. These support a future filter `publication_date <= analysis_date`. That filter is **not implemented**. Both DOT&E chapters have no printed publication date (year = null, flagged), so the rule for undated sources still has to be decided (e.g. exclude, or use `content_not_before` as a lower bound).

## Source concentration

| Source | Share of store (V1 → V2) | Share of results (V1 → hygiene → V2) | Rank-1 questions (V1 / H / V2) |
|---|---|---|---|
| DOTE-FY2010-F35 | 6.5% → 4.0% | 43.1% → 43.1% → 21.5% | 6 / 6 / 2 |
| DOTE-FY2024-F35 | - → 7.1% | - → - → 32.3% | - / - / 7 |
| GAO-02-39 | - → 4.8% | - → - → 0.0% | - / - / 0 |
| GAO-05-271 | - → 10.6% | - → - → 1.5% | - / - / 0 |
| GAO-06-356 | 14.8% → 9.1% | 7.7% → 9.2% → 6.2% | 0 / 0 / 0 |
| GAO-07-360 | - → 8.0% | - → - → 7.7% | - / - / 0 |
| GAO-08-388 | - → 15.1% | - → - → 1.5% | - / - / 1 |
| GAO-09-303 | 26.6% → 14.2% | 4.6% → 4.6% → 0.0% | 0 / 0 / 0 |
| GAO-10-382 | 22.4% → 13.2% | 18.5% → 20.0% → 13.8% | 3 / 4 / 1 |
| GAO-11-325 | 29.8% → 13.9% | 26.2% → 23.1% → 15.4% | 4 / 3 / 2 |

DOT&E share of all results: 43.1% (V1) → 43.1% (hygiene) → **53.8% (V2)**, from 11.1% of the V2 store. **DOT&E concentration increased.** The FY2024 chapter (60 chunks, 7% of the store) took a large share of top-5 slots across eras, while the FY2010 chapter's share fell. The four new GAO reports (327 chunks, 39% of the store) supplied 7 of 65 results. No rebalancing was applied.

Chunks retrieved for more than one question in V2: `DOTE-FY2024-F35-p002-c00` (7x), `DOTE-FY2010-F35-p033-c03` (5x), `DOTE-FY2010-F35-p033-c05` (4x), `GAO-10-382-p010-c02` (4x), `GAO-11-325-p044-c02` (4x), `DOTE-FY2024-F35-p001-c00` (4x), `DOTE-FY2010-F35-p029-c01` (3x), `DOTE-FY2024-F35-p007-c00` (3x), `GAO-10-382-p022-c02` (3x), `GAO-11-325-p045-c00` (2x), `GAO-07-360-p021-c00` (2x), `DOTE-FY2024-F35-p008-c01` (2x), `DOTE-FY2024-F35-p010-c02` (2x).

The new hub is DOT&E FY2024 p.2 (software stop-test / OT planning), which appears in 7 questions. Its text is substantive, but it ranks for questions it does not answer (e.g. Q08 rank 1).

## Preliminary data-sufficiency flags (not the DSM/WTM assessment)

Based only on passages retrieved for the 13 questions and the diagnostic keyword scan of the V2 index. This is not a human review and makes no claim of sufficiency. No dependency weights are implied.

| Evidence needed | Flag | Basis |
|---|---|---|
| Requirements | PARTIAL COVERAGE | KPP status statements (GAO-05-271, GAO-07-360, GAO-08-388) are indexed but rarely retrieved; no ORD/JORD/CDD source documents |
| Program activities | GOOD COVERAGE | Design, manufacturing, software development, flight test and OT activities are described across 2001-2024 |
| Design maturity | GOOD COVERAGE | Drawing releases, design changes, CDRs (GAO-07-360, GAO-10-382, GAO-11-325), technology readiness (GAO-02-39) |
| Predecessor/successor relationships | PARTIAL COVERAGE | Block sequences, knowledge points and production-before-test stated in prose; no schedule network (IMS) in the corpus |
| Schedule dependencies | PARTIAL COVERAGE | Software delays cascading to flight test (GAO-11-325); test-aircraft delays compressing tests (GAO-09-303); TR-3 delaying Block 4 (DOT&E FY2024) |
| Software dependencies | GOOD COVERAGE | Software maturity → flight test (2010-2011); TR-3 hardware/software → delivery and OT (2024) |
| Test dependencies | GOOD COVERAGE | Test-aircraft availability, software stability, instrumentation/OABS readiness gating OT |
| Subsystem coupling | PARTIAL COVERAGE | Helmet display, lift fan/engine, TR-3 avionics, weight across variants: fragments, few explicit couplings |
| Design changes | GOOD COVERAGE | Design-change counts and weight-driven redesign (GAO-05-271, GAO-08-388, GAO-11-325) |
| Rework | PARTIAL COVERAGE | Retrofit and rework stated qualitatively (5 documents); one quantified trend (DOT&E FY2024: 47% reduction in scrap/rework/repair time) |
| Technical deficiencies | GOOD COVERAGE | Lift-fan damage, helmet display, Category 1 software deficiencies |
| Information-flow timing | PARTIAL COVERAGE | Production decisions before test knowledge (GAO-06-356, GAO-07-360); fielding ~2 years before OT (DOT&E FY2024) |
| Cost consequences | PARTIAL COVERAGE | Aggregate cost growth with some attribution ($10B to weight redesign); quantitative tables not indexed; sources disagree on some figures |
| Schedule consequences | PARTIAL COVERAGE | 18-month weight extension, ~3-year software delay, milestone slips; milestone tables not indexed |
| Dependency direction | PARTIAL COVERAGE | Some passages state direction explicitly ("single largest factor causing", "cascading effects hampering flight tests"); most only imply it |
| Dependency strength | WEAK COVERAGE | Only isolated quantified attributions; nothing systematic enough to weight a DSM |
