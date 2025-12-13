"""
training_curve_engine.py

Computes training curve metrics from training sessions.

Counts only sessions where:
  counts_toward_agi == True
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from training_session_store import load_sessions


TRAINING_DIR = Path("docs") / "training"
CURVE_PATH = TRAINING_DIR / "training_curve_latest.json"


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


def _difficulty_weight(diff: str) -> float:
    diff = (diff or "INTERMEDIATE").upper()
    if diff == "BEGINNER":
        return 0.8
    if diff == "ADVERSARIAL":
        return 1.2
    return 1.0


def compute_training_curve() -> Dict[str, Any]:
    sessions = load_sessions()

    counted = [s for s in sessions if isinstance(s, dict) and bool(s.get("counts_toward_agi", False))]

    # If nothing counted yet, return zeros (but stable keys)
    if not counted:
        result = {
            "generated_at": _utc_now_iso(),
            "total_sessions": len(sessions),
            "counted_sessions": 0,
            "AGI": 0.0,
            "improvement_slope": 0.0,
            "difficulty_weighted_average": 0.0,
            "volatility_index": 0.0,
        }
        _write_json(CURVE_PATH, result)
        return result

    scores = [_as_float(s.get("score", 0.0)) for s in counted]
    diffs = [str(s.get("difficulty", "INTERMEDIATE")).upper() for s in counted]

    # AGI proxy: average score (0-100 assumed)
    agi = sum(scores) / max(1, len(scores))

    # improvement slope: last minus first normalized by count
    slope = (scores[-1] - scores[0]) / max(1, (len(scores) - 1))

    # difficulty-weighted average
    weighted_sum = 0.0
    weights_sum = 0.0
    for sc, df in zip(scores, diffs):
        w = _difficulty_weight(df)
        weighted_sum += sc * w
        weights_sum += w
    dwa = weighted_sum / max(1e-9, weights_sum)

    # volatility index: mean absolute change
    if len(scores) == 1:
        vol = 0.0
    else:
        deltas = [abs(scores[i] - scores[i - 1]) for i in range(1, len(scores))]
        vol = sum(deltas) / max(1, len(deltas))

    result = {
        "generated_at": _utc_now_iso(),
        "total_sessions": len(sessions),
        "counted_sessions": len(counted),
        "AGI": round(agi, 2),
        "improvement_slope": round(slope, 2),
        "difficulty_weighted_average": round(dwa, 2),
        "volatility_index": round(vol, 3),
    }

    _write_json(CURVE_PATH, result)
    return result


if __name__ == "__main__":
    r = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {CURVE_PATH}")
    print(f"  Total sessions: {r['total_sessions']}")
    print(f"  Counted sessions: {r['counted_sessions']}")
    print(f"  AGI: {r['AGI']}")
    print(f"  Improvement slope: {r['improvement_slope']}")
    print(f"  Difficulty-weighted avg: {r['difficulty_weighted_average']}")
    print(f"  Volatility index: {r['volatility_index']}")

