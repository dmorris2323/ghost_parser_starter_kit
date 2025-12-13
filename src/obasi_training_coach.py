# src/obasi_training_coach.py
from __future__ import annotations

from typing import Any, Dict, Optional


def build_obasi_training_coach_speech(**payload: Any) -> str:
    """
    Stable public contract:
      - Accepts ANY keyword arguments (future-proof)
      - Returns a STRING (never dict), so Streamlit can render without type errors

    Expected (optional) fields:
      trainee_name: str
      difficulty: str
      curve: dict with AGI / improvement_slope / volatility_index
      last_session: dict with session_valid + invalid_reason
      gate_summary: str
    """
    trainee = str(payload.get("trainee_name") or "Operator").strip()
    difficulty = str(payload.get("difficulty") or "INTERMEDIATE").upper().strip()

    curve = payload.get("curve") or {}
    agi = curve.get("AGI", 0.0)
    slope = curve.get("improvement_slope", 0.0)
    vol = curve.get("volatility_index", 0.0)

    last_session = payload.get("last_session") or {}
    valid = bool(last_session.get("session_valid", False))
    invalid_reason = last_session.get("invalid_reason")

    gate_summary = payload.get("gate_summary")

    # Tone logic (simple, reliable)
    if valid:
        gate_line = "✅ Session counted toward AGI."
    else:
        gate_line = f"⛔ Session blocked (did not count). Reason: {invalid_reason or 'Gate failure/unknown'}"

    # Coaching based on slope + volatility
    if slope > 0.5:
        trend = "Trend: improving. Keep pressure on."
    elif slope < -0.5:
        trend = "Trend: regressing. Slow down, tighten process, eliminate noise."
    else:
        trend = "Trend: flat. Increase reps or raise difficulty gradually."

    if vol >= 15:
        stability = "Stability: volatile. Standardize your workflow and reduce randomness."
    elif vol >= 8:
        stability = "Stability: moderate variance. Good — tighten a few weak points."
    else:
        stability = "Stability: controlled. You’re building consistency."

    lines = []
    lines.append(f"🦉 **OBASI TRAINING COACH**")
    lines.append(f"- Trainee: {trainee}")
    lines.append(f"- Difficulty: {difficulty}")
    if gate_summary:
        lines.append(f"- Gate summary: {gate_summary}")
    lines.append("")
    lines.append(f"**Current Metrics**")
    lines.append(f"- AGI: {agi}")
    lines.append(f"- Improvement slope: {slope}")
    lines.append(f"- Volatility: {vol}")
    lines.append("")
    lines.append(gate_line)
    lines.append(trend)
    lines.append(stability)

    # One actionable next step
    if not valid:
        lines.append("")
        lines.append("**Next action:** Get SIS+SPS GREEN and validation PASS/WARN, then rerun the same scenario at the same difficulty to prove stability.")
    else:
        lines.append("")
        lines.append("**Next action:** Run 1 more session at the same difficulty, then 1 step harder. We want controlled deltas, not chaos.")

    return "\n".join(lines)

