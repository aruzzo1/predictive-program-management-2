"""Critic scoring weights (Capstone Checkpoint 4.1) and the deterministic weighted total."""

from __future__ import annotations

WEIGHTS = {
    "documentary_evidence_score": 0.30,     # documentary evidence quality and traceability
    "engineering_consistency_score": 0.30,  # engineering consistency and hard-constraint compliance
    "model_consistency_score": 0.20,        # consistency with the existing program/dependency model
    "predictive_usefulness_score": 0.20,    # usefulness for downstream predictive modeling
}
NEUTRAL_MODEL_CONSISTENCY = 50.0  # no DSM exists yet, so this criterion is scored neutrally


def weighted_score(documentary: float, engineering: float, model: float, predictive: float) -> float:
    total = (WEIGHTS["documentary_evidence_score"] * documentary + WEIGHTS["engineering_consistency_score"] * engineering
             + WEIGHTS["model_consistency_score"] * model + WEIGHTS["predictive_usefulness_score"] * predictive)
    return round(total, 2)
