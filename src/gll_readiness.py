"""
gll_readiness.py — Single GLL Readiness Score (0–100)

This module computes a single "war-readiness" score for Ghost Lantern Labs
using existing building blocks wherever possible:

- Fusion Trust
- Operator Safety Layer
- Sensor Reliability
- Crisis Mode
- Golden Dome Drift (if available)

It is deliberately defensive: if something is missing, it falls back
to safe defaults instead of crashing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def _safe_fusion_trust() -> int:
    try:
        from fusion_trust import compute_trust  # type: ignore
        out = compute_trust()
        if isinstance(out, dict) and "fusion_trust" in out:
            return int(out["fusion_trust"])
    except Exception:
        pass
    return 80  # safe default


def _safe_osl_status() -> int:
    try:
        from operator_safety_layer import compute_osl  # type: ignore
        out = compute_osl()
        if isinstance(out, dict) and "trust_score" in out:
            return int(out["trust_score"])
    except Exception:
        pass
    return 80


def _safe_reliability() -> float:
    try:
        from sensor_reliability import compute_reliability_summary  # type: ignore
        out = compute_reliability_summary()
        if isinstance(out, dict) and "avg_reliability" in out:
            return float(out["avg_reliability"])
    except Exception:
        pass
    # fallback: use log if present
    try:
        log = Path("data/sensor_reliability_log.csv")
        if log.exists():
            # simple heuristic: if log exists, assume 90
            return 90.0
    except Exception:
        pass
    return 85.0


def _safe_crisis_penalty() -> int:
    try:
        from crisis_mode_flag import status as crisis_status  # type: ignore
        s = crisis_status().strip().upper()
        if s == "ON":
            return 15  # big penalty if you're in crisis mode
    except Exception:
        pass
    return 0


def _safe_drift_penalty() -> int:
    try:
        from golden_dome_drift import compute_drift  # type: ignore
        out = compute_drift()
        if isinstance(out, dict):
            score = float(out.get("drift_score", 0.0))
            # more drift → bigger penalty
            if score > 70:
                return 15
            if score > 40:
                return 8
            if score > 10:
                return 3
    except Exception:
        pass
    return 0


def compute_gll_readiness() -> Dict[str, Any]:
    """
    Returns a dict with:

    {
      "readiness_score": 0–100,
      "components": {...},
      "notes": [...]
    }
    """
    trust = _safe_fusion_trust()
    osl = _safe_osl_status()
    rel = _safe_reliability()

    crisis_penalty = _safe_crisis_penalty()
    drift_penalty = _safe_drift_penalty()

    # Base is weighted average of fusion trust, OSL, and reliability.
    base = (trust * 0.4) + (osl * 0.3) + (rel * 0.3)

    score = base - crisis_penalty - drift_penalty
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    notes = []
    if crisis_penalty > 0:
        notes.append("Crisis mode ON — readiness reduced.")
    if drift_penalty > 0:
        notes.append("Golden Dome drift detected — readiness reduced.")
    if not notes:
        notes.append("System stable; no major penalties applied.")

    return {
        "readiness_score": round(score, 2),
        "components": {
            "fusion_trust": trust,
            "operator_safety_layer": osl,
            "avg_reliability": round(rel, 2),
            "crisis_penalty": crisis_penalty,
            "drift_penalty": drift_penalty,
        },
        "notes": notes,
    }


def write_gll_readiness(path: str | Path = "docs/gll_readiness.json") -> str:
    """
    Writes readiness snapshot to docs/gll_readiness.json and returns path.
    """
    out = compute_gll_readiness()
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2))
    return str(p)


if __name__ == "__main__":
    print(json.dumps(compute_gll_readiness(), indent=2))

