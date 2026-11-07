"""Agentic Phase 1 demonstration: one bounded Tree-of-Thought dependency-reasoning episode.

One evaluation question (data/metadata/rag_evaluation_questions.json) with an explicit MVP
source -> target activity pair, HYBRID_RERANKED_V2_1 retrieval (top 5):
  Q01  A1 Mission-System Software Maturity -> A2 Flight-Test Execution
  Q04  A3 Test-Aircraft Availability       -> A4 Flight-Test Execution / Schedule
  Q08  A5 Development / Test Maturity      -> A6 Production Commitment / Rework Risk

Runs with a real LLM only if one is configured (see ppm_agent.agents.llm); otherwise in
MOCK_AGENT_MODE, which is stated in every output. Trace files go to outputs/agentic_traces/ and are
named with the case id and mode.

Usage:
    python scripts/run_dependency_episode.py                 # Q01, LangGraph orchestration
    python scripts/run_dependency_episode.py --case Q04      # another case
    python scripts/run_dependency_episode.py --python        # plain-Python controller loop
"""

from __future__ import annotations

import argparse

from ppm_agent.agents.episode import run_episode
from ppm_agent.agents.llm import LLMConfigurationError, detect_llm_client
from ppm_agent.models import Activity

QUERY = "What evidence indicates that mission-system software maturity affected F-35 flight-test execution?"  # Q01
A1 = Activity(activity_id="A1", name="Mission-System Software Maturity", description="Maturity of mission-system software.",
              activity_type="software")
A2 = Activity(activity_id="A2", name="Flight-Test Execution", description="Execution of flight testing.", activity_type="test")

CASES = {
    "Q01": (QUERY, A1, A2),
    "Q04": ("What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or "
            "pace of flight testing?",
            Activity(activity_id="A3", name="Test-Aircraft Availability",
                     description="Delivery and availability of developmental test aircraft.", activity_type="test"),
            Activity(activity_id="A4", name="Flight-Test Execution / Schedule",
                     description="Sequence and pace of developmental flight testing.", activity_type="test")),
    "Q08": ("What evidence describes dependencies between F-35 development testing and production decisions "
            "(development-test-production concurrency)?",
            Activity(activity_id="A5", name="Development / Test Maturity",
                     description="Design and performance knowledge demonstrated by development testing.", activity_type="test"),
            Activity(activity_id="A6", name="Production Commitment / Rework Risk",
                     description="Commitment to production quantities and the resulting risk of rework.", activity_type="production")),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", choices=sorted(CASES), default="Q01", help="evaluation question to run (default Q01)")
    parser.add_argument("--python", action="store_true", help="use the plain-Python controller loop instead of LangGraph")
    args = parser.parse_args()

    query, source, target = CASES[args.case]
    llm = detect_llm_client()
    try:
        state, meta = run_episode(query, source, target, llm=llm, use_langgraph=not args.python, case_id=args.case)
    except LLMConfigurationError as exc:
        raise SystemExit(f"REAL_LLM_MODE configuration error (episode aborted, no trace written): {exc}")
    print(f"CASE: {args.case} | {source.activity_id} {source.name} -> {target.activity_id} {target.name}")
    print(f"MODE: {state.agent_mode}" + ("  (no LLM was called; generator and critic are rule-based stand-ins)" if llm is None
                                         else f"  (model {llm.model}; {meta['llm']['input_tokens']} in / {meta['llm']['output_tokens']} out tokens)"))
    print(f"Orchestration: {meta['orchestration']} | retrieval: {meta['retrieval_strategy']} | model calls: {state.model_calls} | "
          f"depth: {state.depth} | status: {state.status} | {meta['elapsed_seconds']} s")
    print("\nEvidence:")
    for e in state.retrieved_evidence:
        print(f"  {e.evidence_id} {e.source_document} p{e.pdf_page} `{e.chunk_id}` | {' '.join(e.text.split())[:110]}...")
    print("\nHypotheses:")
    for h in state.all_hypotheses:
        a = state.assessments.get(h.hypothesis_id)
        print(f"  {h.hypothesis_id} {h.relationship_type:9s} cites {h.supporting_evidence_ids} -> "
              + (f"score {a.overall_score} ({'pass' if a.hard_constraint_pass else 'HARD FAIL'})"
                 f"{f' [{a.evidence_support_label}]' if a.evidence_support_label else ''}" if a else "not assessed"))
    print("\nPruning:")
    for p in state.pruning_log:
        print(f"  d{p['depth']} {p['hypothesis_id']}: {p['action']} - {p['reason']}")
    r = state.comparative_review
    print(f"\nComparative review: {r.status} | reviewed {r.reviewed_hypothesis_ids} | preferred {r.preferred_hypothesis_id} | "
          f"near tie (Python/reviewer) {r.deterministic_near_tie}/{r.near_tie} | calls {state.comparative_model_call_count}")
    if r.comparative_reasoning_summary:
        print(f"  {r.comparative_reasoning_summary}")
    d = state.decision
    print(f"\nDECISION: {d.decision} | {d.selected_relationship_type} | score {d.critic_score} | evidence {d.supporting_evidence_ids}")
    print(f"  {d.decision_summary}")
    print(f"\nTrace: {meta['trace_json']}\n       {meta['trace_md']}")


if __name__ == "__main__":
    main()
