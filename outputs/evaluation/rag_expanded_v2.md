# RAG Baseline Evaluation: rag_expanded_v2

- Run: 2026-10-25T16:53:07+00:00
- Stage: baseline semantic retrieval only (no LLM, no automatic grading)
- Store: `data/processed/chroma`, collection `jsf_corpus`, 848 chunks, 10 documents (ingested 2026-10-25T16:51:46+00:00)
- Retrieval: sentence-transformers/all-MiniLM-L6-v2, top_k=5, candidate_k=15, chunks 220/35 tokens, dedup >= 12 shared words
- Questions: `data/metadata/rag_evaluation_questions.json` (13 questions)

Similarity is cosine similarity (1 - Chroma cosine distance). It measures closeness of embeddings, **not** relevance. All relevance judgments below are left blank for human review.

Judgment values: `RELEVANT`, `PARTIALLY_RELEVANT`, `NOT_RELEVANT`, `NEEDS_REVIEW`

## Objective summary

| ID | Category | Expected | Top sim. | Mean top-5 | Docs | Suppressed | Rank-1 document |
|---|---|---|---|---|---|---|---|
| Q01 | software_integration | YES | 0.7105 | 0.6879 | 3 | 2 | DOTE-FY2024-F35 |
| Q02 | requirements | PARTIAL | 0.6525 | 0.6340 | 4 | 1 | GAO-11-325 |
| Q03 | design_engineering_activities | PARTIAL | 0.6330 | 0.5803 | 2 | 0 | GAO-11-325 |
| Q04 | test_sequencing | YES | 0.7094 | 0.6721 | 4 | 0 | DOTE-FY2010-F35 |
| Q05 | schedule_dependencies | PARTIAL | 0.6223 | 0.6083 | 3 | 0 | DOTE-FY2024-F35 |
| Q06 | technical_deficiencies | PARTIAL | 0.6745 | 0.6013 | 2 | 2 | DOTE-FY2024-F35 |
| Q07 | rework_redesign | UNKNOWN | 0.6105 | 0.5602 | 4 | 0 | GAO-08-388 |
| Q08 | concurrency | YES | 0.6341 | 0.5784 | 4 | 0 | DOTE-FY2024-F35 |
| Q09 | milestone_effects | YES | 0.6463 | 0.6088 | 3 | 0 | DOTE-FY2024-F35 |
| Q10 | subsystem_dependencies | PARTIAL | 0.6398 | 0.5892 | 4 | 0 | DOTE-FY2010-F35 |
| Q11 | information_flow | PARTIAL | 0.5733 | 0.5498 | 4 | 0 | DOTE-FY2024-F35 |
| Q12 | downstream_cost_schedule | PARTIAL | 0.5942 | 0.5746 | 3 | 0 | GAO-10-382 |
| Q13 | software_integration | NO | 0.6813 | 0.6355 | 2 | 1 | DOTE-FY2024-F35 |

Mean top similarity 0.6447; mean of mean top-5 similarity 0.6062; mean distinct documents per question 3.23; duplicate suppression events 6.

## Source concentration across all results

| Document | Results | Share of results | Chunks in store | Share of store | Representation ratio | Rank-1 count |
|---|---|---|---|---|---|---|
| DOTE-FY2010-F35 | 14 | 21.5% | 34 | 4.0% | 5.37 | 2 |
| DOTE-FY2024-F35 | 21 | 32.3% | 60 | 7.1% | 4.57 | 7 |
| GAO-02-39 | 0 | 0.0% | 41 | 4.8% | 0.00 | 0 |
| GAO-05-271 | 1 | 1.5% | 90 | 10.6% | 0.14 | 0 |
| GAO-06-356 | 4 | 6.2% | 77 | 9.1% | 0.68 | 0 |
| GAO-07-360 | 5 | 7.7% | 68 | 8.0% | 0.96 | 0 |
| GAO-08-388 | 1 | 1.5% | 128 | 15.1% | 0.10 | 1 |
| GAO-09-303 | 0 | 0.0% | 120 | 14.2% | 0.00 | 0 |
| GAO-10-382 | 9 | 13.8% | 112 | 13.2% | 1.05 | 1 |
| GAO-11-325 | 10 | 15.4% | 118 | 13.9% | 1.11 | 2 |

