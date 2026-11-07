# Retrieval benchmark: SEMANTIC_V2

- Strategy: `semantic`. Existing dense retrieval (Chroma cosine, candidate_k 15, near-duplicate suppression), unchanged.
- Store: 848 chunks, RAG_EXPANDED_V2 (10 documents; frozen, see data/metadata/rag_expanded_v2_freeze.json); questions: `data/metadata/rag_evaluation_questions.json` (unedited)
- Run: 2026-10-25T17:35:15+00:00. No LLM; relevance judgments left blank.
- Scores: *strategy score* is this strategy's own score (similarity, BM25, RRF or cross-encoder logit) and is **not comparable across strategies**. *sem* is the dense cosine similarity and *dense/bm25* are whole-store ranks, given for every result.

- Reproduces RAG_EXPANDED_V2 top-5 chunk IDs for all 13 questions: **True**

Mean distinct documents per question 3.23; duplicate suppressions 6; Highlights results 2; agency_comments results 7.

## Q01: software_integration

What evidence indicates that mission-system software maturity affected F-35 flight-test execution?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.7105 | 0.7105 | 1 | 28 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.6965 | 0.6965 | 2 | 20 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 3 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.6924 | 0.6924 | 3 | 1 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 4 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c01` | 0.6912 | 0.6912 | 4 | 5 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For  |  |
| 5 | GAO-05-271 (2005) | 11 | `GAO-05-271-p011-c01` | 0.649 | 0.649 | 7 | 49 | Design and software teams have found greater complexity and less efficiency as they develop the 17 million lines of software needed for the system. Program analysis also indicated that some aircraft capabilities will have to be deferred to stay within cost and |  |

## Q02: requirements

What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c01` | 0.6525 | 0.6525 | 1 | 107 | The approval of a new MS B and APB will reflect these budget decisions. Any significant proposed changes to the F-35 budget in future years will be thoroughly reviewed as part of the annual Defense Acquisition Executive Program Reviews and approved as part of  |  |
| 2 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.6399 | 0.6399 | 2 | 33 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |
| 3 | GAO-11-325 (2011) | 45 | `GAO-11-325-p045-c00` | 0.6373 | 0.6373 | 4 | 234 | metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown ve |  |
| 4 | DOTE-FY2010-F35 (?) | 30 | `DOTE-FY2010-F35-p030-c00` | 0.6221 | 0.6221 | 5 | 179 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia,  |  |
| 5 | GAO-06-356 (2006) | 2 | `GAO-06-356-p002-c04` | 0.6184 | 0.6184 | 6 | 57 | Development costs have increased 84 percent, planned purchases have decreased by 535 aircraft, and the completion of development has slipped 5 years, delaying delivery of capabilities to the warfighter. With more than 90 percent of the JSF investment remaining |  |

## Q03: design_engineering_activities

What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 26 | `GAO-11-325-p026-c00` | 0.633 | 0.633 | 1 | 5 | A key indicator of a product's maturity is the stability of its design. The number of engineering drawings released and subsequent changes provide indicators of the maturity of the design. Engineering drawings are critical because they communicate to the manuf |  |
| 2 | GAO-07-360 (2007) | 21 | `GAO-07-360-p021-c00` | 0.5821 | 0.5821 | 2 | 20 | before ensuring design maturity through flight testing significantly increases the risk because of the of costly design changes that will push the program over budget and behind schedule. Failure to capture key design knowledge before producing aircraft in qua |  |
| 3 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 0.5641 | 0.5641 | 3 | 15 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |
| 4 | GAO-07-360 (2007) | 16 | `GAO-07-360-p016-c01` | 0.5614 | 0.5614 | 4 | 71 | According to the contractor and program officials, these inefficiencies are largely due to late delivery of the wing bulkheads because of a change in their manufacturing process. The Defense Contract Management Agency has rated manufacturing as high risk, stat |  |
| 5 | GAO-11-325 (2011) | 18 | `GAO-11-325-p018-c01` | 0.561 | 0.561 | 5 | 11 | The Program Has Not Yet Stabilized Aircraft Designs: Engineering drawings released since design reviews and the number and rate of design changes are excessive compared to plans and best practices. Critical design reviews were completed on the three aircraft v |  |

## Q04: test_sequencing

