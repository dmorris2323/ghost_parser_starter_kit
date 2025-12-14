"""
operator_certification_engine.py

Operator certification tracks:
BEGINNER → INTERMEDIATE → ADVANCED → ADVERSARIAL

Streak logic:
- BEGINNER cert requires 3 GREEN sessions at BEGINNER with score >= threshold
- INTERMEDIATE requires 3 GREEN sessions at INTERMEDIATE with score >= threshold
- ADVANCED requires 3 GREEN sessions at ADVANCED with score >= threshold
- ADVERSARIAL requires 3 GREEN sessions at ADVERSARIAL with score >= threshold

We evaluate from recent history (most recent first) and compute:
- current certified track (highest achieved)
- streak progress for next track
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple


TRACKS = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"]

DEFAULT_THRESHOLDS = {
    "BEGINNER": 60.0,
    "INTERMEDIATE": 70.0,
    "ADVANCED": 80.0,
    "ADVERSARIAL": 85.0,
}

DEFAULT_STREAK_LEN = 3


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _is_green(session: Dict[str, Any]) -> bool:
    return str(session.get("gate_status", "UNKNOWN")).upper() == "GREEN"


def _difficulty(session: Dict[str, Any]) -> str:
    return str(session.get("difficulty", "BEGINNER")).upper()


def _score(session: Dict[str, Any]) -> float:
    return _coerce_float(session.get("score", 0.0), 0.0)


def highest_certified_track(result: Dict[str, Any]) -> str:
    """
    Helper used by feedback engine.
    Returns a string track name.
    """
    return str(result.get("certified_track", "NONE") or "NONE")


@dataclass
class CertificationResult:
    certified_track: str
    streak_target_track: str
    streak_required: int
    streak_current: int
    thresholds: Dict[str, float]
    note: str


def compute_certification(
    sessions: List[Dict[str, Any]],
    *,
    thresholds: Dict[str, float] | None = None,
    streak_len: int = DEFAULT_STREAK_LEN,
) -> Dict[str, Any]:
    thresholds = dict(thresholds or DEFAULT_THRESHOLDS)

    # sort newest first if timestamps exist (fallback to stable order)
    sessions_sorted = list(reversed(sessions))

    def has_streak(track: str) -> bool:
        needed = streak_len
        count = 0
        for s in sessions_sorted:
            if _difficulty(s) != track:
                continue
            if _is_green(s) and _score(s) >= thresholds.get(track, 0.0):
                count += 1
                if count >= needed:
                    return True
        return False

    certified = "NONE"
    for t in TRACKS:
        if has_streak(t):
            certified = t

    # next target
    if certified == "NONE":
        target = "BEGINNER"
    else:
        idx = TRACKS.index(certified)
        target = TRACKS[min(idx + 1, len(TRACKS) - 1)]

    # current streak progress for target
    current = 0
    for s in sessions_sorted:
        if _difficulty(s) != target:
            continue
        if _is_green(s) and _score(s) >= thresholds.get(target, 0.0):
            current += 1

    note = "Keep sessions GREEN and meet score thresholds to progress."
    if certified == "ADVERSARIAL":
        target = "ADVERSARIAL"
        current = streak_len
        note = "Top track achieved. Maintain proficiency."

    result = CertificationResult(
        certified_track=certified,
        streak_target_track=target,
        streak_required=streak_len,
        streak_current=min(current, streak_len),
        thresholds=thresholds,
        note=note,
    )
    return asdict(result)

