"""Tests for the agentic dependency-reasoning layer (models, validation, critic scoring, bounded ToT, traces)."""

import json

import pytest
from pydantic import ValidationError

from ppm_agent.agents.critic import Critic, make_assessment
from ppm_agent.agents.episode import attach_evidence, new_state, render_markdown, save_trace
from ppm_agent.agents.evidence import results_to_evidence
from ppm_agent.agents.generator import ThoughtGenerator
from ppm_agent.agents.graph import run_graph
from ppm_agent.agents.scoring import WEIGHTS, weighted_score
from ppm_agent.agents.tot import ToTConfig, ToTController
from ppm_agent.agents.validation import parse_hypothesis, validate_assessment, validate_hypothesis
from ppm_agent.models import Activity, CriticAssessment, DependencyDecision, DependencyHypothesis, Evidence

SRC = Activity(activity_id="A1", name="Mission-System Software Maturity", description="Maturity of mission-system software.", activity_type="software")
TGT = Activity(activity_id="A2", name="Flight-Test Execution", description="Execution of flight testing.", activity_type="test")
TEXTS = [
    "Delays in mission systems software delivery affected flight test progress and test points flown.",
    "Software integration in the laboratory continued before release of each mission system software increment to flight test.",
    "The engine contractor reported part shortages and late deliveries of components.",
]


def result(i, text):
    return {"rank": i, "chunk_id": f"DOC{i}-p00{i}-c00", "text": text, "document_id": f"DOC{i}", "organization": "GAO",
            "pdf_page": i, "printed_page": None, "section_type": None, "metadata": {"publication_date": "2010-03-19"},
            "strategy_score": 1.0 / i}


def state_with_evidence(texts=TEXTS):
    rs = new_state("q?", SRC, TGT, None)
    results = [result(i, t) for i, t in enumerate(texts, start=1)]
    attach_evidence(rs, results_to_evidence(results, "hybrid_reranked"), [r["chunk_id"] for r in results])
    return rs, [r["chunk_id"] for r in results]


def hyp(hid, rtype="DIRECT", cites=("E1",), **kw):
    return DependencyHypothesis(hypothesis_id=hid, source_activity="A1", target_activity="A2", relationship_type=rtype,
                                reasoning_summary="r", supporting_evidence_ids=list(cites), **kw)


class ScriptedGenerator:
    """Root -> the given hypotheses; each later expansion -> `refinements` fresh successors (or none)."""

    mode = "TEST"

    def __init__(self, root, refinements=0):
        self.root, self.refinements, self.calls = root, refinements, 0

    def propose(self, state, parent=None, max_hypotheses=3):
        self.calls += 1
        if parent is None:
            return [h.model_copy(update={"hypothesis_id": f"D1.{h.hypothesis_id}"}) for h in self.root[:max_hypotheses]], []
        # each refinement names a distinct mediator, so it is a new claim (not a duplicate of its parent)
        return [parent.model_copy(update={"hypothesis_id": f"D{state.depth}.{parent.hypothesis_id}.{k}", "parent_id": parent.hypothesis_id,
                                          "depth": parent.depth + 1, "assumptions": [f"refinement {k}"],
                                          "intermediate_activity": f"mediator {parent.hypothesis_id}.{k}"})
                for k in range(1, self.refinements + 1)][:max_hypotheses], []


class ScriptedCritic:
    """Score by the root hypothesis label (the part after 'D1.'), optionally a hard failure."""

    mode = "TEST"

    def __init__(self, scores, hard_fail=()):
        self.scores, self.hard_fail = scores, set(hard_fail)

    def assess(self, h, state):
        label = h.hypothesis_id.split("D1.", 1)[1].split(".")[0]  # root label, also for refinements "D2.D1.a.1"
        s = self.scores[label] + 0.5 * (h.depth - 1) * (1 if h.hypothesis_id.endswith(".1") else -1)
        failures = ["evidence contradicts relationship"] if label in self.hard_fail else []
        return make_assessment(h.hypothesis_id, s, s, s, s, not failures, failures, "scripted")


def controller(gen, critic, **cfg):
    return ToTController(gen, critic, ToTConfig(**cfg))


# --- models --------------------------------------------------------------------------------


def test_evidence_model_requires_provenance():
    with pytest.raises(ValidationError):
        Evidence(evidence_id="E1", source_document="DOC", pdf_page=0, chunk_id="c", text="t", retrieval_method="X", retrieval_rank=1)
    with pytest.raises(ValidationError):
        Evidence(evidence_id="E1", source_document="DOC", pdf_page=3, chunk_id="", text="t", retrieval_method="X", retrieval_rank=1)


def test_invalid_relationship_type_is_rejected():
    with pytest.raises(ValidationError):
        hyp("H", rtype="CAUSAL")
    h, errors = parse_hypothesis({"hypothesis_id": "H", "source_activity": "A1", "target_activity": "A2", "relationship_type": "CAUSAL",
                                  "reasoning_summary": "r", "supporting_evidence_ids": ["E1"]})
    assert h is None and "invalid relationship_type" in errors[0]


