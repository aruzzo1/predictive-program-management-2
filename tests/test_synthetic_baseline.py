"""Tests for the synthetic IMP / IMS layer (data/synthetic/): structure, provenance, rework loop, scenarios, isolation."""

import copy

import pytest

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.synthetic.baseline import FILES, STATEMENT, build_all
from ppm_agent.synthetic.validation import load_dataset, validate_dataset

SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"


@pytest.fixture(scope="module")
def dataset():
    return load_dataset(SYNTHETIC_DIR)


def broken(ds, mutate):
    ds = copy.deepcopy(ds)
    mutate(ds)
    return validate_dataset(ds)


def row(rows, key, value):
    return next(r for r in rows if r[key] == value)


# --- the committed files ---------------------------------------------------------------------------

def test_committed_files_validate(dataset):
    assert validate_dataset(dataset) == []


def test_frozen_counts(dataset):
    assert len(dataset["ims"]) == 35
    assert len(dataset["imp"]) == 8
    assert len(dataset["provenance"]["dsm_nodes"]) == 8
    assert [s["scenario_id"] for s in dataset["scenarios"]["scenarios"]] == [
        "BASELINE", "DISTURBANCE_1", "DISTURBANCE_2", "INTERVENTION_1", "INTERVENTION_2", "INTERVENTION_3"]


def test_files_are_reproducible_from_definitions(tmp_path):
    for key, path in build_all(tmp_path).items():
        assert path.read_bytes() == (SYNTHETIC_DIR / FILES[key]).read_bytes(), f"{FILES[key]} is out of date; rebuild it"


def test_relative_workdays_only_no_calendar_dates(dataset):
    for r in dataset["ims"]:
        for field in ("baseline_start", "baseline_finish", "forecast_start", "forecast_finish"):
            assert r[field].isdigit()


# --- provenance ------------------------------------------------------------------------------------

def test_provenance_classes_are_not_blurred(dataset):
    assert {r["data_classification"] for r in dataset["ims"]} == {"SYNTHETIC"}
    assert {r["data_classification"] for r in dataset["imp"]} == {"SYNTHETIC"}
    assert {d["data_classification"] for d in dataset["dependencies"]} == {"DERIVED", "SYNTHETIC"}
    assert {d["implementation_classification"] for d in dataset["dependencies"]} == {"SYNTHETIC"}
    assert {o["data_classification"] for o in dataset["provenance"]["observed_evidence"]} == {"OBSERVED"}


def test_statement_is_present_in_provenance_and_scenarios(dataset):
    assert dataset["provenance"]["statement"] == STATEMENT
    assert dataset["scenarios"]["statement"] == STATEMENT
    assert "not an actual or reconstructed F-35 contractor schedule" in STATEMENT


def test_benchmark_concepts_are_implemented_by_derived_links(dataset):
    derived = {(d["source_dsm_node"], d["target_dsm_node"], d["source_case"])
               for d in dataset["dependencies"] if d["data_classification"] == "DERIVED"}
    assert ("D4", "D6", "Q01") in derived  # software maturity -> flight-test execution
    assert ("D5", "D6", "Q04") in derived  # test-aircraft availability -> flight-test execution
    assert ("D3", "D8", "Q07") in derived  # weight / redesign -> cost-schedule exposure
    assert ("D7", "D8", "Q08") in derived  # test maturity -> production readiness (A430 -> A510, v1.1)
    assert ("D6", "D8", "Q08") in derived  # late test discovery -> rework exposure (A420 -> A515)
    assert ("D6", "D4", "Q01") in derived  # test-discovered deficiencies -> software correction (A415 -> A225, v1.1)


def test_observed_dependency_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["dependencies"][0].update(data_classification="OBSERVED"))
    assert any("cannot be OBSERVED" in e for e in errors)


def test_invalid_classification_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["ims"][0].update(data_classification="ESTIMATED"))
    assert any("must be SYNTHETIC" in e for e in errors)


def test_derived_dependency_without_source_case_is_rejected(dataset):
    def mutate(ds):
        next(d for d in ds["dependencies"] if d["data_classification"] == "DERIVED").update(source_case="NONE")
    assert any("DERIVED dependency needs a source case" in e for e in broken(dataset, mutate))


