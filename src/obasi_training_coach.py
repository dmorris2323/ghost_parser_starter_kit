# src/obasi_training_coach.py
from __future__ import annotations

from typing import Any, Dict, List


def _safe_num(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return float(default)
        return float(v)
    except Exception:
        return float(default)


def build_obasi_training_coach_speech(**payload: Any) -> str:
    """
    Stable coach interface.

    MUST:
    - accept any kwargs (future-proof)
    - return a STRING (never dict)
    - never raise on missing keys
    """
    trainee = str(payload.get("trainee_name") or payload.get("trainee") or "Operator")

    difficulty = str(payload.get("difficulty") or payload.get("difficulty_level") or "INTERMEDIATE").upper()

    curve = payload.get("curve") or {}
    if not isinstance(curve, dict):
        curve = {}

    agi = _safe_num(curve.get("AGI"), 0.0)
    slope = _safe_num(curve.get("improvement_slope"), 0.0)
    volatility = _safe_num(curve.get("volatility_index"), 0.0)

    gate = payload.get("gate") or {}
    if not isinstance(gate, dict):
        gate = {}
    gate_status = str(gate.get("status") or "UNKNOWN")
    counted = bool(gate.get("counted_for_agi", False))

    # Tone rules (simple + consistent)
    if gate_status.upper() != "PASS":
        headline = "⚠️ HOLD. Integrity gate is not GREEN."
        action = "Run SIS/SPS checks, fix RED/AMBER items, then log training again."
    else:
        headline = "🟢 GREEN. Training counts."
        action = "Push one clean rep. Then increase difficulty only after stability holds."

    # Difficulty coaching
    if difficulty == "BEGINNER":
        diff_msg = "Beginner mode: focus on clean fundamentals and correct callouts."
    elif difficulty == "ADVERSARIAL":
        diff_msg = "Adversarial mode: expect deception, cross-domain noise, and pressure."
    else:
        diff_msg = "Intermediate mode: balance speed with defensible tradecraft."

    # Curve coaching
    if slope < 0:
        curve_msg = "Your slope is negative. That usually means inconsistency or difficulty spikes too soon."
    elif slope > 0:
        curve_msg = "Your slope is positive. That means consistency is compounding."
    else:
        curve_msg = "Your slope is flat. That’s fine—stability first, then deliberate increase."

    msg_lines: List[str] = []
    msg_lines.append(f"🦉 Obasi Coach — {trainee}")
    msg_lines.append(f"Difficulty: {difficulty}")
    msg_lines.append("")
    msg_lines.append(headline)
    msg_lines.append(f"Gate: {gate_status} | Counted for AGI: {counted}")
    msg_lines.append("")
    msg_lines.append(diff_msg)
    msg_lines.append(curve_msg)
    msg_lines.append("")
    msg_lines.append("Live Metrics:")
    msg_lines.append(f"• AGI: {agi:.1f}")
    msg_lines.append(f"• Improvement slope: {slope:.2f}")
    msg_lines.append(f"• Volatility index: {volatility:.3f}")
    msg_lines.append("")
    msg_lines.append(f"Next action: {action}")

    return "\n".join(msg_lines)

