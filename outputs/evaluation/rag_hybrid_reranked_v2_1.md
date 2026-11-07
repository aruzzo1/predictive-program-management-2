# Retrieval benchmark: HYBRID_RERANKED_V2_1

- Strategy: `hybrid_reranked`. Hybrid pool (union of top 30 dense and BM25) re-scored by cross-encoder/ms-marco-MiniLM-L-6-v2 (local cross-encoder, max 512 tokens).
- Store: 848 chunks, RAG_EXPANDED_V2 (10 documents; frozen, see data/metadata/rag_expanded_v2_freeze.json); questions: `data/metadata/rag_evaluation_questions.json` (unedited)
- Run: 2026-10-25T17:35:24+00:00. No LLM; relevance judgments left blank.
- Scores: *strategy score* is this strategy's own score (similarity, BM25, RRF or cross-encoder logit) and is **not comparable across strategies**. *sem* is the dense cosine similarity and *dense/bm25* are whole-store ranks, given for every result.

Mean distinct documents per question 3.0; duplicate suppressions 10; Highlights results 0; agency_comments results 1.

## Q01: software_integration

What evidence indicates that mission-system software maturity affected F-35 flight-test execution?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 4.6081 | 0.6924 | 3 | 1 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c02` | 3.8981 | 0.6761 | 5 | 2 | Development of mission systems software continued to experience delays that affected flight test progress. • Program leadership began re-planning SDD flight testing at the end of FY10, in conjunction with a restructuring of mission systems software development |  |
| 3 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 3.1591 | 0.6965 | 2 | 20 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 4 | DOTE-FY2010-F35 (?) | 30 | `DOTE-FY2010-F35-p030-c05` | 1.8937 | 0.628 | 11 | 10 | However, during the months since the last program review, more problems with STOVL design and mission systems software arose. • The TBR recommended further changes to the parameters used to plan and model flight test schedules, as well as numerous changes in s |  |
| 5 | GAO-10-382 (2010) | 31 | `GAO-10-382-p031-c01` | 1.8603 | 0.6085 | 17 | 24 | All other software increments are behind schedule. Mission system software, in particular, is behind schedule, poses significant integration challenges, and its progress is difficult to assess. Further delays may affect the already delayed first mission system |  |

## Q02: requirements

What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-07-360 (2007) | 17 | `GAO-07-360-p017-c03` | 0.7832 | 0.4654 | 155 | 1 | The JSF Program Projects Key Performance Parameters Will Be Met Based on Modeling and Simulations Currently, the JSF program estimates that by the time the development program ends the aircraft design will meet all but one of its key performance parameters. Th |  |
| 2 | GAO-09-303 (2009) | 25 | `GAO-09-303-p025-c01` | 0.7138 | 0.5336 | 48 | 13 | Early Operational Assessment Identifies Several Challenges That May Have Operational Impact If Not Addressed: While the program is projecting that it will meet all key performance parameters, most will not be verified through ground and flight testing until fi |  |
| 3 | GAO-10-382 (2010) | 36 | `GAO-10-382-p036-c00` | 0.0245 | 0.5624 | 26 | 134 | nondefense priorities for the federal discretionary dollar. As such, it is critical to maintain affordability while moving forward, prudently balancing program, technical, and funding risks with the achievement of warfighter performance requirements. Risks are |  |
| 4 | GAO-07-360 (2007) | 18 | `GAO-07-360-p018-c01` | -0.2317 | 0.5465 | 39 | 9 | Table 3 shows the program’s estimate for each key performance parameter. The JSF program’s acquisition strategy includes significant challenges to achieve projected cost and schedule goals. The program has begun procurement but not yet demonstrated that the ai |  |
| 5 | DOTE-FY2024-F35 (?) | 10 | `DOTE-FY2024-F35-p010-c01` | -0.3216 | 0.5316 | 49 | 2 | Fleet (FY15 – FY23) reliability metrics as shown in Figure 2, based on adjudicated data reported by the JPO. Higher numbers reflect better performance and a more reliable system. Since FY15, there was some reliability improvement with increased variability. In |  |

## Q03: design_engineering_activities

What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 26 | `GAO-11-325-p026-c00` | 4.9192 | 0.633 | 1 | 5 | A key indicator of a product's maturity is the stability of its design. The number of engineering drawings released and subsequent changes provide indicators of the maturity of the design. Engineering drawings are critical because they communicate to the manuf |  |
| 2 | GAO-07-360 (2007) | 16 | `GAO-07-360-p016-c02` | 4.0922 | 0.5389 | 12 | 1 | In February 2006, the program held its critical design review for production representative conventional and short take-off and vertical landing aircraft. At that time, the program had completed 47 percent of the short take-off aircraft design and 3 percent of |  |
| 3 | GAO-10-382 (2010) | 23 | `GAO-10-382-p023-c01` | 3.1942 | 0.5569 | 6 | 4 | base; increases in the amount of on- and out-of-station work required on aircraft in production; and require costly retrofitting of aircraft already produced and fielded. A best practice is to achieve design stability at the system-level critical design review |  |
| 4 | GAO-11-325 (2011) | 18 | `GAO-11-325-p018-c01` | 1.9521 | 0.561 | 5 | 11 | The Program Has Not Yet Stabilized Aircraft Designs: Engineering drawings released since design reviews and the number and rate of design changes are excessive compared to plans and best practices. Critical design reviews were completed on the three aircraft v |  |
| 5 | GAO-05-271 (2005) | 14 | `GAO-05-271-p014-c01` | 1.9442 | 0.4951 | 35 | 6 | One hundred percent of critical manufacturing processes under statistical control, demonstration of a fully integrated product in its operational environment to show it will work as intended, and reliability goals demonstrated. Development start--2001: Knowled |  |

## Q04: test_sequencing

What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 17 | `GAO-11-325-p017-c00` | 0.7653 | 0.5661 | 33 | 5 | Although still hampered as in prior years by the late delivery of test aircraft, flight tests substantially increased in volume and pace at the two main government test sites--Edwards Air Force Base, California, for CTOL tests and Patuxent River Naval Air Stat |  |
| 2 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c04` | 0.6023 | 0.5626 | 35 | 15 | in previous schedules are not achievable in the flight test program until changes are made to all variants that improve reliability and maintainability in flight test operations. Additionally, the process must begin to reduce the aircraft operating limitations |  |
| 3 | GAO-11-325 (2011) | 31 | `GAO-11-325-p031-c03` | 0.4998 | 0.6374 | 8 | 1 | programs have failed to demonstrate that the system works as intended before entering production, discovering costly design problems late in development when the more complex software and advanced capabilities are integrated and tested. Development Flight Test |  |
| 4 | GAO-09-303 (2009) | 11 | `GAO-09-303-p011-c02` | -0.3014 | 0.6383 | 7 | 32 | Continuing delays in delivering test aircraft are expected to hamper and further compress test schedules. In particular, the joint team projects that the two aircraft dedicated to carrier suitability tests will be late off the production line, thereby delaying |  |
| 5 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c01` | -0.3358 | 0.5464 | 53 | 9 | DOT&E assesses that dedicated operational testing of these aircraft will not occur until mid to late FY26, approximately two years after the configuration began delivery to the field. DESCRIPTION The F-35 Joint Strike Fighter (JSF) is a tri-Service, multinatio |  |

## Q05: schedule_dependencies

What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.8475 | 0.5735 | 6 | 14 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | DOTE-FY2010-F35 (?) | 32 | `DOTE-FY2010-F35-p032-c00` | 0.2664 | 0.6176 | 2 | 10 | training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.5 problems, in the mission systems labs and on the CATB. - The program planned t |  |
| 3 | GAO-11-325 (2011) | 36 | `GAO-11-325-p036-c00` | 0.2427 | 0.589 | 5 | 1 | Delays in developing, integrating, and releasing software to the test program have cascading effects hampering flight tests, training, and lab accreditation. While progress is being made, a substantial amount of software work remains before the program can dem |  |
| 4 | DOTE-FY2024-F35 (?) | 3 | `DOTE-FY2024-F35-p003-c05` | -0.9806 | 0.5434 | 9 | 52 | The Increment 3 Annexes, which cover Block 4 and 41P01, and their associated hardware enablers were approved by DOT&E in November 2024. At the time of this report, the program is undergoing a major review of sequencing and prioritizing the series of additional |  |
| 5 | DOTE-FY2010-F35 (?) | 31 | `DOTE-FY2010-F35-p031-c05` | -1.9294 | 0.5394 | 10 | 16 | Block 0.5 is the infrastructure increment, which contains communications, navigation, and limited radar functionality. - Aircraft BF-4, loaded with Block 0.5, accomplished first flight in April 2010, five months later than planned, and then ferried to Patuxent |  |

## Q06: technical_deficiencies

What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 3.8316 | 0.6745 | 1 | 2 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 2 | DOTE-FY2024-F35 (?) | 12 | `DOTE-FY2024-F35-p012-c04` | 1.7162 | 0.5523 | 13 | 5 | time of this report. » SURVIVABILITY Results from the cyber survivability assessment of the supply chain refurbishment practices were under review at the time of this report. Multiple ALIS cyber survivability deficiency reports were created in FY24 based on th |  |
| 3 | GAO-08-388 (2008) | 23 | `GAO-08-388-p023-c03` | 1.1122 | 0.4872 | 54 | 1 | is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may require redesign, production line changes, and retrofit expenses for aircraft already built. On the basis of the evidence, we expect JSF program costs to i |  |
| 4 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | 0.8646 | 0.5646 | 11 | 120 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |
| 5 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 0.4413 | 0.596 | 4 | 3 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |

## Q07: rework_redesign

What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 34 | `GAO-08-388-p034-c02` | 3.1902 | 0.6105 | 1 | 3 | Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase and 18-month extension in the development schedule since the start of system development. While the weight increase has been addressed for now, projec |  |
| 2 | GAO-10-382 (2010) | 33 | `GAO-10-382-p033-c02` | 1.1014 | 0.455 | 36 | 12 | Further, the lack of a production helmet mounted display configuration at this time could result in a major system redesign or change in concept of operations. • Damage to flight deck and runways. The F-35 engine and integrated power package exhaust may cause  |  |
| 3 | GAO-11-325 (2011) | 5 | `GAO-11-325-p005-c02` | -0.8472 | 0.5014 | 10 | 9 | We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on our audit objectives. Background: The F-35 program is a joint, multinational acquisition to develop and field an affordable, highly common family of ste |  |
| 4 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c03` | -1.9949 | 0.525 | 6 | 2 | The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/Earned Value Management (EVM): A review of Acquisition Procurement Unit Cost, Program Acquisition Unit Cost, Operations and Support costs, and EVM cos |  |
| 5 | GAO-08-388 (2008) | 23 | `GAO-08-388-p023-c03` | -2.2194 | 0.3878 | 139 | 10 | is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may require redesign, production line changes, and retrofit expenses for aircraft already built. On the basis of the evidence, we expect JSF program costs to i |  |