def test_critic_scores_are_bounded_and_total_is_weighted():
    with pytest.raises(ValidationError):
        CriticAssessment(hypothesis_id="H", documentary_evidence_score=120, engineering_consistency_score=1, model_consistency_score=1,
                         predictive_usefulness_score=1, hard_constraint_pass=True, critic_summary="s", overall_score=1)
    a = make_assessment("H", 120, -5, 50, 80, True, [], "s")  # out-of-range model output is clamped, never trusted
    assert (a.documentary_evidence_score, a.engineering_consistency_score) == (100, 0)
    assert a.overall_score == weighted_score(100, 0, 50, 80) == pytest.approx(0.3 * 100 + 0.2 * 50 + 0.2 * 80)
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)
    tampered = a.model_copy(update={"overall_score": 99.0})
    assert any("does not equal" in e for e in validate_assessment(tampered, {"H"}))


def test_decision_schema_only_allows_the_four_verdicts():
    DependencyDecision(source_activity="A1", target_activity="A2", decision="PARTIALLY_SUPPORTED", decision_summary="s")
    with pytest.raises(ValidationError):
        DependencyDecision(source_activity="A1", target_activity="A2", decision="LIKELY", decision_summary="s")
    with pytest.raises(ValidationError):
        DependencyDecision(source_activity="A1", target_activity="A2", decision="SUPPORTED", critic_score=101, decision_summary="s")


# --- deterministic validation -------------------------------------------------------------


def test_validation_rejects_missing_unknown_and_untraceable_citations():
    rs, chunk_ids = state_with_evidence()
    assert validate_hypothesis(hyp("H1"), rs, chunk_ids) == []
    assert "no supporting evidence cited" in validate_hypothesis(hyp("H2", cites=()), rs, chunk_ids)
    assert any("'E9' does not exist" in e for e in validate_hypothesis(hyp("H3", cites=("E9",)), rs, chunk_ids))
    assert any("not returned by retrieval" in e for e in validate_hypothesis(hyp("H4"), rs, chunk_ids[1:]))


def test_validation_rejects_wrong_activities_and_unnamed_mediator():
    rs, chunk_ids = state_with_evidence()
    wrong = hyp("H1").model_copy(update={"target_activity": "A9"})
    assert any("target activity 'A9' does not exist" in e for e in validate_hypothesis(wrong, rs, chunk_ids))
    assert any("intermediate activity" in e for e in validate_hypothesis(hyp("H2", rtype="INDIRECT"), rs, chunk_ids))


# --- bounded ToT ----------------------------------------------------------------------------


def run(gen, critic, **cfg):
    rs, chunk_ids = state_with_evidence()
    decision = controller(gen, critic, **cfg).run(rs, chunk_ids)
    return rs, decision


def test_hard_constraint_failure_rejects_regardless_of_score():
    rs, d = run(ScriptedGenerator([hyp("a"), hyp("b", "NONE")]), ScriptedCritic({"a": 75, "b": 95}, hard_fail={"b"}))
    assert any(p["hypothesis_id"] == "D1.b" and p["reason"].startswith("HARD CONSTRAINT") for p in rs.pruning_log)
    assert d.selected_hypothesis_id == "D1.a"


def test_threshold_pruning_and_no_viable_candidate():
    rs, d = run(ScriptedGenerator([hyp("a"), hyp("b", "INDIRECT", intermediate_activity="integration")]), ScriptedCritic({"a": 69.9, "b": 50}))
    assert {p["hypothesis_id"] for p in rs.pruning_log if "BELOW THRESHOLD" in p["reason"]} == {"D1.a", "D1.b"}
    assert rs.status == "NO_VIABLE_CANDIDATE" and d.decision == "UNRESOLVED"


def test_dominant_candidate_stops_at_depth_one():
    rs, d = run(ScriptedGenerator([hyp("a"), hyp("b", "INDIRECT", intermediate_activity="integration")], refinements=3),
                ScriptedCritic({"a": 90, "b": 72}))
    assert rs.status == "DOMINANT_CANDIDATE" and rs.depth == 1 and rs.model_calls == 3
    assert d.decision == "SUPPORTED" and d.selected_relationship_type == "DIRECT"


def test_beam_width_keeps_only_the_best_three():
    root = [hyp("a"), hyp("b", cites=("E2",)), hyp("c", cites=("E1", "E2"))]
    rs, _ = run(ScriptedGenerator(root, refinements=3), ScriptedCritic({"a": 80, "b": 79, "c": 78}), max_depth=2)
    assert len(rs.active_hypotheses) <= 3
    assert any("OUTSIDE BEAM" in p["reason"] for p in rs.pruning_log)


