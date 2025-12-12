# src/obasi_training_coach.py
from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_obasi_training_coach_speech(*args: Any, **kwargs: Any):
    """
    Backward-compatible coach interface.

    - Old behavior: some code imported this and expected Dict output with zero args.
    - New behavior: training apps call with kwargs (trainee_name, difficulty, curve, sessions, gate, etc.)
      and expect a STRING.

    This function supports BOTH:
      • If called with no args/kwargs -> returns Dict[str, Any]
      • Otherwise -> returns str
    """
    if not args and not kwargs:
        return {
            "message": "Obasi online. Provide trainee_name/difficulty/curve/sessions for coaching output.",
            "version": 2,
        }

    trainee = (kwargs.get("trainee_name") or kwargs.get("operator") or "Trainee")
    difficulty = (kwargs.get("difficulty") or "INTERMEDIATE")
    curve = kwargs.get("curve") or {}
    gate = kwargs.get("gate") or {}
    sessions = kwargs.get("sessions") or []

    agi = curve.get("AGI", curve.get("agi", None))
    slope = curve.get("improvement_slope", None)
    vol = curve.get("volatility_index", None)

    gate_status = gate.get("status", "UNKNOWN")
    counted = gate.get("counted_for_agi", False)

    # Short, coach-style guidance
    lines: List[str] = []
    lines.append(f"🦉 Obasi Coach — {trainee}")
    lines.append(f"Difficulty: {difficulty}")
    lines.append(f"Gate: {gate_status} | Counted for AGI: {'YES' if counted else 'NO'}")

    if agi is not None:
        lines.append(f"AGI: {agi}")
    if slope is not None:
        lines.append(f"Slope: {slope}")
    if vol is not None:
        lines.append(f"Volatility: {vol}")

    # Coaching logic
    if gate_status != "PASS":
        lines.append("")
        lines.append("Action: run integrity/SPS checks until GREEN. Don’t train on a dirty system.")
    else:
        lines.append("")
        if slope is not None and slope < 0:
            lines.append("You’re slipping slightly. Slow down, focus accuracy + tradecraft this session.")
        elif slope is not None and slope >= 0:
            lines.append("Momentum is positive. Increase difficulty when you can hold consistency.")
        else:
            lines.append("Build 3–5 clean sessions at this difficulty before stepping up.")

    lines.append("")
    lines.append(f"Sessions logged: {len(sessions)}")

    return "\n".join(lines)

