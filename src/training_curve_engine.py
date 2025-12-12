# training_curve_engine.py
# Module 7 — Training Curve Engine (SAFE)
#
# Produces:
#   - src/docs/training/training_curve_latest.json
#
# Backward compatibility for GUIs:
#   - Top-level "AGI" (0–100)
#   - Top-level "improvement_slope"
#   - Top-level "improvement_slope_window"
#   - Top-level "difficulty_weighted_average"
#   - Top-level "volatility_index"
#   - Top-level "volatility_window"
#
# Synthetic training-only. No sensitive inputs.

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_SESSIONS_PATH = "src/docs/training/training_sessions.json"
DEFAULT_OUT_PATH = "src/docs/training/training_curve_latest.json"


DIFFICULTY_WEIGHTS = {
    "CADET": 0.90,
    "BEGINNER": 0.90,
    "ANALYST": 1.00,
    "MODERATE": 1.00,
    "SENIOR": 1.10,
    "ADVANCED": 1.10,
    "EXPERT": 1.20,
    "HARD": 1.20,
    "UNKNOWN": 1.00,
}


def _now_utc_iso() -> str:
    # Keep naive UTC isoformat for compatibility; warning is harmless.
    return datetime.utcnow().isoformat()


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _parse_time_any(s: str) -> Optional[datetime]:
    if not s:
        return None
    s = s.replace("Z", "")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _load_sessions(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"schema": 1, "generated_at": _now_utc_iso(), "sessions": []}
    with open(p, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return {"schema": 1, "generated_at": _now_utc_iso(), "sessions": []}


def _extract_sessions(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(doc, list):
        return [x for x in doc if isinstance(x, dict)]
    sessions = doc.get("sessions")
    if isinstance(sessions, list):
        return [x for x in sessions if isinstance(x, dict)]
    return []


def _sort_sessions(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # If timestamps exist, sort; else preserve insertion order.
    decorated = []
    has_any_ts = False
    for i, s in enumerate(sessions):
        t = s.get("timestamp") or s.get("graded_at") or s.get("created_at") or s.get("logged_at")
        dt = _parse_time_any(str(t)) if t else None
        if dt:
            has_any_ts = True
        decorated.append((dt or datetime.min, i, s))

    if not has_any_ts:
        return sessions

    decorated.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in decorated]


def _moving_average(values: List[float], window: int) -> List[float]:
    if window <= 1:
        return values[:]
    out = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        seg = values[start : i + 1]
        out.append(sum(seg) / max(1, len(seg)))
    return out


def _streak(scores: List[float], threshold: float) -> int:
    n = 0
    for s in reversed(scores):
        if s >= threshold:
            n += 1
        else:
            break
    return n


def _recommend_level(avg_recent: float, streak_90: int) -> str:
    if avg_recent >= 90 and streak_90 >= 3:
        return "PROMOTE_ONE_TIER"
    if avg_recent >= 80 and streak_90 >= 2:
        return "HOLD_STEADY"
    if avg_recent < 65:
        return "DROP_DIFFICULTY_OR_REP_FOUNDATIONS"
    return "HOLD_STEADY"


def _compute_agi(avg_recent: float, avg_score: float, total_sessions: int) -> float:
    reps_bonus = min(5.0, total_sessions * 0.25)  # max +5
    agi = (0.7 * avg_recent) + (0.3 * avg_score) + reps_bonus
    return max(0.0, min(100.0, agi))


def _compute_improvement_slope(scores: List[float], slope_window: int) -> float:
    """
    Linear slope using x=1..n over last slope_window sessions.
    Returns delta(score)/session (positive = improving).
    """
    if not scores:
        return 0.0
    w = max(2, int(slope_window))
    seg = scores[-w:] if len(scores) >= w else scores[:]
    n = len(seg)
    if n < 2:
        return 0.0

    xs = list(range(1, n + 1))
    x_mean = sum(xs) / n
    y_mean = sum(seg) / n

    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, seg))
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den


def _difficulty_weighted_average(points: List[Dict[str, Any]]) -> float:
    if not points:
        return 0.0
    num = 0.0
    den = 0.0
    for p in points:
        d = str(p.get("difficulty", "UNKNOWN")).upper()
        w = float(DIFFICULTY_WEIGHTS.get(d, 1.0))
        s = _safe_float(p.get("score"), 0.0)
        num += s * w
        den += w
    if den <= 0:
        return 0.0
    val = num / den
    return max(0.0, min(100.0, val))


