"""Run the deterministic trajectory and intervention comparison (outputs/simulation/).

Four cases from the common DISTURBANCE_1 (D4 = 1.0) on the frozen WTM, t0..t12: NO ACTION, INTERVENTION_1
(software recovery), INTERVENTION_2 (cumulative D6 absorption, capacity 1.0) and INTERVENTION_3 (D8 split
40 / 60). Facts only; no composite score. PNG copy via an already-installed headless browser, if found.

Usage:
    python scripts/build_trajectory_simulation.py            # run, validate and write outputs
    python scripts/build_trajectory_simulation.py --no-png   # skip the PNG copy
    python scripts/build_trajectory_simulation.py --check    # validate and confirm outputs match a fresh run
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.dsm_visualization import find_browser, rasterize_svg
from ppm_agent.tools.trajectory_simulation import render_text_outputs, run, validate

OUT_DIR = PROJECT_ROOT / "outputs" / "simulation"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-png", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    res = run(PROJECT_ROOT)
    errors = validate(res, PROJECT_ROOT)
    texts = render_text_outputs(res)
    if args.check:
        for name, text in texts.items():
            path = OUT_DIR / name
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(f"{path.relative_to(PROJECT_ROOT)} missing or differs from a fresh run")
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, text in texts.items():
            (OUT_DIR / name).write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {(OUT_DIR / name).relative_to(PROJECT_ROOT)}")
        browser = find_browser()
        if args.no_png or not browser:
            print("PNG copy skipped" + ("" if args.no_png else " (no headless browser found)"))
        else:
            png = OUT_DIR / "trajectory_comparison.png"
            ok = rasterize_svg(OUT_DIR / "trajectory_comparison.svg", png, browser)
            print(f"{'wrote' if ok else 'FAILED'} {png.relative_to(PROJECT_ROOT)}")
            if not ok:
                errors.append("could not rasterize trajectory_comparison.svg")

    for c in res["cases"]:
        m = c["metrics"]
        print(f"{c['case_id']} peak {m['peak_total']:.4f} | cumulative {m['cumulative_total']:.4f} | "
              f"cum D6 {m['cumulative_D6']:.4f} | cum D8 {m['cumulative_D8']:.4f}")
    if errors:
        print(f"SIMULATION VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("SIMULATION VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
