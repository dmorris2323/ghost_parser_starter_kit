from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


DIFFICULTY_LEVELS: List[str] = ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"]


@dataclass(frozen=True)
class DifficultyProfile:
    name: str
    # How much this difficulty should count in curve math.
    weight: float
    # Passing threshold expectation (score floor).
    score_floor: float
    # Rubric weight emphasis per difficulty
    rubric_weights: Dict[str, float]


def normalize_difficulty(difficulty: str) -> str:
    if not isinstance(difficulty, str):
        return "INTERMEDIATE"
    d = difficulty.strip().upper()
    return d if d in DIFFICULTY_LEVELS else "INTERMEDIATE"


def get_difficulty_profile(difficulty: str) -> DifficultyProfile:
    d = normalize_difficulty(difficulty)

    # Rubric keys must match instructor_autograder keys.
    if d == "BEGINNER":
        # Emphasize fundamentals + safe reasoning over speed.
        return DifficultyProfile(
            name=d,
            weight=0.80,
            score_floor=60.0,
            rubric_weights={
                "accuracy": 0.30,
                "discipline": 0.30,
                "timeliness": 0.15,
                "comms_clarity": 0.15,
                "procedure": 0.10,
            },
        )
    if d == "ADVERSARIAL":
        # Emphasize discipline + accuracy under pressure.
        return DifficultyProfile(
            name=d,
            weight=1.25,
            score_floor=70.0,
            rubric_weights={
                "accuracy": 0.30,
                "discipline": 0.25,
                "procedure": 0.20,
                "timeliness": 0.15,
                "comms_clarity": 0.10,
            },
        )

    # INTERMEDIATE baseline
    return DifficultyProfile(
        name=d,
        weight=1.00,
        score_floor=65.0,
        rubric_weights={
            "accuracy": 0.28,
            "discipline": 0.22,
            "procedure": 0.18,
            "timeliness": 0.17,
            "comms_clarity": 0.15,
        },
    )


def difficulty_weight(difficulty: str) -> float:
    return float(get_difficulty_profile(difficulty).weight)


def rubric_weights(difficulty: str) -> Dict[str, float]:
    return dict(get_difficulty_profile(difficulty).rubric_weights)


def score_floor(difficulty: str) -> float:
    return float(get_difficulty_profile(difficulty).score_floor)


def list_difficulties() -> List[str]:
    return list(DIFFICULTY_LEVELS)


def explain_difficulty(difficulty: str) -> Tuple[str, str]:
    d = normalize_difficulty(difficulty)
    if d == "BEGINNER":
        return ("BEGINNER", "Fundamentals first. Lower pressure; grading rewards safe procedure and clarity.")
    if d == "ADVERSARIAL":
        return ("ADVERSARIAL", "High pressure. Grading rewards discipline, procedure, and accuracy under stress.")
    return ("INTERMEDIATE", "Balanced difficulty. Grading balances accuracy, discipline, timeliness, and clarity.")