def test_altered_statement_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["provenance"].update(statement="A reconstructed F-35 schedule."))
    assert "provenance statement missing or altered" in errors


# --- structural rules ------------------------------------------------------------------------------

def test_duplicate_activity_id_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["ims"][1].update(activity_id="A100"))
    assert any("duplicate activity id 'A100'" in e for e in errors)


def test_unknown_predecessor_is_rejected(dataset):
    errors = broken(dataset, lambda ds: row(ds["ims"], "activity_id", "A105").update(predecessor_ids="A999"))
    assert any("unknown predecessor 'A999'" in e for e in errors)


def test_unknown_imp_and_dsm_ids_are_rejected(dataset):
    def mutate(ds):
        row(ds["ims"], "activity_id", "A110").update(imp_event="IMP-99", dsm_node="D9")
    errors = broken(dataset, mutate)
    assert any("unknown IMP event 'IMP-99'" in e for e in errors)
    assert any("unknown DSM node 'D9'" in e for e in errors)


def test_extra_activity_breaks_the_count(dataset):
    def mutate(ds):
        extra = dict(row(ds["ims"], "activity_id", "A520"), activity_id="A525", predecessor_ids="A520", successor_ids="")
        ds["ims"].append(extra)
    assert any("expected 35 IMS activities, found 36" in e for e in broken(dataset, mutate))


def test_orphan_activity_is_rejected(dataset):
    def mutate(ds):
        row(ds["ims"], "activity_id", "A400").update(predecessor_ids="")
        ds["dependencies"] = [d for d in ds["dependencies"] if d["target_activity"] != "A400"]
        row(ds["ims"], "activity_id", "A115").update(successor_ids="A120;A200")
    assert any("A400: orphan" in e for e in broken(dataset, mutate))


def test_duplicate_dependency_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["dependencies"].append(dict(ds["dependencies"][0], dependency_id="DEP-999")))
    assert any("duplicate dependency" in e for e in errors)


def test_dependency_file_must_match_predecessors(dataset):
    errors = broken(dataset, lambda ds: ds["dependencies"].pop(0))
    assert any("missing from dependencies" in e for e in errors)


def test_schedule_must_match_forward_pass(dataset):
    errors = broken(dataset, lambda ds: row(ds["ims"], "activity_id", "A520").update(baseline_finish="999"))
    assert any("differ from forward pass" in e for e in errors)


# --- rework loop -----------------------------------------------------------------------------------

def test_rework_loop_is_explicit_and_baseline_stays_acyclic(dataset):
    feedback = [d for d in dataset["dependencies"] if d["relationship_type"] == "FEEDBACK_REWORK"]
    assert [(d["source_activity"], d["target_activity"]) for d in feedback] == [("A425", "A410"), ("A415", "A225")]
    assert "A425" not in row(dataset["ims"], "activity_id", "A410")["predecessor_ids"].split(";")
    assert "A415" not in row(dataset["ims"], "activity_id", "A225")["predecessor_ids"].split(";")
    loop = {r["activity_id"] for r in dataset["ims"] if r["rework_indicator"] == "LOOP"}
    assert loop == {"A410", "A415", "A420", "A425"}


def test_feedback_as_scheduling_predecessor_creates_cycle(dataset):
    def mutate(ds):
        row(ds["ims"], "activity_id", "A410").update(predecessor_ids="A405;A425")
        fb = next(d for d in ds["dependencies"] if d["relationship_type"] == "FEEDBACK_REWORK")
        fb["relationship_type"] = "FINISH_TO_START"
    errors = broken(dataset, mutate)
    assert any("not acyclic" in e for e in errors)
    assert any("must not be a scheduling predecessor" in e for e in errors)


def test_missing_feedback_edge_is_rejected(dataset):
    def mutate(ds):
        ds["dependencies"] = [d for d in ds["dependencies"] if d["relationship_type"] != "FEEDBACK_REWORK"]
    assert any("expected exactly the FEEDBACK_REWORK dependencies" in e for e in broken(dataset, mutate))


# --- v1.1 structural revision ----------------------------------------------------------------------

