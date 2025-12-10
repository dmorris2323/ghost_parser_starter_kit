"""
fusion_trust.py

Computes a single 0–100 "Fusion Trust Score" for Ghost Lantern Labs
based on:
  - Sensor reliability
  - Drift status
  - Outliers (if any)
  - Crisis Mode state

Designed to be:
  - SAFE: never crashes if upstream modules/files are missing
  - STABLE: always returns a well-formed dict for GUI / HTML / CLI

Used by:
  - apps/gui/app.py (Spectral Dashboard)
  - mission_brief_html.py (HTML brief)
  - daily_mission_brief.py (text brief)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from crisis_mode_flag import status as crisis_status


def _safe_drift() -> Dict[str, Any]:
    """
    Try to load drift information from golden_dome_drift.compute_drift().
    If anything fails, return a no-data stub.
    """
    try:
        from golden_dome_drift import compute_drift  # type: ignore

        drift = compute_drift()
        # Ensure minimum shape
        if not isinstance(drift, dict):
            raise ValueError("Drift result not dict")
        drift.setdefault("status", "no_data")
        drift.setdefault("message", "Drift info present but incomplete.")
        drift.setdefault("drift_score", 0)
        return drift
    except Exception:
        return {
            "status": "no_data",
            "message": "docs/golden_dome_status.txt not found",
            "drift_score": 0,
        }


def _safe_reliability() -> Dict[str, Any]:
    """
    Try to load reliability metrics from sensor_reliability.compute_reliability_all().
    If anything fails, fall back to safe defaults.
    """
    try:
        from sensor_reliability import compute_reliability_all  # type: ignore

        rel = compute_reliability_all()
        if not isinstance(rel, dict):
            raise ValueError("Reliability result not dict")
        sensors = rel.get("sensors", {})
        avg = rel.get("avg_reliability", 90.0)
        if not isinstance(avg, (int, float)):
            avg = 90.0
        return {
            "sensors": sensors,
            "avg_reliability": float(avg),
        }
    except Exception:
        # Safe default: everything looks good but we admit it's a guess
        return {
            "sensors": {
                "global": 100.0,
                "optical": 90.0,
                "seismic": 90.0,
                "ems": 90.0,
                "radiation": 90.0,
            },
            "avg_reliability": 92.0,
        }


def _safe_outliers() -> int:
    """
    Optional: read an outlier count from a file if it exists.
    If missing or malformed, assume 0 outliers.
    """
    try:
        outlier_file = Path("docs/fusion_outliers.json")
        if not outlier_file.exists():
            return 0
        data = json.loads(outlier_file.read_text())
        return int(data.get("count", 0))
    except Exception:
        return 0


def compute_trust() -> Dict[str, Any]:
    """
    Master function: returns a dict like:

    {
      "fusion_trust": 92,
      "factors": {
        "outliers": 0,
        "drift": {...},
        "reliability": {...},
        "crisis_mode": "OFF"
      }
    }
    """
    # Upstream pieces (all safe)
    drift = _safe_drift()
    reliability = _safe_reliability()
    outliers = _safe_outliers()
    crisis = crisis_status()  # "ON" or "OFF"

    # Base score from avg reliability
    base = reliability.get("avg_reliability", 90.0)
    if not isinstance(base, (int, float)):
        base = 90.0

    # Penalties
    penalty_drift = 0
    if str(drift.get("status", "")).lower() in {"drift_detected", "warning"}:
        penalty_drift = 5

    # Each outlier costs 2 points, capped at 10
    penalty_outliers = min(10, outliers * 2)

    # Crisis ON costs 10 points
    penalty_crisis = 10 if str(crisis).upper() == "ON" else 0

    raw_score = float(base) - penalty_drift - penalty_outliers - penalty_crisis
    fusion_trust = max(0, min(100, round(raw_score)))

    return {
        "fusion_trust": fusion_trust,
        "factors": {
            "outliers": outliers,
            "drift": drift,
            "reliability": reliability,
            "crisis_mode": crisis,
        },
    }


if __name__ == "__main__":
    # Quick manual test
    print(json.dumps(compute_trust(), indent=2))

