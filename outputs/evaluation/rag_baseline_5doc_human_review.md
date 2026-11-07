# Human Relevance Review: BASELINE_V1_ORIGINAL

- Source results: `outputs/evaluation/rag_baseline_5doc.json` (run 2026-10-25T14:56:19+00:00). Not modified; this worksheet only presents them.
- System: original five-document retrieval, before retrieval-hygiene improvements. 541 chunks; sentence-transformers/all-MiniLM-L6-v2; top_k=5, candidate_k=15, chunks 220/35 tokens.
- Questions: `data/metadata/rag_evaluation_questions.json` (eval_v1).
- Excerpts are the first ~400 characters of each chunk. For borderline cases, read the full chunk `text` in the JSON or the source PDF page before judging.
- Similarity is embedding closeness, not relevance.

## Review guide

**Passage-level Human Judgment** (use only these three values):

- **RELEVANT:** The passage directly provides evidence responsive to the question.
- **PARTIALLY_RELEVANT:** The passage concerns the correct issue but only indirectly supports the requested relationship or evidence.
- **NOT_RELEVANT:** The passage is topically similar but does not substantively answer the question.

**Question-Level Retrieval Assessment:**

- **STRONG:** At least one or more retrieved passages provide clear evidence needed for the analytical question.
- **PARTIAL:** Some useful evidence is present but important information is missing.
- **WEAK:** Results are mostly indirect or generic and do not adequately support the question.
- **FAILED:** The returned passages do not provide meaningful evidence for the question.

**Evidence Missing From Current Corpus?** YES / NO / UNCERTAIN

**Retrieval Miss vs. Corpus Gap:**

- **RETRIEVAL_MISS:** The needed evidence appears to exist in an indexed source but retrieval did not surface it.
- **CORPUS_GAP:** The current indexed documents do not appear to contain the needed evidence.
- **BOTH:** The corpus is incomplete and retrieval quality also appears inadequate.
- **UNCERTAIN:** Additional inspection is required.

---

## Q01

- **QUESTION ID:** Q01
- **CATEGORY:** software_integration
- **QUESTION:** What evidence indicates that mission-system software maturity affected F-35 flight-test execution?
- **WHY IT MATTERS:** Benchmark dependency (Software Maturity -> Flight-Test Execution). It is the candidate dependency already used by the grounded prompt and verifier.
- **EXPECTED EVIDENCE TYPE:** Statements linking software delivery or maturity to flight-test points, sorties, re-flights, or test-schedule changes.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c03` | 0.6965 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ... |  |  |
| 2 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c05` | 0.6924 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ... |  |  |
| 3 | DOTE-FY2010-F35 | 29 | `DOTE-FY2010-F35-p029-c01` | 0.6912 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ... |  |  |
| 4 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c06` | 0.6280 | However, during the months since the last program review, more problems with STOVL design and mission systems software arose. • The TBR recommended further changes to the parameters used to plan and model flight test schedules, as well as numerous changes in staffing and other resources needed to complete SDD and enter IOT&E. Specific changes to the schedule recommended by the TBR include lower ... |  |  |
| 5 | GAO-11-325 | 31 | `GAO-11-325-p031-c02` | 0.6248 | Software development--essential for achieving about 80 percent of the JSF functionality--is significantly behind schedule as it enters its most challenging phase. Software delivery to the test program that is essential to demonstrating full system capability is now expected in late 2014, a 3-year delay. Our work in best practices suggests that a key indicator of a product's maturity and readiness ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q02

- **QUESTION ID:** Q02
- **CATEGORY:** requirements
- **QUESTION:** What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?
- **WHY IT MATTERS:** Requirements volatility is an upstream driver in the DSM; change to requirements propagates into design and test rework.
- **EXPECTED EVIDENCE TYPE:** Statements on capability deferral, requirement changes or relaxations, or capability shortfalls tied to cost, schedule, or technical problems.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 | 44 | `GAO-11-325-p044-c01` | 0.6525 | The approval of a new MS B and APB will reflect these budget decisions. Any significant proposed changes to the F-35 budget in future years will be thoroughly reviewed as part of the annual Defense Acquisition Executive Program Reviews and approved as part of the budget review and submission process. Recommendation 2: The GAO recommends that the Secretary of Defense to establish criteria for the ... |  |  |
| 2 | GAO-10-382 | 10 | `GAO-10-382-p010-c02` | 0.6399 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ... |  |  |
| 3 | GAO-11-325 | 45 | `GAO-11-325-p045-c00` | 0.6373 | metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown versus actual test flights flown (delineated by STOVL variant); and Clean-Wing Flight Envelope coverage (to assess the progress on the ... |  |  |
| 4 | GAO-11-325 | 43 | `GAO-11-325-p043-c00` | 0.6178 | of contact is Colonel Jason Denney, U.S. Air Force. Jason.Denney@%osd.mil, 703-697-3619. Sincerely, Signed by: David G. Ahern: Deputy Assistant Secretary of Defense: GAO Draft Report Dated February 28, 2011: "JOINT STRIKE FIGHTER: RESTRUCTURING PLACES PROGRAM ON FIRMER FOOTING, BUT PROGRESS IS STILL LAGGING OVERALL" The Department remains committed to the F-35 Joint Strike Fighter (JSF) program. ... |  |  |
| 5 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c00` | 0.6136 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q03

