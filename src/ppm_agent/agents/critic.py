"""Critic: scores one hypothesis independently on the Checkpoint 4.1 criteria (0-100 each).

The total is always computed in Python (scoring.weighted_score), never taken from the model. With a
real LLM the critic uses prompts/critic.md; in MOCK_AGENT_MODE it recomputes generic text features
from the evidence itself (it does not read the generator's reasoning) and applies transparent rules.

Hard constraints belong to Python (validation.deterministic_check). In REAL_LLM_MODE the model only
scores and lists qualitative concerns; its claim of a hard failure is advisory and is compared with
Python's result (critic_validation_disagreement). Model consistency is pinned to the neutral 50 in
Python while no DSM exists. In MOCK_AGENT_MODE the rule-based critic's own hard-failure rules remain
binding on top of Python's result (mock behaviour unchanged).

compare() is the comparative review: one call over the final surviving hypotheses (prompts/comparative.md).
It recommends; it never rescores, revives or validates (the controller enforces this).
"""

from __future__ import annotations

from pathlib import Path

from ppm_agent.agents.generator import evidence_block
from ppm_agent.agents.llm import LLMClient, agent_mode
from ppm_agent.agents.scoring import NEUTRAL_MODEL_CONSISTENCY, weighted_score
from ppm_agent.agents.text_features import passage_features
from ppm_agent.agents.validation import critic_disagreement, deterministic_check
from ppm_agent.models import ComparativeReviewOutput, CriticAssessment, CriticOutput, DependencyHypothesis, ReasoningState
from ppm_agent.models.dependency import POSITIVE_RELATIONSHIPS

PROMPT = (Path(__file__).parent / "prompts" / "critic.md").read_text(encoding="utf-8")
COMPARATIVE_PROMPT = (Path(__file__).parent / "prompts" / "comparative.md").read_text(encoding="utf-8")
MODEL_CONSISTENCY_NOTE = ("No DSM or dependency model exists yet: score this criterion 50 (neutral) and say so.")


def build_critic_prompt(h: DependencyHypothesis, state: ReasoningState) -> str:
    return PROMPT.format(model_consistency_note=MODEL_CONSISTENCY_NOTE,
                         source_name=state.activities[state.source_activity].name, target_name=state.activities[state.target_activity].name,
                         hypothesis_id=h.hypothesis_id, relationship_type=h.relationship_type,
                         intermediate=f" via {h.intermediate_activity}" if h.intermediate_activity else "",
                         reasoning_summary=h.reasoning_summary, supporting=h.supporting_evidence_ids,
                         contradicting=h.contradicting_evidence_ids, assumptions=h.assumptions, evidence_block=evidence_block(state))


def make_assessment(hypothesis_id: str, doc: float, eng: float, model: float, pred: float, passed: bool,
                    failures: list[str], summary: str) -> CriticAssessment:
    clamp = lambda x: max(0.0, min(100.0, float(x)))  # noqa: E731
    doc, eng, model, pred = map(clamp, (doc, eng, model, pred))
    return CriticAssessment(hypothesis_id=hypothesis_id, documentary_evidence_score=doc, engineering_consistency_score=eng,
                            model_consistency_score=model, predictive_usefulness_score=pred, hard_constraint_pass=passed,
                            hard_constraint_failures=failures, critic_summary=summary, overall_score=weighted_score(doc, eng, model, pred))


class Critic:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm
        self.mode = agent_mode(llm)

    def assess(self, h: DependencyHypothesis, state: ReasoningState) -> CriticAssessment:
        """One model call per hypothesis (counted by the controller). A separate, stateless call: the critic
        sees the hypothesis and the evidence, never the generator's conversation. Raises LLMCallError."""
        python_errors = deterministic_check(h, state)
        deterministic = {"deterministic_validation_result": "FAIL" if python_errors else "PASS",
                         "deterministic_validation_errors": python_errors}
        if self.llm is None:
            a = mock_assess(h, state)
            return a.model_copy(update={**deterministic, "hard_constraint_pass": a.hard_constraint_pass and not python_errors,
                                        "hard_constraint_failures": python_errors + a.hard_constraint_failures})

        out = self.llm.complete("You are an independent critic of dependency hypotheses.", build_critic_prompt(h, state), CriticOutput)
        claimed_reasons = [r for r in out.critic_claimed_hard_failure_reasons if r.strip()]
        claimed = out.critic_claimed_hard_failure or bool(claimed_reasons)
        reason = critic_disagreement(h, python_errors, claimed, claimed_reasons)
        if out.model_consistency_score != NEUTRAL_MODEL_CONSISTENCY:
            state.events.append(f"{h.hypothesis_id}: critic returned model_consistency_score {out.model_consistency_score}; "
                                f"pinned to {NEUTRAL_MODEL_CONSISTENCY:.0f} (no DSM exists)")
        a = make_assessment(h.hypothesis_id, out.documentary_evidence_score, out.engineering_consistency_score, NEUTRAL_MODEL_CONSISTENCY,
                            out.predictive_usefulness_score, not python_errors, python_errors, out.critic_summary)
        return a.model_copy(update={**deterministic, "evidence_support_label": out.evidence_support_label,
                                    "evidence_strength_summary": out.evidence_strength_summary,
                                    "contradictions": out.contradictions, "unsupported_assumptions": out.unsupported_assumptions,
                                    "critic_concerns": out.critic_concerns, "critic_claimed_hard_failure": claimed,
                                    "critic_claimed_hard_failure_reasons": claimed_reasons,
                                    "critic_validation_disagreement": reason is not None, "disagreement_reason": reason})

    def compare(self, survivors: list[DependencyHypothesis], state: ReasoningState, near_tie_margin: float) -> ComparativeReviewOutput:
        """One comparative call over the surviving hypotheses (score order). Advisory; the controller validates the
        result and guarantees it changes no score. Raises LLMCallError."""
        if self.llm is None:
            return mock_compare(survivors, state, near_tie_margin)
        return self.llm.complete("You compare surviving dependency hypotheses.", build_comparative_prompt(survivors, state, near_tie_margin),
                                 ComparativeReviewOutput)


