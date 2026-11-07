"""One reasoning episode: activities + query -> retrieval -> ToT -> decision -> trace files."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from ppm_agent.agents.critic import Critic
from ppm_agent.agents.evidence import PREFERRED_STRATEGY, STRATEGY_NAMES, retrieve_evidence
from ppm_agent.agents.generator import ThoughtGenerator
from ppm_agent.agents.llm import LLMClient, agent_mode
from ppm_agent.agents.tot import ToTConfig, ToTController
from ppm_agent.agents.validation import validate_evidence
from ppm_agent.config import PROJECT_ROOT
from ppm_agent.models import Activity, CandidateDependency, ReasoningState

TRACE_DIR = PROJECT_ROOT / "outputs" / "agentic_traces"


def new_state(query: str, source: Activity, target: Activity, llm: LLMClient | None) -> ReasoningState:
    return ReasoningState(query=query, source_activity=source.activity_id, target_activity=target.activity_id,
                          activities={source.activity_id: source, target.activity_id: target},
                          candidate=CandidateDependency(source_activity=source.activity_id, target_activity=target.activity_id,
                                                        proposed_relationship=f"{source.name} -> {target.name}"),
                          agent_mode=agent_mode(llm))


def attach_evidence(state: ReasoningState, evidence, chunk_ids: list[str]) -> None:
    state.retrieved_evidence = evidence
    state.candidate.evidence_ids = [e.evidence_id for e in evidence]
    errors = validate_evidence(state, chunk_ids)
    if errors:
        raise ValueError(f"retrieved evidence failed validation: {errors}")
    state.events.append(f"retrieved {len(evidence)} passages via {evidence[0].retrieval_method if evidence else '-'}")


def run_episode(query: str, source: Activity, target: Activity, llm: LLMClient | None = None, top_k: int = 5,
                strategy: str = PREFERRED_STRATEGY, config: ToTConfig = ToTConfig(), bench=None, trace_dir: Path = TRACE_DIR,
                use_langgraph: bool = False, case_id: str | None = None) -> tuple[ReasoningState, dict]:
    start = time.time()
    state = new_state(query, source, target, llm)
    controller = ToTController(ThoughtGenerator(llm), Critic(llm), config)
    meta = {"retrieval_strategy": STRATEGY_NAMES.get(strategy, strategy), "top_k": top_k, "tot_config": config.__dict__,
            "orchestration": "langgraph" if use_langgraph else "python"}
    if case_id:
        meta["case_id"] = case_id  # evaluation question id; labels the trace only

    def retrieve(rs: ReasoningState) -> list[str]:
        evidence, chunk_ids = retrieve_evidence(query, top_k, strategy, bench)
        attach_evidence(rs, evidence, chunk_ids)
        return chunk_ids

    def save(rs: ReasoningState) -> dict:
        if hasattr(llm, "usage_summary"):
            meta["llm"] = llm.usage_summary()
        return save_trace(rs, {**meta, "elapsed_seconds": round(time.time() - start, 2)}, trace_dir)

    if use_langgraph:
        from ppm_agent.agents.graph import run_graph

        state, paths = run_graph(controller, state, retrieve=retrieve, save=save)
    else:
        chunk_ids = retrieve(state)
        controller.run(state, chunk_ids)
        paths = save(state)
    return state, {**meta, "elapsed_seconds": round(time.time() - start, 2), **paths}


def save_trace(state: ReasoningState, meta: dict, trace_dir: Path = TRACE_DIR) -> dict:
    trace_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    case = f"{meta['case_id']}_{state.agent_mode}_" if meta.get("case_id") else ""
    base = trace_dir / f"episode_{stamp}_{case}{state.source_activity}_{state.target_activity}"
    payload = {"agent_mode": state.agent_mode, "meta": meta, "state": state.model_dump(mode="json")}
    json_path, md_path = base.with_suffix(".json"), base.with_suffix(".md")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(state, meta), encoding="utf-8")
    return {"trace_json": str(json_path), "trace_md": str(md_path)}


def hard_constraint_cell(a) -> str:
    text = "pass" if a.hard_constraint_pass else "FAIL: " + " ".join("; ".join(a.hard_constraint_failures).split()).replace("|", "/")
    if a.deterministic_validation_result:
        text += f" (Python: {a.deterministic_validation_result})"
    if a.critic_validation_disagreement:
        text += f"; critic claimed {'FAIL' if a.critic_claimed_hard_failure else 'pass'}: **DISAGREEMENT** (advisory, see below)"
    return text


def render_markdown(state: ReasoningState, meta: dict) -> str:
    acts = state.activities
    src, tgt = acts[state.source_activity], acts[state.target_activity]
    cell = lambda t: " ".join(str(t).split()).replace("|", "/")  # noqa: E731
    mock = state.agent_mode == "MOCK_AGENT_MODE"
    L = [f"# Dependency reasoning episode: {src.name} → {tgt.name}", ""]
    if mock:
        L += ["> **MOCK_AGENT_MODE.** No LLM was called. The generator and critic are deterministic, rule-based stand-ins that "
              "exercise the architecture (validation, scoring, pruning, beam, stop conditions, trace). Their hypotheses and scores are "
              "**not model reasoning** and must not be read as analytical findings.", ""]
    elif "llm" in meta:
        llm = meta["llm"]
        L += [f"> **{state.agent_mode}.** Generator and critic are separate, stateless calls to {llm['model']} ({llm['provider']}, "
              "structured output, temperature 0). Hypotheses and sub-scores are model output; validation, the weighted total, pruning "
              "and the decision are deterministic Python. "
              f"Tokens: {llm['input_tokens']} in / {llm['output_tokens']} out over {llm['successful_responses']} successful responses.", ""]
    L += [f"- Case: **{meta['case_id']}** ({state.agent_mode})"] if meta.get("case_id") else []
    L += [f"- Query: *{state.query}*",
          f"- Activities: {src.activity_id} {src.name} ({src.activity_type}); {tgt.activity_id} {tgt.name} ({tgt.activity_type})",
          f"- Retrieval: {meta['retrieval_strategy']}, top_k {meta['top_k']}; orchestration: {meta['orchestration']}",
          f"- ToT config: {meta['tot_config']}",
          f"- Model calls: {state.model_calls}{' (mock calls, counted against the budget)' if mock else ''}, "
          f"of which comparative review: {state.comparative_model_call_count}; depth reached {state.depth}; "
          f"stop status **{state.status}**; elapsed {meta['elapsed_seconds']} s", "",
          "## Retrieved evidence", "", "| ID | Source | PDF p. | Chunk | Rank | Excerpt |", "|---|---|---|---|---|---|"]
    for e in state.retrieved_evidence:
        L.append(f"| {e.evidence_id} | {e.source_document} ({e.publication_date or 'undated'}) | {e.pdf_page} | `{e.chunk_id}` | "
                 f"{e.retrieval_rank} | {cell(e.text[:220])}… |")
    L += ["", "## Hypotheses and critic assessments", "",
          "| Hypothesis | Depth | Type | Cites | Valid | Doc (30%) | Eng (30%) | Model (20%) | Pred (20%) | Total | Hard constraints |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for h in state.all_hypotheses:
        a = state.assessments.get(h.hypothesis_id)
        v = state.validation_errors.get(h.hypothesis_id)
        L.append(f"| {h.hypothesis_id} | {h.depth} | {h.relationship_type}{f' via {h.intermediate_activity}' if h.intermediate_activity else ''} | "
                 f"{', '.join(h.supporting_evidence_ids)} | {'yes' if v == [] else cell('; '.join(v)) if v else '-'} | "
                 + (" | ".join(f"{x:.0f}" for x in (a.documentary_evidence_score, a.engineering_consistency_score, a.model_consistency_score,
                                                   a.predictive_usefulness_score)) + f" | **{a.overall_score:.1f}** | "
                    + hard_constraint_cell(a) if a else "- | - | - | - | - | not assessed")
                 + " |")
    L += ["", "Reasoning summaries:", ""]
    for h in state.all_hypotheses:
        L.append(f"- **{h.hypothesis_id}**: {h.reasoning_summary} Assumptions: {'; '.join(h.assumptions) or 'none'}")
    findings = [(hid, a) for hid, a in state.assessments.items() if a.evidence_strength_summary]
    if findings:
        L += ["", "Critic findings (qualitative; expressed through the scores, never a structural rejection):", ""]
        for hid, a in findings:
            L.append(f"- **{hid}** [{a.evidence_support_label or 'no label'}]: {a.critic_summary} *Evidence strength:* {a.evidence_strength_summary} "
                     f"*Contradictions:* {'; '.join(a.contradictions) or 'none'}. "
                     f"*Unsupported assumptions:* {'; '.join(a.unsupported_assumptions) or 'none'}. "
                     f"*Other concerns:* {'; '.join(a.critic_concerns) or 'none'}.")
    L += ["", "## Critic / Python validation disagreements", "",
          "Hard constraints are owned by deterministic Python validation; a critic's hard-failure claim is advisory and is "
          "compared with Python's result.", ""]
    if state.critic_disagreements:
        L += ["| Depth | Hypothesis | Python | Critic claimed hard failure | Reason |", "|---|---|---|---|---|"]
        for d in state.critic_disagreements:
            L.append(f"| {d['depth']} | {d['hypothesis_id']} | {d['deterministic_validation_result']} | "
                     f"{'yes' if d['critic_claimed_hard_failure'] else 'no'} | {cell(d['disagreement_reason'])} |")
    else:
        L.append("None recorded.")
    L += ["", "## Pruning decisions", "", "| Depth | Hypothesis | Action | Score | Reason |", "|---|---|---|---|---|"]
    for p in state.pruning_log:
        L.append(f"| {p['depth']} | {p['hypothesis_id']} | {p['action']} | {p['score'] if p['score'] is not None else '-'} | {cell(p['reason'])} |")
    r = state.comparative_review
    L += ["", "## Comparative review of survivors", "",
          "One advisory call after pruning; it cannot rescore, revive a pruned hypothesis or change validation.", ""]
    if r is None:
        L.append("Not run.")
    else:
        L += [f"- Status: **{r.status}** ({r.mode}); comparative model calls: {state.comparative_model_call_count}",
              f"- Reviewed (survivors, score order): {r.reviewed_hypothesis_ids or 'none'}",
              f"- Preferred: {r.preferred_hypothesis_id or '-'}; agrees with score ranking: "
              f"{'-' if r.agrees_with_score_ranking is None else 'yes' if r.agrees_with_score_ranking else 'no'}",
              f"- Near tie: numerical (Python) {'-' if r.deterministic_near_tie is None else r.deterministic_near_tie}; "
              f"judged genuine by reviewer {'-' if r.near_tie is None else r.near_tie}"]
        for label, text in (("Assumptions", r.assumption_comparison), ("Uncertainty", r.uncertainty_assessment),
                            ("Reasoning", r.comparative_reasoning_summary)):
            if text:
                L.append(f"- {label}: {text}")
        L += [f"- Validation note: {n}" for n in r.validation_notes]
    d = state.decision
    L += ["", "## Decision", "",
          f"**{d.decision}**: {d.selected_relationship_type or '-'} (hypothesis {d.selected_hypothesis_id or '-'}, critic score "
          f"{d.critic_score if d.critic_score is not None else '-'}), evidence {d.supporting_evidence_ids}.", "", d.decision_summary, ""]
    if mock:
        L += ["*Decision produced by the MOCK pipeline; it demonstrates control flow only.*", ""]
    L += ["## Events", ""] + [f"- {e}" for e in state.events] + [""]
    return "\n".join(L)
