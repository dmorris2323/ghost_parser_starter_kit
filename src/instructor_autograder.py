from __future__ import annotations

from typing import Any, Dict, Tuple

from difficulty_scaling_engine import normalize_difficulty, rubric_weights, score_floor


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    try:
        x = float(v)
    except Exception:
        return lo
    return max(lo, min(hi, x))


def grade_session(
    *,
    difficulty: str,
    accuracy: float,
    timeliness: float,
    discipline: float,
    comms_clarity: float,
    procedure: float,
    gate_green: bool = True,
) -> Dict[str, Any]:
    """
    Difficulty-aware auto-grader.
    All inputs are 0-100.
    Returns: score (0-100), pass/fail, breakdown, and counted flag.
    """
    d = normalize_difficulty(difficulty)
    w = rubric_weights(d)

    acc = _clamp(accuracy)
    tim = _clamp(timeliness)
    dis = _clamp(discipline)
    com = _clamp(comms_clarity)
    pro = _clamp(procedure)

    weighted = (
        acc * w["accuracy"]
        + dis * w["discipline"]
        + tim * w["timeliness"]
        + com * w["comms_clarity"]
        + pro * w["procedure"]
    )

    floor = score_floor(d)
    passed = bool(weighted >= floor)

    # Gate controls whether this session counts toward AGI.
    counted = bool(gate_green) and passed

    return {
        "difficulty": d,
        "grader_weights": w,
        "score": round(float(weighted), 2),
        "score_floor": float(floor),
        "passed": passed,
        "gate_green": bool(gate_green),
        "counted": counted,
        "inputs": {
            "accuracy": acc,
            "timeliness": tim,
            "discipline": dis,
            "comms_clarity": com,
            "procedure": pro,
        },
    }

