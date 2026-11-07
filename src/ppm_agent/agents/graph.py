"""LangGraph wrapper around the bounded ToT controller.

The graph adds explicit nodes, routing and stop conditions, and nothing else: every node calls the
same ToTController step used by the plain-Python loop, so both orchestrations make the same decisions.

    retrieve_evidence -> generate_hypotheses -> validate_hypotheses -> critic_evaluate -> prune
         prune --(continue: near tie, budget and depth left)--> generate_hypotheses
         prune --(stop)--> decide -> save_trace -> END

``decide`` runs ToTController.decide, which performs the one advisory comparative review of the
survivors before applying the deterministic verdict rule.
"""

from __future__ import annotations

from typing import Callable, TypedDict

from langgraph.graph import END, StateGraph

from ppm_agent.agents.tot import ToTController
from ppm_agent.models import ReasoningState


class GraphState(TypedDict, total=False):
    rs: ReasoningState
    chunk_ids: list[str]
    trace: dict


def build_graph(controller: ToTController, retrieve: Callable[[ReasoningState], list[str]] | None = None,
                save: Callable[[ReasoningState], dict] | None = None):
    """Compile the graph. ``retrieve(state) -> chunk_ids`` attaches evidence; ``save(state) -> paths`` writes the trace."""

    def retrieve_evidence(s: GraphState) -> GraphState:
        rs = s["rs"]
        chunk_ids = s.get("chunk_ids") if rs.retrieved_evidence else retrieve(rs)
        rs.events.append("[graph] retrieve_evidence")
        return {"rs": rs, "chunk_ids": chunk_ids}

    def generate_hypotheses(s: GraphState) -> GraphState:
        controller.generate(s["rs"], s["chunk_ids"])
        s["rs"].events.append(f"[graph] generate_hypotheses (depth {s['rs'].depth})")
        return {"rs": s["rs"]}

    def validate_hypotheses(s: GraphState) -> GraphState:
        controller.validate(s["rs"], s["chunk_ids"])
        return {"rs": s["rs"]}

    def critic_evaluate(s: GraphState) -> GraphState:
        controller.evaluate(s["rs"])
        return {"rs": s["rs"]}

    def prune(s: GraphState) -> GraphState:
        controller.prune(s["rs"])
        return {"rs": s["rs"]}

    def route(s: GraphState) -> str:
        go_on = controller.should_continue(s["rs"])
        s["rs"].events.append(f"[graph] route after prune: {'generate_hypotheses' if go_on else 'decide'} (status {s['rs'].status})")
        return "continue" if go_on else "stop"

    def decide(s: GraphState) -> GraphState:
        controller.decide(s["rs"])
        return {"rs": s["rs"]}

    def save_trace(s: GraphState) -> GraphState:
        return {"trace": save(s["rs"]) if save else {}}

    g = StateGraph(GraphState)
    for name, fn in (("retrieve_evidence", retrieve_evidence), ("generate_hypotheses", generate_hypotheses),
                     ("validate_hypotheses", validate_hypotheses), ("critic_evaluate", critic_evaluate), ("prune", prune),
                     ("decide", decide), ("save_trace", save_trace)):
        g.add_node(name, fn)
    g.set_entry_point("retrieve_evidence")
    g.add_edge("retrieve_evidence", "generate_hypotheses")
    g.add_edge("generate_hypotheses", "validate_hypotheses")
    g.add_edge("validate_hypotheses", "critic_evaluate")
    g.add_edge("critic_evaluate", "prune")
    g.add_conditional_edges("prune", route, {"continue": "generate_hypotheses", "stop": "decide"})
    g.add_edge("decide", "save_trace")
    g.add_edge("save_trace", END)
    return g.compile()


def run_graph(controller: ToTController, state: ReasoningState, chunk_ids: list[str] | None = None,
              retrieve: Callable[[ReasoningState], list[str]] | None = None, save: Callable[[ReasoningState], dict] | None = None):
    """Run the graph; returns (final ReasoningState, trace paths)."""
    out = build_graph(controller, retrieve, save).invoke({"rs": state, "chunk_ids": chunk_ids or []}, {"recursion_limit": 50})
    return out["rs"], out.get("trace", {})
