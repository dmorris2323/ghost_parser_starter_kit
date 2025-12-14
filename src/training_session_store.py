"""
training_session_store.py

Single source of truth for training session persistence.

Rules:
- No other module writes sessions JSON directly.
- All reads/writes go through load_sessions() / append_session().
- Session schema is normalized on load to prevent KeyError drift.

Storage path (relative to repo root):
- src/docs/training/training_sessions.json
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SESSIONS_PATH = Path("src") / "docs" / "training" / "training_sessions.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "sessions": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return raw
        # If someone wrote a list by mistake, salvage it
        if isinstance(raw, list):
            return {"schema_version": 1, "sessions": raw}
    except Exception:
        pass
    return {"schema_version": 1, "sessions": []}


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


@dataclass
class TrainingSession:
    session_id: str
    created_at: str
    difficulty: str
    gate_status: str  # GREEN / YELLOW / RED / UNKNOWN
    score: float      # 0-100 training score proxy
    notes: str = ""
    tags: Optional[List[str]] = None
    # Optional fields that may be present later
    validation_context: Optional[str] = None
    pattern_id: Optional[str] = None


def _normalize_session(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarantee required keys exist so GUIs never KeyError.
    """
    if not isinstance(d, dict):
        d = {}
    d = dict(d)

    d.setdefault("session_id", d.get("id") or str(uuid.uuid4()))
    d.setdefault("created_at", d.get("created_at") or _utc_now_iso())
    d.setdefault("difficulty", (d.get("difficulty") or "BEGINNER"))
    d.setdefault("gate_status", (d.get("gate_status") or "UNKNOWN"))
    d.setdefault("score", float(d.get("score") or 0.0))
    d.setdefault("notes", d.get("notes") or "")
    d.setdefault("tags", d.get("tags") if isinstance(d.get("tags"), list) else [])
    d.setdefault("validation_context", d.get("validation_context"))
    d.setdefault("pattern_id", d.get("pattern_id"))
    return d


def load_sessions() -> List[Dict[str, Any]]:
    raw = _read_json(SESSIONS_PATH)
    sessions = raw.get("sessions", [])
    if not isinstance(sessions, list):
        sessions = []
    normalized = [_normalize_session(s) for s in sessions]
    # Persist normalization to prevent future drift
    _write_json(SESSIONS_PATH, {"schema_version": 1, "sessions": normalized})
    return normalized


def append_session(
    *,
    difficulty: str,
    gate_status: str,
    score: float,
    notes: str = "",
    tags: Optional[List[str]] = None,
    validation_context: Optional[str] = None,
    pattern_id: Optional[str] = None,
) -> Dict[str, Any]:
    sessions = load_sessions()

    sess = TrainingSession(
        session_id=str(uuid.uuid4()),
        created_at=_utc_now_iso(),
        difficulty=str(difficulty or "BEGINNER").upper(),
        gate_status=str(gate_status or "UNKNOWN").upper(),
        score=float(score or 0.0),
        notes=str(notes or ""),
        tags=tags or [],
        validation_context=validation_context,
        pattern_id=pattern_id,
    )

    d = _normalize_session(asdict(sess))
    sessions.append(d)
    _write_json(SESSIONS_PATH, {"schema_version": 1, "sessions": sessions})
    return d