What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.7094 | 0.7094 | 1 | 8 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 2 | GAO-07-360 (2007) | 20 | `GAO-07-360-p020-c00` | 0.6892 | 0.6892 | 2 | 21 | manufacture and deliver 15 flight test aircraft and 7 ground test articles in 5 years—an aggressive schedule when compared with other programs with fewer variables. For example, the F-22A program took almost 8 years to manufacture and deliver nine flight test  |  |
| 3 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.6614 | 0.6614 | 3 | 4 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 4 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c01` | 0.6598 | 0.6598 | 4 | 13 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For  |  |
| 5 | GAO-06-356 (2006) | 14 | `GAO-06-356-p014-c00` | 0.6408 | 0.6408 | 5 | 91 | Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the number of flight test hours needed to verify that the system will work as intended, and affect when key knowledge will be available for making invest |  |

## Q05: schedule_dependencies

What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c00` | 0.6223 | 0.6223 | 1 | 32 | In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block  |  |
| 2 | DOTE-FY2010-F35 (?) | 32 | `DOTE-FY2010-F35-p032-c00` | 0.6176 | 0.6176 | 2 | 10 | training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.5 problems, in the mission systems labs and on the CATB. - The program planned t |  |
| 3 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.6094 | 0.6094 | 3 | 17 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 4 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c02` | 0.6034 | 0.6034 | 4 | 44 | as defined in the Block 4 Modernization Capability Development Document (CDD), specifies required capabilities and associated capability gaps that drive incremental improvements under an agile acquisition framework. The missions of the F-35 aircraft include at |  |
| 5 | GAO-11-325 (2011) | 36 | `GAO-11-325-p036-c00` | 0.589 | 0.589 | 5 | 1 | Delays in developing, integrating, and releasing software to the test program have cascading effects hampering flight tests, training, and lab accreditation. While progress is being made, a substantial amount of software work remains before the program can dem |  |

## Q06: technical_deficiencies

What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.6745 | 0.6745 | 1 | 2 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2024-F35 (?) | 8 | `DOTE-FY2024-F35-p008-c01` | 0.5966 | 0.5966 | 3 | 23 | against capabilities in the 30R08 software, many of which were against capabilities that were working in previous versions of software, an indication of insufficient integration and regression testing. Development Although the program and Services have begun a |  |
| 3 | GAO-10-382 (2010) | 22 | `GAO-10-382-p022-c02` | 0.5814 | 0.5814 | 5 | 665 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including p |  |
| 4 | DOTE-FY2024-F35 (?) | 10 | `DOTE-FY2024-F35-p010-c02` | 0.5778 | 0.5778 | 6 | 38 | It includes failures discovered in the air and on the ground. The MFHBCF for the F-35A peaked in FY20 and has declined ever since, although FY23 was only slightly worse than FY22, possibly leveling off in the worsening trend. The F-35B had its highest MFHBCF i |  |
| 5 | DOTE-FY2024-F35 (?) | 13 | `DOTE-FY2024-F35-p013-c02` | 0.5764 | 0.5764 | 7 | 35 | The F-35 JPO and the Services, as appropriate, should: 1. Continue preparations for required F-35 FOT&E in the JSE beginning with the 30R08 capability release. 2. Ensure programming, funding, and contracting are in place to modify sufficient OT aircraft to mee |  |

## Q07: rework_redesign

What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 34 | `GAO-08-388-p034-c02` | 0.6105 | 0.6105 | 1 | 3 | Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase and 18-month extension in the development schedule since the start of system development. While the weight increase has been addressed for now, projec |  |
| 2 | DOTE-FY2024-F35 (?) | 10 | `DOTE-FY2024-F35-p010-c02` | 0.5563 | 0.5563 | 2 | 228 | It includes failures discovered in the air and on the ground. The MFHBCF for the F-35A peaked in FY20 and has declined ever since, although FY23 was only slightly worse than FY22, possibly leveling off in the worsening trend. The F-35B had its highest MFHBCF i |  |
| 3 | DOTE-FY2024-F35 (?) | 8 | `DOTE-FY2024-F35-p008-c01` | 0.5479 | 0.5479 | 3 | 27 | against capabilities in the 30R08 software, many of which were against capabilities that were working in previous versions of software, an indication of insufficient integration and regression testing. Development Although the program and Services have begun a |  |
| 4 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.5466 | 0.5466 | 4 | 40 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |
| 5 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 0.5395 | 0.5395 | 5 | 19 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |

## Q08: concurrency

What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.6341 | 0.6341 | 1 | 6 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | GAO-10-382 (2010) | 22 | `GAO-10-382-p022-c02` | 0.5846 | 0.5846 | 2 | 265 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including p |  |
| 3 | GAO-07-360 (2007) | 21 | `GAO-07-360-p021-c00` | 0.5635 | 0.5635 | 3 | 19 | before ensuring design maturity through flight testing significantly increases the risk because of the of costly design changes that will push the program over budget and behind schedule. Failure to capture key design knowledge before producing aircraft in qua |  |
| 4 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.5558 | 0.5558 | 4 | 62 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 5 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.554 | 0.554 | 5 | 80 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |

## Q09: milestone_effects

What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.6463 | 0.6463 | 1 | 24 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c00` | 0.6223 | 0.6223 | 2 | 14 | In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block  |  |
| 3 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.6023 | 0.6023 | 3 | 137 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 4 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c01` | 0.5866 | 0.5866 | 4 | 70 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For  |  |
| 5 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.5864 | 0.5864 | 5 | 47 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |

## Q10: subsystem_dependencies

What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.6398 | 0.6398 | 1 | 2 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | GAO-10-382 (2010) | 33 | `GAO-10-382-p033-c02` | 0.5822 | 0.5822 | 2 | 6 | Further, the lack of a production helmet mounted display configuration at this time could result in a major system redesign or change in concept of operations. • Damage to flight deck and runways. The F-35 engine and integrated power package exhaust may cause  |  |
| 3 | GAO-11-325 (2011) | 45 | `GAO-11-325-p045-c00` | 0.5773 | 0.5773 | 3 | 44 | metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown ve |  |
| 4 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 0.5735 | 0.5735 | 4 | 20 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |
| 5 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.5731 | 0.5731 | 5 | 77 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |

## Q11: information_flow

What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c00` | 0.5733 | 0.5733 | 1 | 108 | In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block  |  |
| 2 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 0.5518 | 0.5518 | 2 | 31 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |
| 3 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.5438 | 0.5438 | 3 | 40 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 4 | GAO-06-356 (2006) | 28 | `GAO-06-356-p028-c02` | 0.5416 | 0.5416 | 4 | 57 | DOD provided us with written comments on a draft of this report. The comments appear in appendix III. DOD partially concurred with our recommendation that the Secretary of Defense delay the investment in production aircraft until sufficient testing has at leas |  |
| 5 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.5387 | 0.5387 | 5 | 117 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |

