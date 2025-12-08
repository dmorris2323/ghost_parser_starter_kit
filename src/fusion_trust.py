"""
fusion_trust.py

Computes a single "fusion trust" score for Ghost Lantern Labs.

Design:
- Pulls reliability info (if available)
- Checks crisis mode
- Looks for Golden Dome drift status
- Falls back to safe defaults if anything is missing

This is engineered to NEVER crash. If anything fails,
it returns a safe, bounded trust score with an explanation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _load_reliability() -> Dict[str, Any]:
    """
    Try to load sensor reliability from sensor_reliability.py.
    If that fails, return a safe default.
    """
    try:
        from sensor_reliability import compute_reliability_all  # type: ignore
        data = compute_reliability_all()
        if not isinstance(data, dict):
            raise ValueError("compute_reliability_all did not return dict")
        return data
    except Exception:
        # Safe default
        return {
            "sensors": {"global": 100.0},
            "avg_reliability": 95.0,
        }


def _load_crisis_mode() -> str:
    """
    Try to read crisis mode flag. If missing, return 'OFF' as safe default.
    """
    try:
        from crisis_mode_flag import status as crisis_status  # type: ignore
        state = crisis_status()
        if not isinstance(state, str):
            return "UNKNOWN"
        return state
    except Exception:
        return "OFF"


def _load_drift() -> Dict[str, Any]:
    """
    Try to read Golden Dome status from docs/golden_dome_status.txt.
    If missing or corrupt, return a descriptive stub.
    """
    status_file = Path("docs/golden_dome_status.txt")
    if not status_file.exists():
        return {
            "status": "no_data",
            "message": "docs/golden_dome_status.txt not found",
            "drift_score": 0,
        }

    try:
        raw = status_file.read_text().strip()
        if not raw:
            raise ValueError("empty status file")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("non-dict JSON")
        # Ensure a drift_score key exists
        data.setdefault("drift_score", 0)
        return data
    except Exception:
        return {
            "status": "corrupted",
            "message": "could not parse golden_dome_status.txt",
            "drift_score": 0,
        }


def compute_trust() -> Dict[str, Any]:
    """
    Main public function.

    Returns a dict like:
    {
      "fusion_trust": 87,
      "factors": {
        "outliers": 0,
        "drift": {...},
        "reliability": {...},
        "crisis_mode": "OFF",
      }
    }
    """
    reliability = _load_reliability()
    crisis = _load_crisis_mode()
    drift = _load_drift()

    avg_rel = float(reliability.get("avg_reliability", 90.0))

    # Penalties
    crisis_penalty = 20 if crisis == "ON" else 0
    drift_status = drift.get("status", "no_data")
    drift_penalty = 10 if drift_status in {"drifting", "unstable"} else 0

    raw_trust = avg_rel - crisis_penalty - drift_penalty
    trust = max(0, min(100, round(raw_trust)))

    return {
        "fusion_trust": trust,
        "factors": {
            "outliers": 0,  # placeholder for future anomaly stats
            "drift": drift,
            "reliability": reliability,
            "crisis_mode": crisis,
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute_trust(), indent=2))