## Q08: concurrency

What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-07-360 (2007) | 7 | `GAO-07-360-p007-c00` | 1.0765 | 0.5407 | 13 | 5 | The degree of concurrency between development and production in the JSF program’s acquisition strategy still includes significant risks for cost and schedule overruns or late delivery of promised capabilities to the warfighter. For example, at the time of the  |  |
| 2 | GAO-07-360 (2007) | 20 | `GAO-07-360-p020-c02` | -0.0869 | 0.4554 | 101 | 7 | Past programs have encountered difficulties in developing software, which delayed flight test schedules. JSF program officials acknowledged that the software effort will become particularly challenging during 2007 and 2008 when all five software blocks will be |  |
| 3 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | -0.163 | 0.6341 | 1 | 6 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 4 | GAO-07-360 (2007) | 22 | `GAO-07-360-p022-c00` | -0.6047 | 0.5415 | 10 | 1 | While some concurrency may be beneficial to efficiently transition from the development stage of a program to production, the JSF is currently planned to be significantly more concurrent than the F-22A program that failed to deliver the warfighting capability  |  |
| 5 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c03` | -0.8772 | 0.5558 | 4 | 62 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression  |  |

## Q09: milestone_effects

What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c02` | 2.5514 | 0.5104 | 32 | 23 | Development of mission systems software continued to experience delays that affected flight test progress. • Program leadership began re-planning SDD flight testing at the end of FY10, in conjunction with a restructuring of mission systems software development |  |
| 2 | GAO-10-382 (2010) | 26 | `GAO-10-382-p026-c01` | 1.9755 | 0.4762 | 65 | 21 | Table 6 summarizes recent delays to key JSF test activities Steadily lengthening schedules to complete key system develop efforts further exacerbates the already extreme overlap among development, test, and production activities. Late deliveries of development |  |
| 3 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 1.5472 | 0.6463 | 1 | 24 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 4 | GAO-08-388 (2008) | 14 | `GAO-08-388-p014-c02` | 1.315 | 0.3253 | 528 | 2 | for the most part, but schedules could worsen considerably if the delays in maturing the aircraft and engine designs and manufacturing test aircraft continue to push work effort into later years. This would further compress the time available to complete devel |  |
| 5 | GAO-08-388 (2008) | 19 | `GAO-08-388-p019-c00` | 1.295 | 0.4779 | 60 | 1 | According to our analysis of available evidence, manufacturing test aircraft continue to run behind schedule. The prime contractor has revised the test aircraft manufacturing schedule three times, resulting in slips of up to 16 months in first flight dates of  |  |