## Q12: downstream_cost_schedule

What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.5942 | 0.5942 | 1 | 14 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |
| 2 | GAO-06-356 (2006) | 19 | `GAO-06-356-p019-c01` | 0.5854 | 0.5854 | 2 | 215 | Past single-step development programs have been unsuccessful in predicting acquisition costs and delivery schedules. For example, development costs for the F-22A fighter, B-2 bomber, Crusader artillery vehicle, and Comanche helicopter skyrocketed, and producti |  |
| 3 | GAO-07-360 (2007) | 2 | `GAO-07-360-p002-c02` | 0.5672 | 0.5672 | 3 | 48 | DOD non-concurred, believing its current strategy provides a balance of technical risk, financial constraints, and operational needs. The JSF program has delivered and flown the first development aircraft. However, cost and schedule goals established in the fi |  |
| 4 | GAO-10-382 (2010) | 8 | `GAO-10-382-p008-c01` | 0.5645 | 0.5645 | 4 | 337 | DOD’s funding requirements for the JSF assume economic benefits from these foreign purchases in reducing unit costs for U.S. aircraft. In our March 2009 report, we noted that more money and time would be needed to complete development. At that time, developmen |  |
| 5 | GAO-10-382 (2010) | 22 | `GAO-10-382-p022-c02` | 0.5618 | 0.5618 | 5 | 91 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including p |  |

## Q13: software_integration

What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.6813 | 0.6813 | 1 | 8 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.6767 | 0.6767 | 2 | 6 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 3 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c00` | 0.6181 | 0.6181 | 4 | 21 | In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block  |  |
| 4 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.6032 | 0.6032 | 5 | 16 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 5 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c03` | 0.598 | 0.598 | 6 | 2 | The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rate production in a March 2024 ADM. The full-rate production decision ADM directed the program to designate two major subprograms within the overall acq |  |