Representation ratio = share of results / share of store (1.00 = proportional).

Chunks returned for more than one question: `DOTE-FY2024-F35-p002-c00` (7x), `DOTE-FY2010-F35-p033-c03` (5x), `DOTE-FY2010-F35-p033-c05` (4x), `GAO-10-382-p010-c02` (4x), `GAO-11-325-p044-c02` (4x), `DOTE-FY2024-F35-p001-c00` (4x), `DOTE-FY2010-F35-p029-c01` (3x), `DOTE-FY2024-F35-p007-c00` (3x), `GAO-10-382-p022-c02` (3x), `GAO-11-325-p045-c00` (2x), `GAO-07-360-p021-c00` (2x), `DOTE-FY2024-F35-p008-c01` (2x), `DOTE-FY2024-F35-p010-c02` (2x)

## Results by question

### Q01: software_integration

**Question:** What evidence indicates that mission-system software maturity affected F-35 flight-test execution?

- Why it matters: Benchmark dependency (Software Maturity -> Flight-Test Execution). It is the candidate dependency already used by the grounded prompt and verifier.
- Expected evidence type: Statements linking software delivery or maturity to flight-test points, sorties, re-flights, or test-schedule changes.
- Prior expectation for current corpus: **YES** (Prototype benchmark query; earlier traces returned DOT&E FY2010 passages that discuss software and flight test together.)
- Results 5, distinct documents 3 {'DOTE-FY2024-F35': 1, 'DOTE-FY2010-F35': 3, 'GAO-05-271': 1}, suppressed 2 (of 15 candidates), top 0.7105, mean 0.6879

**#1** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.7105 | original rank 1

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `DOTE-FY2010-F35-p033-c03` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.6965 | original rank 2

> F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2010-F35-p033-c05` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.6924 | original rank 3

> advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2010-F35-p029-c01` | DOTE-FY2010-F35 | PDF p. 29 (printed 13) | similarity 0.6912 | original rank 4

> teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-05-271-p011-c01` | GAO-05-271 | PDF p. 11 (printed n/a) | similarity 0.6490 | original rank 7

> Design and software teams have found greater complexity and less efficiency as they develop the 17 million lines of software needed for the system. Program analysis also indicated that some aircraft capabilities will have to be deferred to stay within cost and schedule constraints. As a result, the program office is working with the warfighters to determine what capabilities could be deferred to ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

- Suppressed `DOTE-FY2010-F35-p029-c02` (original rank 5, similarity 0.6761): duplicate of `DOTE-FY2010-F35-p029-c01`, 14 shared words
- Suppressed `DOTE-FY2010-F35-p033-c02` (original rank 6, similarity 0.6743): duplicate of `DOTE-FY2010-F35-p033-c03`, 26 shared words

**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q02: requirements

**Question:** What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?

- Why it matters: Requirements volatility is an upstream driver in the DSM; change to requirements propagates into design and test rework.
- Expected evidence type: Statements on capability deferral, requirement changes or relaxations, or capability shortfalls tied to cost, schedule, or technical problems.
- Prior expectation for current corpus: **PARTIAL** (The GAO-10-382 title refers to risk of not meeting warfighter requirements on time; the depth of requirement-level detail is unverified.)
- Results 5, distinct documents 4 {'GAO-11-325': 2, 'GAO-10-382': 1, 'DOTE-FY2010-F35': 1, 'GAO-06-356': 1}, suppressed 1 (of 15 candidates), top 0.6525, mean 0.6340

**#1** `GAO-11-325-p044-c01` | GAO-11-325 | PDF p. 44 (printed n/a) | similarity 0.6525 | original rank 1 | section agency_comments

> The approval of a new MS B and APB will reflect these budget decisions. Any significant proposed changes to the F-35 budget in future years will be thoroughly reviewed as part of the annual Defense Acquisition Executive Program Reviews and approved as part of the budget review and submission process. Recommendation 2: The GAO recommends that the Secretary of Defense to establish criteria for the ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-10-382-p010-c02` | GAO-10-382 | PDF p. 10 (printed 6) | similarity 0.6399 | original rank 2

