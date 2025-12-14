# src/training_session_store.py
"""
training_session_store.py

Single source of truth for training sessions persistence.

Hard rules:
- This module does NOT import training_policy, operator_certification_engine, or any GUI code.
- This module ONLY reads/writes the sessions JSON file.
- Gate enforcement and certification logic live elsewhere.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SESSIONS_PATH = Path("src") / "docs" / "training" / "training_sessions.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _ensure_session_shape(s: Dict[str, Any], idx: int) -> Dict[str, Any]:
    # Backfill required keys safely so older sessions don't break the UI.
    if "session_id" not in s or not s.get("session_id"):
        s["session_id"] = f"sess_{idx+1:04d}"
    if "created_at" not in s or not s.get("created_at"):
        s["created_at"] = _utc_now_iso()

    # Defaults expected by downstream logic
    s.setdefault("trainee_name", "Ghost")
    s.setdefault("difficulty", "INTERMEDIATE")
    s.setdefault("score", 0.0)
    s.setdefault("scenario_id", "")
    s.setdefault("pattern_id", "")
    s.setdefault("notes", "")
    s.setdefault("gate_pre_status", "UNKNOWN")
    s.setdefault("gate_post_status", "UNKNOWN")
    s.setdefault("counted_for_agi", False)

    return s


def load_sessions() -> List[Dict[str, Any]]:
    raw = _read_json(SESSIONS_PATH)
    if not raw:
        return []
    if isinstance(raw, dict):
        sessions = raw.get("sessions", [])
    else:
        sessions = raw

    if not isinstance(sessions, list):
        return []

    fixed: List[Dict[str, Any]] = []
    changed = False

    for i, item in enumerate(sessions):
        if isinstance(item, dict):
            before = dict(item)
            fixed_item = _ensure_session_shape(item, i)
            fixed.append(fixed_item)
            if fixed_item != before:
                changed = True

    # Write back only if we had to backfill / repair old sessions.
    if changed:
        _write_json(SESSIONS_PATH, {"sessions": fixed})

    return fixed


def append_session(session: Dict[str, Any]) -> Dict[str, Any]:
    sessions = load_sessions()

    # Generate a stable session id
    next_id = f"sess_{len(sessions)+1:04d}"
    session = dict(session)
    session.setdefault("session_id", next_id)
    session.setdefault("created_at", _utc_now_iso())

    # Ensure all expected keys exist
    session = _ensure_session_shape(session, len(sessions))

    sessions.append(session)
    _write_json(SESSIONS_PATH, {"sessions": sessions})
    return session

