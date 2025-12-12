from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from difficulty_scaling_engine import difficulty_weight
from training_session_store import load_sessions, training_dir


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def _stdev(vals: List[float]) -> float:
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    return var ** 0.5


def _linear_slope(points: List[Tuple[float, float]]) -> float:
    """
    Simple least-squares slope for (x, y).
    """
    n = len(points)
    if n < 2:
        return 0.0
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
    den = sum((xs[i] - x_mean) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den


def compute_training_curve() -> Dict[str, Any]:
    sessions = load_sessions()

    # Only sessions marked counted=True contribute to AGI math.
    counted = [s for s in sessions if bool(s.get("counted", True))]

    scores = [_safe_float(s.get("score", 0.0)) for s in counted]
    diffs = [str(s.get("difficulty", "INTERMEDIATE")).upper() for s in counted]

    # Difficulty-weighted average
    if scores:
        weights = [difficulty_weight(d) for d in diffs]
        denom = sum(weights) if sum(weights) != 0 else 1.0
        dwa = sum(scores[i] * weights[i] for i in range(len(scores))) / denom
    else:
        dwa = 0.0

    # AGI: keep it simple and explainable: difficulty-weighted average clipped to 0-100
    agi = max(0.0, min(100.0, dwa))

    # Improvement slope: slope over session index vs score
    points = [(float(i + 1), _safe_float(counted[i].get("score", 0.0))) for i in range(len(counted))]
    slope = _linear_slope(points)

    # Volatility: standard deviation of scores
    vol = _stdev(scores)

    curve = {
        "generated_at": _utc_now_iso(),
        "sessions_total": len(sessions),
        "sessions_counted": len(counted),
        "AGI": round(float(agi), 2),
        "improvement_slope": round(float(slope), 3),
        "difficulty_weighted_average": round(float(dwa), 2),
        "volatility_index": round(float(vol), 3),
    }

    # Write latest curve file for GUI tiles/command center
    out_dir = training_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "training_curve_latest.json"
    out_path.write_text(json.dumps(curve, indent=2))

    return curve


def main() -> None:
    curve = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: src/docs/training/training_curve_latest.json")
    print(f"  Total sessions: {curve['sessions_total']}")
    print(f"  Counted sessions: {curve['sessions_counted']}")
    print(f"  AGI: {curve['AGI']}")
    print(f"  Improvement slope: {curve['improvement_slope']}")
    print(f"  Difficulty-weighted avg: {curve['difficulty_weighted_average']}")
    print(f"  Volatility index: {curve['volatility_index']}")


if __name__ == "__main__":
    main()

