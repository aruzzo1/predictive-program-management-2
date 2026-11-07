# Retrieval benchmark: HYBRID_V2_1

- Strategy: `hybrid`. Reciprocal Rank Fusion (k = 60) of the top 30 dense and top 30 BM25 chunks.
- Store: 848 chunks, RAG_EXPANDED_V2 (10 documents; frozen, see data/metadata/rag_expanded_v2_freeze.json); questions: `data/metadata/rag_evaluation_questions.json` (unedited)
- Run: 2026-10-25T17:35:16+00:00. No LLM; relevance judgments left blank.
- Scores: *strategy score* is this strategy's own score (similarity, BM25, RRF or cross-encoder logit) and is **not comparable across strategies**. *sem* is the dense cosine similarity and *dense/bm25* are whole-store ranks, given for every result.

Mean distinct documents per question 3.08; duplicate suppressions 9; Highlights results 1; agency_comments results 5.

## Q01: software_integration

What evidence indicates that mission-system software maturity affected F-35 flight-test execution?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.032266 | 0.6924 | 3 | 1 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c02` | 0.031514 | 0.6761 | 5 | 2 | Development of mission systems software continued to experience delays that affected flight test progress. • Program leadership began re-planning SDD flight testing at the end of FY10, in conjunction with a restructuring of mission systems software development |  |
| 3 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c02` | 0.031025 | 0.6743 | 6 | 3 | The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Schedule Re-Planning and Implementation of Changes • The year-long process of analyses during FY10 (JET II implementation, Nunn-McCurdy certification, a |  |
| 4 | DOTE-FY2010-F35 (?) | 30 | `DOTE-FY2010-F35-p030-c05` | 0.02837 | 0.628 | 11 | 10 | However, during the months since the last program review, more problems with STOVL design and mission systems software arose. • The TBR recommended further changes to the parameters used to plan and model flight test schedules, as well as numerous changes in s |  |
| 5 | GAO-07-360 (2007) | 20 | `GAO-07-360-p020-c01` | 0.027984 | 0.6361 | 10 | 13 | As discussed earlier, current JSF schedules are already showing that delivery of early test aircraft will be later than the planned delivery date. The flight test program will also hinge on the delivering aircraft with the expected capabilities. JSF’s expected |  |

## Q02: requirements

What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c03` | 0.029236 | 0.5982 | 11 | 6 | The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/Earned Value Management (EVM): A review of Acquisition Procurement Unit Cost, Program Acquisition Unit Cost, Operations and Support costs, and EVM cos |  |
| 2 | GAO-10-382 (2010) | 26 | `GAO-10-382-p026-c02` | 0.026786 | 0.6005 | 10 | 20 | integrating very large and complex softw requirements essential to JSF capabilities, and (3) maturing sev technologies that are essential to meet operational performance and logistical support requirements. Collectively, these testing and developmental challen |  |
| 3 | GAO-06-356 (2006) | 7 | `GAO-06-356-p007-c02` | 0.026754 | 0.6116 | 8 | 23 | The length and scope of work remaining continue to make it difficult to predict the cost and time needed to complete the program. The Air Force’s JSF predecessor, the F-16 Fighter program, provides a model for a less risky alternative JSF acquisition strategy  |  |
| 4 | GAO-11-325 (2011) | 43 | `GAO-11-325-p043-c00` | 0.02642 | 0.6164 | 7 | 27 | The Department remains committed to the F-35 Joint Strike Fighter (JSF) program. The Fiscal Year (FY) 2012 President's Budget (PB) demonstrates this commitment to the F-35 as the backbone of the future tactical aircraft inventory for the Air Force, Navy, Marin |  |
| 5 | GAO-10-382 (2010) | 15 | `GAO-10-382-p015-c00` | 0.02607 | 0.5591 | 28 | 8 | restructuring is complete and a new comprehensive procurement cost estimate is finalized (and expressed in constant-year dollars), we do not know whether unit cost increases will breach the “critical” or “significant” cost growth threshold. Breaches of either  |  |

## Q03: design_engineering_activities

What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 26 | `GAO-11-325-p026-c00` | 0.031778 | 0.633 | 1 | 5 | A key indicator of a product's maturity is the stability of its design. The number of engineering drawings released and subsequent changes provide indicators of the maturity of the design. Engineering drawings are critical because they communicate to the manuf |  |
| 2 | GAO-10-382 (2010) | 23 | `GAO-10-382-p023-c01` | 0.030777 | 0.5569 | 6 | 4 | base; increases in the amount of on- and out-of-station work required on aircraft in production; and require costly retrofitting of aircraft already produced and fielded. A best practice is to achieve design stability at the system-level critical design review |  |
| 3 | GAO-11-325 (2011) | 17 | `GAO-11-325-p017-c02` | 0.030366 | 0.5421 | 9 | 3 | improve oversight and budgeting, holding people accountable for meeting interim objectives and, for objectives not met, providing criteria and a forum for evaluating reasons why and what should be done. Program Has Still Not Fully Demonstrated a Stable Design  |  |
| 4 | GAO-07-360 (2007) | 16 | `GAO-07-360-p016-c02` | 0.030282 | 0.5389 | 12 | 1 | In February 2006, the program held its critical design review for production representative conventional and short take-off and vertical landing aircraft. At that time, the program had completed 47 percent of the short take-off aircraft design and 3 percent of |  |
| 5 | GAO-02-39 (2001) | 8 | `GAO-02-39-p008-c00` | 0.029631 | 0.5425 | 8 | 7 | In our previous work on best business practices, commercial firms have told us that a key part of product development is getting the technology into the right size, weight, and configuration needed for the intended product—in this case, the final Joint Strike  |  |

## Q04: test_sequencing

What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.031498 | 0.6614 | 3 | 4 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.031099 | 0.7094 | 1 | 8 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 3 | GAO-11-325 (2011) | 31 | `GAO-11-325-p031-c03` | 0.031099 | 0.6374 | 8 | 1 | programs have failed to demonstrate that the system works as intended before entering production, discovering costly design problems late in development when the more complex software and advanced capabilities are integrated and tested. Development Flight Test |  |
| 4 | DOTE-FY2024-F35 (?) | 8 | `DOTE-FY2024-F35-p008-c04` | 0.029572 | 0.622 | 13 | 3 | Prior to starting the delivery of TR-3 configured aircraft out of long-term parking in July, 649 aircraft had been delivered to the U.S. Services. These numbers, which provide the basis of analyses contained in this section of the report, do not include any ai |  |
| 5 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c01` | 0.029324 | 0.6598 | 4 | 13 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For  |  |

## Q05: schedule_dependencies

What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 36 | `GAO-11-325-p036-c00` | 0.031778 | 0.589 | 5 | 1 | Delays in developing, integrating, and releasing software to the test program have cascading effects hampering flight tests, training, and lab accreditation. While progress is being made, a substantial amount of software work remains before the program can dem |  |
| 2 | DOTE-FY2010-F35 (?) | 32 | `DOTE-FY2010-F35-p032-c00` | 0.030415 | 0.6176 | 2 | 10 | training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.5 problems, in the mission systems labs and on the CATB. - The program planned t |  |
| 3 | GAO-07-360 (2007) | 20 | `GAO-07-360-p020-c01` | 0.029274 | 0.5294 | 12 | 5 | As discussed earlier, current JSF schedules are already showing that delivery of early test aircraft will be later than the planned delivery date. The flight test program will also hinge on the delivering aircraft with the expected capabilities. JSF’s expected |  |
| 4 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.02886 | 0.6094 | 3 | 17 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 5 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.028665 | 0.5735 | 6 | 14 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |

## Q06: technical_deficiencies

What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.032522 | 0.6745 | 1 | 2 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.031498 | 0.596 | 4 | 3 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 3 | DOTE-FY2024-F35 (?) | 12 | `DOTE-FY2024-F35-p012-c04` | 0.029083 | 0.5523 | 13 | 5 | time of this report. » SURVIVABILITY Results from the cyber survivability assessment of the supply chain refurbishment practices were under review at the time of this report. Multiple ALIS cyber survivability deficiency reports were created in FY24 based on th |  |
| 4 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.026876 | 0.5403 | 17 | 12 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |
| 5 | DOTE-FY2024-F35 (?) | 10 | `DOTE-FY2024-F35-p010-c01` | 0.026334 | 0.5398 | 18 | 14 | Fleet (FY15 – FY23) reliability metrics as shown in Figure 2, based on adjudicated data reported by the JPO. Higher numbers reflect better performance and a more reliable system. Since FY15, there was some reliability improvement with increased variability. In |  |

## Q07: rework_redesign

What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 34 | `GAO-08-388-p034-c02` | 0.032266 | 0.6105 | 1 | 3 | Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase and 18-month extension in the development schedule since the start of system development. While the weight increase has been addressed for now, projec |  |
| 2 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c03` | 0.031281 | 0.525 | 6 | 2 | The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/Earned Value Management (EVM): A review of Acquisition Procurement Unit Cost, Program Acquisition Unit Cost, Operations and Support costs, and EVM cos |  |
| 3 | GAO-11-325 (2011) | 5 | `GAO-11-325-p005-c02` | 0.028778 | 0.5014 | 10 | 9 | We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on our audit objectives. Background: The F-35 program is a joint, multinational acquisition to develop and field an affordable, highly common family of ste |  |
| 4 | GAO-05-271 (2005) | 9 | `GAO-05-271-p009-c01` | 0.028405 | 0.5041 | 8 | 13 | these costs had increased by $9.6 billion largely because of a 36-month schedule extension to allow more time to mature the mission systems and a more mature cost estimate. By 2004, costs increased an additional $10.4 billion to $44.8 billion. The program offi |  |
| 5 | GAO-10-382 (2010) | 7 | `GAO-10-382-p007-c02` | 0.027673 | 0.4768 | 23 | 4 | The carrier-suitable variant (CV) will provide the Navy a multi-role, stealthy strike aircraft to complement the F/A-18E/F Super Hornet. Background The program began in November 1996 with a 5-year competition between Lockheed Martin and Boeing to determine the |  |

## Q08: concurrency

What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.031545 | 0.6341 | 1 | 6 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | GAO-07-360 (2007) | 22 | `GAO-07-360-p022-c00` | 0.030679 | 0.5415 | 10 | 1 | While some concurrency may be beneficial to efficiently transition from the development stage of a program to production, the JSF is currently planned to be significantly more concurrent than the F-22A program that failed to deliver the warfighting capability  |  |
| 3 | GAO-07-360 (2007) | 7 | `GAO-07-360-p007-c00` | 0.029083 | 0.5407 | 13 | 5 | The degree of concurrency between development and production in the JSF program’s acquisition strategy still includes significant risks for cost and schedule overruns or late delivery of promised capabilities to the warfighter. For example, at the time of the  |  |
| 4 | GAO-07-360 (2007) | 21 | `GAO-07-360-p021-c00` | 0.028531 | 0.5635 | 3 | 19 | before ensuring design maturity through flight testing significantly increases the risk because of the of costly design changes that will push the program over budget and behind schedule. Failure to capture key design knowledge before producing aircraft in qua |  |
| 5 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 0.027894 | 0.5164 | 25 | 2 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |

## Q09: milestone_effects

What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 5 | `DOTE-FY2024-F35-p005-c00` | 0.030331 | 0.5744 | 8 | 4 | associated timelines, DOT&E estimates that DOTs of TR-3 aircraft will likely not begin in earnest until mid to late FY26, two years after the aircraft began being delivered to field units. If readiness criteria involving modifications, instrumentation, OABS an |  |
| 2 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c00` | 0.029643 | 0.6223 | 2 | 14 | In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block  |  |
| 3 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.028298 | 0.6463 | 1 | 24 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 4 | GAO-10-382 (2010) | 9 | `GAO-10-382-p009-c01` | 0.027746 | 0.5397 | 18 | 7 | contractor capabilities and plans for ramping-up and sustaining production at maximum rates, and the Joint Assessment Team (JAT) reviewed F135 engine costs and affordability projections. Among other actions, the restructuring (1) increased funding for the JSF  |  |
| 5 | GAO-09-303 (2009) | 25 | `GAO-09-303-p025-c02` | 0.026541 | 0.5308 | 23 | 9 | For example: * The current F-35 power system may cause excessive damage to runway surfaces which could limit its ability to operate in certain locations. The program is still evaluating the problem and plans to gather data and conduct further studies when full |  |

## Q10: subsystem_dependencies

What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.032522 | 0.6398 | 1 | 2 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | GAO-10-382 (2010) | 33 | `GAO-10-382-p033-c02` | 0.031281 | 0.5822 | 2 | 6 | Further, the lack of a production helmet mounted display configuration at this time could result in a major system redesign or change in concept of operations. • Damage to flight deck and runways. The F-35 engine and integrated power package exhaust may cause  |  |
| 3 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 0.028125 | 0.5735 | 4 | 20 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |
| 4 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c02` | 0.027973 | 0.5507 | 11 | 12 | The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Schedule Re-Planning and Implementation of Changes • The year-long process of analyses during FY10 (JET II implementation, Nunn-McCurdy certification, a |  |
| 5 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c01` | 0.027072 | 0.5342 | 17 | 11 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For  |  |

## Q11: information_flow

What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-06-356 (2006) | 6 | `GAO-06-356-p006-c00` | 0.031054 | 0.5225 | 7 | 2 | case be accompanied by a knowledge-based acquisition approach approach that ensures attainment and use of demonstrated product knowledge before making future investments. In commenting on our report, DOD stated that JSF’s restructured acquisition plan would in |  |
| 2 | GAO-06-356 (2006) | 14 | `GAO-06-356-p014-c00` | 0.028125 | 0.4922 | 20 | 4 | Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the number of flight test hours needed to verify that the system will work as intended, and affect when key knowledge will be available for making invest |  |
| 3 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c01` | 0.025816 | 0.4945 | 19 | 16 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For  |  |
| 4 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c00` | 0.016393 | 0.5733 | 1 | 108 | In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block  |  |
| 5 | GAO-05-271 (2005) | 24 | `GAO-05-271-p024-c00` | 0.016393 | 0.4432 | 78 | 1 | Defense's (DOD) acquisition program management office and prime contractor. To evaluate whether the current acquisition plan follows an evolutionary, knowledge-based approach to meeting business case goals in the future, we applied GAO's methodology for assess |  |

## Q12: downstream_cost_schedule

What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.029907 | 0.5942 | 1 | 14 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |
| 2 | GAO-10-382 (2010) | 12 | `GAO-10-382-p012-c00` | 0.02879 | 0.5581 | 8 | 11 | Engine cost growth and development delays are also contributing substantially to overall program costs. The F135 primary engine development effort—a separate contract from the airframe development effort—is now estimated to cost about $7.3 billion, a 50 percen |  |
| 3 | GAO-10-382 (2010) | 14 | `GAO-10-382-p014-c01` | 0.028624 | 0.5584 | 7 | 13 | assessment was based on the production profile before the changes made by the restructuring, it is not directly comparable to the budget estimate, but we agree with its underlying basis. NAVAIR officials projected higher future procurement costs due to continu |  |
| 4 | GAO-08-388 (2008) | 2 | `GAO-08-388-p002-c04` | 0.026334 | 0.553 | 10 | 23 | be fourth, manufacturing schedule, but test aircraft in manufacturing are still behind, the continuing impacts of late designs, delayed delivery of parts, and manufacturing inefficiencies. We believe that JSF costs will likely be much higher than reported. The |  |
| 5 | GAO-09-303 (2009) | 15 | `GAO-09-303-p015-c04` | 0.026121 | 0.5581 | 9 | 26 | Time and Money Needed for Manufacturing Development Test Aircraft Continue to Increase: The prime contractor has restructured the JSF manufacturing schedule three times, each time lengthening the time to deliver aircraft to the test program. Delays and manufac |  |

## Q13: software_integration

What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c03` | 0.031281 | 0.598 | 6 | 2 | The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rate production in a March 2024 ADM. The full-rate production decision ADM directed the program to designate two major subprograms within the overall acq |  |
| 2 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.031281 | 0.6767 | 2 | 6 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 3 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 0.031099 | 0.6813 | 1 | 8 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 4 | DOTE-FY2024-F35 (?) | 3 | `DOTE-FY2024-F35-p003-c03` | 0.030092 | 0.5483 | 13 | 1 | Block 4 includes DT and OT with aircraft in the TR-2 configuration. For these aircraft, the program has designated flight software using a 30-series designation (i.e., 30RXX for development and flight testing software iterations, and 30PXX for final production |  |
| 5 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.028543 | 0.6032 | 5 | 16 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
