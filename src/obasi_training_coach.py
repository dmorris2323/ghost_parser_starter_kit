# src/obasi_training_coach.py
from __future__ import annotations

from typing import Any, Dict


def build_obasi_training_coach_speech(**payload: Any) -> str:
    """
    Stable, kwargs-based interface used by Streamlit training apps.

    Always returns a STRING (never a dict) so the UI can render it safely.
    Safe to call even with missing fields.
    """
    trainee = str(payload.get("trainee_name", "Operator")).strip() or "Operator"
    difficulty = str(payload.get("difficulty", "INTERMEDIATE")).strip()
    agi = payload.get("AGI", payload.get("agi", None))
    slope = payload.get("improvement_slope", payload.get("slope", None))
    vol = payload.get("volatility_index", payload.get("volatility", None))

    lines = []
    lines.append(f"🦉 Obasi Coaching — {trainee}")
    lines.append(f"Difficulty: {difficulty}")

    if agi is not None:
        lines.append(f"AGI: {agi}")
    if slope is not None:
        lines.append(f"Improvement slope: {slope}")
    if vol is not None:
        lines.append(f"Volatility: {vol}")

    # guidance logic (simple, non-hype, actionable)
    if slope is not None:
        try:
            s = float(slope)
            if s < 0:
                lines.append("Recommendation: slow down and stabilize. Run 2 baseline sessions before going harder.")
            elif s == 0:
                lines.append("Recommendation: you’re flat. Increase repetitions at same difficulty to build consistency.")
            else:
                lines.append("Recommendation: trend is positive. Step difficulty up ONE level, not two.")
        except Exception:
            lines.append("Recommendation: keep sessions consistent and watch slope/volatility stabilize.")

    if vol is not None:
        try:
            v = float(vol)
            if v >= 15:
                lines.append("Volatility is high. Your score is bouncing—tighten your process (same pattern, same difficulty, 3 reps).")
        except Exception:
            pass

    return "\n".join(lines)


# Optional legacy helper (if any older code imported this)
def build_obasi_training_coach_payload(**payload: Any) -> Dict[str, Any]:
    """
    Back-compat helper: returns a dict payload if any older code expects it.
    """
    return {"message": build_obasi_training_coach_speech(**payload), "payload": payload}

