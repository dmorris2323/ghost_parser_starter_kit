"""
src/apps/gui/obasi_training_coach.py

Forward-compatible Obasi coach builder.
Must never break callers (accept any args/kwargs).
"""

from __future__ import annotations
from typing import Any


def build_obasi_training_coach_speech(*args: Any, **kwargs: Any) -> str:
    # Grab commonly passed fields (optional)
    trainee = str(kwargs.get("trainee_name") or kwargs.get("operator") or "Trainee")
    difficulty = str(kwargs.get("difficulty") or "INTERMEDIATE").upper()

    agi = _sf(kwargs.get("agi"))
    slope = _sf(kwargs.get("improvement_slope"))
    vol = _sf(kwargs.get("volatility_index"))
    last = _sf(kwargs.get("last_score"))
    dwa = _sf(kwargs.get("difficulty_weighted_average"))
    notes = str(kwargs.get("notes") or "").strip()

    trend = "flat"
    if slope > 0.5:
        trend = "up"
    elif slope < -0.5:
        trend = "down"

    stability = "stable"
    if vol >= 12:
        stability = "volatile"
    elif 7 <= vol < 12:
        stability = "mixed"

    lines = [
        f"🦉 Obasi Coach — {trainee}",
        f"Difficulty: {difficulty}",
    ]

    if agi > 0:
        lines.append(f"AGI: {agi:.1f} | DWA: {dwa:.1f} | Last: {last:.1f}")
        lines.append(f"Trend: {trend} (slope {slope:.2f}) | Stability: {stability} (vol {vol:.2f})")
    else:
        lines.append("AGI: insufficient sessions. Run a few reps to establish baseline.")

    if trend == "down":
        lines.append("Directive: tighten evidence discipline. Win the process, then speed up.")
    elif trend == "flat":
        lines.append("Directive: change ONE lever—raise difficulty OR raise clarity. Not both.")
    else:
        lines.append("Directive: keep pressure on. Raise difficulty gradually; protect consistency.")

    if stability == "volatile":
        lines.append("Stability fix: reduce randomness. Use checklists. Explain why each alert matters.")
    elif stability == "mixed":
        lines.append("Stability fix: focus on repeatable steps. Your output should look the same every rep.")

    if notes:
        lines.append(f"Note: {notes}")

    return "\n".join(lines)


def _sf(v: Any) -> float:
    try:
        return 0.0 if v is None else float(v)
    except Exception:
        return 0.0

