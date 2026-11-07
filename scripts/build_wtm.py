"""Build the Illustrative Work Transformation / Weighted Propagation Matrix layer (outputs/wtm/).

Reads only the frozen DSM v1.1 outputs, computes the eigenstructure and the normalized D4 disturbance
propagation deterministically (numpy; no model calls), validates, and writes the matrix, eigenvalues,
structural analysis, propagation table, provenance, summary and SVG figures (PNG copies via an
already-installed headless browser, if found). Scenario disturbances and interventions are not run.

Usage:
    python scripts/build_wtm.py            # build and validate
    python scripts/build_wtm.py --no-png   # skip PNG copies
    python scripts/build_wtm.py --check    # validate and confirm outputs/wtm/ matches a fresh build
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.tools.dsm_visualization import find_browser, rasterize_svg
from ppm_agent.tools.wtm_tools import (
    INPUT_FILES,
    SVG_FILES,
    analyse,
    propagation_svg,
    render_text_outputs,
    sha256,
    validate,
    wtm_heatmap_svg,
)

DSM_DIR = PROJECT_ROOT / "outputs" / "dsm"
OUT_DIR = PROJECT_ROOT / "outputs" / "wtm"


def build_texts(res: dict) -> dict[str, str]:
    texts = render_text_outputs(res)
    texts["wtm_heatmap.svg"] = wtm_heatmap_svg(res, DSM_DIR)
    texts["software_disturbance_propagation.svg"] = propagation_svg(res)
    return texts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-png", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    before = {n: sha256(DSM_DIR / n) for n in INPUT_FILES}
    res = analyse(DSM_DIR)
    errors = validate(res, DSM_DIR)
    texts = build_texts(res)
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
            print("PNG copies skipped" + ("" if args.no_png else " (no headless browser found)"))
        else:
            for svg_name in SVG_FILES:
                png = OUT_DIR / svg_name.replace(".svg", ".png")
                ok = rasterize_svg(OUT_DIR / svg_name, png, browser)
                print(f"{'wrote' if ok else 'FAILED'} {png.relative_to(PROJECT_ROOT)}")
                if not ok:
                    errors.append(f"could not rasterize {svg_name}")
    if {n: sha256(DSM_DIR / n) for n in INPUT_FILES} != before:
        errors.append("frozen DSM inputs changed during the build")

    last = res["propagation"][-1]
    print(f"spectral radius {res['spectral_radius']:.4f} ({res['raw_behaviour']}) | coupled blocks {res['coupled_blocks']} | "
          f"D4 run t{last['t']} total {last['total_magnitude']:.4f}")
    if errors:
        print(f"WTM VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("WTM VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
