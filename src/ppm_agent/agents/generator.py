"""Thought generator: proposes up to N competing dependency hypotheses from the retrieved evidence.

With a real LLM it uses prompts/generator.md. In MOCK_AGENT_MODE it applies transparent rules over
generic text features (agents.text_features); this is a stand-in for exercising the architecture,
not reasoning, and is labelled as such everywhere it appears.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from ppm_agent.agents.llm import LLMCallError, LLMClient, agent_mode
from ppm_agent.agents.text_features import passage_features
from ppm_agent.agents.validation import parse_hypothesis
from ppm_agent.models import DependencyHypothesis, GeneratorOutput, ReasoningState

PROMPT = (Path(__file__).parent / "prompts" / "generator.md").read_text(encoding="utf-8")
REFINE_INSTRUCTIONS = ("6. You are REFINING the parent hypothesis shown below. Propose sharper successors: tighten the "
                       "citations to the passages that actually state the relationship, make assumptions explicit, or "
                       "split it into more specific alternatives. Do not repeat it unchanged.")


def evidence_block(state: ReasoningState) -> str:
    return "\n\n".join(f"[{e.evidence_id}] {e.source_document}, PDF p. {e.pdf_page}"
                       f"{f' (printed p. {e.printed_page})' if e.printed_page else ''}"
                       f"{f', section {e.section_type}' if e.section_type else ''}:\n{e.text}" for e in state.retrieved_evidence)


def build_generator_prompt(state: ReasoningState, parent: DependencyHypothesis | None, max_hypotheses: int) -> str:
    src, tgt = state.activities[state.source_activity], state.activities[state.target_activity]
    parent_block = "" if parent is None else (
        f"\nParent hypothesis {parent.hypothesis_id}: {parent.relationship_type}"
        f"{f' via {parent.intermediate_activity}' if parent.intermediate_activity else ''}\n"
        f"Reasoning: {parent.reasoning_summary}\nCited: {parent.supporting_evidence_ids}\nAssumptions: {parent.assumptions}")
    return PROMPT.format(max_hypotheses=max_hypotheses, refinement_instructions="" if parent is None else REFINE_INSTRUCTIONS,
                         source_name=src.name, source_type=src.activity_type, source_description=src.description,
                         target_name=tgt.name, target_type=tgt.activity_type, target_description=tgt.description,
                         query=state.query, evidence_block=evidence_block(state), parent_block=parent_block)


class ThoughtGenerator:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm
        self.mode = agent_mode(llm)

    def propose(self, state: ReasoningState, parent: DependencyHypothesis | None = None,
                max_hypotheses: int = 3) -> tuple[list[DependencyHypothesis], list[str]]:
        """Return (hypotheses, parse errors). Counts as ONE model call (the controller does the counting).

        Ids are D<search depth>.<parent>.<k>, unique because each parent is expanded once.
        """
        depth = 1 if parent is None else parent.depth + 1
        prefix = f"D{state.depth}.{parent.hypothesis_id if parent else 'root'}."
        if self.llm is not None:
            try:
                out = self.llm.complete("You generate competing dependency hypotheses.", build_generator_prompt(state, parent, max_hypotheses),
                                        GeneratorOutput)
            except LLMCallError as exc:
                return [], [f"{prefix}*: generator call failed: {exc}"]
            hyps, errors = [], []
            for k, item in enumerate(out.hypotheses[:max_hypotheses], start=1):
                h, errs = parse_hypothesis({**item.model_dump(), "hypothesis_id": f"{prefix}{k}", "parent_id": parent.hypothesis_id if parent else None,
                                            "depth": depth, "source_activity": state.source_activity, "target_activity": state.target_activity})
                hyps += [h] if h else []
                errors += [f"{prefix}{k}: {e}" for e in errs]
            return hyps, errors
        return mock_propose(state, parent, max_hypotheses, prefix, depth), []


# --- MOCK_AGENT_MODE ------------------------------------------------------------------------------


def mock_propose(state: ReasoningState, parent: DependencyHypothesis | None, max_hypotheses: int, prefix: str,
                 depth: int) -> list[DependencyHypothesis]:
    src, tgt = state.activities[state.source_activity], state.activities[state.target_activity]
    feats = {e.evidence_id: passage_features(e.text, src, tgt) for e in state.retrieved_evidence}
    common = dict(source_activity=state.source_activity, target_activity=state.target_activity, depth=depth,
                  parent_id=parent.hypothesis_id if parent else None)
    if parent is not None:
        return mock_refine(parent, feats, prefix, common)[:max_hypotheses]

    stated = [i for i, f in feats.items() if f["stated_dependency"]]
    co = [i for i, f in feats.items() if f["co_mention"]]
    mediated = [i for i, f in feats.items() if f["mentions_source"] and f["intermediate_terms"]]
    one_sided = [i for i, f in feats.items() if f["mentions_source"] != f["mentions_target"]]
    hyps = []
    if co:
        hyps.append(DependencyHypothesis(
            hypothesis_id=f"{prefix}1", relationship_type="DIRECT",
            reasoning_summary=f"[MOCK] {len(stated)} of {len(feats)} passages mention both activities with dependency language; "
                              f"reads them as {src.name} directly affecting {tgt.name}.",
            supporting_evidence_ids=stated or co, assumptions=["[MOCK] co-mention with dependency language is read as a stated effect"],
            **common))
    if mediated:
        term = Counter(t for i in mediated for t in feats[i]["intermediate_terms"]).most_common(1)[0][0]
        hyps.append(DependencyHypothesis(
            hypothesis_id=f"{prefix}2", relationship_type="INDIRECT", intermediate_activity=f"{term}* (intermediate activity)",
            reasoning_summary=f"[MOCK] {len(mediated)} passages link {src.name} to an intermediate process term ('{term}*'); "
                              f"reads the effect on {tgt.name} as mediated by it.",
            supporting_evidence_ids=mediated, assumptions=[f"[MOCK] '{term}*' is treated as the mediating activity"], **common))
    hyps.append(DependencyHypothesis(
        hypothesis_id=f"{prefix}3", relationship_type="NONE",
        reasoning_summary=f"[MOCK] Null alternative: {len(one_sided)} passages mention only one of the activities; "
                          "the evidence may not establish a defensible dependency.",
        supporting_evidence_ids=one_sided or list(feats)[:1],
        assumptions=["[MOCK] passages about only one activity are read as absence of a stated dependency"], **common))
    return hyps[:max_hypotheses]


def mock_refine(parent: DependencyHypothesis, feats: dict, prefix: str, common: dict) -> list[DependencyHypothesis]:
    """One successor: citations narrowed to passages with stated dependency language (for positive types)."""
    if parent.relationship_type in {"DIRECT", "INDIRECT", "RECIPROCAL"}:
        narrowed = [i for i in parent.supporting_evidence_ids if feats.get(i, {}).get("stated_dependency")] or parent.supporting_evidence_ids
        note = "[MOCK] refinement: citations narrowed to passages with explicit dependency language"
    else:
        narrowed = parent.supporting_evidence_ids
        note = "[MOCK] refinement: null alternative restated unchanged"
    return [parent.model_copy(update={"hypothesis_id": f"{prefix}1", "supporting_evidence_ids": narrowed,
                                      "reasoning_summary": f"{parent.reasoning_summary} (refined)",
                                      "assumptions": parent.assumptions + [note], **common})]
