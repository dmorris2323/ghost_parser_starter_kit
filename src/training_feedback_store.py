# src/training_feedback_store.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from training_paths import ensure_dirs, feedback_path_latest, resolve_existing


def load_latest_feedback() -> Dict[str, Any]:
    """
    Loads the most recent training feedback recommendation.
    Falls back to legacy location automatically.
    """
    ensure_dirs()
    p = resolve_existing(feedback_path_latest())
    if not p.exists():
        return {"status": "NONE", "message": "No feedback recorded yet."}

    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            return obj
        return {"status": "ERROR", "message": "Feedback file not a JSON object."}
    except Exception as e:
        return {"status": "ERROR", "message": f"Failed to read feedback: {e}"}


def write_latest_feedback(feedback: Dict[str, Any]) -> Path:
    ensure_dirs()
    p = feedback_path_latest()
    p.write_text(json.dumps(feedback, indent=2), encoding="utf-8")
    return p

