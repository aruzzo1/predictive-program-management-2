# RAG_RANKING_V2_1: Retrieval Strategy Comparison

Same corpus (RAG_EXPANDED_V2, 848 chunks, frozen), same 13 questions (unedited), same top_k 5 and near-duplicate rule. Strategies and fixed parameters are in `docs/retrieval_ranking_experiment.md`; per-strategy results are in `rag_{semantic,bm25,hybrid,hybrid_reranked}_v2_1.json/.md`; diagnostics are in `rag_ranking_v2_1_diagnostics.json`.

**SEMANTIC_V2 reproduces RAG_EXPANDED_V2 exactly** (top-5 chunk IDs identical for all 13 questions: True).

**How to read this.** Each cell shows source, PDF page, the whole-store dense rank *d* and BM25 rank *b*, and an excerpt. Strategy scores (similarity, BM25, RRF, cross-encoder) are not comparable and are not used to rank strategies. *Preliminary reading* is Claude's reading of the passage texts, **not a human relevance judgment**. Keyword diagnostics ("mentions KPP / concurrency / retrofit / weight") are reporting aids only and are not used by any strategy.

## Aggregate

| Metric | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| Mean distinct sources per question | 3.23 | 3.15 | 3.08 | 3.0 |
| Duplicate-suppression events | 6 | 12 | 9 | 10 |
| DOT&E share of 65 results | 54% | 34% | 45% | 42% |
| DOT&E FY2024 results | 21 | 16 | 16 | 12 |
| Results from the four new GAO reports | 7 | 19 | 11 | 14 |
| Chunks in ≥3 questions (hubs) | 9 | 1 | 4 | 5 |
| Appearances of DOT&E-24 p.2 hub (`DOTE-FY2024-F35-p002-c00`) | 7 | <3 | 5 | 3 |
| agency_comments results | 7 | 5 | 5 | 1 |
| Highlights results | 2 | 1 | 1 | 0 |

| Known-evidence diagnostic (top 5) | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| Q02: passages mentioning KPPs | none | #1 GAO-07-360-p017, #3 GAO-07-360-p018, #5 GAO-11-325-p044 | #1 GAO-11-325-p044 | #1 GAO-07-360-p017, #2 GAO-09-303-p025, #4 GAO-07-360-p018 |
| Q08: passages mentioning concurrency | #3 GAO-07-360-p021 | #1 GAO-07-360-p022, #3 GAO-05-271-p021, #5 GAO-07-360-p007 | #2 GAO-07-360-p022, #3 GAO-07-360-p007, #4 GAO-07-360-p021 | #1 GAO-07-360-p007, #2 GAO-07-360-p020, #4 GAO-07-360-p022 |
| Q12: passages mentioning retrofit | none | #1 GAO-08-388-p023, #3 GAO-10-382-p023 | #3 GAO-10-382-p014 | #2 GAO-08-388-p023 |
| Q07: passages mentioning weight | #1 GAO-08-388-p034 | #1 GAO-08-388-p034, #2 GAO-11-325-p044, #3 GAO-10-382-p007 | #1 GAO-08-388-p034, #2 GAO-11-325-p044, #4 GAO-05-271-p009, #5 GAO-10-382-p007 | #1 GAO-08-388-p034, #4 GAO-11-325-p044 |

## Per question

### Q01: software_integration

*What evidence indicates that mission-system software maturity affected F-35 flight-test execution?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p2 (d1/b28): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-10 p33 (d3/b1): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-10 p33 (d3/b1): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-10 p33 (d3/b1): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… |
| 2 | DOT&E-10 p33 (d2/b20): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… | DOT&E-10 p29 (d5/b2): Development of mission systems software continued to experience delays that affected flight test progress. • P… | DOT&E-10 p29 (d5/b2): Development of mission systems software continued to experience delays that affected flight test progress. • P… | DOT&E-10 p29 (d5/b2): Development of mission systems software continued to experience delays that affected flight test progress. • P… |
| 3 | DOT&E-10 p33 (d3/b1): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-10 p33 (d6/b3): The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Sc… | DOT&E-10 p33 (d6/b3): The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Sc… | DOT&E-10 p33 (d2/b20): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… |
| 4 | DOT&E-10 p29 (d4/b5): teams made significant progress, the results of flight testing and the TBR indicate more time and resources wi… | DOT&E-24 p12 (d343/b4): touch labor time and cure times associated with repairs to LO materials required to correct only the subset of… | DOT&E-10 p30 (d11/b10): However, during the months since the last program review, more problems with STOVL design and mission systems… | DOT&E-10 p30 (d11/b10): However, during the months since the last program review, more problems with STOVL design and mission systems… |
| 5 | GAO-05-271 p11 (d7/b49): Design and software teams have found greater complexity and less efficiency as they develop the 17 million lin… | GAO-06-356 p16 (d25/b6): Flight testing to evaluate the effectiveness and suitability of the fully integrated system is expected to con… | GAO-07-360 p20 (d10/b13): As discussed earlier, current JSF schedules are already showing that delivery of early test aircraft will be l… | GAO-10-382 p31 (d17/b24): All other software increments are behind schedule. Mission system software, in particular, is behind schedule,… |

Sources: SEMANTIC_V2 3, BM25_V2_1 3, HYBRID_V2_1 2, HYBRID_RERANKED_V2_1 2.

**Preliminary reading:** All four keep strong software→flight-test evidence. Hybrid and reranked add DOT&E-10 p.29 ("development of mission systems software continued to experience delays that affected flight test progress"), the most direct statement, and reranked adds GAO-10-382 p.31. They drop GAO-05-271 p.11 (software complexity, capabilities deferred) and the FY2024 stop-test passage. BM25 includes one off-topic passage (DOT&E-24 p.12, maintenance times).

### Q02: requirements

