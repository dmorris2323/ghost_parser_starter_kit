# src/instructor_autograder.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict

from training_difficulty_engine import normalize_difficulty, get_profile, compute_weighted_grade


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AutoGradeResult:
    grader_version: int
    generated_at: str
    difficulty: str
    trainee_name: str
    weighted_grade: Dict[str, Any]
    pass_threshold: float
    passed: bool
    notes: str


def auto_grade_session(
    trainee_name: str,
    difficulty: str,
    raw_scores: Dict[str, float],
) -> Dict[str, Any]:
    """
    Auto-grader: difficulty changes weights AND expectations.
    raw_scores: accuracy/speed/tradecraft in 0..1
    """
    d = normalize_difficulty(difficulty)
    prof = get_profile(d)
    grade = compute_weighted_grade(raw_scores, d)

    # Pass thresholds scale with difficulty (stricter as difficulty increases)
    if d == "BEGINNER":
        threshold = 60.0
    elif d == "ADVERSARIAL":
        threshold = 75.0
    else:
        threshold = 68.0

    passed = float(grade["weighted_grade"]) >= threshold

    notes = (
        "PASS means performance meets difficulty expectations. "
        "If FAIL, focus the lowest contributing category and rerun at same difficulty."
    )

    res = AutoGradeResult(
        grader_version=1,
        generated_at=_utc_now(),
        difficulty=d,
        trainee_name=trainee_name or "Trainee",
        weighted_grade=grade,
        pass_threshold=threshold,
        passed=passed,
        notes=notes,
    )
    out = asdict(res)
    out["difficulty_profile"] = prof
    return out


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            auto_grade_session(
                trainee_name="Ghost",
                difficulty="INTERMEDIATE",
                raw_scores={"accuracy": 0.78, "speed": 0.62, "tradecraft": 0.66},
            ),
            indent=2,
        )
    )