def test_depth_limit_and_successor_limit():
    rs, _ = run(ScriptedGenerator([hyp("a"), hyp("b", cites=("E2",))], refinements=5), ScriptedCritic({"a": 80, "b": 79}), max_depth=2)
    assert rs.depth == 2 and rs.status in {"DEPTH_LIMIT", "DOMINANT_CANDIDATE", "NO_NEW_CANDIDATES"}
    per_parent = {}
    for h in rs.all_hypotheses:
        per_parent[h.parent_id] = per_parent.get(h.parent_id, 0) + 1
    assert max(per_parent.values()) <= 3


def test_model_call_budget_is_never_exceeded():
    root = [hyp("a"), hyp("b", cites=("E2",)), hyp("c", cites=("E1", "E2"))]
    rs, _ = run(ScriptedGenerator(root, refinements=3), ScriptedCritic({"a": 80, "b": 79, "c": 78}), max_model_calls=6)
    assert rs.model_calls <= 6
    assert rs.status == "BUDGET_EXHAUSTED" or any(p["action"] == "NOT_EVALUATED" for p in rs.pruning_log)


def test_near_tie_between_dependency_types_is_partially_supported():
    rs, d = run(ScriptedGenerator([hyp("a"), hyp("b", "INDIRECT", intermediate_activity="integration")]), ScriptedCritic({"a": 82, "b": 79}))
    assert d.decision == "PARTIALLY_SUPPORTED" and "near tie" in d.decision_summary


def test_near_tie_with_no_dependency_is_unresolved():
    rs, d = run(ScriptedGenerator([hyp("a"), hyp("b", "NONE", cites=("E3",))]), ScriptedCritic({"a": 82, "b": 80}))
    assert d.decision == "UNRESOLVED"


def test_dominant_none_is_not_supported():
    rs, d = run(ScriptedGenerator([hyp("a"), hyp("b", "NONE", cites=("E3",))]), ScriptedCritic({"a": 71, "b": 85}))
    assert d.decision == "NOT_SUPPORTED" and d.selected_relationship_type == "NONE"


def test_duplicate_refinements_are_rejected_and_search_converges():
    rs, _ = run(ScriptedGenerator([hyp("a"), hyp("b", cites=("E2",))], refinements=0), ScriptedCritic({"a": 80, "b": 79}))
    assert rs.status == "NO_NEW_CANDIDATES" and rs.depth == 2


# --- mock components and orchestration -------------------------------------------------------


def test_mock_pipeline_runs_end_to_end_without_an_llm():
    rs, chunk_ids = state_with_evidence()
    d = controller(ThoughtGenerator(None), Critic(None)).run(rs, chunk_ids)
    assert rs.agent_mode == "MOCK_AGENT_MODE" and ThoughtGenerator(None).mode == "MOCK_AGENT_MODE"
    assert all(h.reasoning_summary.startswith("[MOCK]") for h in rs.all_hypotheses)
    assert all(a.critic_summary.startswith("[MOCK critic") for a in rs.assessments.values())
    assert d.decision in {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "UNRESOLVED"}
    assert set(d.supporting_evidence_ids) <= {"E1", "E2", "E3"}


def test_mock_critic_rejects_none_when_a_passage_states_the_dependency():
    rs, chunk_ids = state_with_evidence()
    a = Critic(None).assess(hyp("H", "NONE", cites=("E3",)), rs)
    assert not a.hard_constraint_pass
    assert any("contradicting NONE" in f for f in a.hard_constraint_failures)  # E1 states the dependency
    assert any("not traceable" in f for f in a.hard_constraint_failures)       # E3 mentions neither activity


def test_langgraph_and_python_orchestration_agree():
    rs1, chunk_ids = state_with_evidence()
    d1 = controller(ThoughtGenerator(None), Critic(None)).run(rs1, chunk_ids)
    rs2, _ = state_with_evidence()
    rs2, _ = run_graph(controller(ThoughtGenerator(None), Critic(None)), rs2, chunk_ids)
    assert rs2.decision.model_dump() == d1.model_dump()
    assert (rs2.model_calls, rs2.depth, rs2.status) == (rs1.model_calls, rs1.depth, rs1.status)


def test_trace_files_are_written_and_labelled(tmp_path):
    rs, chunk_ids = state_with_evidence()
    controller(ThoughtGenerator(None), Critic(None)).run(rs, chunk_ids)
    meta = {"retrieval_strategy": "HYBRID_RERANKED_V2_1", "top_k": 3, "tot_config": ToTConfig().__dict__, "orchestration": "python",
            "elapsed_seconds": 0.1}
    paths = save_trace(rs, meta, tmp_path)
    data = json.loads(open(paths["trace_json"], encoding="utf-8").read())
    assert data["agent_mode"] == "MOCK_AGENT_MODE"
    for key in ("query", "retrieved_evidence", "all_hypotheses", "assessments", "rejected_hypotheses", "pruning_log", "decision", "model_calls"):
        assert key in data["state"]
    assert "MOCK_AGENT_MODE" in open(paths["trace_md"], encoding="utf-8").read()
    assert "No LLM was called" in render_markdown(rs, meta)
