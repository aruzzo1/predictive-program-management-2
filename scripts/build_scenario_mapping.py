"""Build and validate the schedule-to-WTM scenario mapping (outputs/simulation/).

Translates each frozen scenario's workday slip into the dimensionless WTM initial state:
exposed delay = max(0, net slip - total float), normalized by the synthetic 4-workday reference. Reads the frozen
baseline and WTM node order only; no propagation or intervention comparison is run.

Usage:
    python scripts/build_scenario_mapping.py            # build and validate
    python scripts/build_scenario_mapping.py --check    # validate and confirm outputs match a fresh build
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.scenario_mapping import build_mapping, render_outputs, validate_mapping

OUT_DIR = PROJECT_ROOT / "outputs" / "simulation"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mapping = build_mapping(PROJECT_ROOT)
    errors = validate_mapping(mapping)
    texts = render_outputs(mapping)
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

    for s in mapping["scenarios"]:
        state = ", ".join(f"{n}={v:g}" for n, v in s["initial_wtm_state"].items() if v) or "all 0"
        print(f"{s['scenario_id']:<15} exposed {s['exposed_delay_days']:g} d -> {state}")
    if errors:
        print(f"MAPPING VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("MAPPING VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
