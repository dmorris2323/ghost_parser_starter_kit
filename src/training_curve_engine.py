# src/training_curve_engine.py
"""
training_curve_engine.py

Computes training curve metrics from session store.

Policy:
- Only sessions that are "counted_for_agi" contribute to AGI/slope/volatility.

Also writes operator certification summary into the curve payload.

Outputs:
- src/docs/training/training_curve_latest.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from training_session_store import load_sessions
from operator_certification_engine import compute_certification


OUT_PATH = Path("src") / "docs" / "training" / "training_curve_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _as_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _is_counted(session: Dict[str, Any]) -> bool:
    if "counted_for_agi" in session:
        return bool(session.get("counted_for_agi"))
    pre = str(session.get("gate_pre_status", "UNKNOWN")).upper().strip()
    post = str(session.get("gate_post_status", "UNKNOWN")).upper().strip()
    return (pre in {"GREEN", "PASS"}) and (post in {"GREEN", "PASS"})


def _difficulty_weight(d: str) -> float:
    d = str(d or "").upper().strip()
    return {
        "BEGINNER": 0.85,
        "INTERMEDIATE": 1.00,
        "ADVANCED": 1.15,
        "ADVERSARIAL": 1.30,
    }.get(d, 1.00)


def _stddev(vals: List[float]) -> float:
    n = len(vals)
    if n <= 1:
        return 0.0
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    return var ** 0.5


def _slope(vals: List[float]) -> float:
    n = len(vals)
    if n <= 1:
        return 0.0
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(vals) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, vals))
    den = sum((x - x_mean) ** 2 for x in xs)
    return 0.0 if den == 0 else (num / den)


def compute_training_curve() -> Dict[str, Any]:
    sessions = load_sessions()

    counted = [s for s in sessions if isinstance(s, dict) and _is_counted(s)]
    scores = [_as_float(s.get("score", 0.0), 0.0) for s in counted]
    difficulties = [str(s.get("difficulty", "INTERMEDIATE")).upper().strip() for s in counted]

    certification = compute_certification()

    if not counted:
        curve = {
            "generated_at": _utc_now_iso(),
            "total_sessions": len(sessions),
            "counted_sessions": 0,
            "AGI": 0.0,
            "improvement_slope": 0.0,
            "difficulty_weighted_average": 0.0,
            "volatility_index": 0.0,
            "certification": certification,
        }
        _write_json(OUT_PATH, curve)
        return curve

    agi = sum(scores) / len(scores)
    weights = [_difficulty_weight(d) for d in difficulties]
    denom = sum(weights) if sum(weights) else 1.0
    dwa = sum(s * w for s, w in zip(scores, weights)) / denom
    slope = _slope(scores)
    vol = _stddev(scores)

    curve = {
        "generated_at": _utc_now_iso(),
        "total_sessions": len(sessions),
        "counted_sessions": len(counted),
        "AGI": round(agi, 3),
        "improvement_slope": round(slope, 3),
        "difficulty_weighted_average": round(dwa, 3),
        "volatility_index": round(vol, 3),
        "certification": certification,
    }

    _write_json(OUT_PATH, curve)
    return curve


if __name__ == "__main__":
    curve = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {OUT_PATH}")
    print(f"  Total sessions: {curve.get('total_sessions')}")
    print(f"  Counted sessions: {curve.get('counted_sessions')}")
    print(f"  AGI: {curve.get('AGI')}")
    print(f"  Improvement slope: {curve.get('improvement_slope')}")
    print(f"  Difficulty-weighted avg: {curve.get('difficulty_weighted_average')}")
    print(f"  Volatility index: {curve.get('volatility_index')}")
    cert = (curve.get("certification") or {}).get("certified_level")
    print(f"  Certified: {cert}")

