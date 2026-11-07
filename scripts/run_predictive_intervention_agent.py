"""Run the Predictive Simulation and Intervention Agent (Module 5, Agent 2) once on the frozen comparison.

Interprets outputs/simulation/intervention_comparison.json (plus scenario-mapping and WTM metadata) through one
structured model call in REAL_LLM_MODE, or the rule-based stand-in in MOCK_AGENT_MODE when no provider is
configured (or with --mock). Python supplies and validates every number; the model cites fact ids.

Traces: outputs/agentic_traces/predictive_intervention_agent_<timestamp>.json / .md
Summary (REAL_LLM_MODE only): outputs/evaluation/predictive_intervention_agent_summary_<timestamp>.md
Only a VALIDATED interpretation is usable downstream; every run requires human review.

Usage:
    python scripts/run_predictive_intervention_agent.py           # REAL_LLM_MODE if configured
    python scripts/run_predictive_intervention_agent.py --mock    # force MOCK_AGENT_MODE
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.agents.llm import LLMConfigurationError, detect_llm_client
from ppm_agent.agents.predictive_intervention import run_episode
from ppm_agent.config import PROJECT_ROOT

TRACE_DIR = PROJECT_ROOT / "outputs" / "agentic_traces"
# timestamped so earlier summaries (and their reviewer assessments) are never overwritten
EVAL_PATH = PROJECT_ROOT / "outputs" / "evaluation" / "predictive_intervention_agent_summary_{stamp}.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mock", action="store_true", help="force MOCK_AGENT_MODE (no model call)")
    args = parser.parse_args()

    client = None if args.mock else detect_llm_client()
    print("MOCK_AGENT_MODE (no model call)" if client is None else f"REAL_LLM_MODE, model {client.model}")
    try:
        meta = run_episode(client, PROJECT_ROOT, TRACE_DIR, EVAL_PATH if client is not None else None)
    except LLMConfigurationError as exc:
        print(f"provider configuration error (no trace written): {exc}")
        return 1
    print(f"status {meta['status']} | elapsed {meta['elapsed_seconds']} s | tokens {meta['llm']}")
    print(f"trace {meta['trace_json']}")
    if meta.get("evaluation_summary"):
        print(f"summary {meta['evaluation_summary']}")
    return 0 if meta["status"] != "FAILED" else 1


if __name__ == "__main__":
    sys.exit(main())