def test_v1_0_archive_is_preserved_unchanged():
    import hashlib

    from ppm_agent.synthetic.baseline import VERSION_HISTORY
    v10 = VERSION_HISTORY[0]
    assert v10["version"] == "1.0"
    for name, digest in v10["file_sha256"].items():
        path = PROJECT_ROOT / v10["archive"] / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name


def test_v1_1_is_recorded_and_schedule_calibration_unchanged(dataset):
    prov = dataset["provenance"]
    assert prov["version"] == "1.1" and prov["freeze"]["version"] == "1.1"
    assert [v["version"] for v in prov["version_history"]] == ["1.0", "1.1"]
    assert prov["freeze"]["preserved"]["dependencies"] == 43
    archived = {r["activity_id"]: r for r in load_dataset(PROJECT_ROOT / "data/synthetic/archive/v1.0")["ims"]}
    for r in dataset["ims"]:
        for field in ("baseline_duration_days", "predecessor_ids", "baseline_start", "baseline_finish", "baseline_total_float"):
            assert r[field] == archived[r["activity_id"]][field]


def test_software_rework_feedback_is_feedback_only(dataset):
    (dep,) = [d for d in dataset["dependencies"] if (d["source_activity"], d["target_activity"]) == ("A415", "A225")]
    assert dep["relationship_type"] == "FEEDBACK_REWORK"
    assert (dep["source_dsm_node"], dep["target_dsm_node"]) == ("D6", "D4")
    assert (dep["data_classification"], dep["implementation_classification"]) == ("DERIVED", "SYNTHETIC")


def test_software_feedback_as_scheduling_predecessor_is_rejected(dataset):
    def mutate(ds):
        row(ds["ims"], "activity_id", "A225").update(predecessor_ids="A220;A415")
        fb = next(d for d in ds["dependencies"] if d["source_activity"] == "A415" and d["target_activity"] == "A225")
        fb["relationship_type"] = "FINISH_TO_START"
    errors = broken(dataset, mutate)
    assert any("not acyclic" in e for e in errors)
    assert any("('A415', 'A225') must not be a scheduling predecessor" in e for e in errors)


def test_a510_must_stay_in_d8(dataset):
    errors = broken(dataset, lambda ds: row(ds["ims"], "activity_id", "A510").update(dsm_node="D7"))
    assert any("A510: must map to DSM node D8" in e for e in errors)


# --- scenarios -------------------------------------------------------------------------------------

def test_disturbance_and_intervention_magnitudes(dataset):
    s = {x["scenario_id"]: x for x in dataset["scenarios"]["scenarios"]}
    assert s["DISTURBANCE_1"]["changes"][0] == {"change_type": "DURATION_DELTA", "activity_id": "A210",
                                                "delta_workdays": 8, "data_classification": "SYNTHETIC"}
    assert s["DISTURBANCE_2"]["changes"][0]["activity_id"] == "A305"
    assert s["DISTURBANCE_2"]["changes"][0]["delta_workdays"] == 4
    assert s["INTERVENTION_1"]["base_scenario"] == "DISTURBANCE_1"
    assert s["INTERVENTION_1"]["changes"][0]["delta_workdays"] == -4
    assert all(x["outcome"] == "NOT_COMPUTED" and x["data_classification"] == "SYNTHETIC" for x in s.values())


def test_scenario_changed_magnitude_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["scenarios"]["scenarios"][1]["changes"][0].update(delta_workdays=10))
    assert any("expected the frozen change A210 +8" in e for e in errors)


def test_scenario_unknown_activity_is_rejected(dataset):
    errors = broken(dataset, lambda ds: ds["scenarios"]["scenarios"][2]["changes"][0].update(activity_id="A999"))
    assert any("invalid DURATION_DELTA" in e for e in errors)


def test_scenario_may_not_edit_the_precedence_network(dataset):
    def mutate(ds):
        ds["scenarios"]["scenarios"][5]["changes"] = [{
            "change_type": "ADD_DEPENDENCY", "source_activity": "A430", "target_activity": "A505",
            "lag_workdays": 0, "data_classification": "SYNTHETIC"}]
    assert any("may not edit the precedence network" in e for e in broken(dataset, mutate))


