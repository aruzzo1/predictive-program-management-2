"""Build and validate the node-level DSM from the frozen synthetic baseline (outputs/dsm/).

Deterministic: reads data/synthetic/, validates it, derives the binary and weighted DSM in Python (no model
calls), validates the matrices and writes the registries, matrices, provenance and summary.

Usage:
    python scripts/build_dsm.py            # build, validate and write outputs/dsm/
    python scripts/build_dsm.py --check    # validate and confirm outputs/dsm/ matches a fresh build
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.synthetic.validation import load_dataset, validate_dataset
from ppm_agent.tools.dsm_tools import build_dsm, render_outputs, validate_dsm, validate_structure, write_outputs

SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"
DSM_DIR = PROJECT_ROOT / "outputs" / "dsm"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate and compare with the existing outputs")
    args = parser.parse_args()

    ds = load_dataset(SYNTHETIC_DIR)
    baseline_errors = validate_dataset(ds)
    if baseline_errors:
        print(f"synthetic baseline invalid ({len(baseline_errors)} errors); DSM not built")
        return 1

    dsm = build_dsm(ds)
    errors = validate_dsm(dsm) + validate_structure(dsm)
    texts = render_outputs(dsm, SYNTHETIC_DIR)
    if args.check:
        for name, text in texts.items():
            path = DSM_DIR / name
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(f"{path.relative_to(PROJECT_ROOT)} missing or differs from a fresh build")
    else:
        for path in write_outputs(texts, DSM_DIR):
            print(f"wrote {path.relative_to(PROJECT_ROOT)}")

    print(f"nodes {len(dsm['node_ids'])} | nonzero entries {len(dsm['cells'])} | "
          f"coupled blocks {dsm['coupled_blocks']}")
    if errors:
        print(f"DSM VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("DSM VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
