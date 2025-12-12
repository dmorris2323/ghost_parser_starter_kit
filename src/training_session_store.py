"""
training_session_store.py

Creates/updates the canonical training sessions file:
  src/docs/training/training_sessions.json

Each session stores:
- difficulty (string)
- difficulty_weight (float, from difficulty_scaling_engine)
- score (0–100)
- rubric breakdown (optional)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from difficulty_scaling_engine import normalize_difficulty, get_weight


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _sessions_path() -> Path:
    return _repo_root() / "src" / "docs" / "training" / "training_sessions.json"


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_sessions() -> Dict[str, Any]:
    p = _sessions_path()
    if not p.exists():
        return {"schema_version": 1, "generated_at": _utc_iso(), "sessions": []}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {"schema_version": 1, "generated_at": _utc_iso(), "sessions": []}


def append_training_session(
    difficulty: str,
    score: float,
    scenario_id: Optional[str] = None,
    rubric: Optional[Dict[str, Any]] = None,
    notes: str = "",
) -> Dict[str, Any]:
    d = normalize_difficulty(difficulty)
    w = float(get_weight(d))

    payload = load_sessions()
    sessions = payload.get("sessions", [])
    if not isinstance(sessions, list):
        sessions = []

    entry: Dict[str, Any] = {
        "ts_utc": _utc_iso(),
        "difficulty": d,
        "difficulty_weight": w,
        "score": float(score),
        "scenario_id": scenario_id or "UNKNOWN",
        "rubric": rubric or {},
        "notes": notes,
    }
    sessions.append(entry)

    payload["schema_version"] = 1
    payload["generated_at"] = _utc_iso()
    payload["sessions"] = sessions

    out_path = _sessions_path()
    _safe_mkdir(out_path.parent)
    out_path.write_text(json.dumps(payload, indent=2))
    return {"json_path": str(out_path), "total_sessions": len(sessions), "last_session": entry}


if __name__ == "__main__":
    r = append_training_session("INTERMEDIATE", 75.0, scenario_id="SMOKE_TEST", rubric={"example": 1}, notes="manual test")
    print("Training sessions updated:")
    print(f"  JSON: {r['json_path']}")
    print(f"  Total sessions: {r['total_sessions']}")

