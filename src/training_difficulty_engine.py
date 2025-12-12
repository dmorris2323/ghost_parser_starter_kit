# src/training_difficulty_engine.py
from __future__ import annotations

from typing import Dict


_ALLOWED = {"BEGINNER", "INTERMEDIATE", "ADVERSARIAL"}


def normalize_difficulty(difficulty: str) -> str:
    d = (difficulty or "INTERMEDIATE").strip().upper()
    return d if d in _ALLOWED else "INTERMEDIATE"


def get_profile(difficulty: str) -> Dict[str, object]:
    d = normalize_difficulty(difficulty)

    if d == "BEGINNER":
        return {
            "label": "Beginner",
            "weight_accuracy": 0.55,
            "weight_speed": 0.20,
            "weight_tradecraft": 0.25,
            "expected_pass_threshold": 60.0,
        }

    if d == "ADVERSARIAL":
        return {
            "label": "Adversarial",
            "weight_accuracy": 0.45,
            "weight_speed": 0.15,
            "weight_tradecraft": 0.40,
            "expected_pass_threshold": 75.0,
        }

    return {
        "label": "Intermediate",
        "weight_accuracy": 0.50,
        "weight_speed": 0.20,
        "weight_tradecraft": 0.30,
        "expected_pass_threshold": 68.0,
    }


def compute_weighted_grade(raw_scores: Dict[str, float], difficulty: str) -> Dict[str, object]:
    prof = get_profile(difficulty)

    acc = float(raw_scores.get("accuracy", 0.0))
    spd = float(raw_scores.get("speed", 0.0))
    trd = float(raw_scores.get("tradecraft", 0.0))

    # Clamp 0..1
    acc = max(0.0, min(1.0, acc))
    spd = max(0.0, min(1.0, spd))
    trd = max(0.0, min(1.0, trd))

    w = (
        acc * float(prof["weight_accuracy"])
        + spd * float(prof["weight_speed"])
        + trd * float(prof["weight_tradecraft"])
    )

    return {
        "weighted_grade": round(w * 100.0, 2),
        "components": {"accuracy": acc, "speed": spd, "tradecraft": trd},
        "weights": {
            "accuracy": prof["weight_accuracy"],
            "speed": prof["weight_speed"],
            "tradecraft": prof["weight_tradecraft"],
        },
        "difficulty": normalize_difficulty(difficulty),
    }