def _stddev(values: List[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values) / (n - 1)  # sample stddev
    return math.sqrt(max(0.0, var))


def _volatility_index(scores: List[float], vol_window: int) -> float:
    """
    Volatility index (0–100) from stddev of recent scores.
    Higher = more inconsistent.
    Since scores are 0–100, stddev is naturally bounded; we clamp to 100.
    """
    if not scores:
        return 0.0
    w = max(2, int(vol_window))
    seg = scores[-w:] if len(scores) >= w else scores[:]
    v = _stddev(seg)
    return max(0.0, min(100.0, v))


def compute_training_curve(
    sessions_path: str = DEFAULT_SESSIONS_PATH,
    out_path: str = DEFAULT_OUT_PATH,
    window: int = 5,
) -> Dict[str, Any]:
    doc = _load_sessions(sessions_path)
    sessions = _sort_sessions(_extract_sessions(doc))

    points = []
    for idx, s in enumerate(sessions):
        score = _safe_float(s.get("score"), 0.0)
        difficulty = (s.get("difficulty") or s.get("difficulty_used") or "UNKNOWN").upper()
        scenario_id = s.get("scenario_id") or s.get("id") or f"session_{idx+1}"
        trainee = s.get("trainee") or s.get("operator") or "Ghost"

        t_raw = s.get("timestamp") or s.get("graded_at") or s.get("created_at") or s.get("logged_at")
        dt = _parse_time_any(str(t_raw)) if t_raw else None
        ts = dt.isoformat() if dt else None

        points.append(
            {
                "n": idx + 1,
                "scenario_id": scenario_id,
                "timestamp": ts,
                "difficulty": difficulty,
                "score": round(score, 2),
                "trainee": trainee,
                "source": s.get("source", "unknown"),
            }
        )

    scores = [p["score"] for p in points]
    total = len(scores)

    avg_score = round(sum(scores) / total, 2) if total else 0.0
    avg_recent = round(sum(scores[-window:]) / min(window, total), 2) if total else 0.0
    best = round(max(scores), 2) if total else 0.0
    worst = round(min(scores), 2) if total else 0.0

    ma = _moving_average(scores, window=window) if scores else []
    streak_80 = _streak(scores, 80.0) if total else 0
    streak_90 = _streak(scores, 90.0) if total else 0

    recommendation = _recommend_level(avg_recent, streak_90)
    agi = round(_compute_agi(avg_recent, avg_score, total), 2)

    slope_window = max(2, min(window, total if total else 2))
    improvement_slope = round(_compute_improvement_slope(scores, slope_window), 3)

    dwa = round(_difficulty_weighted_average(points), 2)

    vol_window = max(2, min(window, total if total else 2))
    volatility_index = round(_volatility_index(scores, vol_window), 3)

    payload = {
        "curve_version": 1,
        "generated_at": _now_utc_iso(),
        "sessions_path": sessions_path,
        "window": window,

        # 🔒 GUI back-compat keys:
        "AGI": agi,
        "improvement_slope": improvement_slope,
        "improvement_slope_window": slope_window,
        "difficulty_weighted_average": dwa,
        "volatility_index": volatility_index,
        "volatility_window": vol_window,

        "summary": {
            "total_sessions": total,
            "avg_score": avg_score,
            "avg_recent": avg_recent,
            "best": best,
            "worst": worst,
            "streak_80": streak_80,
            "streak_90": streak_90,
            "recommendation": recommendation,
            "agi_explainer": "AGI = 0.7*avg_recent + 0.3*avg_score + reps_bonus (max +5), clamped 0–100.",
            "slope_explainer": "improvement_slope = linear slope of score over last N sessions (positive = improving).",
            "dwa_explainer": "difficulty_weighted_average = sum(score*weight)/sum(weight), weight by difficulty tier.",
            "vol_explainer": "volatility_index = stddev of recent scores (0–100), higher = less consistent.",
            "difficulty_weights": DIFFICULTY_WEIGHTS,
        },
        "points": points,
        "moving_average": [round(x, 2) for x in ma],
        "safe_notice": "Synthetic training curve derived from your logged sessions; no real telemetry.",
    }

    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w") as f:
        json.dump(payload, f, indent=2)

    return payload


def write_training_curve() -> Dict[str, str]:
    payload = compute_training_curve()
    return {
        "json_path": DEFAULT_OUT_PATH,
        "total_sessions": str(payload["summary"]["total_sessions"]),
        "agi": str(payload.get("AGI", 0)),
        "improvement_slope": str(payload.get("improvement_slope", 0)),
        "difficulty_weighted_average": str(payload.get("difficulty_weighted_average", 0)),
        "volatility_index": str(payload.get("volatility_index", 0)),
    }


if __name__ == "__main__":
    result = write_training_curve()
    print("Training curve written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  Total sessions: {result['total_sessions']}")
    print(f"  AGI: {result['agi']}")
    print(f"  Improvement slope: {result['improvement_slope']}")
    print(f"  Difficulty-weighted avg: {result['difficulty_weighted_average']}")
    print(f"  Volatility index: {result['volatility_index']}")