*What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | GAO-11-325 p44 (d1/b107): The approval of a new MS B and APB will reflect these budget decisions. Any significant proposed changes to th… | GAO-07-360 p17 (d155/b1): The JSF Program Projects Key Performance Parameters Will Be Met Based on Modeling and Simulations Currently, t… | GAO-11-325 p44 (d11/b6): The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/… | GAO-07-360 p17 (d155/b1): The JSF Program Projects Key Performance Parameters Will Be Met Based on Modeling and Simulations Currently, t… |
| 2 | GAO-10-382 p10 (d2/b33): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… | DOT&E-24 p10 (d49/b2): Fleet (FY15 – FY23) reliability metrics as shown in Figure 2, based on adjudicated data reported by the JPO. H… | GAO-10-382 p26 (d10/b20): integrating very large and complex softw requirements essential to JSF capabilities, and (3) maturing sev tech… | GAO-09-303 p25 (d48/b13): Early Operational Assessment Identifies Several Challenges That May Have Operational Impact If Not Addressed:… |
| 3 | GAO-11-325 p45 (d4/b234): metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Revi… | GAO-07-360 p18 (d355/b3): completed less than 1 percent of the flight test program and no structural or durability tests have been start… | GAO-06-356 p7 (d8/b23): The length and scope of work remaining continue to make it difficult to predict the cost and time needed to co… | GAO-10-382 p36 (d26/b134): nondefense priorities for the federal discretionary dollar. As such, it is critical to maintain affordability… |
| 4 | DOT&E-10 p30 (d5/b179): • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full)… | DOT&E-24 p12 (d62/b5): This figure shows yearly average values for each metric for a given fiscal year, and the horizontal line indic… | GAO-11-325 p43 (d7/b27): The Department remains committed to the F-35 Joint Strike Fighter (JSF) program. The Fiscal Year (FY) 2012 Pre… | GAO-07-360 p18 (d39/b9): Table 3 shows the program’s estimate for each key performance parameter. The JSF program’s acquisition strateg… |
| 5 | GAO-06-356 p2 (d6/b57): Development costs have increased 84 percent, planned purchases have decreased by 535 aircraft, and the complet… | GAO-11-325 p44 (d11/b6): The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/… | GAO-10-382 p15 (d28/b8): restructuring is complete and a new comprehensive procurement cost estimate is finalized (and expressed in con… | DOT&E-24 p10 (d49/b2): Fleet (FY15 – FY23) reliability metrics as shown in Figure 2, based on adjudicated data reported by the JPO. H… |

Sources: SEMANTIC_V2 4, BM25_V2_1 3, HYBRID_V2_1 3, HYBRID_RERANKED_V2_1 4.

**Preliminary reading:** **Known retrieval miss partly corrected.** BM25 and reranked surface KPP evidence: GAO-07-360 p.17-18 (KPPs projected to be met from modeling, verification not until 2010-2013) and GAO-09-303 p.25 (reranked). Hybrid surfaces only a DoD response listing KPP tracking. GAO-05-271 p.10-11 (design not meeting speed/maneuverability/RCS specifications) is not surfaced by any strategy. BM25 and reranked also include DOT&E-24 reliability-metric passages matched on "requirements".

### Q03: design_engineering_activities

*What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | GAO-11-325 p26 (d1/b5): A key indicator of a product's maturity is the stability of its design. The number of engineering drawings rel… | GAO-07-360 p16 (d12/b1): In February 2006, the program held its critical design review for production representative conventional and s… | GAO-11-325 p26 (d1/b5): A key indicator of a product's maturity is the stability of its design. The number of engineering drawings rel… | GAO-11-325 p26 (d1/b5): A key indicator of a product's maturity is the stability of its design. The number of engineering drawings rel… |
| 2 | GAO-07-360 p21 (d2/b20): before ensuring design maturity through flight testing significantly increases the risk because of the of cost… | GAO-10-382 p23 (d48/b2): with a stable design. However, despite being well beyond the design reviews for each variant, the total number… | GAO-10-382 p23 (d6/b4): base; increases in the amount of on- and out-of-station work required on aircraft in production; and require c… | GAO-07-360 p16 (d12/b1): In February 2006, the program held its critical design review for production representative conventional and s… |
| 3 | GAO-11-325 p44 (d3/b15): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | GAO-11-325 p17 (d9/b3): improve oversight and budgeting, holding people accountable for meeting interim objectives and, for objectives… | GAO-11-325 p17 (d9/b3): improve oversight and budgeting, holding people accountable for meeting interim objectives and, for objectives… | GAO-10-382 p23 (d6/b4): base; increases in the amount of on- and out-of-station work required on aircraft in production; and require c… |
| 4 | GAO-07-360 p16 (d4/b71): According to the contractor and program officials, these inefficiencies are largely due to late delivery of th… | GAO-11-325 p26 (d1/b5): A key indicator of a product's maturity is the stability of its design. The number of engineering drawings rel… | GAO-07-360 p16 (d12/b1): In February 2006, the program held its critical design review for production representative conventional and s… | GAO-11-325 p18 (d5/b11): The Program Has Not Yet Stabilized Aircraft Designs: Engineering drawings released since design reviews and th… |
| 5 | GAO-11-325 p18 (d5/b11): The Program Has Not Yet Stabilized Aircraft Designs: Engineering drawings released since design reviews and th… | GAO-05-271 p14 (d35/b6): One hundred percent of critical manufacturing processes under statistical control, demonstration of a fully in… | GAO-02-39 p8 (d8/b7): In our previous work on best business practices, commercial firms have told us that a key part of product deve… | GAO-05-271 p14 (d35/b6): One hundred percent of critical manufacturing processes under statistical control, demonstration of a fully in… |

Sources: SEMANTIC_V2 2, BM25_V2_1 4, HYBRID_V2_1 4, HYBRID_RERANKED_V2_1 4.

**Preliminary reading:** Similar across strategies. Hybrid and reranked restore GAO-10-382 p.23 (90%-of-drawings best practice, retrofit risk); BM25, hybrid and reranked add GAO-07-360 p.16 (critical design review status). Semantic's GAO-07-360 p.21 is kept only by semantic.

### Q04: test_sequencing

*What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-10 p33 (d1/b8): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… | GAO-11-325 p31 (d8/b1): programs have failed to demonstrate that the system works as intended before entering production, discovering… | DOT&E-24 p2 (d3/b4): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | GAO-11-325 p17 (d33/b5): Although still hampered as in prior years by the late delivery of test aircraft, flight tests substantially in… |
| 2 | GAO-07-360 p20 (d2/b21): manufacture and deliver 15 flight test aircraft and 7 ground test articles in 5 years—an aggressive schedule w… | GAO-11-325 p44 (d50/b2): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | DOT&E-10 p33 (d1/b8): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… | DOT&E-10 p33 (d35/b15): in previous schedules are not achievable in the flight test program until changes are made to all variants tha… |
| 3 | DOT&E-24 p2 (d3/b4): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p8 (d13/b3): Prior to starting the delivery of TR-3 configured aircraft out of long-term parking in July, 649 aircraft had… | GAO-11-325 p31 (d8/b1): programs have failed to demonstrate that the system works as intended before entering production, discovering… | GAO-11-325 p31 (d8/b1): programs have failed to demonstrate that the system works as intended before entering production, discovering… |
| 4 | DOT&E-10 p29 (d4/b13): teams made significant progress, the results of flight testing and the TBR indicate more time and resources wi… | DOT&E-24 p2 (d3/b4): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p8 (d13/b3): Prior to starting the delivery of TR-3 configured aircraft out of long-term parking in July, 649 aircraft had… | GAO-09-303 p11 (d7/b32): Continuing delays in delivering test aircraft are expected to hamper and further compress test schedules. In p… |
| 5 | GAO-06-356 p14 (d5/b91): Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the… | GAO-11-325 p17 (d33/b5): Although still hampered as in prior years by the late delivery of test aircraft, flight tests substantially in… | DOT&E-10 p29 (d4/b13): teams made significant progress, the results of flight testing and the TBR indicate more time and resources wi… | DOT&E-24 p2 (d53/b9): DOT&E assesses that dedicated operational testing of these aircraft will not occur until mid to late FY26, app… |

Sources: SEMANTIC_V2 4, BM25_V2_1 2, HYBRID_V2_1 3, HYBRID_RERANKED_V2_1 4.

**Preliminary reading:** **Reranked looks strongest:** GAO-11-325 p.17 (late test aircraft hampered flight tests), GAO-09-303 p.11 (late test aircraft will compress test schedules; lost since V2) and DOT&E-10 p.33 (reliability limits on flight test). BM25 includes a DoD response and a TR-3 delivery-count passage.

### Q05: schedule_dependencies

*What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p1 (d1/b32): In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone… | GAO-11-325 p36 (d5/b1): Delays in developing, integrating, and releasing software to the test program have cascading effects hampering… | GAO-11-325 p36 (d5/b1): Delays in developing, integrating, and releasing software to the test program have cascading effects hampering… | DOT&E-10 p33 (d6/b14): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… |
| 2 | DOT&E-10 p32 (d2/b10): training syllabus for the initial cadres at the training center. The development team conducted integration ac… | GAO-06-356 p16 (d23/b2): Flight testing to evaluate the effectiveness and suitability of the fully integrated system is expected to con… | DOT&E-10 p32 (d2/b10): training syllabus for the initial cadres at the training center. The development team conducted integration ac… | DOT&E-10 p32 (d2/b10): training syllabus for the initial cadres at the training center. The development team conducted integration ac… |
| 3 | DOT&E-24 p7 (d3/b17): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | GAO-11-325 p34 (d345/b3): It could also require more production aircraft for a longer period to supplement test assets, resulting in few… | GAO-07-360 p20 (d12/b5): As discussed earlier, current JSF schedules are already showing that delivery of early test aircraft will be l… | GAO-11-325 p36 (d5/b1): Delays in developing, integrating, and releasing software to the test program have cascading effects hampering… |
| 4 | DOT&E-24 p2 (d4/b44): as defined in the Block 4 Modernization Capability Development Document (CDD), specifies required capabilities… | GAO-07-360 p20 (d12/b5): As discussed earlier, current JSF schedules are already showing that delivery of early test aircraft will be l… | DOT&E-24 p7 (d3/b17): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | DOT&E-24 p3 (d9/b52): The Increment 3 Annexes, which cover Block 4 and 41P01, and their associated hardware enablers were approved b… |
| 5 | GAO-11-325 p36 (d5/b1): Delays in developing, integrating, and releasing software to the test program have cascading effects hampering… | GAO-10-382 p31 (d87/b6): moving some capabilities to future blocks in order to keep on schedule. This adds pressure and costs to future… | DOT&E-10 p33 (d6/b14): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-10 p31 (d10/b16): Block 0.5 is the infrastructure increment, which contains communications, navigation, and limited radar functi… |

Sources: SEMANTIC_V2 3, BM25_V2_1 4, HYBRID_V2_1 4, HYBRID_RERANKED_V2_1 3.

**Preliminary reading:** BM25 and hybrid add GAO-11-325 p.36 at rank 1 (software delays have cascading effects), and BM25 adds GAO-10-382 p.31 (moving capabilities to future blocks to keep schedule), a direct block-to-block consequence. Reranked restores DOT&E-10 Block 0.5/1 passages and the FY2024 Block 4 sequencing review. Semantic's generic FY2024 chapter openings drop out.

### Q06: technical_deficiencies

*What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p2 (d1/b2): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | GAO-08-388 p23 (d54/b1): is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may requi… | DOT&E-24 p2 (d1/b2): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p2 (d1/b2): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… |
| 2 | DOT&E-24 p8 (d3/b23): against capabilities in the 30R08 software, many of which were against capabilities that were working in previ… | DOT&E-24 p2 (d1/b2): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p7 (d4/b3): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | DOT&E-24 p12 (d13/b5): time of this report. » SURVIVABILITY Results from the cyber survivability assessment of the supply chain refur… |
| 3 | GAO-10-382 p22 (d5/b665): Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves… | DOT&E-24 p7 (d4/b3): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | DOT&E-24 p12 (d13/b5): time of this report. » SURVIVABILITY Results from the cyber survivability assessment of the supply chain refur… | GAO-08-388 p23 (d54/b1): is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may requi… |
| 4 | DOT&E-24 p10 (d6/b38): It includes failures discovered in the air and on the ground. The MFHBCF for the F-35A peaked in FY20 and has… | GAO-11-325 p26 (d101/b4): Additional changes are likely as development flight testing continues. Some emerging concerns may drive additi… | GAO-10-382 p10 (d17/b12): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… | DOT&E-10 p33 (d11/b120): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… |
| 5 | DOT&E-24 p13 (d7/b35): The F-35 JPO and the Services, as appropriate, should: 1. Continue preparations for required F-35 FOT&E in the… | DOT&E-24 p12 (d13/b5): time of this report. » SURVIVABILITY Results from the cyber survivability assessment of the supply chain refur… | DOT&E-24 p10 (d18/b14): Fleet (FY15 – FY23) reliability metrics as shown in Figure 2, based on adjudicated data reported by the JPO. H… | DOT&E-24 p7 (d4/b3): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… |

Sources: SEMANTIC_V2 2, BM25_V2_1 3, HYBRID_V2_1 2, HYBRID_RERANKED_V2_1 3.

**Preliminary reading:** Mixed for every alternative. BM25 adds GAO-11-325 p.26 (lift-system concerns may drive design changes) and GAO-08-388 p.23 (redesign/retrofit risk). Hybrid is the weakest: three generic FY2024 passages (performance intro, cyber survivability, reliability metrics), and it loses FY2024 p.8 (Category 1 deficiencies, regression testing). Reranked also includes the cyber passage.

### Q07: rework_redesign

*What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | GAO-08-388 p34 (d1/b3): Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase… | GAO-08-388 p34 (d17/b1): Officials told us that a maximum of 35 per year was probably affordable, given budget plans at that time. Cont… | GAO-08-388 p34 (d1/b3): Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase… | GAO-08-388 p34 (d1/b3): Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase… |
| 2 | DOT&E-24 p10 (d2/b228): It includes failures discovered in the air and on the ground. The MFHBCF for the F-35A peaked in FY20 and has… | GAO-11-325 p44 (d6/b2): The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/… | GAO-11-325 p44 (d6/b2): The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/… | GAO-10-382 p33 (d36/b12): Further, the lack of a production helmet mounted display configuration at this time could result in a major sy… |
| 3 | DOT&E-24 p8 (d3/b27): against capabilities in the 30R08 software, many of which were against capabilities that were working in previ… | GAO-10-382 p7 (d23/b4): The carrier-suitable variant (CV) will provide the Navy a multi-role, stealthy strike aircraft to complement t… | GAO-11-325 p5 (d10/b9): We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on ou… | GAO-11-325 p5 (d10/b9): We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on ou… |
| 4 | GAO-10-382 p10 (d4/b40): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… | GAO-07-360 p23 (d409/b5): There are also important competing priorities external to DOD’s budget. Fully funding specific programs or act… | GAO-05-271 p9 (d8/b13): these costs had increased by $9.6 billion largely because of a 36-month schedule extension to allow more time… | GAO-11-325 p44 (d6/b2): The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/… |
| 5 | GAO-11-325 p44 (d5/b19): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | DOT&E-24 p13 (d567/b6): Additionally, once cyber effects are adequately and systematically characterized – through a validation proces… | GAO-10-382 p7 (d23/b4): The carrier-suitable variant (CV) will provide the Navy a multi-role, stealthy strike aircraft to complement t… | GAO-08-388 p23 (d139/b10): is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may requi… |

Sources: SEMANTIC_V2 4, BM25_V2_1 5, HYBRID_V2_1 4, HYBRID_RERANKED_V2_1 3.

**Preliminary reading:** Not tuned. The explicit GAO-08-388 p.34 weight passage ranks **1 under every strategy** (BM25 picks the adjacent chunk of the same page). Hybrid adds the most weight passages: the DoD weight-growth tracking response (GAO-11-325 p.44), GAO-10-382 p.7 (2004 rebaseline to address weight problems) and GAO-05-271 p.9, a **second explicit chain statement** ($4.9 billion and ~18 months of unexpected design work *caused by increased aircraft weight that degraded the aircraft's key performance capabilities*). BM25 adds two of those. Reranked adds only the DoD tracking response.

### Q08: concurrency

*What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p2 (d1/b6): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | GAO-07-360 p22 (d10/b1): While some concurrency may be beneficial to efficiently transition from the development stage of a program to… | DOT&E-24 p2 (d1/b6): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | GAO-07-360 p7 (d13/b5): The degree of concurrency between development and production in the JSF program’s acquisition strategy still i… |
| 2 | GAO-10-382 p22 (d2/b265): Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves… | GAO-11-325 p44 (d25/b2): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | GAO-07-360 p22 (d10/b1): While some concurrency may be beneficial to efficiently transition from the development stage of a program to… | GAO-07-360 p20 (d101/b7): Past programs have encountered difficulties in developing software, which delayed flight test schedules. JSF p… |
| 3 | GAO-07-360 p21 (d3/b19): before ensuring design maturity through flight testing significantly increases the risk because of the of cost… | GAO-05-271 p21 (d115/b3): re-plan strategy is a balance of technical, cost and schedule risk that incorporates a best practice, evolutio… | GAO-07-360 p7 (d13/b5): The degree of concurrency between development and production in the JSF program’s acquisition strategy still i… | DOT&E-24 p2 (d1/b6): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… |
| 4 | DOT&E-10 p33 (d4/b62): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… | DOT&E-24 p8 (d30/b4): against capabilities in the 30R08 software, many of which were against capabilities that were working in previ… | GAO-07-360 p21 (d3/b19): before ensuring design maturity through flight testing significantly increases the risk because of the of cost… | GAO-07-360 p22 (d10/b1): While some concurrency may be beneficial to efficiently transition from the development stage of a program to… |
| 5 | DOT&E-10 p33 (d5/b80): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | GAO-07-360 p7 (d13/b5): The degree of concurrency between development and production in the JSF program’s acquisition strategy still i… | GAO-11-325 p44 (d25/b2): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | DOT&E-10 p33 (d4/b62): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… |

Sources: SEMANTIC_V2 4, BM25_V2_1 4, HYBRID_V2_1 3, HYBRID_RERANKED_V2_1 3.

**Preliminary reading:** **Partly corrected.** BM25, hybrid and reranked surface explicit development-production concurrency from GAO-07-360 (p.7: "the degree of concurrency between development and production ... still includes significant risks"; p.22: "significantly concurrent"). GAO-06-356 still does not appear under any strategy (see Q08 section). Semantic and hybrid keep the generic FY2024 hub at rank 1.

### Q09: milestone_effects

*What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p2 (d1/b24): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | GAO-08-388 p19 (d60/b1): According to our analysis of available evidence, manufacturing test aircraft continue to run behind schedule.… | DOT&E-24 p5 (d8/b4): associated timelines, DOT&E estimates that DOTs of TR-3 aircraft will likely not begin in earnest until mid to… | DOT&E-10 p29 (d32/b23): Development of mission systems software continued to experience delays that affected flight test progress. • P… |
| 2 | DOT&E-24 p1 (d2/b14): In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone… | GAO-08-388 p14 (d528/b2): for the most part, but schedules could worsen considerably if the delays in maturing the aircraft and engine d… | DOT&E-24 p1 (d2/b14): In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone… | GAO-10-382 p26 (d65/b21): Table 6 summarizes recent delays to key JSF test activities Steadily lengthening schedules to complete key sys… |
| 3 | DOT&E-10 p33 (d3/b137): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… | GAO-08-388 p23 (d96/b3): is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may requi… | DOT&E-24 p2 (d1/b24): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p2 (d1/b24): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… |
| 4 | DOT&E-10 p29 (d4/b70): teams made significant progress, the results of flight testing and the TBR indicate more time and resources wi… | DOT&E-24 p5 (d8/b4): associated timelines, DOT&E estimates that DOTs of TR-3 aircraft will likely not begin in earnest until mid to… | GAO-10-382 p9 (d18/b7): contractor capabilities and plans for ramping-up and sustaining production at maximum rates, and the Joint Ass… | GAO-08-388 p14 (d528/b2): for the most part, but schedules could worsen considerably if the delays in maturing the aircraft and engine d… |
| 5 | GAO-10-382 p10 (d5/b47): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… | GAO-07-360 p14 (d164/b5): Event did not or has not occurred Event has occurred New date for event Period of flight testing End of develo… | GAO-09-303 p25 (d23/b9): For example: * The current F-35 power system may cause excessive damage to runway surfaces which could limit i… | GAO-08-388 p19 (d60/b1): According to our analysis of available evidence, manufacturing test aircraft continue to run behind schedule.… |

Sources: SEMANTIC_V2 3, BM25_V2_1 3, HYBRID_V2_1 3, HYBRID_RERANKED_V2_1 4.

**Preliminary reading:** BM25 and reranked shift to earlier, direct schedule evidence: GAO-08-388 p.14 and p.19 (test-aircraft manufacturing behind, schedules could worsen) and GAO-10-382 p.26 (recent delays to key test activities, reranked). Hybrid is dominated by FY2024 passages.

### Q10: subsystem_dependencies

*What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-10 p33 (d1/b2): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | GAO-10-382 p33 (d54/b1): The JSF program has proposed interim solutions, but full support system deployability will not be available by… | DOT&E-10 p33 (d1/b2): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-10 p33 (d1/b2): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… |
| 2 | GAO-10-382 p33 (d2/b6): Further, the lack of a production helmet mounted display configuration at this time could result in a major sy… | DOT&E-10 p33 (d1/b2): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | GAO-10-382 p33 (d2/b6): Further, the lack of a production helmet mounted display configuration at this time could result in a major sy… | DOT&E-10 p34 (d32/b4): Remain prepared to deal with continued discovery in flight test as more complex testing begins. 3. Determine t… |
| 3 | GAO-11-325 p45 (d3/b44): metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Revi… | DOT&E-10 p34 (d32/b4): Remain prepared to deal with continued discovery in flight test as more complex testing begins. 3. Determine t… | GAO-11-325 p44 (d4/b20): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | GAO-10-382 p33 (d2/b6): Further, the lack of a production helmet mounted display configuration at this time could result in a major sy… |
| 4 | GAO-11-325 p44 (d4/b20): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | GAO-11-325 p36 (d46/b5): Development and integration of the most advanced capabilities could be deferred to future increments and deliv… | DOT&E-10 p33 (d11/b12): The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Sc… | GAO-11-325 p5 (d19/b79): We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on ou… |
| 5 | DOT&E-24 p7 (d5/b77): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | DOT&E-10 p29 (d33/b7): Development of mission systems software continued to experience delays that affected flight test progress. • P… | DOT&E-10 p29 (d17/b11): teams made significant progress, the results of flight testing and the TBR indicate more time and resources wi… | DOT&E-10 p29 (d33/b7): Development of mission systems software continued to experience delays that affected flight test progress. • P… |

Sources: SEMANTIC_V2 4, BM25_V2_1 3, HYBRID_V2_1 3, HYBRID_RERANKED_V2_1 3.

**Preliminary reading:** Similar. BM25 and reranked add DOT&E-10 p.34 (impact of critical technical issues), and BM25 adds GAO-11-325 p.36 (advanced capabilities deferred). The helmet-display passage (GAO-10-382 p.33) is kept by semantic, hybrid and reranked.

### Q11: information_flow

*What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p1 (d1/b108): In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone… | GAO-05-271 p24 (d78/b1): Defense's (DOD) acquisition program management office and prime contractor. To evaluate whether the current ac… | GAO-06-356 p6 (d7/b2): case be accompanied by a knowledge-based acquisition approach approach that ensures attainment and use of demo… | GAO-06-356 p6 (d32/b3): the JSF program acquisition strategy captures critical knowledge in time to make production investment decisio… |
| 2 | GAO-11-325 p44 (d2/b31): The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in… | GAO-06-356 p6 (d7/b2): case be accompanied by a knowledge-based acquisition approach approach that ensures attainment and use of demo… | GAO-06-356 p14 (d20/b4): Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the… | GAO-06-356 p14 (d20/b4): Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the… |
| 3 | DOT&E-10 p33 (d3/b40): F-35 mission systems software development and test is tending towards familiar historical patterns of extended… | GAO-06-356 p14 (d20/b4): Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the… | DOT&E-10 p29 (d19/b16): teams made significant progress, the results of flight testing and the TBR indicate more time and resources wi… | GAO-09-303 p25 (d46/b13): For example: * The current F-35 power system may cause excessive damage to runway surfaces which could limit i… |
| 4 | GAO-06-356 p28 (d4/b57): DOD provided us with written comments on a draft of this report. The comments appear in appendix III. DOD part… | GAO-11-325 p5 (d140/b5): established goals; (3) assess elements of design stability and manufacturing maturity and review production re… | DOT&E-24 p1 (d1/b108): In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone… | GAO-09-303 p22 (d57/b15): Limited Knowledge Gained From Flight Testing-More Knowledge Gained From Flight Testing. Notes: Flight testing… |
| 5 | DOT&E-24 p2 (d5/b117): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | GAO-11-325 p17 (d625/b7): heightened scrutiny and two-year probation period directed by the Secretary to engineer solutions, assess impa… | GAO-05-271 p24 (d78/b1): Defense's (DOD) acquisition program management office and prime contractor. To evaluate whether the current ac… | GAO-06-356 p28 (d4/b57): DOD provided us with written comments on a draft of this report. The comments appear in appendix III. DOD part… |

Sources: SEMANTIC_V2 4, BM25_V2_1 3, HYBRID_V2_1 4, HYBRID_RERANKED_V2_1 2.

**Preliminary reading:** **Hybrid and reranked look stronger:** GAO-06-356 p.6 (demonstrated knowledge before investment) and p.14 (test delays affect when knowledge is available for investment decisions) lead. Reranked drops the FY2024 fielding-before-OT evidence and has only 2 sources.

### Q12: downstream_cost_schedule

*What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | GAO-10-382 p10 (d1/b14): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… | GAO-08-388 p23 (d102/b1): is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may requi… | GAO-10-382 p10 (d1/b14): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… | GAO-10-382 p10 (d1/b14): According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous… |
| 2 | GAO-06-356 p19 (d2/b215): Past single-step development programs have been unsuccessful in predicting acquisition costs and delivery sche… | GAO-08-388 p2 (d108/b3): Progress has been reported in several important areas, including partner agreements, first flights of a JSF pr… | GAO-10-382 p12 (d8/b11): Engine cost growth and development delays are also contributing substantially to overall program costs. The F1… | GAO-08-388 p23 (d102/b1): is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may requi… |
| 3 | GAO-07-360 p2 (d3/b48): DOD non-concurred, believing its current strategy provides a balance of technical risk, financial constraints,… | GAO-10-382 p23 (d671/b4): base; increases in the amount of on- and out-of-station work required on aircraft in production; and require c… | GAO-10-382 p14 (d7/b13): assessment was based on the production profile before the changes made by the restructuring, it is not directl… | GAO-10-382 p12 (d8/b11): Engine cost growth and development delays are also contributing substantially to overall program costs. The F1… |
| 4 | GAO-10-382 p8 (d4/b337): DOD’s funding requirements for the JSF assume economic benefits from these foreign purchases in reducing unit… | GAO-07-360 p20 (d196/b5): manufacture and deliver 15 flight test aircraft and 7 ground test articles in 5 years—an aggressive schedule w… | GAO-08-388 p2 (d10/b23): be fourth, manufacturing schedule, but test aircraft in manufacturing are still behind, the continuing impacts… | GAO-10-382 p22 (d5/b91): Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves… |
| 5 | GAO-10-382 p22 (d5/b91): Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves… | GAO-10-382 p34 (d67/b6): Significant Investments in Aircraft Are Planned Before Flight Testing Is Completed Although officials recently… | GAO-09-303 p15 (d9/b26): Time and Money Needed for Manufacturing Development Test Aircraft Continue to Increase: The prime contractor h… | GAO-08-388 p14 (d111/b18): money set aside—in this case about 10 percent of the development contract value remaining—to handle unanticipa… |

Sources: SEMANTIC_V2 3, BM25_V2_1 3, HYBRID_V2_1 3, HYBRID_RERANKED_V2_1 2.

**Preliminary reading:** BM25 surfaces retrofit evidence at ranks 1 and 3 (GAO-08-388 p.23; GAO-10-382 p.23, costly retrofitting of aircraft already produced). Reranked keeps GAO-08-388 p.23, and hybrid has NAVAIR's projected retrofit requirements (GAO-10-382 p.14). Still no quantified retrofit cost under any strategy.

### Q13: software_integration

*What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?*

| # | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|
| 1 | DOT&E-24 p2 (d1/b8): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p3 (d13/b1): Block 4 includes DT and OT with aircraft in the TR-2 configuration. For these aircraft, the program has design… | DOT&E-24 p2 (d6/b2): The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rat… | DOT&E-24 p3 (d13/b1): Block 4 includes DT and OT with aircraft in the TR-2 configuration. For these aircraft, the program has design… |
| 2 | DOT&E-24 p7 (d2/b6): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | DOT&E-24 p2 (d6/b2): The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rat… | DOT&E-24 p7 (d2/b6): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… | DOT&E-24 p2 (d6/b2): The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rat… |
| 3 | DOT&E-24 p1 (d4/b21): In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone… | DOT&E-24 p1 (d81/b4): The program proceeded to full-rate production, based on an acquisition decision memorandum (ADM) signed by USD… | DOT&E-24 p2 (d1/b8): The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the… | DOT&E-24 p3 (d11/b11): The Increment 3 Annexes, which cover Block 4 and 41P01, and their associated hardware enablers were approved b… |
| 4 | DOT&E-10 p33 (d5/b16): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-24 p8 (d3/b5): against capabilities in the 30R08 software, many of which were against capabilities that were working in previ… | DOT&E-24 p3 (d13/b1): Block 4 includes DT and OT with aircraft in the TR-2 configuration. For these aircraft, the program has design… | DOT&E-24 p7 (d2/b6): PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E c… |
| 5 | DOT&E-24 p2 (d6/b2): The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rat… | DOT&E-24 p7 (d17/b7): software to improve capability of fielded systems that have the TR-2 avionics architecture while developing th… | DOT&E-10 p33 (d5/b16): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… | DOT&E-10 p33 (d5/b16): advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that… |

Sources: SEMANTIC_V2 2, BM25_V2_1 1, HYBRID_V2_1 2, HYBRID_RERANKED_V2_1 2.

**Preliminary reading:** Unrestricted: FY2024 Block 4 / TR-3 evidence under every strategy (BM25: all five). See the temporal section for the 2011-12-31 cutoff.

## Q08: where the explicit concurrency chunks rank

Ranks are over the whole store (dense, BM25) or the strategy's candidate list (hybrid = RRF order of the 2×30 pool; reranked = cross-encoder order of the same pool). '-' means not ranked or not in the pool.

| Chunk | Concurrency wording | Dense | BM25 | Hybrid | Reranked | In any top 5 |
|---|---|---|---|---|---|---|
| `GAO-07-360-p007-c00` | concurrency | 13 | 5 | 3 | 1 | BM25_V2_1, HYBRID_V2_1, HYBRID_RERANKED_V2_1 |
| `GAO-07-360-p022-c00` | concurrency | 10 | 1 | 2 | 4 | BM25_V2_1, HYBRID_V2_1, HYBRID_RERANKED_V2_1 |
| `GAO-07-360-p021-c00` | (design before production) | 3 | 19 | 4 | 15 | SEMANTIC_V2, HYBRID_V2_1 |
| `GAO-05-271-p021-c02` | concurrency (DoD response) | 115 | 3 | 15 | 32 | BM25_V2_1 |
| `GAO-06-356-p029-c01` | concurrent | 20 | 188 | 33 | 46 | no |
| `GAO-06-356-p010-c01` | concurrently | 186 | 13 | 26 | 34 | no |
| `GAO-06-356-p006-c02` | concurrent | 347 | 69 | - | - | no |
| `GAO-06-356-p008-c01` | concurrent | 76 | 410 | - | - | no |
| `GAO-05-271-p005-c01` | concurrently | 336 | 504 | - | - | no |

Explicit development-test-production concurrency evidence now reaches the top 5 under BM25, hybrid and reranked, **from GAO-07-360** (and a GAO-05-271 DoD response under BM25). **GAO-06-356 still does not.** Its explicit passages use only *concurrent* and *concurrently*, while the query says *concurrency*. Without stemming these are different tokens, so BM25 cannot match them, and the dense model ranks the most explicit one (p.6, "a highly concurrent approach that makes significant investments ... before flight testing demonstrates the JSF's performance") 347th. This is a **vocabulary-normalization limitation of the pre-registered BM25 design** (no stemming), not a corpus gap. Adding stemming now would be tuning after seeing the evaluation, so it is recorded as a candidate for the next, separately evaluated variant.

## Q07: weight growth (not a tuning target)

| Strategy | Rank of explicit GAO-08-388 p.34 passage | Weight-related passages in top 5 |
|---|---|---|
| SEMANTIC_V2 | #1 (GAO-08-388-p034-c02) | #1 GAO-08-388-p034-c02 |
| BM25_V2_1 | #1 (GAO-08-388-p034-c01) | #1 GAO-08-388-p034-c01, #2 GAO-11-325-p044-c03, #3 GAO-10-382-p007-c02 |
| HYBRID_V2_1 | #1 (GAO-08-388-p034-c02) | #1 GAO-08-388-p034-c02, #2 GAO-11-325-p044-c03, #4 GAO-05-271-p009-c01, #5 GAO-10-382-p007-c02 |
| HYBRID_RERANKED_V2_1 | #1 (GAO-08-388-p034-c02) | #1 GAO-08-388-p034-c02, #4 GAO-11-325-p044-c03 |

The explicit first-order statement in GAO-08-388 (weight-growth redesign → $10 billion and 18 months) ranks first everywhere. Lexical signals (BM25, hybrid) bring in more: the 2004 rebaseline (GAO-10-382 p.7), DoD's weight-growth tracking (GAO-11-325 p.44), and in hybrid GAO-05-271 p.9. That passage is a **second explicit statement**: *"$4.9 billion, was a result of an approximately 18-month delay for unexpected design work caused by increased aircraft weight that degraded the aircraft's key performance capabilities."* It adds the KPP link. The sources now give three magnitudes for the weight episode ($4.9 billion in GAO-05-271, $7 billion in GAO-11-325, $10 billion in GAO-08-388, each with ~18 months), so they need reconciliation (different bases and dates) before any quantitative use. Even the best case (hybrid: 4 weight passages) does not surface the cross-variant effect (GAO-05-271 p.10), the non-production-representative test aircraft (GAO-06-356 p.14) or the bulkhead material change (DOT&E-10 p.32), and no passage links weight growth to retest. **The full chain remains distributed.** The first-order link (weight → redesign → cost/schedule/KPP) is stated explicitly in several sources, but the downstream subsystem and test links exist only as fragments. Better ranking retrieves more fragments for one query; it does not assemble the dependency.

## Q13 + temporal control (analysis_date = 2011-12-31)

| Strategy | A. Unrestricted top 5 | B. analysis_date 2011-12-31 top 5 | Ineligible | REQUIRES_REVIEW (not included) |
|---|---|---|---|---|
| SEMANTIC_V2 | DOT&E-24 p2, DOT&E-24 p7, DOT&E-24 p1, DOT&E-10 p33, DOT&E-24 p2 | GAO-09-303 p25 (2009), GAO-10-382 p22 (2010), GAO-11-325 p5 (2011), GAO-10-382 p32 (2010), GAO-06-356 p16 (2006) | 60 chunks | DOT&E-10: 34 chunks |
| BM25_V2_1 | DOT&E-24 p3, DOT&E-24 p2, DOT&E-24 p1, DOT&E-24 p8, DOT&E-24 p7 | GAO-06-356 p16 (2006), GAO-11-325 p16 (2011), GAO-02-39 p17 (2001), GAO-11-325 p45 (2011), GAO-09-303 p11 (2009) | 60 chunks | DOT&E-10: 34 chunks |
| HYBRID_V2_1 | DOT&E-24 p2, DOT&E-24 p7, DOT&E-24 p2, DOT&E-24 p3, DOT&E-10 p33 | GAO-06-356 p16 (2006), GAO-11-325 p5 (2011), GAO-11-325 p36 (2011), GAO-10-382 p9 (2010), GAO-09-303 p25 (2009) | 60 chunks | DOT&E-10: 34 chunks |
| HYBRID_RERANKED_V2_1 | DOT&E-24 p3, DOT&E-24 p2, DOT&E-24 p3, DOT&E-24 p7, DOT&E-10 p33 | GAO-06-356 p16 (2006), GAO-11-325 p45 (2011), GAO-11-325 p36 (2011), GAO-11-325 p5 (2011), GAO-09-303 p25 (2009) | 60 chunks | DOT&E-10: 34 chunks |

- **Unrestricted:** valid Block 4 / TR-3 evidence from DOT&E FY2024 (on-era since V2).
- **Cutoff 2011-12-31:** all 60 DOT&E FY2024 chunks are **INELIGIBLE**. The source is undated (APPROXIMATE_AVAILABILITY) but describes events of November 2024, so it cannot have existed before the cutoff. Every returned chunk has a verified publication date ≤ 2011 (2001-2011). The 34 DOT&E FY2010 chunks (also approximate: content not before 2010-11, publication date unknown) are **REQUIRES_REVIEW**: reported, not silently included. No future evidence leaked under any strategy.
- Under the cutoff, Q13 has no valid answer, which is correct for a 2011 analysis state. The returned 2006-2011 passages are about earlier software and test issues, i.e. the same wrong-era behaviour the V1 gap probe showed. Date filtering prevents leakage but does not create relevance.

## Hub chunks (in ≥3 questions)

| Strategy | Chunk | Appearances | Questions | Character (preliminary reading) |
|---|---|---|---|---|
| SEMANTIC_V2 | `DOTE-FY2024-F35-p002-c00` | 7 | Q01, Q04, Q06, Q08, Q09, Q11, Q13 | substantively broad (software stop-test, quality escapes, TR-3 OT planning) |
| SEMANTIC_V2 | `DOTE-FY2010-F35-p033-c03` | 5 | Q01, Q04, Q08, Q09, Q11 | substantive (software development patterns, re-plan) |
| SEMANTIC_V2 | `DOTE-FY2010-F35-p033-c05` | 4 | Q01, Q08, Q10, Q13 | substantive (mission-systems test risks, block software) |
| SEMANTIC_V2 | `GAO-10-382-p010-c02` | 4 | Q02, Q07, Q09, Q12 | substantive but broad (JET cost/schedule projections) |
| SEMANTIC_V2 | `GAO-11-325-p044-c02` | 4 | Q03, Q07, Q10, Q11 | DoD response (SAE review process): generic for most questions |
| SEMANTIC_V2 | `DOTE-FY2024-F35-p001-c00` | 4 | Q05, Q09, Q11, Q13 | substantive opening summary (FRP decision, TR-3 pause) |
| SEMANTIC_V2 | `DOTE-FY2010-F35-p029-c01` | 3 | Q01, Q04, Q09 | substantive (flight-test progress, TBR) |
| SEMANTIC_V2 | `DOTE-FY2024-F35-p007-c00` | 3 | Q05, Q10, Q13 | opens generic ("This Annual Report does not include ..."), then Block 4 software delays |
| SEMANTIC_V2 | `GAO-10-382-p022-c02` | 3 | Q06, Q08, Q12 | substantive (engine manufacturing and redesign) |
| BM25_V2_1 | `GAO-08-388-p023-c03` | 3 | Q06, Q09, Q12 | substantive (redesign, production-line change, retrofit risk) |
| HYBRID_V2_1 | `DOTE-FY2024-F35-p002-c00` | 5 | Q04, Q06, Q08, Q09, Q13 | substantively broad (software stop-test, quality escapes, TR-3 OT planning) |
| HYBRID_V2_1 | `DOTE-FY2010-F35-p033-c05` | 4 | Q01, Q05, Q10, Q13 | substantive (mission-systems test risks, block software) |
| HYBRID_V2_1 | `DOTE-FY2010-F35-p029-c01` | 3 | Q04, Q10, Q11 | substantive (flight-test progress, TBR) |
| HYBRID_V2_1 | `DOTE-FY2024-F35-p007-c00` | 3 | Q05, Q06, Q13 | opens generic ("This Annual Report does not include ..."), then Block 4 software delays |
| HYBRID_RERANKED_V2_1 | `DOTE-FY2010-F35-p033-c05` | 4 | Q01, Q05, Q10, Q13 | substantive (mission-systems test risks, block software) |
| HYBRID_RERANKED_V2_1 | `DOTE-FY2010-F35-p029-c02` | 3 | Q01, Q09, Q10 | substantive (software delays affected flight test) |
| HYBRID_RERANKED_V2_1 | `DOTE-FY2010-F35-p033-c03` | 3 | Q01, Q06, Q08 | substantive (software development patterns, re-plan) |
| HYBRID_RERANKED_V2_1 | `DOTE-FY2024-F35-p002-c00` | 3 | Q06, Q08, Q09 | substantively broad (software stop-test, quality escapes, TR-3 OT planning) |
| HYBRID_RERANKED_V2_1 | `GAO-08-388-p023-c03` | 3 | Q06, Q07, Q12 | substantive (redesign, production-line change, retrofit risk) |

No hub chunk was suppressed. The FY2024 p.2 hub drops from 7 questions (semantic) to 5 (hybrid), 3 (reranked) and under 3 (BM25).

## Source concentration (share of the 65 results; rank-1 questions)

| Source | Store share | SEMANTIC_V2 | BM25_V2_1 | HYBRID_V2_1 | HYBRID_RERANKED_V2_1 |
|---|---|---|---|---|---|
| DOT&E-10 | 4.0% | 22% (2) | 9% (1) | 20% (2) | 23% (4) |
| DOT&E-24 | 7.1% | 32% (7) | 25% (1) | 25% (5) | 18% (2) |
| GAO-02-39 | 4.8% | 0% (0) | 0% (0) | 2% (0) | 0% (0) |
| GAO-05-271 | 10.6% | 2% (0) | 5% (1) | 3% (0) | 2% (0) |
| GAO-06-356 | 9.1% | 6% (0) | 6% (0) | 5% (1) | 5% (1) |
| GAO-07-360 | 8.0% | 8% (0) | 14% (3) | 9% (0) | 9% (2) |
| GAO-08-388 | 15.1% | 2% (1) | 11% (4) | 3% (1) | 11% (1) |
| GAO-09-303 | 14.2% | 0% (0) | 0% (0) | 3% (0) | 6% (0) |
| GAO-10-382 | 13.2% | 14% (1) | 9% (1) | 15% (1) | 14% (1) |
| GAO-11-325 | 13.9% | 15% (2) | 22% (2) | 15% (3) | 12% (2) |

No rebalancing was applied. BM25 shifts results toward the GAO reports and the new sources. Hybrid sits between semantic and BM25, and reranked between hybrid and the GAO-heavy BM25.

## Summary (preliminary, pending human review)

- **Known retrieval misses corrected (partly):** Q02 (KPP evidence: BM25, reranked), Q08 (explicit concurrency from GAO-07-360: BM25, hybrid, reranked), Q12 (qualitative retrofit evidence: all three alternatives), Q04 (late test aircraft: reranked).
- **Not corrected:** GAO-06-356 concurrency (word-form mismatch); GAO-05-271 KPP specifications; quantified retrofit cost (not observed in the corpus).
- **Useful evidence lost:** Q06 FY2024 Category 1 deficiency and regression-testing passage (hybrid, reranked); GAO-05-271 software deferral (Q01: hybrid, reranked); FY2024 fielding-before-OT evidence (Q11: reranked); GAO-07-360 p.21 design-maturity passage (Q03, Q08: kept only by semantic and hybrid).
- **New failure modes:** BM25 term-frequency matches on generic words ("requirements", "test", "software") pull in off-topic passages (maintenance times, reliability metrics, cyber, budget priorities) and double the duplicate suppressions (12). Hybrid inherits some generic FY2024 passages (Q06). Reranked narrows sources on some questions (Q11: 2) and admits wrong-topic passages (Q06 cyber, Q10 background).
- **Temporal behavior:** correct and conservative under every strategy; see the Q13 section.