> According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `GAO-11-325-p045-c00` | GAO-11-325 | PDF p. 45 (printed n/a) | similarity 0.6373 | original rank 4 | section agency_comments

> metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown versus actual test flights flown (delineated by STOVL variant); and Clean-Wing Flight Envelope coverage (to assess the progress on the ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2010-F35-p030-c00` | DOTE-FY2010-F35 | PDF p. 30 (printed 14) | similarity 0.6221 | original rank 5

> • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-06-356-p002-c04` | GAO-06-356 | PDF p. 2 (printed n/a) | similarity 0.6184 | original rank 6 | section highlights

> Development costs have increased 84 percent, planned purchases have decreased by 535 aircraft, and the completion of development has slipped 5 years, delaying delivery of capabilities to the warfighter. With more than 90 percent of the JSF investment remaining, DOD officials have the opportunity to adopt a knowledge-based and evolutionary acquisition strategy that would maximize DOD’s return on ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

- Suppressed `GAO-11-325-p044-c02` (original rank 3, similarity 0.6375): duplicate of `GAO-11-325-p044-c01`, 26 shared words

**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q03: design_engineering_activities

**Question:** What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?

- Why it matters: Design-maturity measures are observable engineering-activity states. They supply DSM activity definitions and readiness criteria.
- Expected evidence type: Percentages or counts of released drawings, design-review outcomes, and statements about design stability at production decisions.
- Prior expectation for current corpus: **PARTIAL** (GAO JSF reports from this period assess knowledge-based readiness for production; specific measures may be in tables that are not indexed.)
- Results 5, distinct documents 2 {'GAO-11-325': 3, 'GAO-07-360': 2}, suppressed 0 (of 15 candidates), top 0.6330, mean 0.5803

**#1** `GAO-11-325-p026-c00` | GAO-11-325 | PDF p. 26 (printed n/a) | similarity 0.6330 | original rank 1

> A key indicator of a product's maturity is the stability of its design. The number of engineering drawings released and subsequent changes provide indicators of the maturity of the design. Engineering drawings are critical because they communicate to the manufacturer and suppliers how the part functions, what it looks like, and what materials and critical processes are used to build the product. ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-07-360-p021-c00` | GAO-07-360 | PDF p. 21 (printed 17) | similarity 0.5821 | original rank 2

> before ensuring design maturity through flight testing significantly increases the risk because of the of costly design changes that will push the program over budget and behind schedule. Failure to capture key design knowledge before producing aircraft in quantity can lead to problems that eventually cascade and become magnified through the product development and production phases. Figure 5 is ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `GAO-11-325-p044-c02` | GAO-11-325 | PDF p. 44 (printed n/a) | similarity 0.5641 | original rank 3 | section agency_comments

> The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `GAO-07-360-p016-c01` | GAO-07-360 | PDF p. 16 (printed 12) | similarity 0.5614 | original rank 4

> According to the contractor and program officials, these inefficiencies are largely due to late delivery of the wing bulkheads because of a change in their manufacturing process. The Defense Contract Management Agency has rated manufacturing as high risk, stating that the primary cause of risk is the late delivery of parts to properly support the manufacturing work flow. It projects further ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-11-325-p018-c01` | GAO-11-325 | PDF p. 18 (printed n/a) | similarity 0.5610 | original rank 5

> The Program Has Not Yet Stabilized Aircraft Designs: Engineering drawings released since design reviews and the number and rate of design changes are excessive compared to plans and best practices. Critical design reviews were completed on the three aircraft variants in 2006 and 2007 and the designs declared mature, but the program continues to experience numerous changes. Since 2007, the program ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q04: test_sequencing

**Question:** What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?

- Why it matters: Test-asset availability gates the test sequence. It is a resource dependency for the simulation layer.
- Expected evidence type: Statements on test-aircraft delivery dates, aircraft available vs. planned, flight rates, and their effect on test progress.
- Prior expectation for current corpus: **YES** (Inventory topic notes for GAO-10-382 cite late test aircraft and slow flight testing; the DOT&E FY2010 chapter covers 2010 flight-test progress.)
- Results 5, distinct documents 4 {'DOTE-FY2010-F35': 2, 'GAO-07-360': 1, 'DOTE-FY2024-F35': 1, 'GAO-06-356': 1}, suppressed 0 (of 15 candidates), top 0.7094, mean 0.6721

**#1** `DOTE-FY2010-F35-p033-c03` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.7094 | original rank 1

> F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-07-360-p020-c00` | GAO-07-360 | PDF p. 20 (printed 16) | similarity 0.6892 | original rank 2

> manufacture and deliver 15 flight test aircraft and 7 ground test articles in 5 years—an aggressive schedule when compared with other programs with fewer variables. For example, the F-22A program took almost 8 years to manufacture and deliver nine flight test aircraft and two ground test articles of a single aircraft design. When the B-2 program began flight testing in July 1989, it estimated ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.6614 | original rank 3

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2010-F35-p029-c01` | DOTE-FY2010-F35 | PDF p. 29 (printed 13) | similarity 0.6598 | original rank 4

> teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-06-356-p014-c00` | GAO-06-356 | PDF p. 14 (printed 10) | similarity 0.6408 | original rank 5

> Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the number of flight test hours needed to verify that the system will work as intended, and affect when key knowledge will be available for making investment decisions. For example, when the B-2 program began flight testing in July 1989, it estimated that the flight test program would last ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q05: schedule_dependencies

**Question:** What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?

- Why it matters: Block-to-block precedence and deferral is a schedule dependency chain and a source of capability migration (rework).
- Expected evidence type: Block definitions (e.g., Block 1, 2, 3), planned vs. actual release dates, and capability moved from one block to a later one.
- Prior expectation for current corpus: **PARTIAL** (The DOT&E FY2010 chapter mentions Block 2 and Block 3 software and deferrals to later increments; complete block sequencing is unverified.)
- Results 5, distinct documents 3 {'DOTE-FY2024-F35': 3, 'DOTE-FY2010-F35': 1, 'GAO-11-325': 1}, suppressed 0 (of 15 candidates), top 0.6223, mean 0.6083

**#1** `DOTE-FY2024-F35-p001-c00` | DOTE-FY2024-F35 | PDF p. 1 (printed 44) | similarity 0.6223 | original rank 1

> In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration, in terms of its operational effectiveness, suitability, and survivability. The report included a separate annex that ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `DOTE-FY2010-F35-p032-c00` | DOTE-FY2010-F35 | PDF p. 32 (printed 16) | similarity 0.6176 | original rank 2

> training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.5 problems, in the mission systems labs and on the CATB. - The program planned to release the first Block 1 increment to flight test aircraft in August 2010, but F-35 flight testing did not begin until November 2010. By ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2024-F35-p007-c00` | DOTE-FY2024-F35 | PDF p. 7 (printed 50) | similarity 0.6094 | original rank 3

> PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration in terms of its operational effectiveness, suitability, and survivability. The report ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2024-F35-p002-c02` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.6034 | original rank 4

> as defined in the Block 4 Modernization Capability Development Document (CDD), specifies required capabilities and associated capability gaps that drive incremental improvements under an agile acquisition framework. The missions of the F-35 aircraft include attacking fixed and mobile land targets, surface combatants at sea, and air threats, including advanced aircraft and cruise missiles, in ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-11-325-p036-c00` | GAO-11-325 | PDF p. 36 (printed n/a) | similarity 0.5890 | original rank 5

> Delays in developing, integrating, and releasing software to the test program have cascading effects hampering flight tests, training, and lab accreditation. While progress is being made, a substantial amount of software work remains before the program can demonstrate full warfighting capability. The program released block 0.5 for flight test nearly 2 years later than planned in the 2006 plan, ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q06: technical_deficiencies

**Question:** What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?

- Why it matters: Discovered deficiencies drive rework loops. They are central to the WTM and system-dynamics rework structure.
- Expected evidence type: Named deficiencies (e.g., structural, propulsion, STOVL, helmet) with the corrective action and any retest or retrofit.
- Prior expectation for current corpus: **PARTIAL** (Inventory topic notes mention STOVL design changes and test-discovered problems (DOT&E FY2010, GAO-11-325); whether corrective actions are described is unverified.)
- Results 5, distinct documents 2 {'DOTE-FY2024-F35': 4, 'GAO-10-382': 1}, suppressed 2 (of 15 candidates), top 0.6745, mean 0.6013

**#1** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.6745 | original rank 1

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `DOTE-FY2024-F35-p008-c01` | DOTE-FY2024-F35 | PDF p. 8 (printed 51) | similarity 0.5966 | original rank 3

> against capabilities in the 30R08 software, many of which were against capabilities that were working in previous versions of software, an indication of insufficient integration and regression testing. Development Although the program and Services have begun accepting aircraft off the production line, as well as those coming out of long-term parking over the last year, no OT has been completed to ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `GAO-10-382-p022-c02` | GAO-10-382 | PDF p. 22 (printed 18) | similarity 0.5814 | original rank 5

> Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontractor management issues, and test failures. Engine redesigns and manufacturing problems caused ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2024-F35-p010-c02` | DOTE-FY2024-F35 | PDF p. 10 (printed 53) | similarity 0.5778 | original rank 6

> It includes failures discovered in the air and on the ground. The MFHBCF for the F-35A peaked in FY20 and has declined ever since, although FY23 was only slightly worse than FY22, possibly leveling off in the worsening trend. The F-35B had its highest MFHBCF in FY21, declined significantly in FY22, but then regained some ground in FY23 while remaining below requirement. It has approached, but ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `DOTE-FY2024-F35-p013-c02` | DOTE-FY2024-F35 | PDF p. 13 (printed 56) | similarity 0.5764 | original rank 7

> The F-35 JPO and the Services, as appropriate, should: 1. Continue preparations for required F-35 FOT&E in the JSE beginning with the 30R08 capability release. 2. Ensure programming, funding, and contracting are in place to modify sufficient OT aircraft to meet operational test requirements, including 4-ship test formations for each variant, with the appropriate capabilities, life limit, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

- Suppressed `DOTE-FY2024-F35-p003-c02` (original rank 2, similarity 0.5973): duplicate of `DOTE-FY2024-F35-p002-c00`, 20 shared words
- Suppressed `DOTE-FY2024-F35-p007-c00` (original rank 4, similarity 0.5960): duplicate of `DOTE-FY2024-F35-p008-c01`, 17 shared words

**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q07: rework_redesign

**Question:** What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?

- Why it matters: Weight growth is a classic design-rework driver with cross-subsystem propagation.
- Expected evidence type: Statements on weight margins, weight-reduction redesign efforts, and the resulting schedule or cost impact.
- Prior expectation for current corpus: **UNKNOWN** (The weight-driven redesign predates GAO-06-356, so later reports may refer back to it; whether the indexed text discusses it is unverified.)
- Results 5, distinct documents 4 {'GAO-08-388': 1, 'DOTE-FY2024-F35': 2, 'GAO-10-382': 1, 'GAO-11-325': 1}, suppressed 0 (of 15 candidates), top 0.6105, mean 0.5602

**#1** `GAO-08-388-p034-c02` | GAO-08-388 | PDF p. 34 (printed 29) | similarity 0.6105 | original rank 1

> Redesign efforts to address weight growth was the single largest factor causing the $10 billion cost increase and 18-month extension in the development schedule since the start of system development. While the weight increase has been addressed for now, projections are that the aircraft weight will continue to increase during the balance of the development period, consistent with weight increases ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `DOTE-FY2024-F35-p010-c02` | DOTE-FY2024-F35 | PDF p. 10 (printed 53) | similarity 0.5563 | original rank 2

> It includes failures discovered in the air and on the ground. The MFHBCF for the F-35A peaked in FY20 and has declined ever since, although FY23 was only slightly worse than FY22, possibly leveling off in the worsening trend. The F-35B had its highest MFHBCF in FY21, declined significantly in FY22, but then regained some ground in FY23 while remaining below requirement. It has approached, but ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2024-F35-p008-c01` | DOTE-FY2024-F35 | PDF p. 8 (printed 51) | similarity 0.5479 | original rank 3

> against capabilities in the 30R08 software, many of which were against capabilities that were working in previous versions of software, an indication of insufficient integration and regression testing. Development Although the program and Services have begun accepting aircraft off the production line, as well as those coming out of long-term parking over the last year, no OT has been completed to ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `GAO-10-382-p010-c02` | GAO-10-382 | PDF p. 10 (printed 6) | similarity 0.5466 | original rank 4

> According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-11-325-p044-c02` | GAO-11-325 | PDF p. 44 (printed n/a) | similarity 0.5395 | original rank 5 | section agency_comments

> The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q08: concurrency

**Question:** What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?

- Why it matters: Concurrency is the central dependency theme for the DSM. Production committed before test knowledge creates downstream rework.
- Expected evidence type: Statements on low-rate initial production quantities committed before testing, the overlap of test and production schedules, and the risks of that overlap.
- Prior expectation for current corpus: **YES** (The GAO-06-356 title states that production would start before testing demonstrates acceptable performance; GAO-09-303 covers accelerated procurement.)
- Results 5, distinct documents 4 {'DOTE-FY2024-F35': 1, 'GAO-10-382': 1, 'GAO-07-360': 1, 'DOTE-FY2010-F35': 2}, suppressed 0 (of 15 candidates), top 0.6341, mean 0.5784

**#1** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.6341 | original rank 1

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-10-382-p022-c02` | GAO-10-382 | PDF p. 22 (printed 18) | similarity 0.5846 | original rank 2

> Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontractor management issues, and test failures. Engine redesigns and manufacturing problems caused ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `GAO-07-360-p021-c00` | GAO-07-360 | PDF p. 21 (printed 17) | similarity 0.5635 | original rank 3

> before ensuring design maturity through flight testing significantly increases the risk because of the of costly design changes that will push the program over budget and behind schedule. Failure to capture key design knowledge before producing aircraft in quantity can lead to problems that eventually cascade and become magnified through the product development and production phases. Figure 5 is ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2010-F35-p033-c03` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.5558 | original rank 4

> F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `DOTE-FY2010-F35-p033-c05` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.5540 | original rank 5

> advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q09: milestone_effects

**Question:** What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?

- Why it matters: Milestone slips are the observable outputs the predictive layer must reproduce.
- Expected evidence type: Original vs. revised milestone dates and the stated reason for each change.
- Prior expectation for current corpus: **YES** (GAO-11-325 covers the 2010 restructuring, and GAO-10-382 covers delays; milestone tables may not be indexed, but the prose likely states the slips.)
- Results 5, distinct documents 3 {'DOTE-FY2024-F35': 2, 'DOTE-FY2010-F35': 2, 'GAO-10-382': 1}, suppressed 0 (of 15 candidates), top 0.6463, mean 0.6088

**#1** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.6463 | original rank 1

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `DOTE-FY2024-F35-p001-c00` | DOTE-FY2024-F35 | PDF p. 1 (printed 44) | similarity 0.6223 | original rank 2

> In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration, in terms of its operational effectiveness, suitability, and survivability. The report included a separate annex that ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2010-F35-p033-c03` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.6023 | original rank 3

> F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2010-F35-p029-c01` | DOTE-FY2010-F35 | PDF p. 29 (printed 13) | similarity 0.5866 | original rank 4

> teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-10-382-p010-c02` | GAO-10-382 | PDF p. 10 (printed 6) | similarity 0.5864 | original rank 5

> According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q10: subsystem_dependencies

**Question:** What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?

- Why it matters: Subsystem-to-subsystem coupling defines off-diagonal DSM entries.
- Expected evidence type: Statements that a problem or delay in one subsystem blocked or delayed integration or testing of another.
- Prior expectation for current corpus: **PARTIAL** (Earlier DOT&E FY2010 retrievals mention the helmet-mounted display gating Block 2 flight test; broader subsystem coupling is unverified.)
- Results 5, distinct documents 4 {'DOTE-FY2010-F35': 1, 'GAO-10-382': 1, 'GAO-11-325': 2, 'DOTE-FY2024-F35': 1}, suppressed 0 (of 15 candidates), top 0.6398, mean 0.5892

**#1** `DOTE-FY2010-F35-p033-c05` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.6398 | original rank 1

> advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-10-382-p033-c02` | GAO-10-382 | PDF p. 33 (printed 29) | similarity 0.5822 | original rank 2

> Further, the lack of a production helmet mounted display configuration at this time could result in a major system redesign or change in concept of operations. • Damage to flight deck and runways. The F-35 engine and integrated power package exhaust may cause excessive damage to the flight deck environment and runway surfaces that may result in operating limits or drive costly upgrades and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `GAO-11-325-p045-c00` | GAO-11-325 | PDF p. 45 (printed n/a) | similarity 0.5773 | original rank 3 | section agency_comments

> metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown versus actual test flights flown (delineated by STOVL variant); and Clean-Wing Flight Envelope coverage (to assess the progress on the ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `GAO-11-325-p044-c02` | GAO-11-325 | PDF p. 44 (printed n/a) | similarity 0.5735 | original rank 4 | section agency_comments

> The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `DOTE-FY2024-F35-p007-c00` | DOTE-FY2024-F35 | PDF p. 7 (printed 50) | similarity 0.5731 | original rank 5

> PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration in terms of its operational effectiveness, suitability, and survivability. The report ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q11: information_flow

**Question:** What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?

- Why it matters: Information-flow timing determines when rework is discovered. It underpins the information-dependency view of the DSM.
- Expected evidence type: Statements that decisions were made before key knowledge (test data, design maturity) was available, or on knowledge gaps at decision points.
- Prior expectation for current corpus: **PARTIAL** (GAO's knowledge-based acquisition framing in GAO-06-356 addresses knowledge at decision points; it may be framed as general principle rather than F-35-specific data flows.)
- Results 5, distinct documents 4 {'DOTE-FY2024-F35': 2, 'GAO-11-325': 1, 'DOTE-FY2010-F35': 1, 'GAO-06-356': 1}, suppressed 0 (of 15 candidates), top 0.5733, mean 0.5498

**#1** `DOTE-FY2024-F35-p001-c00` | DOTE-FY2024-F35 | PDF p. 1 (printed 44) | similarity 0.5733 | original rank 1

> In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration, in terms of its operational effectiveness, suitability, and survivability. The report included a separate annex that ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-11-325-p044-c02` | GAO-11-325 | PDF p. 44 (printed n/a) | similarity 0.5518 | original rank 2 | section agency_comments

> The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2010-F35-p033-c03` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.5438 | original rank 3

> F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `GAO-06-356-p028-c02` | GAO-06-356 | PDF p. 28 (printed 24) | similarity 0.5416 | original rank 4

> DOD provided us with written comments on a draft of this report. The comments appear in appendix III. DOD partially concurred with our recommendation that the Secretary of Defense delay the investment in production aircraft until sufficient testing has at least demonstrated the basic airframe design of each JSF variant in important parts of the flight envelope, including combinations of critical ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.5387 | original rank 5

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q12: downstream_cost_schedule

**Question:** What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?

- Why it matters: Quantified propagation is needed to calibrate the system-dynamics layer.
- Expected evidence type: Dollar or schedule figures linking a development or test problem to later cost or schedule growth, including retrofit or concurrency cost estimates.
- Prior expectation for current corpus: **PARTIAL** (These GAO reports address cost growth, but many quantitative values are in tables, which extraction drops.)
- Results 5, distinct documents 3 {'GAO-10-382': 3, 'GAO-06-356': 1, 'GAO-07-360': 1}, suppressed 0 (of 15 candidates), top 0.5942, mean 0.5746

**#1** `GAO-10-382-p010-c02` | GAO-10-382 | PDF p. 10 (printed 6) | similarity 0.5942 | original rank 1

> According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `GAO-06-356-p019-c01` | GAO-06-356 | PDF p. 19 (printed 15) | similarity 0.5854 | original rank 2

> Past single-step development programs have been unsuccessful in predicting acquisition costs and delivery schedules. For example, development costs for the F-22A fighter, B-2 bomber, Crusader artillery vehicle, and Comanche helicopter skyrocketed, and production quantities were either substantially reduced or the program was canceled. Such outcomes are a poor return on investment and a failure to ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `GAO-07-360-p002-c02` | GAO-07-360 | PDF p. 2 (printed n/a) | similarity 0.5672 | original rank 3 | section highlights

> DOD non-concurred, believing its current strategy provides a balance of technical risk, financial constraints, and operational needs. The JSF program has delivered and flown the first development aircraft. However, cost and schedule goals established in the fiscal year 2004 rebaselined program have not been met. Total JSF program acquisition costs (through 2027) have increased by $31.6 billion ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `GAO-10-382-p008-c01` | GAO-10-382 | PDF p. 8 (printed 4) | similarity 0.5645 | original rank 4

> DOD’s funding requirements for the JSF assume economic benefits from these foreign purchases in reducing unit costs for U.S. aircraft. In our March 2009 report, we noted that more money and time would be needed to complete development. At that time, development costs were projected to increase between $2.4 billion and $7.4 billion and the schedule extended from 1 to 3 years according to two ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `GAO-10-382-p022-c02` | GAO-10-382 | PDF p. 22 (printed 18) | similarity 0.5618 | original rank 5

> Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontractor management issues, and test failures. Engine redesigns and manufacturing problems caused ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:


**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---

### Q13: software_integration

**Question:** What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?

- Why it matters: Temporal-gap probe. It checks whether retrieval returns topically similar but wrong-era evidence when the corpus lacks the period.
- Expected evidence type: Statements on TR-3 hardware delivery, Block 4 software iterations, and the test or fielding consequences.
- Prior expectation for current corpus: **NO** (Block 4 and TR-3 postdate the newest prototype document (2011); only the non-indexed FY2022 and FY2024 DOT&E reports cover them.)
- Results 5, distinct documents 2 {'DOTE-FY2024-F35': 4, 'DOTE-FY2010-F35': 1}, suppressed 1 (of 15 candidates), top 0.6813, mean 0.6355

**#1** `DOTE-FY2024-F35-p002-c00` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.6813 | original rank 1

> The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30R08) – intended as the last version of software fielded on the TR-2 aircraft – due to stability problems, shortfalls in capability, and ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#2** `DOTE-FY2024-F35-p007-c00` | DOTE-FY2024-F35 | PDF p. 7 (printed 50) | similarity 0.6767 | original rank 2

> PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration in terms of its operational effectiveness, suitability, and survivability. The report ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#3** `DOTE-FY2024-F35-p001-c00` | DOTE-FY2024-F35 | PDF p. 1 (printed 44) | similarity 0.6181 | original rank 4

> In February 2024, DOT&E published a classified F-35 combined IOT&E and LFT&E report, supporting the Milestone C Defense Acquisition Board review in March. The report provides an independent assessment of the overall mission capability of the F-35 in the Block 3F configuration, in terms of its operational effectiveness, suitability, and survivability. The report included a separate annex that ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#4** `DOTE-FY2010-F35-p033-c05` | DOTE-FY2010-F35 | PDF p. 33 (printed 17) | similarity 0.6032 | original rank 5

> advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

**#5** `DOTE-FY2024-F35-p002-c03` | DOTE-FY2024-F35 | PDF p. 2 (printed 45) | similarity 0.5980 | original rank 6

> The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rate production in a March 2024 ADM. The full-rate production decision ADM directed the program to designate two major subprograms within the overall acquisition program – one for the engine modernization effort and one for F-35 Block 4 development. The Block 4 development subprogram will ...

Judgment: `____________` (RELEVANT / PARTIALLY_RELEVANT / NOT_RELEVANT / NEEDS_REVIEW)  Notes:

- Suppressed `DOTE-FY2024-F35-p008-c01` (original rank 3, similarity 0.6552): duplicate of `DOTE-FY2024-F35-p007-c00`, 17 shared words

**Question-level judgment** (does the top-5 contain usable evidence?): `____________`  Notes:

---
