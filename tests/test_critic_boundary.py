"""Responsibility boundary between deterministic Python validation (owns hard constraints) and the LLM
critic (owns qualitative evaluation). No live API calls: the critic runs against a fake Responses client."""

import json

from ppm_agent.agents.critic import Critic
from ppm_agent.agents.episode import render_markdown, save_trace
from ppm_agent.agents.generator import ThoughtGenerator
from ppm_agent.agents.graph import run_graph
from ppm_agent.agents.tot import ToTConfig, ToTController
from ppm_agent.models import CriticAssessment, CriticOutput
from test_agentic import ScriptedGenerator, hyp, state_with_evidence
from test_llm_provider import critic_out, real_client, response

FALSE_CLAIM = "The hypothesis cites no evidence, or cites IDs that are not in the retrieved evidence."
META = {"retrieval_strategy": "HYBRID_RERANKED_V2_1", "top_k": 3, "tot_config": ToTConfig().__dict__, "orchestration": "python",
        "elapsed_seconds": 0.1}


def run_real(root, *critic_outputs):
    """ToT over scripted root hypotheses, judged by the real critic code path with scripted model outputs."""
    rs, chunk_ids = state_with_evidence()
    client, fake = real_client(*[response(o) for o in critic_outputs])
    decision = ToTController(ScriptedGenerator(root), Critic(client)).run(rs, chunk_ids)
    return rs, decision, fake


def reasons(rs, hid):
    return [p["reason"] for p in rs.pruning_log if p["hypothesis_id"] == hid]


# 1
def test_python_valid_evidence_is_not_rejected_on_a_false_critic_claim():
    rs, d, _ = run_real([hyp("a", cites=("E1",))], critic_out(95, claimed=True, reasons=[FALSE_CLAIM]))  # total 86.0
    a = rs.assessments["D1.a"]
    assert a.hard_constraint_pass and a.deterministic_validation_result == "PASS"
    assert a.critic_claimed_hard_failure and a.critic_validation_disagreement
    assert "PASSED" in a.disagreement_reason and "'E1'" in a.disagreement_reason
    assert not any(r.startswith("HARD CONSTRAINT") for r in reasons(rs, "D1.a"))
    assert d.selected_hypothesis_id == "D1.a" and d.decision == "SUPPORTED"


# 2
def test_weak_evidence_lowers_scores_but_is_not_a_hard_failure():
    weak = critic_out(60, doc=30, model=90, strength="E1 is valid evidence but only partially supports the relationship")
    rs, d, _ = run_real([hyp("a")], weak)
    a = rs.assessments["D1.a"]
    assert a.hard_constraint_pass and a.hard_constraint_failures == [] and not a.critic_validation_disagreement
    assert a.documentary_evidence_score == 30 and "partially" in a.evidence_strength_summary
    assert a.model_consistency_score == 50  # pinned neutral in Python while no DSM exists; the deviation is logged
    assert any("pinned to 50" in e for e in rs.events)
    assert any(r.startswith("BELOW THRESHOLD") for r in reasons(rs, "D1.a"))
    assert not any(r.startswith("HARD CONSTRAINT") for r in reasons(rs, "D1.a"))


# 3
def test_genuinely_missing_evidence_id_is_rejected_deterministically():
    rs, d, fake = run_real([hyp("a", cites=("E9",))])  # no scripted critic output: calling the critic would fail the test
    assert fake.requests == [] and rs.model_calls == 1
    assert any("VALIDATION" in r and "'E9' does not exist" in r for r in reasons(rs, "D1.a"))
    assert d.decision == "UNRESOLVED"
    # assessed directly, Python's FAIL stands even when the critic misses it, and the miss is recorded
    rs, _ = state_with_evidence()
    client, _ = real_client(response(critic_out(95)))
    a = Critic(client).assess(hyp("H", cites=("E9",)), rs)
    assert not a.hard_constraint_pass and a.deterministic_validation_result == "FAIL"
    assert a.critic_validation_disagreement and "Python deterministic validation FAILED" in a.disagreement_reason


# 4
def test_invalid_activity_is_rejected_deterministically():
    wrong_target = hyp("a").model_copy(update={"target_activity": "A9"})
    rs, d, fake = run_real([wrong_target])
    assert fake.requests == []
    assert any("VALIDATION" in r and "target activity 'A9' does not exist" in r for r in reasons(rs, "D1.a"))
    assert d.decision == "UNRESOLVED"


# 5
def test_disagreement_is_recorded_in_the_trace(tmp_path):
    rs, _, _ = run_real([hyp("a")], critic_out(85, claimed=True, reasons=[FALSE_CLAIM]))
    paths = save_trace(rs, META, tmp_path)
    state = json.loads(open(paths["trace_json"], encoding="utf-8").read())["state"]
    a = state["assessments"]["D1.a"]
    assert (a["deterministic_validation_result"], a["critic_claimed_hard_failure"], a["critic_validation_disagreement"]) == ("PASS", True, True)
    assert a["disagreement_reason"] and a["critic_claimed_hard_failure_reasons"] == [FALSE_CLAIM]
    assert state["critic_disagreements"][0]["hypothesis_id"] == "D1.a"
    md = open(paths["trace_md"], encoding="utf-8").read()
    assert "## Critic / Python validation disagreements" in md and "DISAGREEMENT" in md and "None recorded." not in md


# 6
def test_disagreement_survives_pruning_and_both_orchestrations():
    low = critic_out(40, claimed=True, reasons=[FALSE_CLAIM])
    rs, d, _ = run_real([hyp("a")], low)  # pruned below threshold; the disagreement must still be visible
    assert any(r.startswith("BELOW THRESHOLD") for r in reasons(rs, "D1.a")) and d.decision == "UNRESOLVED"
    assert [x["hypothesis_id"] for x in rs.critic_disagreements] == ["D1.a"]
    assert any("disagreement on D1.a" in e for e in rs.events)
    assert "DISAGREEMENT" in render_markdown(rs, META)

    rs2, chunk_ids = state_with_evidence()
    client, _ = real_client(response(low))
    rs2, _ = run_graph(ToTController(ScriptedGenerator([hyp("a")]), Critic(client)), rs2, chunk_ids)
    assert rs2.critic_disagreements == rs.critic_disagreements


# 7
def test_mock_agent_mode_still_works_and_records_python_validation():
    rs, chunk_ids = state_with_evidence()
    d = ToTController(ThoughtGenerator(None), Critic(None)).run(rs, chunk_ids)
    assert rs.agent_mode == "MOCK_AGENT_MODE" and d.decision in {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "UNRESOLVED"}
    assert rs.assessments and all(a.deterministic_validation_result == "PASS" for a in rs.assessments.values())
    assert rs.critic_disagreements == []
    md = render_markdown(rs, META)
    assert "No LLM was called" in md and "None recorded." in md


# 8
def test_real_critic_schema_cannot_set_deterministic_fields_and_is_strict_valid():
    for field in ("hard_constraint_pass", "hard_constraint_failures", "overall_score", "deterministic_validation_result",
                  "critic_validation_disagreement", "disagreement_reason", "hypothesis_id"):
        assert field not in CriticOutput.model_fields
    assert set(CriticOutput.model_fields) <= set(CriticAssessment.model_fields)
    from openai.lib._pydantic import to_strict_json_schema  # the conversion responses.parse applies

    schema = to_strict_json_schema(CriticOutput)
    assert schema["additionalProperties"] is False and sorted(schema["required"]) == sorted(schema["properties"])
