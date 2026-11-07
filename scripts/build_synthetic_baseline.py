"""Build and validate the Evidence-Calibrated Synthetic F-35 Development Baseline v1.0 (data/synthetic/).

Writes the synthetic IMP / IMS, dependency, scenario and provenance files from ppm_agent.synthetic.baseline,
then runs the deterministic validation. Touches nothing else: no corpus, embeddings or vector store.

Usage:
    python scripts/build_synthetic_baseline.py            # write the files, then validate
    python scripts/build_synthetic_baseline.py --check    # validate the existing files only
"""

from __future__ import annotations

import argparse
import sys

from ppm_agent.config import PROJECT_ROOT
from ppm_agent.synthetic.baseline import build_all
from ppm_agent.synthetic.validation import load_dataset, validate_dataset

SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate existing files without rewriting them")
    args = parser.parse_args()

    if not args.check:
        for path in build_all(SYNTHETIC_DIR).values():
            print(f"wrote {path.relative_to(PROJECT_ROOT)}")

    ds = load_dataset(SYNTHETIC_DIR)
    errors = validate_dataset(ds)
    derived = sum(d["data_classification"] == "DERIVED" for d in ds["dependencies"])
    finish = max(int(r["baseline_finish"]) for r in ds["ims"])
    print(f"IMP events {len(ds['imp'])} | IMS activities {len(ds['ims'])} | DSM nodes {len(ds['provenance']['dsm_nodes'])} | "
          f"dependencies {len(ds['dependencies'])} ({derived} DERIVED concepts) | "
          f"scenarios {len(ds['scenarios']['scenarios'])} | baseline finish workday {finish}")
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
