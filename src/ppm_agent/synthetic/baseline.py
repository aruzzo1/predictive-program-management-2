"""Evidence-Calibrated Synthetic F-35 Development Baseline v1.1: the definitions behind data/synthetic/.

v1.1 is a minor structural revision of the frozen v1.0 (archived in data/synthetic/archive/v1.0/): one cross-node
rework feedback (A415 -> A225) and A510 moved to D8. See VERSION_HISTORY.

This module is the single source of truth for the synthetic IMP / IMS. scripts/build_synthetic_baseline.py
writes the files in data/synthetic/ from it, and ppm_agent.synthetic.validation checks them.

It is NOT an actual or reconstructed F-35 contractor IMP / IMS. Provenance classes:
  OBSERVED  - directly supported by public F-35 source documentation (the evidence register only);
  DERIVED   - an analytical dependency concept inferred from observed evidence (Q01, Q04, Q07, Q08);
  SYNTHETIC - durations, schedule positions, activity structure, disturbances, interventions and outcomes.
Every activity, IMP event and scenario is SYNTHETIC. A dependency is DERIVED only at the concept level; the
specific activity-to-activity link that implements it is always SYNTHETIC (implementation_classification).

Time is in relative workdays from synthetic day 0. No calendar dates are used. The schedule is planned,
not statused: percent_complete is 0 and forecast equals baseline in the BASELINE files.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

DATASET_NAME = "Evidence-Calibrated Synthetic F-35 Development Baseline"
DATASET_VERSION = "1.1"
FREEZE = {
    "status": "FROZEN",
    "scope": "Capstone MVP",
    "version": DATASET_VERSION,
    "frozen_on": "2026-11-01",
    "preserved": {"imp_events": 8, "ims_activities": 35, "dsm_nodes": 8, "dependencies": 43, "scenarios": 6,
                  "A230_total_float": 4, "A325_total_float": 0, "baseline_program_duration_workdays": 355},
    "change_policy": ("No further changes to durations, float, scenario magnitudes, predecessor logic or policy values "
                      "unless a genuine implementation defect is found; any such fix must be recorded as a new version."),
    "decisions": ["INTERVENTION_2 stays based on DISTURBANCE_1 (mission-system software delay): resequencing lets test "
                  "content that does not need the delayed mission-system capability proceed after the A405 readiness gate.",
                  "Q04 keeps weight 0.50 in the DSM: where an agentic decision exists (Q04 UNRESOLVED), it governs the weight."],
}
VERSION_HISTORY = [
    {"version": "1.0", "status": "SUPERSEDED (archived, unchanged)", "archive": "data/synthetic/archive/v1.0/",
     "summary": "Original frozen synthetic baseline (42 dependencies; A510 in D7; rework feedback A425 -> A410 only).",
     "file_sha256": {
         "synthetic_imp.csv": "6c3d8e2e98193463c71350ef0220d862fa9e8b52b751342dbbb283e54c39ad8d",
         "synthetic_ims.csv": "8f030be5a999cca70b1388479f5ce81c31e919d6f28a7fc89561019e3e3d86ac",
         "synthetic_dependencies.csv": "c327c16425f3f3120980b2423d3447939587dcfd1922edd4eca47bd8308a8cca",
         "synthetic_scenarios.json": "b7c49795c89e0408bf1e6028e59ca425359858e2b18ff98d1a0caf4121a0b743",
         "synthetic_provenance.json": "6e5ce36af2979c86f2d8f50feb30cc0d2e21238aa142388544dcaf252e183fed",
     }},
    {"version": "1.1", "status": "FROZEN (current)",
     "summary": "Minor structural-model revision made after DSM aggregation exposed two abstraction defects.",
     "changes": [
         "1. Cross-node rework feedback: added FEEDBACK_REWORK dependency A415 -> A225 (D6 -> D4), concept DERIVED "
         "(Q01), implementation SYNTHETIC; not a scheduling predecessor. Dependencies 42 -> 43.",
         "2. DSM-node assignment: A510 moved from D7 to D8, so the existing A430 -> A510 (Q08) maps to D7 -> D8.",
     ],
     "unchanged": ("Durations, predecessor schedule, baseline dates, total floats (A230 4, A325 0), the 355-workday "
                   "duration, IMP / IMS counts, scenario magnitudes and intervention policies. No schedule calibration changed.")},
]
STATEMENT = ("This synthetic IMP/IMS is an evidence-calibrated experimental model created for the Predictive Program "
             "Management 2.0 capstone. It is not an actual or reconstructed F-35 contractor schedule.")

OBSERVED, DERIVED, SYNTHETIC = "OBSERVED", "DERIVED", "SYNTHETIC"
PROVENANCE_CLASSES = (OBSERVED, DERIVED, SYNTHETIC)
SOURCE_CASES = ("Q01", "Q04", "Q07", "Q08")
NO_CASE = "NONE"

FINISH_TO_START = "FINISH_TO_START"
FEEDBACK_REWORK = "FEEDBACK_REWORK"  # rework return path; documented, never a scheduling predecessor
RELATIONSHIP_TYPES = (FINISH_TO_START, FEEDBACK_REWORK)

# support for a DERIVED dependency concept (my reading of the retrieved passages; not a validated label)
EXPLICIT_PASSAGE, FRAGMENTARY, NOT_APPLICABLE = "EXPLICIT_PASSAGE", "FRAGMENTARY", "NOT_APPLICABLE"
SUPPORT_LABELS = {
    EXPLICIT_PASSAGE: "At least one passage recorded in the project's evaluation outputs states the relationship concept directly.",
    FRAGMENTARY: "The concept is assembled from separate fragments across passages or documents; no single passage states it.",
    NOT_APPLICABLE: "Synthetic sequencing; no corpus support is claimed.",
}

RISK_STATES = ("LOW", "MEDIUM", "HIGH")
REWORK_INDICATORS = {
    "NONE": "Not a rework activity.",
    "CORRECTIVE": "Planned correction of deficiencies found upstream (outside the explicit loop).",
    "LOOP": "Member of the explicit flight-test rework loop A410 -> A415 -> A420 -> A425 (-> A410).",
    "EXPOSURE": "Assesses accumulated rework / cost-schedule exposure.",
}

EXPECTED_IMS_COUNT, EXPECTED_IMP_COUNT, EXPECTED_DSM_COUNT = 35, 8, 8
START_ACTIVITY, FINISH_ACTIVITY = "A100", "A520"
REWORK_LOOP = ("A410", "A415", "A420", "A425")
REWORK_FEEDBACK = ("A425", "A410")            # within flight test: regression results -> further flight test (D6 -> D6)
SOFTWARE_REWORK_FEEDBACK = ("A415", "A225")   # v1.1: test-discovered deficiencies -> software correction (D6 -> D4)
REWORK_FEEDBACKS = (REWORK_FEEDBACK, SOFTWARE_REWORK_FEEDBACK)
NODE_ASSIGNMENT_CHECKS = {"A430": "D7", "A510": "D8"}  # v1.1 abstraction boundary

# SYNTHETIC design calibrations and scenario-policy values (v1.0 revision; experimental assumptions, not history)
READINESS_GATE, READINESS_GATE_PREDECESSORS = "A405", ("A400", "A230", "A325")
SOFTWARE_PATH_END, TARGET_SOFTWARE_FLOAT = "A230", 4
RESEQUENCING_POLICY, DELAY_ABSORPTION_DAYS = "FLIGHT_TEST_RESEQUENCING_AFTER_READINESS", 4
STAGED_COMMITMENT_POLICY = "STAGED_PRODUCTION_COMMITMENT"
PRE_MATURITY_COMMITMENT_FRACTION, POST_MATURITY_COMMITMENT_FRACTION = 0.40, 0.60

FILES = {
    "imp": "synthetic_imp.csv",
    "ims": "synthetic_ims.csv",
    "dependencies": "synthetic_dependencies.csv",
    "scenarios": "synthetic_scenarios.json",
    "provenance": "synthetic_provenance.json",
}

REQ = "Requirements / KPPs"
AVD = "Air Vehicle Design / Weight"
MSS = "Mission-System Software"
TAA = "Test-Aircraft Availability"
FTE = "Flight-Test Execution"
DTM = "Development / Test Maturity"
PRC = "Production Commitment"
RWK = "Rework / Cost-Schedule Exposure"
WORKSTREAMS = (REQ, AVD, MSS, TAA, FTE, DTM, PRC, RWK)

IMP_EVENTS = [
    ("IMP-01", "Requirements Baseline Established", "Requirements and interfaces allocated and reviewed."),
    ("IMP-02", "Air Vehicle Design Maturity Achieved", "Weight corrections implemented and controlled design baseline released."),
    ("IMP-03", "Mission-System Integration Baseline Ready", "Critical integration deficiencies corrected and integration baseline verified."),
    ("IMP-04", "Test-Aircraft Readiness Achieved", "Test aircraft configured, instrumented, checked out and certified available."),
    ("IMP-05", "Development Flight-Test Entry Criteria Met", "Test plans approved and test readiness review passed."),
    ("IMP-06", "Flight-Test Maturity Demonstrated", "Initial block, correction and regression complete; technical maturity assessed."),
    ("IMP-07", "Development / Production Readiness Assessed", "Production planning and long-lead commitment assessed against test maturity."),
    ("IMP-08", "Controlled Production Configuration Released", "Residual rework risk evaluated and production configuration released."),
]

DSM_NODES = [
    ("D1", "Requirements / KPP Definition", []),
    ("D2", "Air Vehicle Design Maturity", []),
    ("D3", "Weight / Structural Maturity", ["Q07"]),
    ("D4", "Mission-System Software Maturity", ["Q01"]),
    ("D5", "Test-Aircraft Availability", ["Q04"]),
    ("D6", "Flight-Test Execution", ["Q01", "Q04"]),
    ("D7", "Development / Test Maturity", ["Q08"]),
    ("D8", "Production Commitment / Rework Exposure", ["Q07", "Q08"]),
]

NO_EVIDENCE = "None claimed: generic development-program activity."


def _act(aid, name, workstream, imp, duration, preds, dsm, maturity, rework, risk, cases, evidence, note=""):
    assumption = f"Activity definition, {duration}-workday duration, predecessors and {risk} risk state are synthetic."
    return {
        "activity_id": aid, "activity_name": name, "workstream": workstream, "imp_event": imp, "dsm_node": dsm,
        "baseline_duration_days": duration, "predecessor_ids": preds, "maturity_indicator": maturity,
        "rework_indicator": rework, "risk_state": risk, "source_case": cases or [NO_CASE],
        "evidence_basis": evidence, "synthetic_assumption": f"{assumption} {note}".strip(),
    }


ACTIVITIES = [
    # Requirements / baseline
    _act("A100", "Establish Program Requirements Baseline", REQ, "IMP-01", 20, [], "D1",
         "Requirements baseline approved", "NONE", "LOW", [], NO_EVIDENCE, "Network start activity."),
    _act("A105", "Identify Critical KPP and Performance Drivers", REQ, "IMP-01", 10, ["A100"], "D1",
         "KPP and performance-driver list agreed", "NONE", "MEDIUM", ["Q07"],
         "Theme: STOVL weight-driven design changes affected key performance parameters (GAO-05-271 p.10, fragment "
         "found by the Q07 diagnostic scan). No requirements documents (ORD/JORD/CDD) are in the corpus."),
    _act("A110", "Allocate System and Interface Requirements", REQ, "IMP-01", 15, ["A105"], "D1",
         "Requirements allocated to subsystems and interfaces", "NONE", "LOW", [], NO_EVIDENCE),
    _act("A115", "Complete Requirements / Interface Review", REQ, "IMP-01", 5, ["A110"], "D1",
         "Requirements / interface review closed", "NONE", "LOW", [], NO_EVIDENCE),
    # Air vehicle design / weight
    _act("A120", "Develop Air Vehicle Preliminary Design Baseline", AVD, "IMP-02", 30, ["A115"], "D2",
         "Preliminary design baseline complete", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A125", "Perform Structural and Weight Assessment", AVD, "IMP-02", 20, ["A120"], "D3",
         "Weight estimate vs. allocation", "NONE", "HIGH", ["Q07"],
         "Theme: weight problems found during system integration and design review (GAO-10-382 p.7; GAO-11-325 p.5)."),
    _act("A130", "Evaluate Weight Margin Against Performance Requirements", AVD, "IMP-02", 10, ["A125", "A105"], "D3",
         "Weight margin vs. KPP thresholds", "NONE", "HIGH", ["Q07"],
         "Theme: weight growth and its impact on key performance parameters (GAO-05-271 p.10)."),
    _act("A135", "Implement Weight / Structural Design Corrections", AVD, "IMP-02", 25, ["A130"], "D3",
         "Weight-reduction design changes closed", "CORRECTIVE", "HIGH", ["Q07"],
         "Theme: redesign to address weight growth was the largest factor in development cost and schedule growth "
         "(GAO-08-388 p.34)."),
    _act("A140", "Conduct Air Vehicle Design Maturity Review", AVD, "IMP-02", 10, ["A135"], "D2",
         "Design stability / drawing-release status", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A145", "Release Controlled Air Vehicle Design Baseline", AVD, "IMP-02", 5, ["A140"], "D2",
         "Controlled design baseline released", "NONE", "MEDIUM", [], NO_EVIDENCE),
    # Mission systems / software
    _act("A200", "Establish Mission-System Software Requirements Baseline", MSS, "IMP-03", 15, ["A115"], "D4",
         "Software requirements baselined", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A205", "Develop Mission-System Software Increment", MSS, "IMP-03", 66, ["A200"], "D4",
         "Increment code complete vs. plan", "NONE", "HIGH", ["Q01"],
         "Theme: mission-system software behind schedule (GAO-10-382 p.31).",
         "Float calibration (v1.0 revision): duration raised from 40 to 66 so the software path reaches A405 with "
         "4 workdays of total float; chosen for a decision-relevant demonstration, not to reproduce F-35 history."),
    _act("A210", "Integrate Mission-System Software Components", MSS, "IMP-03", 25, ["A205"], "D4",
         "Integration build stability", "NONE", "HIGH", ["Q01"],
         "Theme: software and sensor integration risk (DOT&E FY2010 p.33).", "DISTURBANCE_1 target."),
    _act("A215", "Conduct Software / Hardware Integration Testing", MSS, "IMP-03", 20, ["A210"], "D4",
         "Integration test pass rate", "NONE", "HIGH", ["Q01"],
         "Theme: integration before verification (DOT&E FY2010 p.33)."),
    _act("A220", "Analyze Integration Deficiencies", MSS, "IMP-03", 10, ["A215"], "D4",
         "Open integration deficiency count", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A225", "Correct Critical Software / Integration Deficiencies", MSS, "IMP-03", 20, ["A220"], "D4",
         "Critical deficiency closure rate", "CORRECTIVE", "HIGH", [], NO_EVIDENCE),
    _act("A230", "Verify Mission-System Integration Baseline", MSS, "IMP-03", 10, ["A225"], "D4",
         "Integration baseline verified", "NONE", "MEDIUM", ["Q01"],
         "Theme: software delays affected flight-test progress (DOT&E FY2010 p.29)."),
    # Test aircraft / infrastructure
    _act("A300", "Define Development Test-Aircraft Configuration", TAA, "IMP-04", 15, ["A120"], "D5",
         "Test-aircraft configuration defined", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A305", "Modify / Configure Development Test Aircraft", TAA, "IMP-04", 30, ["A300", "A145"], "D5",
         "Aircraft configured vs. planned", "NONE", "HIGH", ["Q04", "Q07"],
         "Themes: late delivery of test aircraft (GAO-11-325 p.17, p.31; GAO-09-303 p.11); early test aircraft did "
         "not include the weight-reduction design changes (GAO-06-356 p.14).", "DISTURBANCE_2 target."),
    _act("A310", "Install Flight-Test Instrumentation", TAA, "IMP-04", 15, ["A305"], "D5",
         "Instrumentation installed", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A315", "Verify Instrumentation and Data Systems", TAA, "IMP-04", 10, ["A310"], "D5",
         "Data systems verified", "NONE", "LOW", [], NO_EVIDENCE),
    _act("A320", "Conduct Ground Checkout of Test Aircraft", TAA, "IMP-04", 10, ["A315"], "D5",
         "Ground checkout complete", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A325", "Certify Test-Aircraft Readiness and Availability", TAA, "IMP-04", 5, ["A320"], "D5",
         "Aircraft available vs. planned", "NONE", "HIGH", ["Q04"],
         "Theme: test-aircraft availability constrained flight-test pace (GAO-11-325 p.17, p.31)."),
    # Flight test (A420 sits in the rework workstream but in the flight-test DSM node)
    _act("A400", "Develop Flight-Test Plans and Procedures", FTE, "IMP-05", 20, ["A115"], "D6",
         "Test plans approved", "NONE", "LOW", [], NO_EVIDENCE),
    _act("A405", "Conduct Development Test Readiness Review", FTE, "IMP-05", 5, ["A400", "A230", "A325"], "D6",
         "Flight-test entry criteria met", "NONE", "HIGH", ["Q01", "Q04"],
         "Gate where software maturity (Q01) and test-aircraft availability (Q04) meet flight-test execution."),
    _act("A410", "Execute Initial Development Flight-Test Block", FTE, "IMP-06", 40, ["A405"], "D6",
         "Test points completed vs. planned", "LOOP", "HIGH", ["Q01", "Q04"],
         "Themes: software delays affected flight-test progress (DOT&E FY2010 p.29); late test aircraft hampered "
         "flight tests (GAO-11-325 p.17).", "Rework-loop entry; receives the A425 feedback."),
    _act("A415", "Analyze Flight-Test Results and Deficiencies", FTE, "IMP-06", 15, ["A410"], "D6",
         "Deficiencies discovered in flight test", "LOOP", "HIGH", ["Q01"],
         "Theme: discovery in flight test and deferrals to later increments (DOT&E FY2010 p.33)."),
    _act("A420", "Implement Corrective Engineering / Software Changes", RWK, "IMP-06", 20, ["A415"], "D6",
         "Corrective changes closed", "LOOP", "HIGH", ["Q01"],
         "Theme: extended development after discovery in flight test (DOT&E FY2010 p.33)."),
    _act("A425", "Execute Regression / Verification Testing", FTE, "IMP-06", 20, ["A420"], "D6",
         "Regression pass rate", "LOOP", "MEDIUM", [], NO_EVIDENCE, "Rework-loop exit; feeds back to A410."),
    _act("A430", "Assess Flight-Test Completion and Technical Maturity", DTM, "IMP-06", 10, ["A425"], "D7",
         "Test-maturity assessment", "NONE", "MEDIUM", ["Q08"],
         "Theme: test knowledge available at production decisions (GAO-07-360 p.7)."),
    # Production / concurrency
    _act("A500", "Establish Initial Production Planning Baseline", PRC, "IMP-07", 15, ["A145"], "D8",
         "Production planning baseline set", "NONE", "MEDIUM", [], NO_EVIDENCE),
    _act("A505", "Commit Long-Lead Production Resources", PRC, "IMP-07", 20, ["A500"], "D8",
         "Long-lead commitment made", "NONE", "HIGH", ["Q08"],
         "Theme: production commitments made before testing demonstrates performance (GAO-07-360 p.7; GAO-06-356 p.6).",
         "Deliberately not gated on A430 in the baseline (concurrency); INTERVENTION_3 stages the commitment instead."),
    _act("A510", "Conduct Development / Production Readiness Assessment", DTM, "IMP-07", 10, ["A505", "A430"], "D8",
         "Development / production readiness", "NONE", "HIGH", ["Q08"],
         "Theme: development-test-production concurrency (GAO-07-360 p.7, p.22).",
         "DSM node moved from D7 to D8 in v1.1 so the Q08 link A430 -> A510 crosses the node boundary."),
    _act("A515", "Evaluate Residual Rework and Configuration Risk", RWK, "IMP-08", 10, ["A510", "A420", "A135"], "D8",
         "Residual rework exposure", "EXPOSURE", "HIGH", ["Q07", "Q08"],
         "Themes: weight redesign drove cost and schedule growth (GAO-08-388 p.34); problems found may require "
         "redesign, production-line changes and retrofit of aircraft already built (GAO-08-388 p.23)."),
    _act("A520", "Release Controlled Production Configuration", PRC, "IMP-08", 5, ["A515"], "D8",
         "Production configuration released", "NONE", "MEDIUM", [], NO_EVIDENCE, "Network finish activity."),
]

# DERIVED dependency concepts and the synthetic links that implement them: (source, target) -> details
DERIVED_LINKS = {
    ("A105", "A130"): ("Q07", FRAGMENTARY, "KPP / performance requirements -> weight-margin evaluation",
                       "GAO-05-271 p.10: STOVL weight-driven design changes and their impact on key performance parameters."),
    ("A130", "A135"): ("Q07", EXPLICIT_PASSAGE, "Weight growth -> redesign",
                       "GAO-08-388 p.34: redesign efforts to address weight growth."),
    ("A145", "A305"): ("Q07", FRAGMENTARY, "Weight-driven redesign -> test-aircraft configuration",
                       "GAO-06-356 p.14: first flight-test aircraft would not include the weight-reduction design changes."),
    ("A135", "A515"): ("Q07", EXPLICIT_PASSAGE, "Weight / redesign -> downstream cost / schedule exposure",
                       "GAO-08-388 p.34: weight redesign was the single largest factor in the $10 billion cost increase and "
                       "18-month development extension (GAO-11-325 p.40 gives $7 billion / 18 months; not reconciled)."),
    ("A230", "A405"): ("Q01", EXPLICIT_PASSAGE, "Mission-system software maturity -> flight-test execution",
                       "DOT&E FY2010 p.29: software delays that affected flight-test progress; GAO-10-382 p.31: software "
                       "behind schedule may delay first mission-system flight test."),
    ("A325", "A405"): ("Q04", EXPLICIT_PASSAGE, "Test-aircraft availability -> flight-test execution",
                       "GAO-11-325 p.17: flight tests hampered by late delivery of test aircraft; GAO-11-325 p.31; "
                       "GAO-09-303 p.11: test-aircraft delays expected to compress test schedules."),
    ("A415", "A420"): ("Q01", FRAGMENTARY, "Discovery in flight test -> corrective engineering / software changes",
                       "DOT&E FY2010 p.33: extended development, discovery in flight test, deferrals to later increments."),
    ("A430", "A510"): ("Q08", EXPLICIT_PASSAGE, "Development / test maturity -> production commitment",
                       "GAO-07-360 p.7: at the LRIP decision less than 1 percent of the test program will have been "
                       "completed; GAO-07-360 p.22: more concurrent than the F-22A."),
    ("A420", "A515"): ("Q08", FRAGMENTARY, "Late test discovery -> rework exposure for committed production",
                       "GAO-08-388 p.23: problems found may require redesign, production-line changes and retrofit for "
                       "aircraft already built (qualitative; no quantified rework cost observed)."),
    ("A425", "A410"): ("Q01", FRAGMENTARY, "Regression results -> further flight test (rework loop)",
                       "DOT&E FY2010 p.33: familiar pattern of discovery in flight test followed by further development."),
    ("A415", "A225"): ("Q01", FRAGMENTARY,
                       "Test-discovered software / integration deficiencies -> corrective software / integration work",
                       "DOT&E FY2010 p.33: extended development, discovery in flight test, deferrals to later increments; "
                       "DOT&E FY2010 p.29: software delays affected flight-test progress."),
}

SCENARIOS = [
    {"scenario_id": "BASELINE", "scenario_type": "BASELINE", "name": "Synthetic planned baseline", "base_scenario": None,
     "related_source_case": NO_CASE, "description": "The frozen v1.0 network with no disturbance or intervention.",
     "changes": []},
    {"scenario_id": "DISTURBANCE_1", "scenario_type": "DISTURBANCE", "base_scenario": "BASELINE",
     "name": "Mission-system software integration late", "related_source_case": "Q01",
     "description": "A210 Integrate Mission-System Software Components is projected to finish 8 workdays late.",
     "changes": [{"change_type": "DURATION_DELTA", "activity_id": "A210", "delta_workdays": 8}]},
    {"scenario_id": "DISTURBANCE_2", "scenario_type": "DISTURBANCE", "base_scenario": "BASELINE",
     "name": "Test-aircraft configuration late", "related_source_case": "Q04",
     "description": "A305 Modify / Configure Development Test Aircraft is projected to finish 4 workdays late.",
     "changes": [{"change_type": "DURATION_DELTA", "activity_id": "A305", "delta_workdays": 4}]},
    {"scenario_id": "INTERVENTION_1", "scenario_type": "INTERVENTION", "base_scenario": "DISTURBANCE_1",
     "name": "Software recovery action", "related_source_case": "Q01",
     "description": "A software recovery action on A210 recovers 4 of the 8 late workdays.",
     "changes": [{"change_type": "DURATION_DELTA", "activity_id": "A210", "delta_workdays": -4}]},
    {"scenario_id": "INTERVENTION_2", "scenario_type": "INTERVENTION", "base_scenario": "DISTURBANCE_1",
     "name": "Flight-test resequencing after readiness", "related_source_case": "Q01",
     "description": ("A405 keeps all its predecessors; readiness is never bypassed. After A405 is satisfied, flight-test "
                     "content that does not need the delayed mission-system capability is flown first while the affected "
                     "content waits, absorbing up to 4 workdays of the delay that reaches the A410 flight-test block."),
     "changes": [{"change_type": "POLICY", "policy": RESEQUENCING_POLICY, "readiness_gate_activity": "A405",
                  "applies_to_activity": "A410", "delay_absorption_days": DELAY_ABSORPTION_DAYS,
                  "intended_simulator_semantics": (
                      "Let d = delay of A410's start versus baseline. A410 finish = baseline finish + max(0, d - "
                      "delay_absorption_days). A405 and A410 start are unchanged by the policy; no predecessor is removed.")}]},
    {"scenario_id": "INTERVENTION_3", "scenario_type": "INTERVENTION", "base_scenario": "BASELINE",
     "name": "Staged production commitment", "related_source_case": "Q08",
     "description": ("Concurrency is retained: A505 still starts without waiting for A430. Only 40% of the modeled "
                     "long-lead commitment is made before A430 Development / Test Maturity; the remaining 60% is gated "
                     "on A430. Compares full concurrent commitment with reduced pre-maturity exposure."),
     "changes": [{"change_type": "POLICY", "policy": STAGED_COMMITMENT_POLICY, "commitment_activity": "A505",
                  "maturity_gate_activity": "A430",
                  "pre_maturity_commitment_fraction": PRE_MATURITY_COMMITMENT_FRACTION,
                  "post_maturity_commitment_fraction": POST_MATURITY_COMMITMENT_FRACTION,
                  "intended_simulator_semantics": (
                      "Exposure to rework found before A430 applies to pre_maturity_commitment_fraction of the A505 "
                      "commitment; post_maturity_commitment_fraction is committed only once A430 finishes. No baseline "
                      "predecessor is added. Rework and cost effects are not modeled yet.")}]},
]

# Evidence register: OBSERVED statements, as recorded in the project's evaluation outputs (not re-read from the PDFs)
OBSERVED_EVIDENCE = [
    ("OBS-01", "Q01", "DOT&E FY2010", "p.29", "Mission-system software experienced delays that affected flight-test progress.",
     "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-02", "Q01", "DOT&E FY2010", "p.33", "Mission-systems software tending towards familiar historical patterns of "
     "extended development, discovery in flight test, and deferrals to later increments.",
     "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-03", "Q01", "GAO-10-382", "p.31", "Software behind schedule; may delay first mission-system flight test.",
     "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-04", "Q04", "GAO-11-325", "p.17", "Flight tests hampered, as in prior years, by the late delivery of test aircraft.",
     "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-05", "Q04", "GAO-11-325", "p.31", "Continuing effects from late delivery of test aircraft substantially reduced "
     "accomplishments.", "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-06", "Q04", "GAO-09-303", "p.11", "Delays in delivering test aircraft are expected to hamper and further compress "
     "test schedules.", "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-07", "Q07", "GAO-08-388", "p.34", "Redesign efforts to address weight growth was the single largest factor causing "
     "the $10 billion cost increase and 18-month extension in the development schedule.",
     "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-08", "Q07", "GAO-10-382; GAO-11-325", "p.7; p.5", "Weight problems found during system integration and design "
     "review led to the 2004 rebaseline and schedule extension.", "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-09", "Q07", "GAO-05-271", "p.10", "STOVL weight-driven design changes affected key performance parameters; the "
     "other variants' designs were affected as well.", "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-10", "Q07", "GAO-06-356", "p.14", "The first flight-test aircraft would not include the weight-reduction design "
     "changes and so would not represent the production configuration.", "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-11", "Q07", "GAO-11-325", "p.40", "The re-plan to address weight added $7 billion and 18 months (differs from "
     "GAO-08-388's $10 billion; not reconciled).", "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-12", "Q08", "GAO-07-360", "p.7", "Concurrency risks: at the LRIP decision less than 1 percent of the test program "
     "will have been completed.", "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-13", "Q08", "GAO-07-360", "p.22", "The JSF was planned to be significantly more concurrent than the F-22A.",
     "outputs/evaluation/agentic_phase1_three_case_summary.md"),
    ("OBS-14", "Q08", "GAO-06-356", "p.6", "A highly concurrent approach that makes significant investments in manufacturing "
     "capabilities and production aircraft before flight testing demonstrates performance.",
     "outputs/evaluation/rag_v1_v2_comparison.md"),
    ("OBS-15", "Q08", "GAO-08-388", "p.23", "Problems found may require redesign, production-line changes, and retrofit "
     "expenses for aircraft already built.", "outputs/evaluation/rag_v1_v2_comparison.md"),
]

SOURCE_CASE_NOTES = {
    "Q01": {
        "question": "What evidence indicates that mission-system software maturity affected F-35 flight-test execution?",
        "derived_concept": ("Mission-System Software Maturity -> Flight-Test Execution (D4 -> D6), with test-discovered "
                            "deficiencies feeding back to software correction (D6 -> D4, v1.1)"),
        "agentic_phase1_result": "PARTIALLY_SUPPORTED (DIRECT 70.5, near-tied with INDIRECT; single REAL_LLM_MODE run)",
        "how_it_informed": ("Software integration activities (A205-A230) gate the flight-test readiness review (A230 -> A405); "
                            "discovery in flight test motivates the explicit rework loop and the A415 -> A225 software rework "
                            "feedback (v1.1); DISTURBANCE_1, INTERVENTION_1 and INTERVENTION_2 act on this path."),
    },
    "Q04": {
        "question": ("What evidence describes how late delivery or limited availability of F-35 test aircraft constrained "
                     "the sequence or pace of flight testing?"),
        "derived_concept": "Test-Aircraft Availability -> Flight-Test Execution (D5 -> D6)",
        "agentic_phase1_result": "UNRESOLVED (best DIRECT 69.5, 0.5 below threshold; single run)",
        "how_it_informed": ("A dedicated test-aircraft chain (A300-A325) gates the readiness review (A325 -> A405); "
                            "this chain controls A405 at baseline; motivates DISTURBANCE_2."),
    },
    "Q07": {
        "question": "What evidence shows that F-35 aircraft weight growth caused redesign or schedule consequences?",
        "derived_concept": "Weight / redesign -> downstream cost / schedule exposure (D3 -> D8; also D3 -> D2 -> D5)",
        "agentic_phase1_result": "Not run as an agentic case. Retrieval found one explicit passage; the rest of the chain is fragmentary.",
        "how_it_informed": ("Weight assessment, margin evaluation and correction (A125-A135) sit on the design path; the "
                            "redesign feeds test-aircraft configuration (A145 -> A305) and residual rework exposure (A135 -> A515)."),
    },
    "Q08": {
        "question": ("What evidence describes dependencies between F-35 development testing and production decisions "
                     "(development-test-production concurrency)?"),
        "derived_concept": "Development / Test Maturity -> Production Commitment / Rework Exposure (D7 -> D8)",
        "agentic_phase1_result": "UNRESOLVED (best 65.5; single run)",
        "how_it_informed": ("Long-lead commitment (A505) deliberately precedes flight-test maturity (concurrency); the readiness "
                            "assessment waits for A430 (A430 -> A510, D7 -> D8 since v1.1); late corrections feed rework "
                            "exposure (A420 -> A515); "
                            "INTERVENTION_3 stages the commitment (40% before / 60% after A430) without removing concurrency."),
    },
}


# --- schedule ----------------------------------------------------------------------------------------

def forward_pass(durations: dict[str, int], edges: list[tuple[str, str, int]]) -> dict[str, tuple[int, int]]:
    """Earliest start / finish (workday offsets) for a finish-to-start network. Raises ValueError on a cycle."""
    preds = defaultdict(list)
    indegree = {a: 0 for a in durations}
    for src, tgt, lag in edges:
        preds[tgt].append((src, lag))
        indegree[tgt] += 1
    order = [a for a in durations if indegree[a] == 0]
    succs = defaultdict(list)
    for src, tgt, _ in edges:
        succs[src].append(tgt)
    schedule: dict[str, tuple[int, int]] = {}
    i = 0
    while i < len(order):
        a = order[i]
        i += 1
        start = max([schedule[p][1] + lag for p, lag in preds[a]], default=0)
        schedule[a] = (start, start + durations[a])
        for s in succs[a]:
            indegree[s] -= 1
            if indegree[s] == 0:
                order.append(s)
    if len(schedule) != len(durations):
        raise ValueError(f"cycle among: {sorted(set(durations) - set(schedule))}")
    return schedule


def total_float(durations: dict[str, int], edges: list[tuple[str, str, int]]) -> dict[str, int]:
    """Total float (latest start - earliest start) against the network finish, via a backward pass."""
    early = forward_pass(durations, edges)
    project_finish = max(f for _, f in early.values())
    succs = defaultdict(list)
    for src, tgt, lag in edges:
        succs[src].append((tgt, lag))
    late_start: dict[str, int] = {}
    for a in reversed(list(early)):  # forward_pass returns activities in topological order
        late_finish = min([late_start[s] - lag for s, lag in succs[a]], default=project_finish)
        late_start[a] = late_finish - durations[a]
    return {a: late_start[a] - early[a][0] for a in early}


def schedule_edges() -> list[tuple[str, str, int]]:
    return [(p, a["activity_id"], 0) for a in ACTIVITIES for p in a["predecessor_ids"]]


# --- table builders ----------------------------------------------------------------------------------

def _join(items) -> str:
    return ";".join(items)


def ims_rows() -> list[dict]:
    durations = {a["activity_id"]: a["baseline_duration_days"] for a in ACTIVITIES}
    schedule = forward_pass(durations, schedule_edges())
    floats = total_float(durations, schedule_edges())
    successors = defaultdict(list)
    for a in ACTIVITIES:
        for p in a["predecessor_ids"]:
            successors[p].append(a["activity_id"])
    rows = []
    for a in ACTIVITIES:
        start, finish = schedule[a["activity_id"]]
        rows.append({
            "activity_id": a["activity_id"], "activity_name": a["activity_name"], "workstream": a["workstream"],
            "imp_event": a["imp_event"], "dsm_node": a["dsm_node"], "baseline_duration_days": a["baseline_duration_days"],
            "predecessor_ids": _join(a["predecessor_ids"]), "successor_ids": _join(successors[a["activity_id"]]),
            "baseline_start": start, "baseline_finish": finish, "baseline_total_float": floats[a["activity_id"]],
            "forecast_start": start, "forecast_finish": finish,
            "percent_complete": 0, "maturity_indicator": a["maturity_indicator"], "rework_indicator": a["rework_indicator"],
            "risk_state": a["risk_state"], "data_classification": SYNTHETIC, "evidence_basis": a["evidence_basis"],
            "source_case": _join(a["source_case"]), "synthetic_assumption": a["synthetic_assumption"],
        })
    return rows


def imp_rows() -> list[dict]:
    ims = ims_rows()
    rows = []
    for imp_id, name, criteria in IMP_EVENTS:
        members = [r for r in ims if r["imp_event"] == imp_id]
        cases = sorted({c for r in members for c in r["source_case"].split(";") if c != NO_CASE})
        rows.append({
            "imp_event_id": imp_id, "imp_event_name": name, "completion_criteria": criteria,
            "activity_ids": _join(r["activity_id"] for r in members),
            "workstreams": _join(dict.fromkeys(r["workstream"] for r in members)),
            "baseline_complete_workday": max(r["baseline_finish"] for r in members),
            "data_classification": SYNTHETIC,
            "evidence_basis": ("Event structure is synthetic; themes of its activities are informed by "
                               + ", ".join(cases) + ".") if cases else "None claimed: generic program event.",
            "source_case": _join(cases) or NO_CASE,
            "synthetic_assumption": "Event definition, grouping of activities and completion criteria are synthetic.",
        })
    return rows


def dependency_rows() -> list[dict]:
    dsm = {a["activity_id"]: a["dsm_node"] for a in ACTIVITIES}
    edges = [(src, tgt, FINISH_TO_START) for src, tgt, _ in schedule_edges()] + \
        [(src, tgt, FEEDBACK_REWORK) for src, tgt in REWORK_FEEDBACKS]
    rows = []
    for n, (src, tgt, rel) in enumerate(edges, start=1):
        derived = DERIVED_LINKS.get((src, tgt))
        if derived:
            case, support, concept, evidence = derived
            note = (f"Concept DERIVED ({concept}); the specific {src} -> {tgt} link, its type and lag are SYNTHETIC.")
        else:
            case, support, evidence = NO_CASE, NOT_APPLICABLE, "None claimed."
            note = "Generic synthetic sequencing."
        if rel == FEEDBACK_REWORK:
            note += (" Feedback (rework return) path: not a scheduling predecessor, so the baseline network stays acyclic; "
                     "rework iterations are left to the later simulation.")
        rows.append({
            "dependency_id": f"DEP-{n:03d}", "source_activity": src, "target_activity": tgt, "relationship_type": rel,
            "lag_workdays": 0, "source_dsm_node": dsm[src], "target_dsm_node": dsm[tgt],
            "data_classification": DERIVED if derived else SYNTHETIC, "implementation_classification": SYNTHETIC,
            "evidence_basis": evidence, "source_case": case, "confidence_or_support": support,
            "synthetic_implementation_note": note,
        })
    return rows


def scenarios_document() -> dict:
    return {
        "dataset": DATASET_NAME, "version": DATASET_VERSION, "statement": STATEMENT, "data_classification": SYNTHETIC,
        "time_unit": "workdays (relative)",
        "note": ("Scenario definitions only. Every magnitude, policy value and effect is SYNTHETIC (an experimental "
                 "assumption, not historically derived). Outcomes are NOT_COMPUTED: forward simulation is not yet "
                 "implemented. Changes apply on top of base_scenario. DURATION_DELTA changes a synthetic duration; POLICY "
                 "changes are parameters for the later deterministic simulator and never alter baseline predecessor logic."),
        "scenarios": [{**s, "data_classification": SYNTHETIC, "outcome": "NOT_COMPUTED",
                       "changes": [{**c, "data_classification": SYNTHETIC} for c in s["changes"]]} for s in SCENARIOS],
    }


def provenance_document() -> dict:
    deps = dependency_rows()
    return {
        "statement": STATEMENT,
        "dataset": DATASET_NAME, "version": DATASET_VERSION,
        "freeze": FREEZE,
        "version_history": VERSION_HISTORY,
        "purpose": ("Provides a structured, inspectable program schedule for the later DSM, WTM and forward-simulation stages. "
                    "The public JSF corpus contains no contractor IMP/IMS, so a synthetic one is needed to demonstrate those "
                    "methods; its dependency themes are calibrated against evidence retrieved from that corpus."),
        "not_a_reconstruction": ("Not an actual, leaked or reconstructed F-35 contractor IMP/IMS. No historical accuracy is claimed "
                                 "for any activity, duration, sequence, date or outcome."),
        "separation_from_corpus": ("Stored in data/synthetic/ only. Not placed in data/raw/jsf, not ingested, not embedded and "
                                   "not in the vector store; RAG ingestion is manifest-driven and no manifest references these files."),
        "provenance_classes": {
            OBSERVED: "Directly supported by public F-35 source documentation. Used only in observed_evidence below.",
            DERIVED: "An analytical dependency or relationship inferred from observed evidence. Used for dependency concepts and DSM node groupings.",
            SYNTHETIC: ("A duration, schedule position, activity structure, disturbance, intervention or simulated outcome created "
                        "for the capstone demonstration. Every IMS activity, IMP event, scenario and dependency implementation is SYNTHETIC."),
        },
        "classification_rules": [
            "IMS activities and IMP events: data_classification SYNTHETIC; evidence_basis names the observed theme, if any.",
            "Dependencies: data_classification is DERIVED (concept inferred from Q01/Q04/Q07/Q08 evidence) or SYNTHETIC (generic "
            "sequencing); implementation_classification is always SYNTHETIC because the exact activity-to-activity link is invented.",
            "No dependency or activity is OBSERVED: the corpus states relationships between program themes, not between these activities.",
            "Scenarios and all their magnitudes: SYNTHETIC.",
        ],
        "support_labels": SUPPORT_LABELS,
        "rework_indicators": REWORK_INDICATORS,
        "conventions": {
            "time": "Relative workdays from synthetic day 0; finish = start + duration. No calendar dates.",
            "total_float": "baseline_total_float = latest start - earliest start against the network finish (backward pass).",
            "status": "Planned baseline only: percent_complete 0 and forecast equals baseline.",
            "risk_state": "Synthetic qualitative label (LOW / MEDIUM / HIGH).",
            "rework_loop": ("A410 -> A415 -> A420 -> A425 are finish-to-start links. Two FEEDBACK_REWORK links are recorded "
                            "and excluded from predecessor_ids, so the baseline validates as acyclic: A425 -> A410 (regression "
                            "results -> further flight test, D6 -> D6) and, since v1.1, A415 -> A225 (test-discovered "
                            "software / integration deficiencies -> corrective software work, D6 -> D4)."),
            "agentic_activity_mapping": ("Agentic Phase 1 MVP pairs map to DSM nodes: A1 -> D4, A2 / A4 -> D6, A3 -> D5, "
                                         "A5 -> D7, A6 -> D8."),
        },
        "dsm_nodes": [{"node_id": nid, "name": name, "concept_classification": DERIVED, "source_cases": cases,
                       "note": "Node definition only; the DSM matrix is not built."} for nid, name, cases in DSM_NODES],
        "observed_evidence": [{"evidence_id": eid, "data_classification": OBSERVED, "source_case": case, "source_document": doc,
                               "page": page, "summary": text, "recorded_in": where}
                              for eid, case, doc, page, text, where in OBSERVED_EVIDENCE],
        "source_cases": SOURCE_CASE_NOTES,
        "derived_relationships": [{"dependency_id": d["dependency_id"], "source_activity": d["source_activity"],
                                   "target_activity": d["target_activity"], "source_case": d["source_case"],
                                   "confidence_or_support": d["confidence_or_support"]}
                                  for d in deps if d["data_classification"] == DERIVED],
        "synthetic_values": [
            "All 35 activities: their definitions, workstream / IMP / DSM assignment, durations, predecessors and risk states",
            "All 8 IMP event definitions and completion criteria",
            "Every baseline / forecast start and finish (computed from synthetic durations)",
            "Every activity-to-activity dependency link, type and lag",
            "All scenario disturbances and intervention values (A210 +8, A305 +4, A210 -4, delay_absorption_days 4, "
            "commitment fractions 0.40 / 0.60)",
            "The software-path float calibration (A205 duration 66, giving A230 total float 4)",
        ],
        "design_calibrations": {
            "data_classification": SYNTHETIC,
            "software_path_float": (
                "A205 was lengthened from 40 to 66 workdays so the software chain reaches the A405 readiness gate with 4 "
                "workdays of total float instead of 30. The path is near-critical but does not control the baseline finish; "
                "an 8-workday A210 disturbance consumes the float and then propagates, so the 4-workday recovery is "
                "decision-relevant. Selected for the proof of concept, not to reproduce F-35 schedule performance. No "
                "evidence-derived relationship was changed."),
            "resequencing_after_readiness": (
                "INTERVENTION_2 keeps every A405 predecessor. Readiness is a gate: resequencing only reorders flight-test "
                "content after A405, absorbing up to 4 workdays (delay_absorption_days) of the delay reaching A410."),
            "staged_production_commitment": (
                "INTERVENTION_3 keeps the baseline concurrency (A505 is not gated on A430). It limits pre-maturity "
                "commitment to 40% and gates the remaining 60% on A430, to compare full concurrent commitment with reduced "
                "pre-maturity exposure. The 40/60 split is a synthetic policy assumption, not historically derived."),
        },
        "limitations": [
            "Observed evidence is summarized from the project's evaluation outputs; page numbers are as recorded there and were not re-checked against the PDFs.",
            "Support labels are the author's reading of retrieved passages, not human-annotated ground truth.",
            "Agentic Phase 1 verdicts for Q01 / Q04 / Q08 were single runs within about 0.5 points of the threshold.",
            "Cost figures for the weight re-plan differ between GAO-08-388 and GAO-11-325 and are not used quantitatively.",
            "Durations are illustrative and not calibrated to any real program data.",
        ],
    }


# --- writers -----------------------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")


def build_all(out_dir: Path) -> dict[str, Path]:
    """Write the five synthetic data files to out_dir. Deterministic: same definitions, same bytes."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {k: out_dir / name for k, name in FILES.items()}
    _write_csv(paths["imp"], imp_rows())
    _write_csv(paths["ims"], ims_rows())
    _write_csv(paths["dependencies"], dependency_rows())
    _write_json(paths["scenarios"], scenarios_document())
    _write_json(paths["provenance"], provenance_document())
    return paths
