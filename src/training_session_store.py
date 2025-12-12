# src/training_session_store.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _training_dir() -> Path:
    d = _repo_root() / "src" / "docs" / "training"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sessions_path() -> Path:
    return _training_dir() / "training_sessions.json"


def load_sessions() -> List[Dict[str, Any]]:
    p = sessions_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("sessions"), list):
            return raw["sessions"]
        if isinstance(raw, list):
            return raw
        return []
    except Exception:
        return []


def save_sessions(sessions: List[Dict[str, Any]]) -> None:
    p = sessions_path()
    payload = {"version": 1, "updated_at": _utc_now(), "sessions": sessions}
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_session(session: Dict[str, Any]) -> Dict[str, Any]:
    sessions = load_sessions()
    session = dict(session)
    session.setdefault("session_id", f"sess_{len(sessions)+1:04d}")
    session.setdefault("timestamp", _utc_now())
    sessions.append(session)
    save_sessions(sessions)
    return session

