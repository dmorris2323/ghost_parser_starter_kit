# src/training_difficulty_engine.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class DifficultyProfile:
    difficulty: str
    label: str
    expected_accuracy: float
    expected_speed: float
    expected_tradecraft: float
    # weights sum to 1.0
    weights: Dict[str, float]


PROFILES: Dict[str, DifficultyProfile] = {
    "BEGINNER": DifficultyProfile(
        difficulty="BEGINNER",
        label="Beginner",
        expected_accuracy=0.65,
        expected_speed=0.50,
        expected_tradecraft=0.45,
        weights={"accuracy": 0.55, "speed": 0.20, "tradecraft": 0.25},
    ),
    "INTERMEDIATE": DifficultyProfile(
        difficulty="INTERMEDIATE",
        label="Intermediate",
        expected_accuracy=0.75,
        expected_speed=0.65,
        expected_tradecraft=0.60,
        weights={"accuracy": 0.45, "speed": 0.25, "tradecraft": 0.30},
    ),
    "ADVERSARIAL": DifficultyProfile(
        difficulty="ADVERSARIAL",
        label="Adversarial",
        expected_accuracy=0.80,
        expected_speed=0.70,
        expected_tradecraft=0.75,
        weights={"accuracy": 0.35, "speed": 0.25, "tradecraft": 0.40},
    ),
}


def normalize_difficulty(d: str) -> str:
    if not d:
        return "INTERMEDIATE"
    d2 = d.strip().upper()
    if d2 in PROFILES:
        return d2
    return "INTERMEDIATE"


def get_profile(difficulty: str) -> Dict[str, Any]:
    key = normalize_difficulty(difficulty)
    return asdict(PROFILES[key])


def compute_weighted_grade(
    raw_scores: Dict[str, float],
    difficulty: str,
) -> Dict[str, Any]:
    """
    raw_scores keys: accuracy, speed, tradecraft (0..1)
    """
    prof = PROFILES[normalize_difficulty(difficulty)]
    w = prof.weights

    a = float(raw_scores.get("accuracy", 0.0))
    s = float(raw_scores.get("speed", 0.0))
    t = float(raw_scores.get("tradecraft", 0.0))

    weighted = a * w["accuracy"] + s * w["speed"] + t * w["tradecraft"]

    # expectation delta (how far above/below difficulty expectations)
    exp = (
        prof.expected_accuracy * w["accuracy"]
        + prof.expected_speed * w["speed"]
        + prof.expected_tradecraft * w["tradecraft"]
    )
    delta = weighted - exp

    return {
        "difficulty": prof.difficulty,
        "weights": w,
        "raw_scores": {"accuracy": a, "speed": s, "tradecraft": t},
        "weighted_grade": round(weighted * 100, 2),
        "expected_grade": round(exp * 100, 2),
        "delta_vs_expected": round(delta * 100, 2),
    }

