# src/training_grading_weights.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


ALLOWED_DIFFICULTIES = ("BEGINNER", "INTERMEDIATE", "ADVERSARIAL")


@dataclass(frozen=True)
class DifficultyProfile:
    difficulty: str
    # Rubric weights must sum to 1.0
    w_accuracy: float
    w_reasoning: float
    w_stability: float
    w_speed: float

    # Training curve & gate semantics
    volatility_tolerance: float  # higher tolerance for beginner
    score_multiplier: float      # optional: makes hard sessions “count more”


_PROFILES: Dict[str, DifficultyProfile] = {
    "BEGINNER": DifficultyProfile(
        difficulty="BEGINNER",
        w_accuracy=0.35,
        w_reasoning=0.25,
        w_stability=0.25,
        w_speed=0.15,
        volatility_tolerance=20.0,
        score_multiplier=0.90,
    ),
    "INTERMEDIATE": DifficultyProfile(
        difficulty="INTERMEDIATE",
        w_accuracy=0.40,
        w_reasoning=0.30,
        w_stability=0.20,
        w_speed=0.10,
        volatility_tolerance=15.0,
        score_multiplier=1.00,
    ),
    "ADVERSARIAL": DifficultyProfile(
        difficulty="ADVERSARIAL",
        w_accuracy=0.45,
        w_reasoning=0.35,
        w_stability=0.15,
        w_speed=0.05,
        volatility_tolerance=10.0,
        score_multiplier=1.10,
    ),
}


def normalize_difficulty(difficulty: str | None) -> str:
    if not difficulty:
        return "INTERMEDIATE"
    d = str(difficulty).strip().upper()
    if d not in _PROFILES:
        return "INTERMEDIATE"
    return d


def get_profile(difficulty: str | None) -> DifficultyProfile:
    d = normalize_difficulty(difficulty)
    return _PROFILES[d]


def weights_as_dict(difficulty: str | None) -> Dict[str, Any]:
    p = get_profile(difficulty)
    return {
        "difficulty": p.difficulty,
        "weights": {
            "accuracy": p.w_accuracy,
            "reasoning": p.w_reasoning,
            "stability": p.w_stability,
            "speed": p.w_speed,
        },
        "volatility_tolerance": p.volatility_tolerance,
        "score_multiplier": p.score_multiplier,
    }


def compute_weighted_score(
    *,
    accuracy: float,
    reasoning: float,
    stability: float,
    speed: float,
    difficulty: str | None,
) -> float:
    """
    Inputs expected 0..100
    Returns 0..100
    """
    p = get_profile(difficulty)

    def clamp(x: float) -> float:
        return max(0.0, min(100.0, float(x)))

    a = clamp(accuracy)
    r = clamp(reasoning)
    s = clamp(stability)
    sp = clamp(speed)

    base = (
        a * p.w_accuracy
        + r * p.w_reasoning
        + s * p.w_stability
        + sp * p.w_speed
    )
    # multiplier affects training curve difficulty weighting later,
    # but base rubric score should remain interpretable 0..100
    return round(base, 2)

