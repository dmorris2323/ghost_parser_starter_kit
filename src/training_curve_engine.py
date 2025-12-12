# src/training_curve_engine.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import math

from training_session_store import load_sessions
from training_difficulty_engine import normalize_difficulty


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_weighted_grade(session: Dict[str, Any]) -> float:
    # Prefer auto_grade weighted_grade
    ag = session.get("auto_grade") or {}
    if isinstance(ag, dict):
        wg = ag.get("weighted_grade") or {}
        if isinstance(wg, dict) and "weighted_grade" in wg:
            try:
                return float(wg["weighted_grade"])
            except Exception:
                pass
        # Some sessions store grade directly
        if "weighted_grade" in ag:
            try:
                return float(ag["weighted_grade"])
            except Exception:
                pass

    # Fallback: compute from raw_scores crudely
    rs = session.get("raw_scores") or {}
    if isinstance(rs, dict):
        a = float(rs.get("accuracy", 0.0))
        s = float(rs.get("speed", 0.0))
        t = float(rs.get("tradecraft", 0.0))
        a = max(0.0, min(1.0, a))
        s = max(0.0, min(1.0, s))
        t = max(0.0, min(1.0, t))
        return (0.5 * a + 0.2 * s + 0.3 * t) * 100.0

    return 0.0


def compute_training_curve(difficulty_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Reads training sessions and computes:
    - AGI (0-100): mean of counted weighted grades
    - improvement_slope: simple linear slope over session index
    - difficulty_weighted_average: same as AGI for now (placeholder)
    - volatility_index: stdev / 100
    """
    sessions = load_sessions()

    d_filter = normalize_difficulty(difficulty_filter) if difficulty_filter else None

    # Only counted sessions contribute to AGI
    counted: List[Dict[str, Any]] = []
    for s in sessions:
        if not isinstance(s, dict):
            continue
        if not bool(s.get("counted_for_agi", False)):
            continue
        if d_filter and normalize_difficulty(str(s.get("difficulty", ""))) != d_filter:
            continue
        counted.append(s)

    grades = [float(_extract_weighted_grade(s)) for s in counted]
    n = len(grades)

    if n == 0:
        return {
            "curve_version": 3,
            "generated_at": _utc_now(),
            "difficulty_filter": d_filter or "ALL",
            "total_sessions": 0,
            "AGI": 0.0,
            "improvement_slope": 0.0,
            "difficulty_weighted_average": 0.0,
            "volatility_index": 0.0,
        }

    agi = sum(grades) / n

    # Slope on index 1..n
    xs = list(range(1, n + 1))
    x_mean = sum(xs) / n
    y_mean = agi
    # Proper y mean from grades
    y_mean = sum(grades) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, grades))
    den = sum((x - x_mean) ** 2 for x in xs) or 1.0
    slope = num / den

    # Volatility: stddev normalized
    var = sum((g - agi) ** 2 for g in grades) / max(1, n - 1)
    stdev = math.sqrt(var)
    volatility = stdev / 100.0

    return {
        "curve_version": 3,
        "generated_at": _utc_now(),
        "difficulty_filter": d_filter or "ALL",
        "total_sessions": n,
        "AGI": round(agi, 1),
        "improvement_slope": round(slope, 2),
        "difficulty_weighted_average": round(agi, 1),
        "volatility_index": round(volatility, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(compute_training_curve(), indent=2))

