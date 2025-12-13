# src/operator_certification_mode.py
from __future__ import annotations

from typing import Any, Dict, List

from difficulty_profiles import normalize_difficulty_key, get_profile
from instructor_grader import grade_session


def compute_certification_status(
    *,
    sessions: List[Dict[str, Any]],
    target_difficulty: str,
    required_pass_streak: int = 5,
    require_no_safety_flags: bool = True,
) -> Dict[str, Any]:
    """
    Operator Certification Mode (training):
      - lock a target difficulty
      - require a PASS streak length
      - optionally require no safety violations
    """
    diff = normalize_difficulty_key(target_difficulty)
    p = get_profile(diff)

    # newest-last order expected; handle either way by sorting on timestamp if present
    def _ts(s: Dict[str, Any]) -> str:
        return str(s.get("timestamp", ""))

    ordered = sorted(sessions, key=_ts)

    streak = 0
    evaluated = 0
    last_results: List[Dict[str, Any]] = []

    for s in reversed(ordered):
        # only count sessions at target difficulty
        if normalize_difficulty_key(str(s.get("difficulty", ""))) != diff:
            continue

        evaluated += 1

        procedure_ok = bool(s.get("procedure_ok", True))
        safety_ok = bool(s.get("safety_ok", True))
        explanation_q = float(s.get("explanation_quality", 0.7))

        # enforce safety constraint
        if require_no_safety_flags and not safety_ok:
            streak = 0
            last_results.append({"session_id": s.get("session_id"), "status": "FAIL", "reason": "Safety violation"})
            continue

        g = grade_session(
            difficulty=diff,
            score=float(s.get("score", 0.0)),
            max_score=float(s.get("max_score", 100.0)),
            procedure_ok=procedure_ok,
            explanation_quality=explanation_q,
            safety_ok=safety_ok,
        )

        last_results.append({"session_id": s.get("session_id"), "rubric": g})

        if g["status"] == "PASS":
            streak += 1
        else:
            streak = 0

        if streak >= required_pass_streak:
            break

    last_results = list(reversed(last_results))[:10]

    certified = streak >= required_pass_streak
    return {
        "mode": "OPERATOR_CERTIFICATION",
        "target_difficulty": diff,
        "required_pass_streak": required_pass_streak,
        "require_no_safety_flags": require_no_safety_flags,
        "pass_threshold": p.pass_threshold,
        "current_pass_streak": streak,
        "sessions_evaluated_at_difficulty": evaluated,
        "certified": certified,
        "guidance": (
            "Certified at target difficulty."
            if certified
            else f"Need {required_pass_streak - streak} more PASS sessions in a row at {diff}."
        ),
        "recent_evaluations": last_results,
    }

