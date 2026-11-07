"""Critic calibration (evidence-support label, scoring anchors) and the comparative review of survivors.
No live API calls: the critic runs against a fake Responses client with scripted outputs."""

import json

import pytest
from openai.lib._pydantic import to_strict_json_schema
from pydantic import ValidationError

from ppm_agent.agents.critic import COMPARATIVE_PROMPT, PROMPT, Critic
from ppm_agent.agents.episode import save_trace
from ppm_agent.agents.generator import ThoughtGenerator
from ppm_agent.agents.tot import ToTConfig, ToTController
from ppm_agent.models import ComparativeReviewOutput, CriticAssessment, CriticOutput
from test_agentic import ScriptedGenerator, hyp, state_with_evidence
from test_llm_provider import critic_out, real_client, response

META = {"retrieval_strategy": "HYBRID_RERANKED_V2_1", "top_k": 3, "tot_config": ToTConfig().__dict__, "orchestration": "python",
        "elapsed_seconds": 0.1}
# a (DIRECT) and b (INDIRECT) survive in a near tie (82.0 vs 80.4); c (NONE) is pruned below threshold (42.0)
ROOT = [hyp("a", cites=("E1",)), hyp("b", "INDIRECT", cites=("E2",), intermediate_activity="integration"), hyp("c", "NONE", cites=("E3",))]
SCORES = (critic_out(90, label="DIRECTLY_STATED"), critic_out(88, label="INFERRED"), critic_out(40, label="WEAKLY_SUPPORTED"))


def compare_out(preferred="D1.a", near_tie=False):
    return ComparativeReviewOutput(preferred_hypothesis_id=preferred, near_tie=near_tie, assumption_comparison="DIRECT needs fewer steps",
                                   uncertainty_assessment="low", comparative_reasoning_summary="E1 states the effect directly")


def controller(client, root=ROOT, **cfg):
    return ToTController(ScriptedGenerator(root), Critic(client), ToTConfig(**cfg))


def search(ctl, rs, chunk_ids):
    """The run() loop without the final decide(), so the state can be inspected just before the review."""
    while True:
        ctl.generate(rs, chunk_ids), ctl.validate(rs, chunk_ids), ctl.evaluate(rs), ctl.prune(rs)
        if not ctl.should_continue(rs):
            return


def run(*outputs, root=ROOT, **cfg):
    rs, chunk_ids = state_with_evidence()
    client, fake = real_client(*[response(o) for o in outputs])
    d = controller(client, root, **cfg).run(rs, chunk_ids)
    return rs, d, fake


# --- calibration --------------------------------------------------------------------------------


def test_scoring_anchor_schema_is_strict_compatible_and_prompts_are_generic():
    label = to_strict_json_schema(CriticOutput)["properties"]["evidence_support_label"]
    assert set(label["enum"]) == {"DIRECTLY_STATED", "STRONGLY_SUPPORTED", "INFERRED", "WEAKLY_SUPPORTED", "UNSUPPORTED"}
    assert set(CriticOutput.model_fields) <= set(CriticAssessment.model_fields)
    review = to_strict_json_schema(ComparativeReviewOutput)
    assert review["additionalProperties"] is False and sorted(review["required"]) == sorted(review["properties"])
    for band in ("90-100", "75-89", "60-74", "40-59", "0-39"):
        assert band in PROMPT
    for prompt in (PROMPT, COMPARATIVE_PROMPT):  # not tied to any evaluation question
        assert not any(word in prompt for word in ("Q01", "F-35", "flight", "mission-system"))


def test_direct_statement_label_is_carried_into_the_assessment_and_trace(tmp_path):
    rs, _, _ = run(critic_out(95, label="DIRECTLY_STATED"), root=[hyp("a")])
    assert rs.assessments["D1.a"].evidence_support_label == "DIRECTLY_STATED"
    paths = save_trace(rs, META, tmp_path)
    assert json.loads(open(paths["trace_json"], encoding="utf-8").read())["state"]["assessments"]["D1.a"]["evidence_support_label"] == "DIRECTLY_STATED"
    assert "[DIRECTLY_STATED]" in open(paths["trace_md"], encoding="utf-8").read()
    with pytest.raises(ValidationError):
        critic_out(label="PROBABLE")


# --- comparative review ------------------------------------------------------------------------


