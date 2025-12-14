"""
training_policy.py

Central policy for training:
- Difficulty expectations (thresholds & grading weights)
- Gate enforcement: only GREEN sessions count toward AGI
- Certification mode behaviors (strictness knobs)

This file MUST NOT import training_session_store to avoid circular imports.
"""

from __future__ import annotations

from typing import Any, Dict


DIFFICULTY_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"]

# Instructor expectations by difficulty
EXPECTATIONS = {
    "BEGINNER": {
        "min_score": 60.0,
        "grader_weight_accuracy": 0.50,
        "grader_weight_process": 0.50,
        "notes": "Basic competence, stable steps, correct terminology.",
    },
    "INTERMEDIATE": {
        "min_score": 70.0,
        "grader_weight_accuracy": 0.60,
        "grader_weight_process": 0.40,
        "notes": "Good analysis + fewer misses; handle mild ambiguity.",
    },
    "ADVANCED": {
        "min_score": 80.0,
        "grader_weight_accuracy": 0.70,
        "grader_weight_process": 0.30,
        "notes": "High accuracy under pressure; recognizes deception cues.",
    },
    "ADVERSARIAL": {
        "min_score": 85.0,
        "grader_weight_accuracy": 0.75,
        "grader_weight_process": 0.25,
        "notes": "Handles injected patterns; maintains discipline; no panic.",
    },
}


def normalize_difficulty(d: str) -> str:
    d = (d or "BEGINNER").upper().strip()
    return d if d in EXPECTATIONS else "BEGINNER"


def counts_toward_agi(*, gate_status: str) -> bool:
    """
    Non-negotiable: only GREEN sessions count toward AGI.
    """
    return str(gate_status or "UNKNOWN").upper() == "GREEN"


def can_log_difficulty(
    *,
    requested_difficulty: str,
    certified_track: str,
) -> bool:
    """
    Prevents logging difficulties above certification track+1.
    (So you don't spam ADVERSARIAL before you're ready.)

    certified_track can be "NONE" or one of DIFFICULTY_LEVELS.
    """
    req = normalize_difficulty(requested_difficulty)
    cert = (certified_track or "NONE").upper().strip()

    if cert == "NONE":
        return req == "BEGINNER"

    if cert not in DIFFICULTY_LEVELS:
        return req == "BEGINNER"

    cert_idx = DIFFICULTY_LEVELS.index(cert)
    req_idx = DIFFICULTY_LEVELS.index(req)

    # allow current or next track
    return req_idx <= min(cert_idx + 1, len(DIFFICULTY_LEVELS) - 1)


def get_expectations(difficulty: str) -> Dict[str, Any]:
    return EXPECTATIONS[normalize_difficulty(difficulty)]