- **QUESTION ID:** Q03
- **CATEGORY:** design_engineering_activities
- **QUESTION:** What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?
- **WHY IT MATTERS:** Design-maturity measures are observable engineering-activity states. They supply DSM activity definitions and readiness criteria.
- **EXPECTED EVIDENCE TYPE:** Percentages or counts of released drawings, design-review outcomes, and statements about design stability at production decisions.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 | 26 | `GAO-11-325-p026-c01` | 0.6321 | 2016: January; Anticipated design changes (2007 plan): 0; Anticipated future design changes (2010 plan): 0. Source: GAO analysis of DOD data. A key indicator of a product's maturity is the stability of its design. The number of engineering drawings released and subsequent changes provide indicators of the maturity of the design. Engineering drawings are critical because they communicate to the ... |  |  |
| 2 | GAO-11-325 | 44 | `GAO-11-325-p044-c02` | 0.5641 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ... |  |  |
| 3 | GAO-10-382 | 23 | `GAO-10-382-p023-c01` | 0.5569 | base; increases in the amount of on- and out-of-station work required on aircraft in production; and require costly retrofitting of aircraft already produced and fielded. A best practice is to achieve design stability at the system-level critical design review, usually held midway through system development. Completion of at least 90 percent of engineering drawings at this point provides tangible ... |  |  |
| 4 | GAO-11-325 | 18 | `GAO-11-325-p018-c01` | 0.5522 | The Program Has Not Yet Stabilized Aircraft Designs: Engineering drawings released since design reviews and the number and rate of design changes are excessive compared to plans and best practices. Critical design reviews were completed on the three aircraft variants in 2006 and 2007 and the designs declared mature, but the program continues to experience numerous changes. Since 2007, the program ... |  |  |
| 5 | GAO-11-325 | 17 | `GAO-11-325-p017-c03` | 0.5421 | improve oversight and budgeting, holding people accountable for meeting interim objectives and, for objectives not met, providing criteria and a forum for evaluating reasons why and what should be done. Program Has Still Not Fully Demonstrated a Stable Design and Mature Manufacturing Processes as It Enters Its Fifth Year of Production: After completing 9 years of system development and 4 years of ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q04

