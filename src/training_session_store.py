"""
training_session_store.py

Single source of truth for training sessions storage.

- Reads/writes: docs/training/training_sessions.json
- Provides:
    load_sessions() -> list[dict]
    append_session(session: dict) -> dict (normalized + stored)

Design rules:
- NO imports from operator_certification_engine
- NO imports from training_policy
- Avoid circular imports at all costs
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


TRAINING_DIR = Path("docs") / "training"
SESSIONS_PATH = TRAINING_DIR / "training_sessions.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _normalize_session(s: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforces schema so GUIs never KeyError.
    """
    out: Dict[str, Any] = dict(s) if isinstance(s, dict) else {}

    # Required identifiers
    out["session_id"] = str(out.get("session_id") or uuid.uuid4().hex[:12])
    out["timestamp"] = str(out.get("timestamp") or _utc_now_iso())

    # Core training knobs
    out["difficulty"] = str(out.get("difficulty") or "INTERMEDIATE").upper()
    out["pattern_id"] = out.get("pattern_id") or None

    # Results
    out["verdict"] = str(out.get("verdict") or "UNKNOWN").upper()
    out["score"] = float(out.get("score") or 0.0)

    # Gates (SIS/SPS)
    gates = out.get("gates") if isinstance(out.get("gates"), dict) else {}
    out["gates"] = gates
    out["counts_toward_agi"] = bool(out.get("counts_toward_agi", False))

    # Optional notes
    out["notes"] = str(out.get("notes") or "")

    return out


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

    normalized = [_normalize_session(s) for s in sessions if isinstance(s, dict)]
    return normalized


def append_session(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize session, append to store, return normalized session.
    """
    s = _normalize_session(session)
    sessions = load_sessions()

    # Prevent accidental duplicates by session_id
    existing_ids = {x.get("session_id") for x in sessions if isinstance(x, dict)}
    if s["session_id"] in existing_ids:
        # If collision, mint a new id
        s["session_id"] = uuid.uuid4().hex[:12]

    sessions.append(s)

    payload = {
        "version": 1,
        "updated_at": _utc_now_iso(),
        "sessions": sessions,
    }
    _write_json(SESSIONS_PATH, payload)
    return s

