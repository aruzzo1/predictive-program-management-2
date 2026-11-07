"""Module 6: run the deterministic safety layer over the three preserved real agent episodes (outputs/safety/).

No model calls and no reruns. Reads the preserved traces and frozen artifacts, checks baseline integrity, routes each
episode, writes human-review records (decision PENDING), the safety policy, a multi-metric evaluation (no composite
score), a summary and a flow diagram (PNG copy via an already-installed headless browser, if found).

Usage:
    python scripts/build_safety_evaluation.py            # build
    python scripts/build_safety_evaluation.py --no-png   # skip the PNG copy
    python scripts/build_safety_evaluation.py --check    # confirm outputs/safety/ matches a fresh build
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.safety.reporting import render_outputs
from ppm_agent.safety.safety_guardrails import (
    check_baseline_integrity,
    evaluate_preserved_episodes,
    evaluation,
    fault_injection_matrix,
    policy_document,
)
from ppm_agent.tools.dsm_visualization import find_browser, rasterize_svg

OUT_DIR = PROJECT_ROOT / "outputs" / "safety"


def build() -> tuple[dict[str, str], dict, list]:
    integrity = check_baseline_integrity(PROJECT_ROOT)
    inputs, records = evaluate_preserved_episodes(PROJECT_ROOT)
    ev = evaluation(inputs, records, fault_injection_matrix(PROJECT_ROOT), integrity)
    return render_outputs(policy_document(), ev, records), ev, records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-png", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    texts, ev, records = build()
    errors = []
    if args.check:
        for name, text in texts.items():
            path = OUT_DIR / name
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(f"{path.relative_to(PROJECT_ROOT)} missing or differs from a fresh build")
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, text in texts.items():
            (OUT_DIR / name).write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {(OUT_DIR / name).relative_to(PROJECT_ROOT)}")
        browser = find_browser()
        if args.no_png or not browser:
            print("PNG copy skipped" + ("" if args.no_png else " (no headless browser found)"))
        elif rasterize_svg(OUT_DIR / "safety_flow.svg", OUT_DIR / "safety_flow.png", browser):
            print("wrote outputs/safety/safety_flow.png")
        else:
            errors.append("could not rasterize safety_flow.svg")

    sm = ev["safety_metrics"]
    for r in records:
        print(f"{r.trace_id}: {r.safety_route} | review {r.review_required} | decision {r.reviewer_decision}")
    print(f"unsafe_downstream_releases {sm['unsafe_downstream_releases']} | blocked {sm['episodes_blocked']}/"
          f"{sm['total_agent_episodes_evaluated']} | baseline violations {len(ev['robustness']['baseline_integrity_violations'])}")
    if sm["unsafe_downstream_releases"] or ev["robustness"]["baseline_integrity_violations"]:
        errors.append("unsafe release or baseline integrity violation")
    if errors:
        for e in errors:
            print(f"  - {e}")
        return 1
    print("SAFETY EVALUATION OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