- **QUESTION ID:** Q04
- **CATEGORY:** test_sequencing
- **QUESTION:** What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?
- **WHY IT MATTERS:** Test-asset availability gates the test sequence. It is a resource dependency for the simulation layer.
- **EXPECTED EVIDENCE TYPE:** Statements on test-aircraft delivery dates, aircraft available vs. planned, flight rates, and their effect on test progress.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c03` | 0.7094 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ... |  |  |
| 2 | DOTE-FY2010-F35 | 29 | `DOTE-FY2010-F35-p029-c01` | 0.6598 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ... |  |  |
| 3 | GAO-06-356 | 14 | `GAO-06-356-p014-c00` | 0.6408 | Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the number of flight test hours needed to verify that the system will work as intended, and affect when key knowledge will be available for making investment decisions. For example, when the B-2 program began flight testing in July 1989, it estimated that the flight test program would last ... |  |  |
| 4 | GAO-09-303 | 6 | `GAO-09-303-p006-c02` | 0.6397 | of production jets on order and is still working to deliver test jets and mature manufacturing processes, plans to accelerate procurement will be difficult to achieve in a cost-effective manner. DOD's revised test plan adds an extra year to the schedule, better aligns resources and availability dates, and lessens the overlap between development and operational testing, but it is still aggressive ... |  |  |
| 5 | GAO-09-303 | 11 | `GAO-09-303-p011-c02` | 0.6383 | Continuing delays in delivering test aircraft are expected to hamper and further compress test schedules. In particular, the joint team projects that the two aircraft dedicated to carrier suitability tests will be late off the production line, thereby delaying test activities. It also projected that the JSF will require about 2,700 hours of flight testing for mission systems, significantly more ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q05

- **QUESTION ID:** Q05
- **CATEGORY:** schedule_dependencies
- **QUESTION:** What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?
- **WHY IT MATTERS:** Block-to-block precedence and deferral is a schedule dependency chain and a source of capability migration (rework).
- **EXPECTED EVIDENCE TYPE:** Block definitions (e.g., Block 1, 2, 3), planned vs. actual release dates, and capability moved from one block to a later one.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 | 32 | `DOTE-FY2010-F35-p032-c00` | 0.6176 | training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.5 problems, in the mission systems labs and on the CATB. - The program planned to release the first Block 1 increment to flight test aircraft in August 2010, but F-35 flight testing did not begin until November 2010. By ... |  |  |
| 2 | GAO-11-325 | 36 | `GAO-11-325-p036-c00` | 0.5890 | Delays in developing, integrating, and releasing software to the test program have cascading effects hampering flight tests, training, and lab accreditation. While progress is being made, a substantial amount of software work remains before the program can demonstrate full warfighting capability. The program released block 0.5 for flight test nearly 2 years later than planned in the 2006 plan, ... |  |  |
| 3 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c05` | 0.5735 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ... |  |  |
| 4 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c00` | 0.5456 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ... |  |  |
| 5 | DOTE-FY2010-F35 | 31 | `DOTE-FY2010-F35-p031-c05` | 0.5394 | Block 0.5 is the infrastructure increment, which contains communications, navigation, and limited radar functionality. - Aircraft BF-4, loaded with Block 0.5, accomplished first flight in April 2010, five months later than planned, and then ferried to Patuxent River NAS, Maryland, in June, two months later than planned, and began Block 0.5 flight test. - Test teams attempted approximately 70 ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q06

- **QUESTION ID:** Q06
- **CATEGORY:** technical_deficiencies
- **QUESTION:** What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?
- **WHY IT MATTERS:** Discovered deficiencies drive rework loops. They are central to the WTM and system-dynamics rework structure.
- **EXPECTED EVIDENCE TYPE:** Named deficiencies (e.g., structural, propulsion, STOVL, helmet) with the corrective action and any retest or retrofit.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 | 22 | `GAO-10-382-p022-c02` | 0.5814 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontractor management issues, and test failures. Engine redesigns and manufacturing problems caused ... |  |  |
| 2 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c02` | 0.5677 | The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Schedule Re-Planning and Implementation of Changes • The year-long process of analyses during FY10 (JET II implementation, Nunn-McCurdy certification, and TBR) served to develop a more realistic estimate of SDD completion for Block 3 in all variants and identify steps to reduce risk in ... |  |  |
| 3 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c05` | 0.5674 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ... |  |  |
| 4 | GAO-10-382 | 32 | `GAO-10-382-p032-c01` | 0.5433 | Nonetheless, completing the design modifications will likely result in carrier suitability test delays of at least 4 months, according to an official from DOT&E. • JSF engine. The program continues to address significant technical and design challenges with the F135 engine. The STOVL engine’s lift fan has required design changes in response to damages incurred during testing which will limit ... |  |  |
| 5 | DOTE-FY2010-F35 | 29 | `DOTE-FY2010-F35-p029-c01` | 0.5423 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q07

- **QUESTION ID:** Q07
- **CATEGORY:** rework_redesign
- **QUESTION:** What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?
- **WHY IT MATTERS:** Weight growth is a classic design-rework driver with cross-subsystem propagation.
- **EXPECTED EVIDENCE TYPE:** Statements on weight margins, weight-reduction redesign efforts, and the resulting schedule or cost impact.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 | 10 | `GAO-10-382-p010-c02` | 0.5466 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ... |  |  |
| 2 | GAO-11-325 | 44 | `GAO-11-325-p044-c02` | 0.5395 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ... |  |  |
| 3 | GAO-11-325 | 45 | `GAO-11-325-p045-c00` | 0.5096 | metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown versus actual test flights flown (delineated by STOVL variant); and Clean-Wing Flight Envelope coverage (to assess the progress on the ... |  |  |
| 4 | GAO-06-356 | 21 | `GAO-06-356-p021-c01` | 0.5019 | Structuring the program into separate and manageable increments based on what is achievable now and in the future would allow more predictable cost and delivery estimates. Over the past three decades, the Air Force successfully procured more than 2,200 F-16s. The F-16 acquisition approach allowed the timely and affordable delivery of aircraft and capability to meet the warfighter’s needs, ... |  |  |
| 5 | GAO-11-325 | 5 | `GAO-11-325-p005-c02` | 0.5014 | We believe that the evidence obtained provides a reasonable basis for our findings and conclusions based on our audit objectives. Background: The F-35 program is a joint, multinational acquisition to develop and field an affordable, highly common family of stealthy, next-generation strike fighter aircraft for the United States Air Force, Marine Corps, Navy, and eight international partners. The ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q08

- **QUESTION ID:** Q08
- **CATEGORY:** concurrency
- **QUESTION:** What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?
- **WHY IT MATTERS:** Concurrency is the central dependency theme for the DSM. Production committed before test knowledge creates downstream rework.
- **EXPECTED EVIDENCE TYPE:** Statements on low-rate initial production quantities committed before testing, the overlap of test and production schedules, and the risks of that overlap.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 | 22 | `GAO-10-382-p022-c02` | 0.5846 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontractor management issues, and test failures. Engine redesigns and manufacturing problems caused ... |  |  |
| 2 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c03` | 0.5558 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ... |  |  |
| 3 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c05` | 0.5540 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ... |  |  |
| 4 | GAO-10-382 | 9 | `GAO-10-382-p009-c01` | 0.5471 | contractor capabilities and plans for ramping-up and sustaining production at maximum rates, and the Joint Assessment Team (JAT) reviewed F135 engine costs and affordability projections. Among other actions, the restructuring (1) increased funding for the JSF development and procurement programs to the revised JET estimates over the next 5 years; (2) extended development flight testing by 13 ... |  |  |
| 5 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c00` | 0.5429 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q09

