# src/training_curve_engine.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _sessions_path() -> Path:
    return _repo_root() / "src" / "docs" / "training" / "training_sessions.json"


def _curve_path() -> Path:
    p = _repo_root() / "src" / "docs" / "training" / "training_curve_latest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_sessions() -> List[Dict[str, Any]]:
    p = _sessions_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text())
        sessions = raw.get("sessions", [])
        return sessions if isinstance(sessions, list) else []
    except Exception:
        return []


def _linear_slope(points: List[Tuple[float, float]]) -> float:
    # Simple least-squares slope
    if len(points) < 2:
        return 0.0
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    num = sum((x - x_mean) * (y - y_mean) for x, y in points)
    den = sum((x - x_mean) ** 2 for x in xs)
    return float(num / den) if den != 0 else 0.0


def _volatility(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return float(var ** 0.5)


def compute_training_curve() -> Dict[str, Any]:
    sessions = _load_sessions()
    valid = [s for s in sessions if s.get("session_valid") is True]

    # Default empty curve
    curve: Dict[str, Any] = {
        "curve_version": 2,
        "generated_at": _utc_now(),
        "total_sessions": len(sessions),
        "valid_sessions": len(valid),
        "AGI": 0.0,
        "improvement_slope": 0.0,
        "difficulty_weighted_average": 0.0,
        "volatility_index": 0.0,
        "note": "Only valid sessions (SIS+SPS GREEN and Validation PASS/WARN) count toward metrics.",
    }

    if not valid:
        _curve_path().write_text(json.dumps(curve, indent=2))
        return curve

    # Use weighted_score for training performance
    scores = [float(s.get("weighted_score", 0.0)) for s in valid]
    curve["AGI"] = round(sum(scores) / len(scores), 2)

    # Difficulty-weighted average = same as AGI here, but kept explicit for UI tiles
    curve["difficulty_weighted_average"] = curve["AGI"]

    # Improvement slope over time index (1..n)
    pts = [(float(i + 1), scores[i]) for i in range(len(scores))]
    curve["improvement_slope"] = round(_linear_slope(pts), 3)

    # Volatility index = std dev of scores
    curve["volatility_index"] = round(_volatility(scores), 3)

    _curve_path().write_text(json.dumps(curve, indent=2))
    return curve


if __name__ == "__main__":
    c = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {_curve_path()}")
    print(f"  Total sessions: {c['total_sessions']}")
    print(f"  Valid sessions: {c['valid_sessions']}")
    print(f"  AGI: {c['AGI']}")
    print(f"  Improvement slope: {c['improvement_slope']}")
    print(f"  Volatility index: {c['volatility_index']}")

