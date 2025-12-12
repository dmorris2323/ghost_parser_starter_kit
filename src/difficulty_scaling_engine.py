"""
difficulty_scaling_engine.py

Single source of truth for difficulty behavior across:
- training sessions (stored difficulty + weight)
- scenario engine (parameter scaling)
- instructor grading weights (difficulty multiplier)

Difficulties:
BEGINNER, INTERMEDIATE, ADVANCED, ADVERSARIAL
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


VALID_DIFFICULTIES = ("BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL")


@dataclass(frozen=True)
class DifficultyProfile:
    name: str
    weight: float                 # used for instructor grading + training curve weighting
    noise: float                  # used by scenarios: randomness/entropy
    anomaly_rate: float           # scenario: probability of anomaly flags
    attack_like_rate: float       # scenario: probability of attack_like flags
    crit_rate: float              # scenario: probability of CRIT severity
    pattern_intensity_boost: float # scenario: how “strong” injected patterns appear


_PROFILES: Dict[str, DifficultyProfile] = {
    "BEGINNER": DifficultyProfile(
        name="BEGINNER", weight=0.85, noise=0.15, anomaly_rate=0.10, attack_like_rate=0.05, crit_rate=0.01, pattern_intensity_boost=0.70
    ),
    "INTERMEDIATE": DifficultyProfile(
        name="INTERMEDIATE", weight=1.00, noise=0.25, anomaly_rate=0.18, attack_like_rate=0.10, crit_rate=0.02, pattern_intensity_boost=0.85
    ),
    "ADVANCED": DifficultyProfile(
        name="ADVANCED", weight=1.15, noise=0.35, anomaly_rate=0.26, attack_like_rate=0.16, crit_rate=0.04, pattern_intensity_boost=1.00
    ),
    "ADVERSARIAL": DifficultyProfile(
        name="ADVERSARIAL", weight=1.30, noise=0.45, anomaly_rate=0.34, attack_like_rate=0.22, crit_rate=0.06, pattern_intensity_boost=1.15
    ),
}


def normalize_difficulty(difficulty: str) -> str:
    d = (difficulty or "").strip().upper()
    return d if d in _PROFILES else "INTERMEDIATE"


def get_profile(difficulty: str) -> DifficultyProfile:
    return _PROFILES[normalize_difficulty(difficulty)]


def get_weight(difficulty: str) -> float:
    return float(get_profile(difficulty).weight)


def profiles_summary() -> Dict[str, Any]:
    return {
        k: {
            "weight": v.weight,
            "noise": v.noise,
            "anomaly_rate": v.anomaly_rate,
            "attack_like_rate": v.attack_like_rate,
            "crit_rate": v.crit_rate,
            "pattern_intensity_boost": v.pattern_intensity_boost,
        }
        for k, v in _PROFILES.items()
    }