- **QUESTION ID:** Q09
- **CATEGORY:** milestone_effects
- **QUESTION:** What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?
- **WHY IT MATTERS:** Milestone slips are the observable outputs the predictive layer must reproduce.
- **EXPECTED EVIDENCE TYPE:** Original vs. revised milestone dates and the stated reason for each change.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c03` | 0.6023 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ... |  |  |
| 2 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c00` | 0.5906 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ... |  |  |
| 3 | DOTE-FY2010-F35 | 29 | `DOTE-FY2010-F35-p029-c01` | 0.5866 | teams made significant progress, the results of flight testing and the TBR indicate more time and resources will be needed to complete SDD than incorporated in the June 2010 program baseline. • All three F-35 variants had entered flight test by June 2010. For the first time, all three integrated test forces at Fort Worth, Texas; Patuxent River Naval Air Station (NAS), Maryland; and Edwards AFB, ... |  |  |
| 4 | GAO-10-382 | 10 | `GAO-10-382-p010-c02` | 0.5864 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ... |  |  |
| 5 | GAO-10-382 | 22 | `GAO-10-382-p022-c02` | 0.5803 | Nonetheless, supplier costs are expected to make up a substantial share of total expenses as the program moves further into production. The F135 engine contractor has experienced manufacturing challenges similar to those of the aircraft contractor, including part shortages, late deliveries, subcontractor management issues, and test failures. Engine redesigns and manufacturing problems caused ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q10

- **QUESTION ID:** Q10
- **CATEGORY:** subsystem_dependencies
- **QUESTION:** What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?
- **WHY IT MATTERS:** Subsystem-to-subsystem coupling defines off-diagonal DSM entries.
- **EXPECTED EVIDENCE TYPE:** Statements that a problem or delay in one subsystem blocked or delayed integration or testing of another.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c05` | 0.6398 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ... |  |  |
| 2 | GAO-10-382 | 33 | `GAO-10-382-p033-c02` | 0.5822 | Further, the lack of a production helmet mounted display configuration at this time could result in a major system redesign or change in concept of operations. • Damage to flight deck and runways. The F-35 engine and integrated power package exhaust may cause excessive damage to the flight deck environment and runway surfaces that may result in operating limits or drive costly upgrades and ... |  |  |
| 3 | GAO-11-325 | 45 | `GAO-11-325-p045-c00` | 0.5773 | metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown versus actual test flights flown (delineated by STOVL variant); and Clean-Wing Flight Envelope coverage (to assess the progress on the ... |  |  |
| 4 | GAO-11-325 | 44 | `GAO-11-325-p044-c02` | 0.5735 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ... |  |  |
| 5 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c00` | 0.5644 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q11

