# src/training_session_store.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from training_paths import (
    ensure_dirs,
    sessions_path_latest,
    resolve_existing,
)

ALLOWED_DIFFICULTIES = {"BEGINNER", "INTERMEDIATE", "ADVERSARIAL"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_sessions() -> List[Dict[str, Any]]:
    """
    Loads sessions from canonical docs/training, falling back to src/docs/training.
    Always returns a list.
    """
    ensure_dirs()
    p = resolve_existing(sessions_path_latest())
    if not p.exists():
        return []

    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        sessions = raw.get("sessions", [])
        if isinstance(sessions, list):
            return sessions
        return []
    except Exception:
        return []


def write_sessions(sessions: List[Dict[str, Any]]) -> Path:
    ensure_dirs()
    p = sessions_path_latest()
    payload = {
        "version": 1,
        "generated_at": _utc_now_iso(),
        "sessions": sessions,
    }
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


def append_session(
    *,
    trainee_name: str,
    difficulty: str,
    score: float,
    max_score: float,
    notes: str = "",
    tags: Optional[List[str]] = None,
    gate_pre_status: str = "UNKNOWN",
    gate_post_status: str = "UNKNOWN",
) -> Dict[str, Any]:
    """
    Appends a session to training_sessions.json.
    """
    difficulty = (difficulty or "").upper().strip()
    if difficulty not in ALLOWED_DIFFICULTIES:
        difficulty = "INTERMEDIATE"

    tags = tags or []

    sessions = load_sessions()
    session = {
        "timestamp": _utc_now_iso(),
        "trainee_name": trainee_name.strip() or "Unknown",
        "difficulty": difficulty,
        "score": float(score),
        "max_score": float(max_score),
        "notes": notes.strip(),
        "tags": tags,
        "gate_pre_status": gate_pre_status,
        "gate_post_status": gate_post_status,
    }
    sessions.append(session)
    write_sessions(sessions)
    return session

