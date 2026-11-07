"""Supervisor agent: architectural placeholder only. Not implemented.

A unified cross-agent supervisor (routing work between the retrieval, evidence / dependency, simulation and
interpretation agents) was proposed in the capstone architecture but was not implemented within the capstone scope.
This module intentionally contains no functionality.

Current coordination:
  - LangGraph orchestrates the Evidence and Dependency reasoning workflow (ppm_agent.agents.graph).
  - The downstream stages (synthetic baseline, DSM, WTM, schedule-to-WTM mapping, trajectory simulation, the
    Predictive Simulation and Intervention Agent and the Module 6 safety layer) are coordinated by deterministic
    scripts and structured artifact handoffs (scripts/, outputs/).

A unified supervisor remains future work.
"""
