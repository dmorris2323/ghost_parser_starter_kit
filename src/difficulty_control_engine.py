"""
difficulty_control_engine.py

Single source of truth for training difficulty behavior.
SAFE: synthetic/training only.
"""

from dataclasses import dataclass


@dataclass
class DifficultyProfile:
    name: str
    noise_multiplier: float
    pattern_intensity: float
    grading_expectation: float
    volatility_tolerance: float


DIFFICULTY_PROFILES = {
    "BEGINNER": DifficultyProfile(
        name="BEGINNER",
        noise_multiplier=0.6,
        pattern_intensity=0.4,
        grading_expectation=0.75,
        volatility_tolerance=25.0,
    ),
    "INTERMEDIATE": DifficultyProfile(
        name="INTERMEDIATE",
        noise_multiplier=1.0,
        pattern_intensity=0.7,
        grading_expectation=0.85,
        volatility_tolerance=18.0,
    ),
    "ADVERSARIAL": DifficultyProfile(
        name="ADVERSARIAL",
        noise_multiplier=1.4,
        pattern_intensity=1.0,
        grading_expectation=0.92,
        volatility_tolerance=12.0,
    ),
}


def get_difficulty_profile(name: str) -> DifficultyProfile:
    key = (name or "INTERMEDIATE").upper()
    return DIFFICULTY_PROFILES.get(key, DIFFICULTY_PROFILES["INTERMEDIATE"])

