# src/instructor_grader.py
from __future__ import annotations

from typing import Any, Dict

from difficulty_profiles import get_profile, normalize_difficulty_key


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def grade_session(
    *,
    difficulty: str,
    score: float,
    max_score: float,
    procedure_ok: bool = True,
    explanation_quality: float = 0.7,  # 0..1
    safety_ok: bool = True,
) -> Dict[str, Any]:
    """
    Safe training-only grader. This is NOT operational evaluation.
    It produces:
      - normalized score
      - weighted rubric score (0..100)
      - PASS/FAIL vs difficulty thresholds
      - simple reasons
    """
    diff = normalize_difficulty_key(difficulty)
    p = get_profile(diff)

    denom = float(max_score) if float(max_score) > 0 else 100.0
    normalized = _clamp01(float(score) / denom)

    procedure = 1.0 if procedure_ok else 0.0
    explanation = _clamp01(float(explanation_quality))
    safety = 1.0 if safety_ok else 0.0

    # rubric weighted score (0..1)
    rubric_01 = (
        normalized * p.weight_accuracy
        + procedure * p.weight_procedure
        + explanation * p.weight_explanation
        + safety * p.weight_safety
    )
    rubric_100 = round(rubric_01 * 100.0, 2)

    status = "PASS" if rubric_01 >= p.pass_threshold else "FAIL"
    excellence = rubric_01 >= p.excellence_threshold

    reasons = []
    if status == "FAIL":
        if normalized < p.pass_threshold:
            reasons.append("Raw score too low for selected difficulty.")
        if not procedure_ok:
            reasons.append("Procedure errors flagged.")
        if explanation < 0.5:
            reasons.append("Explanation quality too low.")
        if not safety_ok:
            reasons.append("Safety violation flagged.")
    else:
        reasons.append("Meets difficulty expectation band.")
        if excellence:
            reasons.append("Excellence band achieved.")

    return {
        "difficulty": diff,
        "normalized_score": round(normalized, 4),
        "rubric_score": rubric_100,
        "status": status,
        "excellence": bool(excellence),
        "thresholds": {
            "pass_threshold": p.pass_threshold,
            "excellence_threshold": p.excellence_threshold,
        },
        "weights": {
            "accuracy": p.weight_accuracy,
            "procedure": p.weight_procedure,
            "explanation": p.weight_explanation,
            "safety": p.weight_safety,
        },
        "reasons": reasons,
    }