## Q10: subsystem_dependencies

What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 2.5456 | 0.6398 | 1 | 2 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | DOTE-FY2010-F35 (?) | 34 | `DOTE-FY2010-F35-p034-c04` | 0.4062 | 0.485 | 32 | 4 | Remain prepared to deal with continued discovery in flight test as more complex testing begins. 3. Determine the impact of resolution of known critical technical issues, including Helmet Mounted Display, STOVL mechanization, handling characteristics, and after |  |
| 3 | GAO-10-382 (2010) | 33 | `GAO-10-382-p033-c02` | 0.0561 | 0.5822 | 2 | 6 | Further, the lack of a production helmet mounted display configuration at this time could result in a major system redesign or change in concept of operations. • Damage to flight deck and runways. The F-35 engine and integrated power package exhaust may cause  |  |
| 4 | GAO-11-325 (2011) | 5 | `GAO-11-325-p005-c02` | -0.8202 | 0.5277 | 19 | 79 | We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on our audit objectives. Background: The F-35 program is a joint, multinational acquisition to develop and field an affordable, highly common family of ste |  |
| 5 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c02` | -1.2834 | 0.4808 | 33 | 7 | Development of mission systems software continued to experience delays that affected flight test progress. • Program leadership began re-planning SDD flight testing at the end of FY10, in conjunction with a restructuring of mission systems software development |  |

## Q11: information_flow

What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-06-356 (2006) | 6 | `GAO-06-356-p006-c01` | -0.594 | 0.4745 | 32 | 3 | the JSF program acquisition strategy captures critical knowledge in time to make production investment decisions and (2) identified an alternative to the current acquisition strategy to improve JSF program outcomes. The act also requires us to certify whether  |  |
| 2 | GAO-06-356 (2006) | 14 | `GAO-06-356-p014-c00` | -0.5943 | 0.4922 | 20 | 4 | Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the number of flight test hours needed to verify that the system will work as intended, and affect when key knowledge will be available for making invest |  |
| 3 | GAO-09-303 (2009) | 25 | `GAO-09-303-p025-c02` | -1.0142 | 0.4627 | 46 | 13 | For example: * The current F-35 power system may cause excessive damage to runway surfaces which could limit its ability to operate in certain locations. The program is still evaluating the problem and plans to gather data and conduct further studies when full |  |
| 4 | GAO-09-303 (2009) | 22 | `GAO-09-303-p022-c00` | -1.4493 | 0.4548 | 57 | 15 | Limited Knowledge Gained From Flight Testing-More Knowledge Gained From Flight Testing. Notes: Flight testing data reflect the percentage of total development flight tests completed at the time of the planned investment decision, which is expected in January o |  |
| 5 | GAO-06-356 (2006) | 28 | `GAO-06-356-p028-c02` | -1.5214 | 0.5416 | 4 | 57 | DOD provided us with written comments on a draft of this report. The comments appear in appendix III. DOD partially concurred with our recommendation that the Secretary of Defense delay the investment in production aircraft until sufficient testing has at leas |  |

## Q12: downstream_cost_schedule

What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 (2010) | 10 | `GAO-10-382-p010-c02` | 0.6106 | 0.5942 | 1 | 14 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Am |  |
| 2 | GAO-08-388 (2008) | 23 | `GAO-08-388-p023-c03` | 0.3434 | 0.4926 | 102 | 1 | is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may require redesign, production line changes, and retrofit expenses for aircraft already built. On the basis of the evidence, we expect JSF program costs to i |  |
| 3 | GAO-10-382 (2010) | 12 | `GAO-10-382-p012-c00` | 0.2562 | 0.5581 | 8 | 11 | Engine cost growth and development delays are also contributing substantially to overall program costs. The F135 primary engine development effort—a separate contract from the airframe development effort—is now estimated to cost about $7.3 billion, a 50 percen |  |
| 4 | GAO-10-382 (2010) | 22 | `GAO-10-382-p022-c02` | -1.8656 | 0.5618 | 5 | 91 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including p |  |
| 5 | GAO-08-388 (2008) | 14 | `GAO-08-388-p014-c01` | -1.9299 | 0.4889 | 111 | 18 | money set aside—in this case about 10 percent of the development contract value remaining—to handle unanticipated changes and other risks encountered as a development program proceeds. Weight growth early in development and subsequent problems resulting from l |  |

## Q13: software_integration

What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 3 | `DOTE-FY2024-F35-p003-c03` | 2.1275 | 0.5483 | 13 | 1 | Block 4 includes DT and OT with aircraft in the TR-2 configuration. For these aircraft, the program has designated flight software using a 30-series designation (i.e., 30RXX for development and flight testing software iterations, and 30PXX for final production |  |
| 2 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c03` | 1.8753 | 0.598 | 6 | 2 | The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rate production in a March 2024 ADM. The full-rate production decision ADM directed the program to designate two major subprograms within the overall acq |  |
| 3 | DOTE-FY2024-F35 (?) | 3 | `DOTE-FY2024-F35-p003-c05` | 1.7828 | 0.5529 | 11 | 11 | The Increment 3 Annexes, which cover Block 4 and 41P01, and their associated hardware enablers were approved by DOT&E in November 2024. At the time of this report, the program is undergoing a major review of sequencing and prioritizing the series of additional |  |
| 4 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 1.6105 | 0.6767 | 2 | 6 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 5 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 0.7645 | 0.6032 | 5 | 16 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
