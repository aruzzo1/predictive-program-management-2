"""Bounded Tree-of-Thought controller for one dependency question.

Parameters (Capstone Checkpoint 4.1; model-call budget reduced for the MVP):
  max successors per retained state 3, beam width 3, max depth 3, score threshold 70,
  near tie = within 5 points, max model calls 20.

Each depth: expand every retained state (the root at depth 1) with the generator (1 call), validate
the successors deterministically, send valid ones to the critic (1 call each), reject hard-constraint
failures and scores below threshold, then keep the best `beam_width` candidates (new and previously
retained). Each hypothesis is expanded at most once. Stop when a candidate clearly dominates (above
threshold and more than the near-tie margin ahead of the runner-up), when nothing viable remains, when
every retained hypothesis has been expanded without producing anything new (NO_NEW_CANDIDATES), at
the depth limit, or when the budget is spent.

After the search stops, decide() first runs one comparative critic review of the surviving hypotheses
(at most one model call, counted against the budget). It is advisory: the verdict rule below stays
deterministic on the individual scores, and the review is recorded in the trace and decision summary.
Running it inside decide() keeps the LangGraph topology unchanged and both orchestrations identical.

The steps are separate methods so the LangGraph wrapper (agents.graph) drives exactly the same logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from ppm_agent.agents.critic import Critic
from ppm_agent.agents.generator import ThoughtGenerator
from ppm_agent.agents.llm import LLMCallError
from ppm_agent.agents.validation import validate_assessment, validate_hypothesis
from ppm_agent.models import ComparativeReview, DependencyDecision, DependencyHypothesis, ReasoningState
from ppm_agent.models.dependency import POSITIVE_RELATIONSHIPS

SUPPORTED_SCORE = 80.0  # MVP decision rule (not from Checkpoint 4.1): >= 80 SUPPORTED, 70-80 PARTIALLY_SUPPORTED


@dataclass(frozen=True)
class ToTConfig:
    max_successors: int = 3
    beam_width: int = 3
    max_depth: int = 3
    score_threshold: float = 70.0
    near_tie: float = 5.0
    max_model_calls: int = 20


class ToTController:
    def __init__(self, generator: ThoughtGenerator, critic: Critic, config: ToTConfig = ToTConfig()):
        self.generator, self.critic, self.config = generator, critic, config

    # --- helpers ------------------------------------------------------------------------------

    def _budget_left(self, state: ReasoningState) -> bool:
        return state.model_calls < self.config.max_model_calls

    def _log(self, state: ReasoningState, hypothesis_id: str, action: str, reason: str, score: float | None = None):
        state.pruning_log.append({"depth": state.depth, "hypothesis_id": hypothesis_id, "action": action, "reason": reason, "score": score})

    def _reject(self, state: ReasoningState, h: DependencyHypothesis, reason: str, score: float | None = None):
        state.rejected_hypotheses.append(h)
        self._log(state, h.hypothesis_id, "REJECTED", reason, score)

    def ranked(self, state: ReasoningState) -> list[DependencyHypothesis]:
        return sorted(state.active_hypotheses, key=lambda h: (-state.assessments[h.hypothesis_id].overall_score, h.hypothesis_id))

    # --- steps --------------------------------------------------------------------------------

    def generate(self, state: ReasoningState, retrieval_chunk_ids: list[str]) -> None:
        """Expand the retained states (or the root) with the generator; successors go to pending."""
        state.depth += 1
        if state.depth == 1:
            parents = [None]  # expand the root
        else:  # expand retained hypotheses that have not been expanded yet (each once)
            parents = [h for h in self.ranked(state) if h.hypothesis_id not in state.expanded_ids]
        for parent in parents[: self.config.beam_width]:
            if not self._budget_left(state):
                state.events.append(f"depth {state.depth}: budget reached before expanding {parent.hypothesis_id if parent else 'root'}")
                break
            state.model_calls += 1
            if parent is not None:
                state.expanded_ids.append(parent.hypothesis_id)
            hyps, errors = self.generator.propose(state, parent, self.config.max_successors)
            for e in errors:
                state.events.append(f"generator output rejected: {e}")
            hyps = hyps[: self.config.max_successors]
            state.pending_hypotheses.extend(hyps)
            state.all_hypotheses.extend(hyps)
            state.events.append(f"depth {state.depth}: generator expanded {parent.hypothesis_id if parent else 'root'} -> "
                                f"{[h.hypothesis_id for h in hyps]} ({self.generator.mode})")

    def validate(self, state: ReasoningState, retrieval_chunk_ids: list[str]) -> None:
        """Deterministic checks; invalid hypotheses never reach the critic."""
        valid = []
        for h in state.pending_hypotheses:
            errors = validate_hypothesis(h, state, retrieval_chunk_ids)
            state.validation_errors[h.hypothesis_id] = errors
            if errors:
                self._reject(state, h, "VALIDATION: " + "; ".join(errors))
            else:
                valid.append(h)
        state.pending_hypotheses = valid

    def evaluate(self, state: ReasoningState) -> None:
        """Critic call per valid pending hypothesis, while budget remains."""
        judged = []
        for h in state.pending_hypotheses:
            if not self._budget_left(state):
                self._log(state, h.hypothesis_id, "NOT_EVALUATED", "model-call budget reached")
                continue
            state.model_calls += 1
            try:
                a = self.critic.assess(h, state)
            except LLMCallError as exc:  # no score is invented for a failed call
                self._reject(state, h, f"CRITIC CALL FAILED: {exc}")
                continue
            errors = validate_assessment(a, {h.hypothesis_id})
            if errors:
                self._reject(state, h, "INVALID ASSESSMENT: " + "; ".join(errors))
                continue
            state.assessments[h.hypothesis_id] = a
            if a.critic_validation_disagreement:  # audit evidence: recorded, never acted on
                state.critic_disagreements.append({"depth": state.depth, "hypothesis_id": h.hypothesis_id,
                                                   "deterministic_validation_result": a.deterministic_validation_result,
                                                   "critic_claimed_hard_failure": a.critic_claimed_hard_failure,
                                                   "critic_claimed_hard_failure_reasons": a.critic_claimed_hard_failure_reasons,
                                                   "disagreement_reason": a.disagreement_reason})
                state.events.append(f"critic/Python validation disagreement on {h.hypothesis_id}: {a.disagreement_reason}")
            judged.append(h)
        state.pending_hypotheses = judged

    def prune(self, state: ReasoningState) -> None:
        """Hard-constraint failures and sub-threshold scores are rejected; the best beam_width survive.

        hard_constraint_pass is Python's deterministic result (plus the mock critic's rules in MOCK_AGENT_MODE);
        a real critic's claimed hard failure never reaches this check.
        """
        survivors = []
        for h in state.pending_hypotheses:
            a = state.assessments[h.hypothesis_id]
            if not a.hard_constraint_pass:
                self._reject(state, h, "HARD CONSTRAINT: " + "; ".join(a.hard_constraint_failures), a.overall_score)
            elif a.overall_score < self.config.score_threshold:
                self._reject(state, h, f"BELOW THRESHOLD ({a.overall_score} < {self.config.score_threshold})", a.overall_score)
            else:
                survivors.append(h)
        state.pending_hypotheses = []
        state.active_hypotheses = state.active_hypotheses + survivors
        ranked = self.ranked(state)
        for h in ranked[self.config.beam_width:]:
            self._reject(state, h, f"OUTSIDE BEAM (width {self.config.beam_width})", state.assessments[h.hypothesis_id].overall_score)
        state.active_hypotheses = ranked[: self.config.beam_width]
        for h in state.active_hypotheses:
            self._log(state, h.hypothesis_id, "RETAINED", "in beam", state.assessments[h.hypothesis_id].overall_score)

    def should_continue(self, state: ReasoningState) -> bool:
        """Set the stop status; True means expand another depth."""
        ranked = self.ranked(state)
        if not ranked:
            state.status = "NO_VIABLE_CANDIDATE"
            return False
        top = state.assessments[ranked[0].hypothesis_id].overall_score
        runner_up = state.assessments[ranked[1].hypothesis_id].overall_score if len(ranked) > 1 else None
        if runner_up is None or top - runner_up > self.config.near_tie:
            state.status = "DOMINANT_CANDIDATE"
            return False
        if all(h.hypothesis_id in state.expanded_ids for h in ranked):
            state.status = "NO_NEW_CANDIDATES"  # every retained hypothesis was expanded without producing a better one
            return False
        if state.depth >= self.config.max_depth:
            state.status = "DEPTH_LIMIT"
            return False
        if not self._budget_left(state):
            state.status = "BUDGET_EXHAUSTED"
            return False
        state.events.append(f"depth {state.depth}: near tie ({top} vs {runner_up}); refining")
        return True

    def review(self, state: ReasoningState) -> ComparativeReview:
        """Comparative critic review of the final survivors: at most one call per episode, advisory only.

        Only hypotheses in the beam (validated, passing hard constraints, at or above threshold) are shown.
        Python enforces the limits: the recommended id must be a survivor (a pruned hypothesis cannot be
        revived), and the individual assessments are restored if anything changed them.
        """
        ranked = self.ranked(state)
        ids = [h.hypothesis_id for h in ranked]
        scores = [state.assessments[i].overall_score for i in ids]
        review = ComparativeReview(status="COMPLETED", mode=self.critic.mode, reviewed_hypothesis_ids=ids,
                                   deterministic_near_tie=(scores[0] - scores[1] <= self.config.near_tie) if len(ids) > 1 else None)
        if not ranked:
            review.status = "NO_SURVIVORS"
        elif len(ranked) == 1:
            review.status = "SINGLE_SURVIVOR"
        elif not hasattr(self.critic, "compare"):
            review.status = "NOT_AVAILABLE"
        elif not self._budget_left(state):
            review.status = "SKIPPED_BUDGET"
        else:
            state.model_calls += 1
            state.comparative_model_call_count += 1
            snapshot = {k: v.model_copy(deep=True) for k, v in state.assessments.items()}
            try:
                out = self.critic.compare([h.model_copy(deep=True) for h in ranked], state, self.config.near_tie)
            except LLMCallError as exc:
                review.status, review.validation_notes = "FAILED", [f"comparative call failed: {exc}"]
                out = None
            if state.assessments != snapshot:
                state.assessments = snapshot
                review.validation_notes.append("individual assessments were modified during the review; restored")
            if out is not None:
                review.near_tie = out.near_tie
                review.assumption_comparison, review.uncertainty_assessment = out.assumption_comparison, out.uncertainty_assessment
                review.comparative_reasoning_summary = out.comparative_reasoning_summary
                if out.preferred_hypothesis_id in ids:
                    review.preferred_hypothesis_id = out.preferred_hypothesis_id
                    review.agrees_with_score_ranking = out.preferred_hypothesis_id == ids[0]
                else:
                    review.validation_notes.append(f"recommended {out.preferred_hypothesis_id!r} is not a surviving hypothesis {ids}; "
                                                   "recommendation discarded")
        state.comparative_review = review
        state.events.append(f"comparative review: {review.status}"
                            + (f", preferred {review.preferred_hypothesis_id} (score leader {ids[0]})" if review.preferred_hypothesis_id else "")
                            + (f"; {'; '.join(review.validation_notes)}" if review.validation_notes else ""))
        return review

    def decide(self, state: ReasoningState) -> DependencyDecision:
        if state.comparative_review is None:
            self.review(state)
        ranked = self.ranked(state)
        src, tgt = state.source_activity, state.target_activity
        if not ranked:
            decision = DependencyDecision(source_activity=src, target_activity=tgt, decision="UNRESOLVED",
                                          decision_summary="No hypothesis survived validation, hard constraints and the score threshold.")
            state.decision = decision
            return decision
        best = ranked[0]
        a = state.assessments[best.hypothesis_id]
        rivals = [h for h in ranked[1:] if a.overall_score - state.assessments[h.hypothesis_id].overall_score <= self.config.near_tie]
        positive = best.relationship_type in POSITIVE_RELATIONSHIPS
        if rivals and any((r.relationship_type in POSITIVE_RELATIONSHIPS) != positive for r in rivals):
            verdict, why = "UNRESOLVED", f"near tie between a dependency and a no-dependency interpretation ({[r.hypothesis_id for r in rivals]})"
        elif not positive:
            verdict, why = ("NOT_SUPPORTED" if best.relationship_type == "NONE" else "UNRESOLVED"), "best surviving hypothesis is " + best.relationship_type
        elif rivals and any(r.relationship_type != best.relationship_type for r in rivals):
            verdict, why = "PARTIALLY_SUPPORTED", f"a dependency is supported but its type is in a near tie with {[r.relationship_type for r in rivals]}"
        elif a.overall_score >= SUPPORTED_SCORE:
            verdict, why = "SUPPORTED", f"{best.relationship_type} hypothesis scored {a.overall_score} (>= {SUPPORTED_SCORE})"
        else:
            verdict, why = "PARTIALLY_SUPPORTED", f"{best.relationship_type} hypothesis scored {a.overall_score} (threshold {self.config.score_threshold}-{SUPPORTED_SCORE})"
        state.accepted_hypothesis = best
        r = state.comparative_review
        advisory = (f" Comparative review (advisory): prefers {r.preferred_hypothesis_id}, "
                    f"{'agreeing with' if r.agrees_with_score_ranking else 'differing from'} the score ranking; "
                    f"near tie judged {'genuine' if r.near_tie else 'not genuine'}." if r and r.preferred_hypothesis_id else "")
        decision = DependencyDecision(source_activity=src, target_activity=tgt, decision=verdict, selected_relationship_type=best.relationship_type,
                                      selected_hypothesis_id=best.hypothesis_id, supporting_evidence_ids=best.supporting_evidence_ids,
                                      critic_score=a.overall_score,
                                      decision_summary=f"{why}. Stop status: {state.status}. Mode: {state.agent_mode}.{advisory}")
        state.decision = decision
        return decision

    # --- plain-Python driver --------------------------------------------------------------------

    def run(self, state: ReasoningState, retrieval_chunk_ids: list[str]) -> DependencyDecision:
        while True:
            self.generate(state, retrieval_chunk_ids)
            self.validate(state, retrieval_chunk_ids)
            self.evaluate(state)
            self.prune(state)
            if not self.should_continue(state):
                break
        return self.decide(state)
