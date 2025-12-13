# src/training_grading_weights.py
from __future__ import annotations

from typing import Dict


def weights_as_dict(difficulty: str) -> Dict[str, float]:
    d = (difficulty or "INTERMEDIATE").upper().strip()

    # Weights sum to 1.0
    if d == "BEGINNER":
        # Encourage learning: accuracy + reasoning matter most
        return {
            "accuracy_w": 0.35,
            "reasoning_w": 0.35,
            "stability_w": 0.20,
            "speed_w": 0.10,
            "expected_min_score": 55.0,
        }
    if d == "ADVERSARIAL":
        # Real-world pressure: stability matters more, speed matters more
        return {
            "accuracy_w": 0.25,
            "reasoning_w": 0.25,
            "stability_w": 0.35,
            "speed_w": 0.15,
            "expected_min_score": 70.0,
        }

    # INTERMEDIATE default
    return {
        "accuracy_w": 0.30,
        "reasoning_w": 0.30,
        "stability_w": 0.25,
        "speed_w": 0.15,
        "expected_min_score": 62.0,
    }


def score_from_rubric(difficulty: str, rubric: Dict[str, float]) -> float:
    w = weights_as_dict(difficulty)
    acc = float((rubric or {}).get("accuracy", 0))
    rea = float((rubric or {}).get("reasoning", 0))
    sta = float((rubric or {}).get("stability", 0))
    spe = float((rubric or {}).get("speed", 0))

    score = (
        acc * w["accuracy_w"]
        + rea * w["reasoning_w"]
        + sta * w["stability_w"]
        + spe * w["speed_w"]
    )
    # Clamp 0–100
    return max(0.0, min(100.0, score))

