from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # src/training_session_store.py -> parents[1] == src, parents[2] == repo root
    return Path(__file__).resolve().parents[1].parent


def training_dir() -> Path:
    return _repo_root() / "src" / "docs" / "training"


def sessions_path() -> Path:
    return training_dir() / "training_sessions.json"


def ensure_training_store() -> None:
    d = training_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = sessions_path()
    if not p.exists():
        p.write_text(json.dumps({"schema_version": 1, "created_at": _utc_now_iso(), "sessions": []}, indent=2))


def load_sessions() -> List[Dict[str, Any]]:
    ensure_training_store()
    p = sessions_path()
    try:
        raw = json.loads(p.read_text())
        sessions = raw.get("sessions", [])
        if isinstance(sessions, list):
            return sessions
        return []
    except Exception:
        return []


def write_sessions(sessions: List[Dict[str, Any]]) -> None:
    ensure_training_store()
    payload = {"schema_version": 1, "updated_at": _utc_now_iso(), "sessions": sessions}
    sessions_path().write_text(json.dumps(payload, indent=2))


def append_session(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appends a session and returns the stored record (with id/timestamps).
    """
    ensure_training_store()
    sessions = load_sessions()

    rec = dict(session)
    rec.setdefault("created_at", _utc_now_iso())
    rec.setdefault("session_id", f"sess_{len(sessions) + 1:05d}")

    sessions.append(rec)
    write_sessions(sessions)
    return rec

