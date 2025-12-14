# apps/gui/obasi_training_coach.py
"""
Duplicate on purpose.

Some Streamlit/PYTHONPATH runs have historically pulled this location.
We keep it identical to src/obasi_training_coach.py so either import path works.
"""

from __future__ import annotations

# We import from src version if available; otherwise fall back to local definition.
try:
    from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore
except Exception:
    # If this file is imported directly without src on sys.path,
    # we provide a minimal safe fallback.
    def build_obasi_training_coach_speech(**payload):  # type: ignore
        return "OBASI COACH (SAFE MODE): fallback coach loaded; check sys.path to include /src."