def test_comparative_review_only_receives_surviving_hypotheses(tmp_path):
    rs, d, fake = run(*SCORES, compare_out("D1.a", near_tie=True))
    prompt = fake.requests[-1]["input"]
    assert fake.requests[-1]["text_format"] is ComparativeReviewOutput
    assert "[D1.a]" in prompt and "[D1.b]" in prompt and "D1.c" not in prompt
    r = rs.comparative_review
    assert r.status == "COMPLETED" and r.reviewed_hypothesis_ids == ["D1.a", "D1.b"]
    assert (r.preferred_hypothesis_id, r.near_tie, r.deterministic_near_tie, r.agrees_with_score_ranking) == ("D1.a", True, True, True)
    assert rs.comparative_model_call_count == 1 and "Comparative review (advisory)" in d.decision_summary
    state = json.loads(open(save_trace(rs, META, tmp_path)["trace_json"], encoding="utf-8").read())["state"]
    assert state["comparative_model_call_count"] == 1
    assert {"preferred_hypothesis_id", "comparative_reasoning_summary", "near_tie"} <= set(state["comparative_review"])


def test_comparative_review_cannot_revive_a_pruned_hypothesis():
    rs, d, _ = run(*SCORES, compare_out("D1.c"))
    r = rs.comparative_review
    assert r.preferred_hypothesis_id is None and any("not a surviving hypothesis" in n for n in r.validation_notes)
    assert "D1.c" in {h.hypothesis_id for h in rs.rejected_hypotheses}
    assert "D1.c" not in {h.hypothesis_id for h in rs.active_hypotheses}
    assert d.selected_hypothesis_id == "D1.a"  # decision still from the deterministic rule over survivors


def test_comparative_review_preserves_individual_scores_and_the_verdict_rule():
    rs, chunk_ids = state_with_evidence()
    client, _ = real_client(*[response(o) for o in SCORES], response(compare_out("D1.b")))  # prefers the runner-up
    ctl = controller(client)
    search(ctl, rs, chunk_ids)
    before = {k: v.model_copy(deep=True) for k, v in rs.assessments.items()}
    d = ctl.decide(rs)
    assert rs.assessments == before
    assert rs.comparative_review.agrees_with_score_ranking is False
    assert d.selected_hypothesis_id == "D1.a" and d.decision == "PARTIALLY_SUPPORTED"  # advisory only

    class TamperingCritic(Critic):  # a review that tries to rescore is undone
        def compare(self, survivors, state, margin):
            state.assessments["D1.b"] = state.assessments["D1.b"].model_copy(update={"overall_score": 99.0})
            return compare_out("D1.b")

    rs, chunk_ids = state_with_evidence()
    client, _ = real_client(*[response(o) for o in SCORES])
    ctl = ToTController(ScriptedGenerator(ROOT), TamperingCritic(client))
    search(ctl, rs, chunk_ids)
    before = {k: v.model_copy(deep=True) for k, v in rs.assessments.items()}
    ctl.decide(rs)
    assert rs.assessments == before and any("restored" in n for n in rs.comparative_review.validation_notes)


def test_no_survivors_is_unresolved_without_a_comparative_call():
    rs, d, fake = run(critic_out(40), critic_out(30), critic_out(20))
    assert d.decision == "UNRESOLVED" and rs.status == "NO_VIABLE_CANDIDATE"
    assert rs.comparative_review.status == "NO_SURVIVORS" and rs.comparative_model_call_count == 0
    assert len(fake.requests) == 3 and rs.model_calls == 4  # 1 generator + 3 critic


def test_model_call_budget_is_enforced_including_the_review():
    rs, _, fake = run(*SCORES[:2], root=ROOT[:2], max_model_calls=3)  # 1 generator + 2 critic = budget
    assert rs.model_calls == 3 and rs.status == "BUDGET_EXHAUSTED"
    assert rs.comparative_review.status == "SKIPPED_BUDGET" and rs.comparative_model_call_count == 0 and len(fake.requests) == 2


def test_mock_mode_runs_a_labelled_rule_based_review():
    rs, chunk_ids = state_with_evidence()
    ToTController(ThoughtGenerator(None), Critic(None)).run(rs, chunk_ids)
    r = rs.comparative_review
    assert rs.agent_mode == "MOCK_AGENT_MODE" and r.mode == "MOCK_AGENT_MODE"
    if r.status == "COMPLETED":
        assert r.comparative_reasoning_summary.startswith("[MOCK") and r.agrees_with_score_ranking
