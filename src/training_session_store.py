# src/training_session_store.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # src/ -> repo root
    return Path(__file__).resolve().parents[1]


def _sessions_path() -> Path:
    # Keep all training artifacts under src/docs/training
    return _repo_root() / "src" / "docs" / "training" / "training_sessions.json"


def ensure_training_dirs() -> None:
    p = _sessions_path()
    p.parent.mkdir(parents=True, exist_ok=True)


def load_sessions() -> List[Dict[str, Any]]:
    ensure_training_dirs()
    p = _sessions_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text())
        sessions = raw.get("sessions", [])
        if isinstance(sessions, list):
            return sessions
        return []
    except Exception:
        return []


def write_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    ensure_training_dirs()
    p = _sessions_path()
    payload = {
        "version": 1,
        "updated_at": _utc_now(),
        "sessions": sessions,
    }
    p.write_text(json.dumps(payload, indent=2))
    return {"path": str(p), "count": len(sessions)}


def append_session(session: Dict[str, Any]) -> Dict[str, Any]:
    sessions = load_sessions()
    sid = f"TS-{len(sessions)+1:05d}"
    stamped = dict(session)
    stamped["session_id"] = sid
    stamped.setdefault("created_at", _utc_now())
    sessions.append(stamped)
    meta = write_sessions(sessions)
    stamped["store_path"] = meta["path"]
    return stamped

