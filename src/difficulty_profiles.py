# src/difficulty_profiles.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class DifficultyProfile:
    key: str
    label: str
    # expected performance bands (used by grader + certification)
    pass_threshold: float          # normalized 0..1
    excellence_threshold: float    # normalized 0..1
    # weighting emphasis (used by rubric weights)
    weight_accuracy: float
    weight_procedure: float
    weight_explanation: float
    weight_safety: float
    # training expectations
    expected_patterns: List[str]


_PROFILES: Dict[str, DifficultyProfile] = {
    "BEGINNER": DifficultyProfile(
        key="BEGINNER",
        label="Beginner",
        pass_threshold=0.70,
        excellence_threshold=0.85,
        weight_accuracy=0.40,
        weight_procedure=0.30,
        weight_explanation=0.20,
        weight_safety=0.10,
        expected_patterns=["NONE", "LOW_NOISE", "SINGLE_DOMAIN_SPIKE"],
    ),
    "INTERMEDIATE": DifficultyProfile(
        key="INTERMEDIATE",
        label="Intermediate",
        pass_threshold=0.75,
        excellence_threshold=0.88,
        weight_accuracy=0.45,
        weight_procedure=0.30,
        weight_explanation=0.15,
        weight_safety=0.10,
        expected_patterns=["LOW_NOISE", "CROSS_SENSOR_DRIFT", "COMMS_DEGRADATION"],
    ),
    "ADVERSARIAL": DifficultyProfile(
        key="ADVERSARIAL",
        label="Adversarial",
        pass_threshold=0.80,
        excellence_threshold=0.92,
        weight_accuracy=0.50,
        weight_procedure=0.25,
        weight_explanation=0.15,
        weight_safety=0.10,
        expected_patterns=["CROSS_DOMAIN_CONFUSION", "ALERT_STORM", "DECOY_SIGNAL", "CHAIN_REACTION"],
    ),
}


def normalize_difficulty_key(x: str) -> str:
    if not x:
        return "INTERMEDIATE"
    x = str(x).strip().upper()
    if x in _PROFILES:
        return x
    # allow shorthand
    if x.startswith("ADV"):
        return "ADVERSARIAL"
    if x.startswith("INT"):
        return "INTERMEDIATE"
    if x.startswith("BEG"):
        return "BEGINNER"
    return "INTERMEDIATE"


def get_profile(difficulty: str) -> DifficultyProfile:
    k = normalize_difficulty_key(difficulty)
    return _PROFILES[k]


def list_profiles() -> List[DifficultyProfile]:
    return list(_PROFILES.values())


def as_dict(difficulty: str) -> Dict[str, float | str | list]:
    p = get_profile(difficulty)
    return {
        "key": p.key,
        "label": p.label,
        "pass_threshold": p.pass_threshold,
        "excellence_threshold": p.excellence_threshold,
        "weights": {
            "accuracy": p.weight_accuracy,
            "procedure": p.weight_procedure,
            "explanation": p.weight_explanation,
            "safety": p.weight_safety,
        },
        "expected_patterns": p.expected_patterns,
    }

