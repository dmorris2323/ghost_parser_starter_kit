"""
training_curve_engine.py

Computes training curve metrics from sessions:
- AGI (0-100 proxy)
- improvement_slope (trend over last N sessions)
- difficulty_weighted_average
- volatility_index (score variability)

Rules:
- Only GREEN sessions count toward AGI + curve (gate enforced).
- No circular imports. This module imports ONLY session store + policy.

Writes:
- src/docs/training/training_curve_latest.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from training_session_store import load_sessions
from training_policy import counts_toward_agi, normalize_difficulty


OUT_PATH = Path("src") / "docs" / "training" / "training_curve_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


DIFF_WEIGHT = {
    "BEGINNER": 1.00,
    "INTERMEDIATE": 1.10,
    "ADVANCED": 1.20,
    "ADVERSARIAL": 1.35,
}


def _green_sessions(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for s in sessions:
        if counts_toward_agi(gate_status=str(s.get("gate_status", "UNKNOWN"))):
            out.append(s)
    return out


def _compute_slope(scores: List[float]) -> float:
    """
    Simple slope over index: slope of best-fit line for points (i, score_i).
    No numpy dependency.
    """
    n = len(scores)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(scores) / n
    num = sum((xs[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
    den = sum((xs[i] - x_mean) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den


def _volatility(scores: List[float]) -> float:
    n = len(scores)
    if n < 2:
        return 0.0
    mean = sum(scores) / n
    var = sum((s - mean) ** 2 for s in scores) / (n - 1)
    return var ** 0.5


def compute_training_curve(*, last_n: int = 20) -> Dict[str, Any]:
    all_sessions = load_sessions()
    green = _green_sessions(all_sessions)

    # Use most recent last_n GREEN sessions
    green_sorted = sorted(green, key=lambda x: str(x.get("created_at", "")))
    green_recent = green_sorted[-last_n:] if last_n > 0 else green_sorted

    scores = [_coerce_float(s.get("score", 0.0), 0.0) for s in green_recent]
    diffs = [normalize_difficulty(str(s.get("difficulty", "BEGINNER"))) for s in green_recent]

    if not scores:
        result = {
            "generated_at": _utc_now_iso(),
            "total_sessions": len(all_sessions),
            "counted_green_sessions": 0,
            "AGI": 0.0,
            "improvement_slope": 0.0,
            "difficulty_weighted_average": 0.0,
            "volatility_index": 0.0,
        }
        _write_json(OUT_PATH, result)
        return result

    # AGI: average score of GREEN sessions (bounded)
    agi = max(0.0, min(100.0, sum(scores) / len(scores)))

    # Slope: trend over recent scores
    slope = _compute_slope(scores)

    # Difficulty-weighted avg
    weighted_sum = 0.0
    weight_total = 0.0
    for sc, d in zip(scores, diffs):
        w = DIFF_WEIGHT.get(d, 1.0)
        weighted_sum += sc * w
        weight_total += w
    dwa = weighted_sum / weight_total if weight_total else agi
    dwa = max(0.0, min(100.0, dwa))

    vol = _volatility(scores)

    result = {
        "generated_at": _utc_now_iso(),
        "total_sessions": len(all_sessions),
        "counted_green_sessions": len(scores),
        "AGI": round(agi, 3),
        "improvement_slope": round(slope, 3),
        "difficulty_weighted_average": round(dwa, 3),
        "volatility_index": round(vol, 3),
    }
    _write_json(OUT_PATH, result)
    return result


def write_training_curve_latest() -> str:
    curve = compute_training_curve()
    return str(OUT_PATH)


if __name__ == "__main__":
    curve = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {OUT_PATH}")
    print(f"  Total sessions: {curve['total_sessions']}")
    print(f"  Counted GREEN sessions: {curve['counted_green_sessions']}")
    print(f"  AGI: {curve['AGI']}")
    print(f"  Improvement slope: {curve['improvement_slope']}")
    print(f"  Difficulty-weighted avg: {curve['difficulty_weighted_average']}")
    print(f"  Volatility index: {curve['volatility_index']}")

