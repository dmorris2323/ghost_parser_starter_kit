"""
readiness_score.py — Compute overall GLL mission readiness score (0–100).

Inputs:
  - avg sensor reliability
  - golden dome drift (drift_magnitude)
  - golden dome agreement_score
  - Spectral Owl confidence
  - crisis mode flag

Output:
  {
    "score": float,
    "components": {...}
  }
"""

from __future__ import annotations

from typing import Dict, Any

from sensor_reliability import compute_reliability_all
from golden_dome_drift import compute_drift
from spectral_owl.owl_confidence import compute_confidence
from crisis_mode_flag import status as crisis_status


def compute_readiness_score() -> Dict[str, Any]:
    # Defaults
    avg_rel = 90.0
    total_crit = 0
    total_warn = 0

    try:
        rel = compute_reliability_all()
        if isinstance(rel, dict):
            avg_rel = rel.get("avg_reliability", avg_rel) or avg_rel
            total_crit = rel.get("total_critical", 0) or 0
            total_warn = rel.get("total_warnings", 0) or 0
    except Exception:
        pass

    drift_mag = 0.0
    agreement = 90.0
    try:
        drift = compute_drift()
        if isinstance(drift, dict):
            drift_mag = drift.get("drift_magnitude", 0.0) or 0.0
            agreement = drift.get("agreement_score", agreement) or agreement
    except Exception:
        pass

    # Owl confidence based on those numbers
    conf_sample = {
        "critical_alerts": total_crit,
        "warning_alerts": total_warn,
        "avg_reliability": avg_rel,
    }
    owl_conf = compute_confidence(conf_sample)

    # Crisis mode penalty
    crisis = crisis_status()
    crisis_penalty = 0.0
    if crisis.upper() == "ON":
        crisis_penalty = 15.0

    # Drift penalty (cap drift magnitude used)
    used_drift = min(max(drift_mag, 0.0), 20.0)
    drift_penalty = 0.5 * used_drift

    # Weighted combo
    base = 0.4 * avg_rel + 0.4 * owl_conf + 0.2 * agreement
    score = base - drift_penalty - crisis_penalty

    # Clamp
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 2),
        "components": {
            "avg_reliability": round(avg_rel, 2),
            "owl_confidence": round(owl_conf, 2),
            "agreement_score": round(agreement, 2),
            "drift_magnitude": round(drift_mag, 2),
            "crisis_mode": crisis,
            "drift_penalty": round(drift_penalty, 2),
            "crisis_penalty": round(crisis_penalty, 2),
        },
    }


if __name__ == "__main__":
    out = compute_readiness_score()
    print("=== GLL Mission Readiness Score ===")
    print(out)

