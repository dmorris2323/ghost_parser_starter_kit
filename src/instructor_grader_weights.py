"""
instructor_grader_weights.py

Instructor Mode: difficulty-dependent grading weights + expectations.

This file is pure logic (no IO), safe to use from CLI/GUI.
"""

from __future__ import annotations

from typing import Dict


def get_grading_profile(difficulty: str) -> Dict[str, float]:
    d = str(difficulty).upper().strip()

    # Categories (sum to 1.0):
    # - detection: did you catch the pattern/anomaly?
    # - reasoning: did you explain it coherently?
    # - tradecraft: correct terminology/steps/checks
    # - speed: time/decisiveness (proxy)
    # - discipline: followed gates/policy, no sloppiness

    if d == "BEGINNER":
        return {
            "detection": 0.35,
            "reasoning": 0.20,
            "tradecraft": 0.20,
            "speed": 0.10,
            "discipline": 0.15,
        }

    if d == "ADVERSARIAL":
        return {
            "detection": 0.30,
            "reasoning": 0.25,
            "tradecraft": 0.25,
            "speed": 0.05,
            "discipline": 0.15,
        }

    # INTERMEDIATE default
    return {
        "detection": 0.32,
        "reasoning": 0.23,
        "tradecraft": 0.23,
        "speed": 0.07,
        "discipline": 0.15,
    }


def expected_pass_threshold(difficulty: str) -> int:
    d = str(difficulty).upper().strip()
    if d == "BEGINNER":
        return 70
    if d == "ADVERSARIAL":
        return 80
    return 75

