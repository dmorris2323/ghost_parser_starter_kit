# src/instructor_grading_weights.py
from __future__ import annotations

from typing import Dict, Tuple

from difficulty_scaling_engine import get_profile, normalize_difficulty


# Rubric categories (0–100 each)
CATEGORIES = [
    "signal_hygiene",      # clean data handling, no nonsense
    "fusion_reasoning",    # does the analyst explain/justify decisions?
    "alert_discipline",    # avoids alert spam / false positives
    "response_quality",    # chooses correct actions / mitigations
    "documentation",       # notes, SITREP clarity, reproducibility
]


# Base weights must sum to 1.0
_BASE_WEIGHTS: Dict[str, float] = {
    "signal_hygiene": 0.22,
    "fusion_reasoning": 0.22,
    "alert_discipline": 0.22,
    "response_quality": 0.22,
    "documentation": 0.12,
}


def get_weights_for_difficulty(difficulty: str) -> Dict[str, float]:
    """
    Adjust instructor expectations depending on difficulty:
    - BEGINNER: reward hygiene + documentation slightly more
    - ADVERSARIAL: reward alert discipline + response quality slightly more
    """
    d = normalize_difficulty(difficulty)
    w = dict(_BASE_WEIGHTS)

    if d == "BEGINNER":
        w["signal_hygiene"] += 0.03
        w["documentation"] += 0.03
        w["response_quality"] -= 0.03
        w["alert_discipline"] -= 0.03

    elif d == "ADVERSARIAL":
        w["alert_discipline"] += 0.03
        w["response_quality"] += 0.03
        w["documentation"] -= 0.03
        w["signal_hygiene"] -= 0.03

    # Normalize for safety
    s = sum(w.values())
    if s <= 0:
        return dict(_BASE_WEIGHTS)
    for k in w:
        w[k] = w[k] / s
    return w


def score_session(rubric_scores: Dict[str, float], difficulty: str) -> Tuple[float, Dict[str, float]]:
    """
    Returns: (final_score_0_100, breakdown)
    final_score includes a difficulty scalar (harder sessions count more).
    """
    weights = get_weights_for_difficulty(difficulty)
    prof = get_profile(difficulty)

    raw = 0.0
    breakdown: Dict[str, float] = {}
    for k, wt in weights.items():
        v = float(rubric_scores.get(k, 0.0))
        v = max(0.0, min(100.0, v))
        breakdown[k] = v
        raw += v * wt

    # difficulty scalar boosts the effective score, but clamp to 100
    final = raw * prof.weight_scalar
    final = max(0.0, min(100.0, final))
    return final, breakdown


def expectation_band(difficulty: str) -> Dict[str, float]:
    prof = get_profile(difficulty)
    return {
        "expected_min": prof.expected_min_score,
        "expected_target": prof.expected_target_score,
        "expected_max": prof.expected_max_score,
        "volatility_tolerance": prof.volatility_tolerance,
        "weight_scalar": prof.weight_scalar,
    }

