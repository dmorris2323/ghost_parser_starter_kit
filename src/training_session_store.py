# src/training_session_store.py
"""
training_session_store.py

Single source of truth for training sessions storage.

Hard contract:
- load_sessions() -> list[dict]
- append_session(session: dict) -> dict (written session)

No imports from certification / curve / feedback engines.
(Prevents circular imports.)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


STORE_PATH = Path("src") / "docs" / "training" / "training_sessions.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _safe_read_json(path: Path) -> Any:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _normalize_session(s: Dict[str, Any]) -> Dict[str, Any]:
    # Accept older keys + enforce stable keys used by the UI/curve engines.
    sid = s.get("session_id") or s.get("id") or s.get("Session") or f"session_{int(datetime.now().timestamp())}"
    ts = s.get("timestamp") or s.get("ts") or s.get("created_at") or _utc_now_iso()

    difficulty = str(s.get("difficulty", s.get("Difficulty", "UNKNOWN"))).upper().strip()
    if difficulty not in {"BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"}:
        difficulty = "UNKNOWN"

    score = s.get("score", s.get("Score", 0))
    try:
        score = float(score)
    except Exception:
        score = 0.0

    # gate + counting flags
    gate_pre = str(s.get("gate_pre_status", s.get("gate_status", "UNKNOWN"))).upper().strip()
    gate_post = str(s.get("gate_post_status", "UNKNOWN")).upper().strip()
    counted = bool(s.get("counted_for_agi", False))

    return {
        "session_id": str(sid),
        "timestamp": str(ts),
        "difficulty": difficulty,
        "score": score,
        "scenario_id": str(s.get("scenario_id", "")),
        "pattern_id": str(s.get("pattern_id", "")),
        "gate_pre_status": gate_pre,
        "gate_post_status": gate_post,
        "counted_for_agi": counted,
        "notes": str(s.get("notes", "")),
    }


def load_sessions() -> List[Dict[str, Any]]:
    raw = _safe_read_json(STORE_PATH)
    if not raw:
        return []
    if isinstance(raw, dict):
        sessions = raw.get("sessions", [])
    else:
        sessions = raw
    if not isinstance(sessions, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in sessions:
        if isinstance(item, dict):
            out.append(_normalize_session(item))
    return out


def append_session(session: Dict[str, Any]) -> Dict[str, Any]:
    sessions = load_sessions()
    normalized = _normalize_session(session)
    sessions.append(normalized)
    _safe_write_json(STORE_PATH, {"sessions": sessions})
    return normalized

