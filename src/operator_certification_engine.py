# src/operator_certification_engine.py
"""
operator_certification_engine.py

Certification streak logic across tracks:
BEGINNER → INTERMEDIATE → ADVANCED → ADVERSARIAL

Definition (simple + stable):
- Only COUNTED sessions are eligible (counted_for_agi == True).
- A streak for a given target difficulty requires consecutive eligible sessions
  at EXACTLY that difficulty with score >= threshold.
- Once certified at a level, operator is considered certified at all lower levels.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from training_session_store import load_sessions


LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"]

# Score thresholds per difficulty (you can tune later).
THRESHOLDS = {
    "BEGINNER": 70,
    "INTERMEDIATE": 75,
    "ADVANCED": 80,
    "ADVERSARIAL": 85,
}

# Required streak length for certification at each level.
STREAK_REQUIRED = {
    "BEGINNER": 3,
    "INTERMEDIATE": 3,
    "ADVANCED": 3,
    "ADVERSARIAL": 3,
}


def _norm_diff(d: Any) -> str:
    return str(d or "").upper().strip()


def _eligible(s: Dict[str, Any]) -> bool:
    return bool(s.get("counted_for_agi", False))


def _score(s: Dict[str, Any]) -> float:
    try:
        return float(s.get("score", 0.0))
    except Exception:
        return 0.0


def _difficulty(s: Dict[str, Any]) -> str:
    return _norm_diff(s.get("difficulty", "INTERMEDIATE"))


def _compute_streak_for_level(sessions: List[Dict[str, Any]], level: str) -> int:
    """
    Count consecutive eligible sessions from the end that meet:
    - difficulty == level
    - score >= THRESHOLDS[level]
    """
    level = _norm_diff(level)
    need = THRESHOLDS.get(level, 75)
    streak = 0

    for s in reversed(sessions):
        if not _eligible(s):
            break
        if _difficulty(s) != level:
            break
        if _score(s) < need:
            break
        streak += 1

    return streak


def highest_certified_track(summary: Dict[str, Any]) -> str:
    """
    Return the highest certified difficulty (or NONE).
    """
    cert = summary.get("certified_level", "NONE")
    return str(cert).upper().strip()


def compute_certification() -> Dict[str, Any]:
    sessions = load_sessions()

    # Streaks per level (from end)
    streaks = {lvl: _compute_streak_for_level(sessions, lvl) for lvl in LEVELS}

    certified = "NONE"
    for lvl in LEVELS:
        if streaks[lvl] >= STREAK_REQUIRED[lvl]:
            certified = lvl

    # Determine next target (one above current certified)
    if certified == "NONE":
        next_target = "BEGINNER"
    else:
        idx = LEVELS.index(certified)
        next_target = LEVELS[idx + 1] if idx + 1 < len(LEVELS) else None

    if next_target:
        next_streak = streaks[next_target]
        next_need = STREAK_REQUIRED[next_target]
        remaining = max(0, next_need - next_streak)
    else:
        next_streak = 0
        next_need = 0
        remaining = 0

    return {
        "certified_level": certified,
        "thresholds": THRESHOLDS,
        "streak_required": STREAK_REQUIRED,
        "streaks": streaks,
        "next_target": next_target,
        "next_target_progress": {
            "current_streak": next_streak,
            "required": next_need,
            "remaining": remaining,
        },
    }

