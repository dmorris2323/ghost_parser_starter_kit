# apps/gui/obasi_training_coach.py
from __future__ import annotations

# Duplicate on purpose: keep training apps stable no matter how Streamlit sets sys.path.
from typing import Any

try:
    # Prefer the canonical coach in src if available
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent
    src_path = str((repo_root / "src").resolve())
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore
except Exception:
    # Fallback local implementation
    def build_obasi_training_coach_speech(*args: Any, **kwargs: Any):
        trainee = kwargs.get("trainee_name") or "Trainee"
        difficulty = kwargs.get("difficulty") or "INTERMEDIATE"
        return f"🦉 Obasi Coach — {trainee}\nDifficulty: {difficulty}\n(Status: fallback coach)"

