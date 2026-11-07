# Retrieval benchmark: BM25_V2_1

- Strategy: `bm25`. Okapi BM25 (k1 1.5, b 0.75) over the same chunk texts; generic stopwords, no stemming.
- Store: 848 chunks, RAG_EXPANDED_V2 (10 documents; frozen, see data/metadata/rag_expanded_v2_freeze.json); questions: `data/metadata/rag_evaluation_questions.json` (unedited)
- Run: 2026-10-25T17:35:16+00:00. No LLM; relevance judgments left blank.
- Scores: *strategy score* is this strategy's own score (similarity, BM25, RRF or cross-encoder logit) and is **not comparable across strategies**. *sem* is the dense cosine similarity and *dense/bm25* are whole-store ranks, given for every result.

Mean distinct documents per question 3.15; duplicate suppressions 12; Highlights results 1; agency_comments results 5.

## Q01: software_integration

What evidence indicates that mission-system software maturity affected F-35 flight-test execution?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 17.5412 | 0.6924 | 3 | 1 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 2 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c02` | 16.9691 | 0.6761 | 5 | 2 | Development of mission systems software continued to experience delays that affected flight test progress. • Program leadership began re-planning SDD flight testing at the end of FY10, in conjunction with a restructuring of mission systems software development |  |
| 3 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c02` | 15.1612 | 0.6743 | 6 | 3 | The aircraft is being prepared for ballistic testing. The test team will begin this testing in 1QFY11. Test Schedule Re-Planning and Implementation of Changes • The year-long process of analyses during FY10 (JET II implementation, Nunn-McCurdy certification, a |  |
| 4 | DOTE-FY2024-F35 (?) | 12 | `DOTE-FY2024-F35-p012-c02` | 14.77 | 0.4238 | 343 | 4 | touch labor time and cure times associated with repairs to LO materials required to correct only the subset of failures that prevent the F-35 from being able to perform a specific mission. It indicates the average time for maintainers to return an aircraft fro |  |
| 5 | GAO-06-356 (2006) | 16 | `GAO-06-356-p016-c02` | 13.4262 | 0.5965 | 25 | 6 | Flight testing to evaluate the effectiveness and suitability of the fully integrated system is expected to continue until the full-rate decision in late 2013. JSF’s expected performance is largely dependent on demonstrating software that supports vehicle, miss |  |

## Q02: requirements

What evidence shows that F-35 warfighter requirements or key performance parameters were deferred, relaxed, or at risk of not being met because of development problems?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-07-360 (2007) | 17 | `GAO-07-360-p017-c03` | 18.5612 | 0.4654 | 155 | 1 | The JSF Program Projects Key Performance Parameters Will Be Met Based on Modeling and Simulations Currently, the JSF program estimates that by the time the development program ends the aircraft design will meet all but one of its key performance parameters. Th |  |
| 2 | DOTE-FY2024-F35 (?) | 10 | `DOTE-FY2024-F35-p010-c01` | 14.7245 | 0.5316 | 49 | 2 | Fleet (FY15 – FY23) reliability metrics as shown in Figure 2, based on adjudicated data reported by the JPO. Higher numbers reflect better performance and a more reliable system. Since FY15, there was some reliability improvement with increased variability. In |  |
| 3 | GAO-07-360 (2007) | 18 | `GAO-07-360-p018-c00` | 14.7039 | 0.4056 | 355 | 3 | completed less than 1 percent of the flight test program and no structural or durability tests have been started. According to the program’s test and evaluation master plan, the key performance parameters will be verified during testing from 2010 to 2013. Tabl |  |
| 4 | DOTE-FY2024-F35 (?) | 12 | `DOTE-FY2024-F35-p012-c01` | 14.1239 | 0.5217 | 62 | 5 | This figure shows yearly average values for each metric for a given fiscal year, and the horizontal line indicates the threshold requirement. For maintainability metrics, lower values are better, indicating shorter average maintenance durations. For all varian |  |
| 5 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c03` | 14.1131 | 0.5982 | 11 | 6 | The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/Earned Value Management (EVM): A review of Acquisition Procurement Unit Cost, Program Acquisition Unit Cost, Operations and Support costs, and EVM cos |  |

## Q03: design_engineering_activities

What evidence describes design-maturity measures, such as engineering drawing releases or design reviews, used to judge whether the F-35 design was stable enough for production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-07-360 (2007) | 16 | `GAO-07-360-p016-c02` | 24.0176 | 0.5389 | 12 | 1 | In February 2006, the program held its critical design review for production representative conventional and short take-off and vertical landing aircraft. At that time, the program had completed 47 percent of the short take-off aircraft design and 3 percent of |  |
| 2 | GAO-10-382 (2010) | 23 | `GAO-10-382-p023-c00` | 21.9447 | 0.4801 | 48 | 2 | with a stable design. However, despite being well beyond the design reviews for each variant, the total number of engineering drawings continues to grow due to design changes and other revisions to drawings (see fig. 4). Contractor officials estimated in 2007  |  |
| 3 | GAO-11-325 (2011) | 17 | `GAO-11-325-p017-c02` | 21.2463 | 0.5421 | 9 | 3 | improve oversight and budgeting, holding people accountable for meeting interim objectives and, for objectives not met, providing criteria and a forum for evaluating reasons why and what should be done. Program Has Still Not Fully Demonstrated a Stable Design  |  |
| 4 | GAO-11-325 (2011) | 26 | `GAO-11-325-p026-c00` | 20.992 | 0.633 | 1 | 5 | A key indicator of a product's maturity is the stability of its design. The number of engineering drawings released and subsequent changes provide indicators of the maturity of the design. Engineering drawings are critical because they communicate to the manuf |  |
| 5 | GAO-05-271 (2005) | 14 | `GAO-05-271-p014-c01` | 20.4253 | 0.4951 | 35 | 6 | One hundred percent of critical manufacturing processes under statistical control, demonstration of a fully integrated product in its operational environment to show it will work as intended, and reliability goals demonstrated. Development start--2001: Knowled |  |

## Q04: test_sequencing

What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 31 | `GAO-11-325-p031-c03` | 17.8809 | 0.6374 | 8 | 1 | programs have failed to demonstrate that the system works as intended before entering production, discovering costly design problems late in development when the more complex software and advanced capabilities are integrated and tested. Development Flight Test |  |
| 2 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 14.818 | 0.5502 | 50 | 2 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |
| 3 | DOTE-FY2024-F35 (?) | 8 | `DOTE-FY2024-F35-p008-c04` | 14.7921 | 0.622 | 13 | 3 | Prior to starting the delivery of TR-3 configured aircraft out of long-term parking in July, 649 aircraft had been delivered to the U.S. Services. These numbers, which provide the basis of analyses contained in this section of the report, do not include any ai |  |
| 4 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 13.9339 | 0.6614 | 3 | 4 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 5 | GAO-11-325 (2011) | 17 | `GAO-11-325-p017-c00` | 13.898 | 0.5661 | 33 | 5 | Although still hampered as in prior years by the late delivery of test aircraft, flight tests substantially increased in volume and pace at the two main government test sites--Edwards Air Force Base, California, for CTOL tests and Patuxent River Naval Air Stat |  |

## Q05: schedule_dependencies

What evidence describes the planned sequence of F-35 software blocks and how delays in one block affected the content or timing of later blocks?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-11-325 (2011) | 36 | `GAO-11-325-p036-c00` | 24.1413 | 0.589 | 5 | 1 | Delays in developing, integrating, and releasing software to the test program have cascading effects hampering flight tests, training, and lab accreditation. While progress is being made, a substantial amount of software work remains before the program can dem |  |
| 2 | GAO-06-356 (2006) | 16 | `GAO-06-356-p016-c02` | 23.7404 | 0.4777 | 23 | 2 | Flight testing to evaluate the effectiveness and suitability of the fully integrated system is expected to continue until the full-rate decision in late 2013. JSF’s expected performance is largely dependent on demonstrating software that supports vehicle, miss |  |
| 3 | GAO-11-325 (2011) | 34 | `GAO-11-325-p034-c03` | 21.6772 | 0.3039 | 345 | 3 | It could also require more production aircraft for a longer period to supplement test assets, resulting in fewer systems at training sites and operational bases. Contractor utilization of labs has increased markedly and the number and integration of labs is im |  |
| 4 | GAO-07-360 (2007) | 20 | `GAO-07-360-p020-c01` | 19.8449 | 0.5294 | 12 | 5 | As discussed earlier, current JSF schedules are already showing that delivery of early test aircraft will be later than the planned delivery date. The flight test program will also hinge on the delivering aircraft with the expected capabilities. JSF’s expected |  |
| 5 | GAO-10-382 (2010) | 31 | `GAO-10-382-p031-c00` | 18.8234 | 0.3903 | 87 | 6 | moving some capabilities to future blocks in order to keep on schedule. This adds pressure and costs to future efforts and increases the probability of defects being realized later in the program. Software is developed, integrated, and released in five increme |  |

## Q06: technical_deficiencies

What evidence identifies technical deficiencies discovered during F-35 development or testing that required redesign, retrofit, or retesting?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 23 | `GAO-08-388-p023-c03` | 15.7653 | 0.4872 | 54 | 1 | is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may require redesign, production line changes, and retrofit expenses for aircraft already built. On the basis of the evidence, we expect JSF program costs to i |  |
| 2 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c00` | 14.1709 | 0.6745 | 1 | 2 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop test” of the software they were testing (30 |  |
| 3 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c00` | 13.9793 | 0.596 | 4 | 3 | PERFORMANCE » EFFECTIVENESS This Annual Report does not include effectiveness results contained in the DOT&E classified F-35 combined IOT&E and LFT&E report published in February 2024. That report provided an independent assessment of the overall mission capab |  |
| 4 | GAO-11-325 (2011) | 26 | `GAO-11-325-p026-c02` | 13.6352 | 0.4529 | 101 | 4 | Additional changes are likely as development flight testing continues. Some emerging concerns may drive additional and substantive design changes: * JSF Lift System Development and Integration. Essential to STOVL operations, the lift fan continues to be a prim |  |
| 5 | DOTE-FY2024-F35 (?) | 12 | `DOTE-FY2024-F35-p012-c04` | 13.4437 | 0.5523 | 13 | 5 | time of this report. » SURVIVABILITY Results from the cyber survivability assessment of the supply chain refurbishment practices were under review at the time of this report. Multiple ALIS cyber survivability deficiency reports were created in FY24 based on th |  |

## Q07: rework_redesign

What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 34 | `GAO-08-388-p034-c01` | 19.3903 | 0.4826 | 17 | 1 | Officials told us that a maximum of 35 per year was probably affordable, given budget plans at that time. Containing Future Weight Growth Weight growth was the most significant challenge faced by the JSF program early in development. Redesign efforts to addres |  |
| 2 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c03` | 15.303 | 0.525 | 6 | 2 | The topics and metrics that are assessed include, but are not limited to, the following: * Cost/Affordability/Earned Value Management (EVM): A review of Acquisition Procurement Unit Cost, Program Acquisition Unit Cost, Operations and Support costs, and EVM cos |  |
| 3 | GAO-10-382 (2010) | 7 | `GAO-10-382-p007-c02` | 12.94 | 0.4768 | 23 | 4 | The carrier-suitable variant (CV) will provide the Navy a multi-role, stealthy strike aircraft to complement the F/A-18E/F Super Hornet. Background The program began in November 1996 with a 5-year competition between Lockheed Martin and Boeing to determine the |  |
| 4 | GAO-07-360 (2007) | 23 | `GAO-07-360-p023-c01` | 11.4062 | 0.3126 | 409 | 5 | There are also important competing priorities external to DOD’s budget. Fully funding specific programs or activities will undoubtedly create shortfalls in others. Unprecedented Funding Requirements Could Challenge Program Execution Funding challenges will be  |  |
| 5 | DOTE-FY2024-F35 (?) | 13 | `DOTE-FY2024-F35-p013-c01` | 10.6024 | 0.2793 | 567 | 6 | Additionally, once cyber effects are adequately and systematically characterized – through a validation process and informed by intelligence centers cyber threat assessments – emulation during mission rehearsals in the JSE, or as appropriate in open-air exerci |  |

## Q08: concurrency

What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-07-360 (2007) | 22 | `GAO-07-360-p022-c00` | 13.7915 | 0.5415 | 10 | 1 | While some concurrency may be beneficial to efficiently transition from the development stage of a program to production, the JSF is currently planned to be significantly more concurrent than the F-22A program that failed to deliver the warfighting capability  |  |
| 2 | GAO-11-325 (2011) | 44 | `GAO-11-325-p044-c02` | 12.9081 | 0.5164 | 25 | 2 | The intent is to allow each JSF variant to proceed and demonstrate success at its own pace and could result in separate full-rate production decisions. DOD Response: Concur. The Service Acquisition Executives (SAEs) for the Department of the Navy and Air Force |  |
| 3 | GAO-05-271 (2005) | 21 | `GAO-05-271-p021-c02` | 12.7309 | 0.4467 | 115 | 3 | re-plan strategy is a balance of technical, cost and schedule risk that incorporates a best practice, evolutionary approach to system acquisition as outlined in the latest Department regulations and instructions. The second GAO recommendation is to develop and |  |
| 4 | DOTE-FY2024-F35 (?) | 8 | `DOTE-FY2024-F35-p008-c01` | 12.2187 | 0.5104 | 30 | 4 | against capabilities in the 30R08 software, many of which were against capabilities that were working in previous versions of software, an indication of insufficient integration and regression testing. Development Although the program and Services have begun a |  |
| 5 | GAO-07-360 (2007) | 7 | `GAO-07-360-p007-c00` | 11.9669 | 0.5407 | 13 | 5 | The degree of concurrency between development and production in the JSF program’s acquisition strategy still includes significant risks for cost and schedule overruns or late delivery of promised capabilities to the warfighter. For example, at the time of the  |  |

## Q09: milestone_effects

What evidence shows that development or test delays moved major F-35 program milestones, such as the end of development, the start of operational test, or full-rate production?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 19 | `GAO-08-388-p019-c00` | 18.0034 | 0.4779 | 60 | 1 | According to our analysis of available evidence, manufacturing test aircraft continue to run behind schedule. The prime contractor has revised the test aircraft manufacturing schedule three times, resulting in slips of up to 16 months in first flight dates of  |  |
| 2 | GAO-08-388 (2008) | 14 | `GAO-08-388-p014-c02` | 17.9661 | 0.3253 | 528 | 2 | for the most part, but schedules could worsen considerably if the delays in maturing the aircraft and engine designs and manufacturing test aircraft continue to push work effort into later years. This would further compress the time available to complete devel |  |
| 3 | GAO-08-388 (2008) | 23 | `GAO-08-388-p023-c03` | 17.8883 | 0.4589 | 96 | 3 | is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may require redesign, production line changes, and retrofit expenses for aircraft already built. On the basis of the evidence, we expect JSF program costs to i |  |
| 4 | DOTE-FY2024-F35 (?) | 5 | `DOTE-FY2024-F35-p005-c00` | 17.8827 | 0.5744 | 8 | 4 | associated timelines, DOT&E estimates that DOTs of TR-3 aircraft will likely not begin in earnest until mid to late FY26, two years after the aircraft began being delivered to field units. If readiness criteria involving modifications, instrumentation, OABS an |  |
| 5 | GAO-07-360 (2007) | 14 | `GAO-07-360-p014-c00` | 17.363 | 0.43 | 164 | 5 | Event did not or has not occurred Event has occurred New date for event Period of flight testing End of development; start of full-rate production The program has completed manufacturing of its first development aircraft and manufacturing data indicates that t |  |

## Q10: subsystem_dependencies

What evidence describes dependencies between F-35 subsystems, such as the helmet-mounted display, mission-system sensors, propulsion, or the STOVL lift system, that affected integration or test progress?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-10-382 (2010) | 33 | `GAO-10-382-p033-c01` | 33.1681 | 0.4557 | 54 | 1 | The JSF program has proposed interim solutions, but full support system deployability will not be available by the Marine Corp’s and Air Force’s initial operational capability dates. • Helmet Mounted Display. Critical to information integration and situational |  |
| 2 | DOTE-FY2010-F35 (?) | 33 | `DOTE-FY2010-F35-p033-c05` | 30.9109 | 0.6398 | 1 | 2 | advanced data link, distributed aperture system, infrared/ electro-optical fused sensor tracks) are risks that affect the ability to accurately predict the conclusion of mission systems flight test. Completion by early 2016 is possible provided further delays  |  |
| 3 | DOTE-FY2010-F35 (?) | 34 | `DOTE-FY2010-F35-p034-c04` | 29.6502 | 0.485 | 32 | 4 | Remain prepared to deal with continued discovery in flight test as more complex testing begins. 3. Determine the impact of resolution of known critical technical issues, including Helmet Mounted Display, STOVL mechanization, handling characteristics, and after |  |
| 4 | GAO-11-325 (2011) | 36 | `GAO-11-325-p036-c02` | 26.5424 | 0.4616 | 46 | 5 | Development and integration of the most advanced capabilities could be deferred to future increments and delivered to the warfighter at a later date. The recent technical baseline review identified software as a significant challenge, slowing system developmen |  |
| 5 | DOTE-FY2010-F35 (?) | 29 | `DOTE-FY2010-F35-p029-c02` | 20.4896 | 0.4808 | 33 | 7 | Development of mission systems software continued to experience delays that affected flight test progress. • Program leadership began re-planning SDD flight testing at the end of FY10, in conjunction with a restructuring of mission systems software development |  |

## Q11: information_flow

What evidence describes whether test results, technical data, or design knowledge were available in time to inform F-35 investment or production decisions?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-05-271 (2005) | 24 | `GAO-05-271-p024-c00` | 17.2202 | 0.4432 | 78 | 1 | Defense's (DOD) acquisition program management office and prime contractor. To evaluate whether the current acquisition plan follows an evolutionary, knowledge-based approach to meeting business case goals in the future, we applied GAO's methodology for assess |  |
| 2 | GAO-06-356 (2006) | 6 | `GAO-06-356-p006-c00` | 16.2297 | 0.5225 | 7 | 2 | case be accompanied by a knowledge-based acquisition approach approach that ensures attainment and use of demonstrated product knowledge before making future investments. In commenting on our report, DOD stated that JSF’s restructured acquisition plan would in |  |
| 3 | GAO-06-356 (2006) | 14 | `GAO-06-356-p014-c00` | 15.4949 | 0.4922 | 20 | 4 | Unplanned manufacturing and technical problems can delay the completion of a flight test program, increase the number of flight test hours needed to verify that the system will work as intended, and affect when key knowledge will be available for making invest |  |
| 4 | GAO-11-325 (2011) | 5 | `GAO-11-325-p005-c01` | 14.2726 | 0.4168 | 140 | 5 | established goals; (3) assess elements of design stability and manufacturing maturity and review production results; and (4) report status of development testing and technical challenges facing the program. To conduct this work, we evaluated DOD's restructurin |  |
| 5 | GAO-11-325 (2011) | 17 | `GAO-11-325-p017-c01` | 14.076 | 0.3054 | 625 | 7 | heightened scrutiny and two-year probation period directed by the Secretary to engineer solutions, assess impacts, and inform a future decision as to whether and how to proceed with this variant. Evaluating annual performance against stated goals can be an eff |  |

## Q12: downstream_cost_schedule

What evidence quantifies how F-35 development delays or problems propagated into cost growth or schedule slip in later phases, including retrofit costs for aircraft already produced?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GAO-08-388 (2008) | 23 | `GAO-08-388-p023-c03` | 18.7025 | 0.4926 | 102 | 1 | is not expected to enter flight testing until fiscal year 2012, increasing risks that problems found may require redesign, production line changes, and retrofit expenses for aircraft already built. On the basis of the evidence, we expect JSF program costs to i |  |
| 2 | GAO-08-388 (2008) | 2 | `GAO-08-388-p002-c03` | 14.1362 | 0.4902 | 108 | 3 | Progress has been reported in several important areas, including partner agreements, first flights of a JSF prototype and test bed, and a more realistic procurement schedule. The midcourse plan carries the risk of design and performance problems not being disc |  |
| 3 | GAO-10-382 (2010) | 23 | `GAO-10-382-p023-c01` | 14.1215 | 0.3206 | 671 | 4 | base; increases in the amount of on- and out-of-station work required on aircraft in production; and require costly retrofitting of aircraft already produced and fielded. A best practice is to achieve design stability at the system-level critical design review |  |
| 4 | GAO-07-360 (2007) | 20 | `GAO-07-360-p020-c00` | 13.9839 | 0.4642 | 196 | 5 | manufacture and deliver 15 flight test aircraft and 7 ground test articles in 5 years—an aggressive schedule when compared with other programs with fewer variables. For example, the F-22A program took almost 8 years to manufacture and deliver nine flight test  |  |
| 5 | GAO-10-382 (2010) | 34 | `GAO-10-382-p034-c01` | 13.783 | 0.504 | 67 | 6 | Significant Investments in Aircraft Are Planned Before Flight Testing Is Completed Although officials recently reduced near-term procurement plans and added test aircraft, DOD is still planning significant investments in procuring large quantities of JSF aircr |  |

## Q13: software_integration

What evidence shows that Block 4 or Technology Refresh 3 (TR-3) hardware-software dependencies affected F-35 testing or fielding?

| # | Source (year) | PDF p. | Chunk | Strategy score | sem | dense | bm25 | Excerpt | Judgment |
|---|---|---|---|---|---|---|---|---|---|
| 1 | DOTE-FY2024-F35 (?) | 3 | `DOTE-FY2024-F35-p003-c03` | 31.1984 | 0.5483 | 13 | 1 | Block 4 includes DT and OT with aircraft in the TR-2 configuration. For these aircraft, the program has designated flight software using a 30-series designation (i.e., 30RXX for development and flight testing software iterations, and 30PXX for final production |  |
| 2 | DOTE-FY2024-F35 (?) | 2 | `DOTE-FY2024-F35-p002-c03` | 29.9789 | 0.598 | 6 | 2 | The report supported a subsequent Defense Acquisition Board, which resulted in the USD(A&S) approving full-rate production in a March 2024 ADM. The full-rate production decision ADM directed the program to designate two major subprograms within the overall acq |  |
| 3 | DOTE-FY2024-F35 (?) | 1 | `DOTE-FY2024-F35-p001-c01` | 28.1293 | 0.4345 | 81 | 4 | The program proceeded to full-rate production, based on an acquisition decision memorandum (ADM) signed by USD(A&S) in March 2024. The transition to full-rate production occurred in the middle of nearly a year-long pause in acceptance of production aircraft, a |  |
| 4 | DOTE-FY2024-F35 (?) | 8 | `DOTE-FY2024-F35-p008-c01` | 26.2269 | 0.6552 | 3 | 5 | against capabilities in the 30R08 software, many of which were against capabilities that were working in previous versions of software, an indication of insufficient integration and regression testing. Development Although the program and Services have begun a |  |
| 5 | DOTE-FY2024-F35 (?) | 7 | `DOTE-FY2024-F35-p007-c01` | 24.592 | 0.543 | 17 | 7 | software to improve capability of fielded systems that have the TR-2 avionics architecture while developing the 40-series software required to run on the new TR-3 architecture. Challenges added with the TR-3 avionics upgrades, both in development and testing,  |  |
