# src/apps/gui/obasi_training_coach.py
from __future__ import annotations

from typing import Any

# Delegate to the canonical implementation in src/
try:
    from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore
except Exception:
    # ultra-safe fallback
    def build_obasi_training_coach_speech(**payload: Any) -> str:
        trainee = str(payload.get("trainee_name") or "Operator")
        return f"🦉 OBASI (fallback): Coaching offline for {trainee}. Fix imports."