- **QUESTION ID:** Q11
- **CATEGORY:** information_flow
- **QUESTION:** What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?
- **WHY IT MATTERS:** Information-flow timing determines when rework is discovered. It underpins the information-dependency view of the DSM.
- **EXPECTED EVIDENCE TYPE:** Statements that decisions were made before key knowledge (test data, design maturity) was available, or on knowledge gaps at decision points.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 | 44 | `GAO-11-325-p044-c02` | 0.5518 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force have established a battle rhythm of monthly SAE reviews with the F-35 PEO to assess the overall F-35 program, with additional emphasis on ... |  |  |
| 2 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c03` | 0.5438 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ... |  |  |
| 3 | GAO-06-356 | 28 | `GAO-06-356-p028-c02` | 0.5416 | DOD provided us with written comments on a draft of this report. The comments appear in appendix III. DOD partially concurred with our recommendation that the Secretary of Defense delay the investment in production aircraft until sufficient testing has at least demonstrated the basic airframe design of each JSF variant in important parts of the flight envelope, including combinations of critical ... |  |  |
| 4 | GAO-11-325 | 45 | `GAO-11-325-p045-c00` | 0.5278 | metrics that indicate the desired value(s), the current status, margin, and trends). * F-35B Flight Test: Review of F-35B flight test data, to include, planned/scheduled test points to be flown versus achieved test points flown; scheduled test flights flown versus actual test flights flown (delineated by STOVL variant); and Clean-Wing Flight Envelope coverage (to assess the progress on the ... |  |  |
| 5 | GAO-06-356 | 6 | `GAO-06-356-p006-c00` | 0.5225 | case be accompanied by a knowledge-based acquisition approach approach that ensures attainment and use of demonstrated product knowledge before making future investments. In commenting on our report, DOD stated that JSF’s restructured acquisition plan would incorporate a knowledge-based, evolutionary approach consistent with DOD policy. This is our second report. Specifically, we (1) determined ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q12

- **QUESTION ID:** Q12
- **CATEGORY:** downstream_cost_schedule
- **QUESTION:** What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?
- **WHY IT MATTERS:** Quantified propagation is needed to calibrate the system-dynamics layer.
- **EXPECTED EVIDENCE TYPE:** Dollar or schedule figures linking a development or test problem to later cost or schedule growth, including retrofit or concurrency cost estimates.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 | 28 | `GAO-11-325-p028-c00` | 0.6015 | Aircraft: BF3; Aircraft: BF4; Aircraft: AF1; Aircraft: AF2; Aircraft: AF3; Aircraft: CF1; Aircraft: CF2; Aircraft: CF3; Aircraft: BF5; Aircraft: AF4; Source: GAO analysis of DOD data. Manufacturing production aircraft is different from building test aircraft, and some gains in learning as more aircraft are built can be expected to, over time, reduce labor hour costs. However, the experience to ... |  |  |
| 2 | GAO-10-382 | 10 | `GAO-10-382-p010-c02` | 0.5942 | According to defense officials, the new budget reflects the findings of the JET. Consistent with its previous 2008 study, the JET projected higher development costs and greater schedule delays compared to the internal program estimates reported to Congress. Among other factors, the JET projected (1) more engineering staff needed for longer periods of time to complete development, evaluate test ... |  |  |
| 3 | GAO-06-356 | 19 | `GAO-06-356-p019-c01` | 0.5854 | Past single-step development programs have been unsuccessful in predicting acquisition costs and delivery schedules. For example, development costs for the F-22A fighter, B-2 bomber, Crusader artillery vehicle, and Comanche helicopter skyrocketed, and production quantities were either substantially reduced or the program was canceled. Such outcomes are a poor return on investment and a failure to ... |  |  |
| 4 | GAO-09-303 | 9 | `GAO-09-303-p009-c03` | 0.5682 | New Estimates Project Rising Costs and Further Delays to Complete JSF Development: Development costs are projected to increase between $2.4 billion and $7.4 billion and the schedule for completing system development extended from 1 to 3 years, according to recent estimates--one by the JSF Program Office and one by a joint team of Office of the Secretary of Defense (OSD), Air Force, and Navy ... |  |  |
| 5 | GAO-10-382 | 8 | `GAO-10-382-p008-c01` | 0.5645 | DOD’s funding requirements for the JSF assume economic benefits from these foreign purchases in reducing unit costs for U.S. aircraft. In our March 2009 report, we noted that more money and time would be needed to complete development. At that time, development costs were projected to increase between $2.4 billion and $7.4 billion and the schedule extended from 1 to 3 years according to two ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Q13

- **QUESTION ID:** Q13
- **CATEGORY:** software_integration
- **QUESTION:** What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?
- **WHY IT MATTERS:** Temporal-gap probe. It checks whether retrieval returns topically similar but wrong-era evidence when the corpus lacks the period.
- **EXPECTED EVIDENCE TYPE:** Statements on TR-3 hardware delivery, Block 4 software iterations, and the test or fielding consequences.

| Rank | Source | PDF Page | Chunk ID | Similarity | Evidence Excerpt | Human Judgment | Reviewer Notes |
|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c05` | 0.6032 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays in delivery of Block 2 and Block 3 software are not incurred, and the program can overcome the helmet mounted display problem before Block ... |  |  |
| 2 | DOTE-FY2010-F35 | 33 | `DOTE-FY2010-F35-p033-c03` | 0.5819 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by the TBR (lower fly rates, more regression and re-fly margin, more flights, and other resource additions) that result in completion of SDD flight test for Block 3 in all three ... |  |  |
| 3 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c07` | 0.5463 | F-35 Flight Test STOVL Flight Sciences, Flight Test with BF-1, BF-2, and BF-3 Test Aircraft • BF-3 ferried to Patuxent River NAS, Maryland, in February 2010; it is the last of three B-model flight sciences aircraft. • Maintenance, test operations, and engineering staffs increased significantly (approximately 25 percent) in FY10 at Patuxent River, NAS. The program intends to reach full strength in ... |  |  |
| 4 | DOTE-FY2010-F35 | 30 | `DOTE-FY2010-F35-p030-c00` | 0.5322 | • The program incrementally provides mission capability: Block 1 (initial), Block 2 (advanced), Block 3 (full). • The F-35 is under development by a partnership of countries: the United States, Great Britain, Italy, the Netherlands, Turkey, Canada, Australia, Denmark, and Norway. • A force equipped with F-35 units should permit the Combatant Commander to attack targets day or night, in all ... |  |  |
| 5 | DOTE-FY2010-F35 | 32 | `DOTE-FY2010-F35-p032-c00` | 0.5237 | training syllabus for the initial cadres at the training center. The development team conducted integration activity with an initial version of Block 1, including fixes to Block 0.5 problems, in the mission systems labs and on the CATB. - The program planned to release the first Block 1 increment to flight test aircraft in August 2010, but F-35 flight testing did not begin until November 2010. By ... |  |  |

**Question-Level Retrieval Assessment:** [ ]
*(STRONG / PARTIAL / WEAK / FAILED)*

**Evidence Missing From Current Corpus?** [ ]
*(YES / NO / UNCERTAIN)*

**Retrieval Miss vs. Corpus Gap:** [ ]
*(RETRIEVAL_MISS / CORPUS_GAP / BOTH / UNCERTAIN)*

**Reviewer Comments:** [ ]

---

## Summary

| Question ID | Category | Question-Level Assessment | Corpus Gap? | Retrieval Miss? | Notes |
|---|---|---|---|---|---|
| Q01 | software_integration |  |  |  |  |
| Q02 | requirements |  |  |  |  |
| Q03 | design_engineering_activities |  |  |  |  |
| Q04 | test_sequencing |  |  |  |  |
| Q05 | schedule_dependencies |  |  |  |  |
| Q06 | technical_deficiencies |  |  |  |  |
| Q07 | rework_redesign |  |  |  |  |
| Q08 | concurrency |  |  |  |  |
| Q09 | milestone_effects |  |  |  |  |
| Q10 | subsystem_dependencies |  |  |  |  |
| Q11 | information_flow |  |  |  |  |
| Q12 | downstream_cost_schedule |  |  |  |  |
| Q13 | software_integration |  |  |  |  |
