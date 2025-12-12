# training_curve_engine.py
# Module 7 — Training Curve Engine (SAFE)
#
# Reads training session logs and produces a training curve artifact:
#   - src/docs/training/training_curve_latest.json
#
# Designed to be imported by Streamlit GUIs and CLI without breaking.
# No LLMs. No sensitive data. Synthetic training-only.

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_SESSIONS_PATH = "src/docs/training/training_sessions.json"
DEFAULT_OUT_PATH = "src/docs/training/training_curve_latest.json"


def _now_utc_iso() -> str:
    return datetime.utcnow().isoformat()


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _parse_time_any(s: str) -> Optional[datetime]:
    if not s:
        return None
    # accept ISO strings; tolerate trailing Z
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
    # support either {"sessions":[...]} or raw list
    if isinstance(doc, list):
        return [x for x in doc if isinstance(x, dict)]
    sessions = doc.get("sessions")
    if isinstance(sessions, list):
        return [x for x in sessions if isinstance(x, dict)]
    return []


def _sort_sessions(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def key_fn(s: Dict[str, Any]) -> Tuple[int, str]:
        # prefer explicit timestamps if present
        t = s.get("timestamp") or s.get("graded_at") or s.get("created_at") or s.get("logged_at")
        dt = _parse_time_any(str(t)) if t else None
        return (1 if dt else 0, dt.isoformat() if dt else "")

    # stable: if no timestamps, keep insertion order
    # if timestamps exist, sort by them
    has_any_ts = any(_parse_time_any(str(s.get("timestamp") or s.get("graded_at") or "")) for s in sessions)
    if not has_any_ts:
        return sessions
    # sort by parsed dt, fallback to original ordering for ties
    decorated = []
    for i, s in enumerate(sessions):
        t = s.get("timestamp") or s.get("graded_at") or s.get("created_at") or s.get("logged_at")
        dt = _parse_time_any(str(t)) if t else None
        decorated.append((dt or datetime.min, i, s))
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
    # consecutive scores from the end that meet/exceed threshold
    n = 0
    for s in reversed(scores):
        if s >= threshold:
            n += 1
        else:
            break
    return n


def _recommend_level(avg_recent: float, streak_len: int) -> str:
    # conservative promotion rules
    if avg_recent >= 90 and streak_len >= 3:
        return "PROMOTE_ONE_TIER"
    if avg_recent >= 80 and streak_len >= 2:
        return "HOLD_STEADY"
    if avg_recent < 65:
        return "DROP_DIFFICULTY_OR_REP_FOUNDATIONS"
    return "HOLD_STEADY"


def compute_training_curve(
    sessions_path: str = DEFAULT_SESSIONS_PATH,
    out_path: str = DEFAULT_OUT_PATH,
    window: int = 5,
) -> Dict[str, Any]:
    """
    Reads sessions and writes training_curve_latest.json.
    Returns the curve payload for direct GUI use.
    """
    doc = _load_sessions(sessions_path)
    sessions = _sort_sessions(_extract_sessions(doc))

    # extract key fields
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
    ma = _moving_average(scores, window=window) if scores else []

    # basic stats
    total = len(scores)
    avg = round(sum(scores) / total, 2) if total else 0.0
    avg_recent = round(sum(scores[-window:]) / min(window, total), 2) if total else 0.0
    best = round(max(scores), 2) if total else 0.0
    worst = round(min(scores), 2) if total else 0.0

    # streak thresholds (schoolhouse style)
    streak_80 = _streak(scores, 80.0) if total else 0
    streak_90 = _streak(scores, 90.0) if total else 0

    recommendation = _recommend_level(avg_recent, streak_90)

    payload = {
        "curve_version": 1,
        "generated_at": _now_utc_iso(),
        "sessions_path": sessions_path,
        "window": window,
        "summary": {
            "total_sessions": total,
            "avg_score": avg,
            "avg_recent": avg_recent,
            "best": best,
            "worst": worst,
            "streak_80": streak_80,
            "streak_90": streak_90,
            "recommendation": recommendation,
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
    """
    Convenience wrapper for CLI.
    """
    payload = compute_training_curve()
    return {"json_path": DEFAULT_OUT_PATH, "total_sessions": str(payload["summary"]["total_sessions"])}


if __name__ == "__main__":
    result = write_training_curve()
    print("Training curve written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  Total sessions: {result['total_sessions']}")

