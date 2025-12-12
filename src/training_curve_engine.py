# src/training_curve_engine.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from difficulty_scaling_engine import get_profile, normalize_difficulty
from training_session_store import load_sessions, training_dir


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _linear_slope(y: List[float]) -> float:
    """
    Simple slope vs index using least squares.
    """
    n = len(y)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(y) / n
    num = sum((xs[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    den = sum((xs[i] - x_mean) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den


def _stdev(vals: List[float]) -> float:
    n = len(vals)
    if n < 2:
        return 0.0
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    return var ** 0.5


def _difficulty_weighted_average(scores: List[float], diffs: List[str]) -> float:
    if not scores or not diffs or len(scores) != len(diffs):
        return 0.0
    num = 0.0
    den = 0.0
    for s, d in zip(scores, diffs):
        prof = get_profile(d)
        w = prof.weight_scalar
        num += s * w
        den += w
    return (num / den) if den > 0 else 0.0


def compute_training_curve(max_sessions: int = 50, only_gated: bool = False) -> Dict[str, Any]:
    sessions = load_sessions()

    # Filter
    usable: List[Dict[str, Any]] = []
    for s in sessions:
        if only_gated and s.get("gate_passed") is not True:
            continue
        usable.append(s)

    usable = usable[-max_sessions:] if max_sessions > 0 else usable

    scores: List[float] = []
    diffs: List[str] = []
    for s in usable:
        scores.append(_safe_float(s.get("final_score"), 0.0))
        diffs.append(normalize_difficulty(s.get("difficulty", "INTERMEDIATE")))

    agi = sum(scores) / len(scores) if scores else 0.0
    slope = _linear_slope(scores)
    volatility = _stdev(scores)
    dwa = _difficulty_weighted_average(scores, diffs)

    curve = {
        "version": 2,
        "generated_at": _utc_now_iso(),
        "total_sessions": len(sessions),
        "used_sessions": len(usable),
        "AGI": round(agi, 1),
        "improvement_slope": round(slope, 2),
        "volatility_index": round(volatility, 3),
        "difficulty_weighted_average": round(dwa, 1),
        "only_gated": bool(only_gated),
    }
    return curve


def write_training_curve_json(max_sessions: int = 50, only_gated: bool = False) -> Tuple[str, Dict[str, Any]]:
    training_dir().mkdir(parents=True, exist_ok=True)
    curve = compute_training_curve(max_sessions=max_sessions, only_gated=only_gated)

    out = training_dir() / "training_curve_latest.json"
    out.write_text(json.dumps(curve, indent=2))
    return str(out), curve


if __name__ == "__main__":
    path, curve = write_training_curve_json()
    print("Training curve written:")
    print(f"  JSON: {path}")
    print(f"  Total sessions: {curve['total_sessions']}")
    print(f"  AGI: {curve['AGI']}")
    print(f"  Improvement slope: {curve['improvement_slope']}")
    print(f"  Difficulty-weighted avg: {curve['difficulty_weighted_average']}")
    print(f"  Volatility index: {curve['volatility_index']}")

