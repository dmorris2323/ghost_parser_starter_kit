"""
instructor_rubric_autograder.py

Auto-grades a scenario/session using a simple rubric and applies
difficulty scaling weight from difficulty_scaling_engine.

This is *training* evaluation only.
"""

from __future__ import annotations

from typing import Any, Dict

from difficulty_scaling_engine import normalize_difficulty, get_weight


DEFAULT_RUBRIC_WEIGHTS = {
    "situation_awareness": 0.25,
    "evidence_handling": 0.25,
    "decision_quality": 0.25,
    "communication": 0.15,
    "discipline_under_pressure": 0.10,
}


def auto_grade_scenario(
    difficulty: str,
    trainee_inputs: Dict[str, Any],
    scenario: Dict[str, Any],
    rubric_weights: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    """
    trainee_inputs can be simple:
      {
        "summary_quality": 0-100,
        "evidence_quality": 0-100,
        "decision_quality": 0-100,
        "communication": 0-100,
        "discipline": 0-100
      }
    """
    d = normalize_difficulty(difficulty)
    dw = float(get_weight(d))
    w = dict(DEFAULT_RUBRIC_WEIGHTS)
    if rubric_weights:
        w.update(rubric_weights)

    # Map expected keys -> rubric categories
    raw = {
        "situation_awareness": float(trainee_inputs.get("summary_quality", 0.0)),
        "evidence_handling": float(trainee_inputs.get("evidence_quality", 0.0)),
        "decision_quality": float(trainee_inputs.get("decision_quality", 0.0)),
        "communication": float(trainee_inputs.get("communication", 0.0)),
        "discipline_under_pressure": float(trainee_inputs.get("discipline", 0.0)),
    }

    # Weighted base score
    base_score = 0.0
    for k, wk in w.items():
        base_score += raw.get(k, 0.0) * float(wk)

    # Difficulty-adjusted final score
    # We do NOT inflate above 100; we let higher difficulty demand higher competence.
    # Weight is applied as a modest multiplier to reward harder reps, capped to 100.
    final = min(100.0, base_score * (0.90 + 0.10 * dw))

    return {
        "difficulty": d,
        "difficulty_weight": dw,
        "rubric_weights": w,
        "raw_scores": raw,
        "base_score": round(base_score, 2),
        "final_score": round(final, 2),
        "scenario_id": scenario.get("paths", {}).get("json_stamped") or scenario.get("paths", {}).get("json_latest") or "UNKNOWN",
    }

