# training_curve_engine.py
# Computes a simple training curve + Analyst Growth Index (AGI) from training sessions.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List
from statistics import mean, pstdev

from training_session_store import load_sessions


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


@dataclass
class CurvePoint:
    idx: int
    score: float
    difficulty: str


def compute_training_curve() -> Dict[str, Any]:
    """
    Returns:
      - session_count
      - scores (list)
      - average_score
      - volatility_index (0..1-ish)
      - improvement_slope (rough)
      - agi (0..100)
    """
    store = load_sessions()
    sessions: List[Dict[str, Any]] = store.get("sessions", [])

    if not sessions:
        return {
            "session_count": 0,
            "scores": [],
            "average_score": 0.0,
            "volatility_index": 0.0,
            "improvement_slope": 0.0,
            "agi": 0,
        }

    # Pull scores
    scores = [_safe_float(s.get("score", 0.0), 0.0) for s in sessions]
    avg = mean(scores) if scores else 0.0
    vol = (pstdev(scores) / 100.0) if len(scores) > 1 else 0.0  # normalize-ish

    # Rough slope: compare early vs late average
    split = max(1, len(scores) // 3)
    early = mean(scores[:split])
    late = mean(scores[-split:])
    slope = (late - early) / max(1, len(scores))  # small number

    # AGI: weighted mix of avg + stability + improvement
    stability = _clamp(1.0 - vol, 0.0, 1.0)
    improvement = _clamp((late - early) / 30.0, 0.0, 1.0)

    agi = int(_clamp((avg * 0.65) + (stability * 25.0) + (improvement * 10.0), 0.0, 100.0))

    return {
        "session_count": len(scores),
        "scores": scores,
        "average_score": round(avg, 2),
        "volatility_index": round(vol, 4),
        "improvement_slope": round(slope, 4),
        "agi": agi,
    }