def build_comparative_prompt(survivors: list[DependencyHypothesis], state: ReasoningState, near_tie_margin: float) -> str:
    blocks = []
    for h in survivors:
        a = state.assessments[h.hypothesis_id]
        blocks.append(f"[{h.hypothesis_id}] {h.relationship_type}{f' via {h.intermediate_activity}' if h.intermediate_activity else ''}; "
                      f"total {a.overall_score} (documentary {a.documentary_evidence_score:.0f}, engineering {a.engineering_consistency_score:.0f}, "
                      f"model {a.model_consistency_score:.0f}, predictive {a.predictive_usefulness_score:.0f}); "
                      f"support label {a.evidence_support_label or 'n/a'}\n"
                      f"  Reasoning: {h.reasoning_summary}\n  Cited: {h.supporting_evidence_ids}; contradicting: {h.contradicting_evidence_ids}\n"
                      f"  Assumptions: {h.assumptions}\n  Individual critic: {a.critic_summary}")
    return COMPARATIVE_PROMPT.format(near_tie_margin=f"{near_tie_margin:g}", source_name=state.activities[state.source_activity].name,
                                     target_name=state.activities[state.target_activity].name,
                                     hypotheses_block="\n\n".join(blocks), evidence_block=evidence_block(state))


# --- MOCK_AGENT_MODE ------------------------------------------------------------------------------


def mock_assess(h: DependencyHypothesis, state: ReasoningState) -> CriticAssessment:
    src, tgt = state.activities[state.source_activity], state.activities[state.target_activity]
    evidence = state.evidence_by_id()
    feats = {e.evidence_id: passage_features(e.text, src, tgt) for e in state.retrieved_evidence}
    cited = [i for i in h.supporting_evidence_ids if i in feats]
    failures = []

    # hard constraints judged from the evidence itself
    untraceable = [i for i in cited if not (feats[i]["source_terms"] or feats[i]["target_terms"])]
    if untraceable:
        failures.append(f"cited passages {untraceable} mention neither activity: relationship not traceable to them")
    stated_anywhere = [i for i, f in feats.items() if f["stated_dependency"]]
    if h.relationship_type == "NONE" and stated_anywhere:
        failures.append(f"retrieved passages {stated_anywhere} state a dependency between the activities, contradicting NONE")
    if not cited:
        failures.append("no cited evidence")

    n = max(len(cited), 1)
    docs = {evidence[i].source_document for i in cited}
    provenance = sum(bool(evidence[i].pdf_page and evidence[i].chunk_id) for i in cited) / n
    if h.relationship_type in POSITIVE_RELATIONSHIPS:
        relevant = sum(feats[i]["stated_dependency"] for i in cited) / n if h.relationship_type == "DIRECT" else \
            sum(bool(feats[i]["intermediate_terms"]) and feats[i]["mentions_source"] for i in cited) / n
    else:
        relevant = sum(not feats[i]["co_mention"] for i in cited) / n
    doc = 40 * provenance + 50 * relevant + 5 * min(len(docs) - 1, 2)  # independent sources add up to 10

    if h.relationship_type == "DIRECT":
        eng = 90 if any(feats[i]["stated_dependency"] for i in cited) else 50
    elif h.relationship_type == "INDIRECT":
        eng = 80 if any(feats[i]["intermediate_terms"] and feats[i]["mentions_target"] for i in cited) else 55
    elif h.relationship_type == "RECIPROCAL":
        eng = 50  # mock rules cannot see direction in both senses
    else:
        eng = 30 if stated_anywhere else 70
    pred = {"DIRECT": 85, "INDIRECT": 75, "RECIPROCAL": 70}.get(h.relationship_type, 30)

    summary = (f"[MOCK critic, rule-based] {len(cited)} cited passages from {len(docs)} documents; "
               f"{sum(feats[i]['stated_dependency'] for i in cited)} state a dependency with both activities; "
               f"model consistency scored neutral ({NEUTRAL_MODEL_CONSISTENCY:.0f}) because no DSM exists.")
    return make_assessment(h.hypothesis_id, doc, eng, NEUTRAL_MODEL_CONSISTENCY, pred, not failures, failures, summary)


def mock_compare(survivors: list[DependencyHypothesis], state: ReasoningState, near_tie_margin: float) -> ComparativeReviewOutput:
    """Rule-based stand-in: prefers the top-scoring survivor; the 'near tie' is the score margin. No comparison of explanations."""
    top, second = (state.assessments[h.hypothesis_id].overall_score for h in survivors[:2])
    return ComparativeReviewOutput(
        preferred_hypothesis_id=survivors[0].hypothesis_id, near_tie=top - second <= near_tie_margin,
        assumption_comparison="[MOCK] not assessed", uncertainty_assessment="[MOCK] not assessed",
        comparative_reasoning_summary="[MOCK comparative review, rule-based] preferred = highest-scoring survivor; "
                                      "no comparison of explanations was performed.")
