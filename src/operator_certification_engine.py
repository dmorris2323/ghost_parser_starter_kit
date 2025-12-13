"""
operator_certification_engine.py

Computes operator certification state from sessions:
- streak logic
- difficulty tracks

Returns dicts (stable API) so callers never assume strings.

No imports from training_policy to avoid cycles.
"""

from __future__ import annotations

from typing import Any, Dict, List


TRACKS = ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"]


def _counts(session: Dict[str, Any]) -> bool:
    return bool(session.get("counts_toward_agi", False))


def compute_certification(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Certification is based on consecutive counted sessions at/above a track.
    """
    streaks = {t: 0 for t in TRACKS}
    best = "NONE"

    # We compute streaks in chronological order (sessions are already ordered append-wise)
    for s in sessions:
        if not isinstance(s, dict):
            continue
        if not _counts(s):
            # breaks streak for all tracks
            for t in TRACKS:
                streaks[t] = 0
            continue

        diff = str(s.get("difficulty", "BEGINNER")).upper()
        # if a session is INTERMEDIATE, it counts for BEGINNER and INTERMEDIATE tracks
        for t in TRACKS:
            if TRACKS.index(diff) >= TRACKS.index(t):
                streaks[t] += 1
            else:
                streaks[t] = 0

    # thresholds (tune later)
    thresholds = {"BEGINNER": 3, "INTERMEDIATE": 5, "ADVERSARIAL": 7}
    for t in TRACKS:
        if streaks[t] >= thresholds[t]:
            best = t

    return {
        "highest_certified": best,
        "streaks": streaks,
        "thresholds": thresholds,
    }


def highest_certified_track() -> Dict[str, Any]:
    """
    Convenience wrapper that loads sessions internally.
    Kept as dict return to match your updated ecosystem.
    """
    from training_session_store import load_sessions  # local import is safe

    sessions = load_sessions()
    return compute_certification(sessions)

