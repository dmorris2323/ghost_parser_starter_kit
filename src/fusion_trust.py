"""
fusion_trust.py — Computes Global Fusion Trust Score for GLL
------------------------------------------------------------
Outputs a dict:

{
  "fusion_trust": <0-100>,
  "factors": {
      "outliers": int,
      "drift": {...},
      "reliability": {...},
      "crisis_mode": "ON"/"OFF"
  }
}
"""

import json
from pathlib import Path
from reliability_trend import compute_trend
from golden_dome_drift import compute_drift


def _load_crisis_mode() -> str:
    """
    Reads crisis mode flag if present.
    Default: 'OFF'
    """
    # We used data/crisis_mode.txt earlier
    path = Path("data/crisis_mode.txt")
    if not path.exists():
        return "OFF"
    try:
        return path.read_text().strip() or "OFF"
    except Exception:
        return "OFF"


def compute_trust() -> dict:
    """
    Compute a Fusion Trust Score based primarily on:
      - avg sensor reliability
      - drift score
      - crisis mode
    """

    # --- Reliability trend ---
    rel = compute_trend()
    if isinstance(rel, dict):
        avg_rel = float(rel.get("avg_reliability", 90.0))
    else:
        avg_rel = 90.0

    # --- Drift data ---
    drift = compute_drift()
    drift_score = float(drift.get("drift_score", 0.0))

    # --- Crisis flag ---
    crisis = _load_crisis_mode()

    # --- Basic formula: reliability minus drift penalty ---
    base = avg_rel - (drift_score * 3.0)

    # Crisis mode penalty
    if crisis == "ON":
        base -= 10.0

    # Clamp to 0–100
    trust_value = int(max(0, min(100, round(base))))

    return {
        "fusion_trust": trust_value,
        "factors": {
            "outliers": 0,      # reserved for future outlier logic
            "drift": drift,
            "reliability": rel,
            "crisis_mode": crisis,
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute_trust(), indent=2))