def test_resequencing_policy_respects_the_readiness_gate(dataset):
    s = {x["scenario_id"]: x for x in dataset["scenarios"]["scenarios"]}["INTERVENTION_2"]
    assert s["base_scenario"] == "DISTURBANCE_1"
    assert s["changes"] == [{**s["changes"][0], "change_type": "POLICY", "policy": "FLIGHT_TEST_RESEQUENCING_AFTER_READINESS",
                             "readiness_gate_activity": "A405", "applies_to_activity": "A410",
                             "delay_absorption_days": 4, "data_classification": "SYNTHETIC"}]
    assert set(row(dataset["ims"], "activity_id", "A405")["predecessor_ids"].split(";")) == {"A400", "A230", "A325"}


def test_staged_commitment_policy_keeps_concurrency(dataset):
    s = {x["scenario_id"]: x for x in dataset["scenarios"]["scenarios"]}["INTERVENTION_3"]
    (policy,) = s["changes"]
    assert policy["policy"] == "STAGED_PRODUCTION_COMMITMENT" and policy["data_classification"] == "SYNTHETIC"
    assert (policy["pre_maturity_commitment_fraction"], policy["post_maturity_commitment_fraction"]) == (0.40, 0.60)
    assert row(dataset["ims"], "activity_id", "A505")["predecessor_ids"] == "A500"  # not gated on A430


def test_changed_policy_values_are_rejected(dataset):
    def mutate(ds):
        ds["scenarios"]["scenarios"][4]["changes"][0]["delay_absorption_days"] = 6
        ds["scenarios"]["scenarios"][5]["changes"][0].update(pre_maturity_commitment_fraction=0.5)
    errors = broken(dataset, mutate)
    assert any(e.startswith("INTERVENTION_2: expected the frozen policy") for e in errors)
    assert any("must sum to 1" in e for e in errors)


def test_bypassing_the_readiness_gate_is_rejected(dataset):
    def mutate(ds):
        row(ds["ims"], "activity_id", "A405").update(predecessor_ids="A400;A230")
        ds["dependencies"] = [d for d in ds["dependencies"] if (d["source_activity"], d["target_activity"]) != ("A325", "A405")]
    assert any("readiness gate must keep predecessors" in e for e in broken(dataset, mutate))


def test_gating_production_on_maturity_in_the_baseline_is_rejected(dataset):
    def mutate(ds):
        row(ds["ims"], "activity_id", "A505").update(predecessor_ids="A500;A430")
    assert any("concurrency is intentional" in e for e in broken(dataset, mutate))


# --- synthetic float calibration -------------------------------------------------------------------

def test_software_path_is_near_critical_and_test_aircraft_path_controls_a405(dataset):
    floats = {r["activity_id"]: int(r["baseline_total_float"]) for r in dataset["ims"]}
    assert floats["A230"] == 4 and floats["A210"] == 4
    assert floats["A325"] == 0 and floats["A405"] == 0
    assert max(int(r["baseline_finish"]) for r in dataset["ims"]) == 355


def test_float_must_match_backward_pass(dataset):
    errors = broken(dataset, lambda ds: row(ds["ims"], "activity_id", "A230").update(baseline_total_float="30"))
    assert any("baseline_total_float differs from backward pass" in e for e in errors)


def test_reverting_the_float_calibration_is_rejected(dataset):
    errors = broken(dataset, lambda ds: row(ds["ims"], "activity_id", "A205").update(baseline_duration_days="40"))
    assert any("A230: total float must be 4" in e for e in errors)


# --- isolation from the RAG corpus -----------------------------------------------------------------

def test_synthetic_files_are_kept_out_of_the_documentary_corpus():
    raw_jsf = PROJECT_ROOT / "data" / "raw" / "jsf"
    assert not any("synthetic" in p.name.lower() for p in raw_jsf.rglob("*"))
    for manifest in ("prototype_corpus.json", "expanded_corpus_v2.json"):
        text = (PROJECT_ROOT / "data" / "metadata" / manifest).read_text(encoding="utf-8")
        assert "synthetic" not in text.lower()
