# src/difficulty_scaling_engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


DIFFICULTIES: List[str] = ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"]


@dataclass(frozen=True)
class DifficultyProfile:
    name: str
    weight_scalar: float          # used for difficulty-weighted scoring/averages
    expected_min_score: float     # instructor expectation band
    expected_target_score: float
    expected_max_score: float
    volatility_tolerance: float   # how much volatility is "acceptable"


_PROFILES: Dict[str, DifficultyProfile] = {
    "BEGINNER": DifficultyProfile(
        name="BEGINNER",
        weight_scalar=0.85,
        expected_min_score=55.0,
        expected_target_score=72.0,
        expected_max_score=95.0,
        volatility_tolerance=8.0,
    ),
    "INTERMEDIATE": DifficultyProfile(
        name="INTERMEDIATE",
        weight_scalar=1.00,
        expected_min_score=60.0,
        expected_target_score=75.0,
        expected_max_score=95.0,
        volatility_tolerance=12.0,
    ),
    "ADVERSARIAL": DifficultyProfile(
        name="ADVERSARIAL",
        weight_scalar=1.20,
        expected_min_score=50.0,
        expected_target_score=70.0,
        expected_max_score=92.0,
        volatility_tolerance=16.0,
    ),
}


def normalize_difficulty(difficulty: str) -> str:
    d = (difficulty or "INTERMEDIATE").strip().upper()
    if d not in _PROFILES:
        return "INTERMEDIATE"
    return d


def get_profile(difficulty: str) -> DifficultyProfile:
    return _PROFILES[normalize_difficulty(difficulty)]


def list_difficulties() -> List[str]:
    return list(DIFFICULTIES)

