# src/training_session_store.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from training_grading_weights import score_from_rubric
from training_validation_gate import decide_training_gate, summarize_gate


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # file is src/training_session_store.py → repo root is parent of src
    return Path(__file__).resolve().parents[1]


def _store_path() -> Path:
    p = _repo_root() / "src" / "docs" / "training" / "training_sessions.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_sessions() -> List[Dict[str, Any]]:
    p = _store_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text())
        sessions = raw.get("sessions", [])
        return sessions if isinstance(sessions, list) else []
    except Exception:
        return []


def _write_sessions(sessions: List[Dict[str, Any]]) -> None:
    p = _store_path()
    payload = {"version": 1, "updated_at": _utc_now(), "sessions": sessions}
    p.write_text(json.dumps(payload, indent=2))


def append_session(
    trainee_name: str,
    difficulty: str,
    rubric: Dict[str, float],
    scenario_id: str,
    pattern_id: Optional[str],
    pattern_seed: Optional[int],
    sis_status: str,
    sps_status: str,
    validation_verdict: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    sessions = load_sessions()

    gate = decide_training_gate(sis_status, sps_status, validation_verdict)
    weighted_score = score_from_rubric(difficulty, rubric)

    session = {
        "created_at": _utc_now(),
        "trainee_name": trainee_name,
        "difficulty": (difficulty or "INTERMEDIATE").upper().strip(),
        "scenario_id": scenario_id,
        "pattern_id": pattern_id,
        "pattern_seed": pattern_seed,
        "rubric": rubric,
        "weighted_score": round(weighted_score, 2),
        "sis_status": (sis_status or "UNKNOWN").upper().strip(),
        "sps_status": (sps_status or "UNKNOWN").upper().strip(),
        "validation_verdict": (validation_verdict or "UNKNOWN").upper().strip(),
        "session_valid": bool(gate.ok),
        "invalid_reason": None if gate.ok else gate.reason,
        "gate_summary": summarize_gate(gate),
        "extra": extra or {},
    }

    sessions.append(session)
    _write_sessions(sessions)

    valid_sessions = [s for s in sessions if s.get("session_valid") is True]
    return {
        "session": session,
        "total_sessions": len(sessions),
        "valid_sessions": len(valid_sessions),
        "store_path": str(_store_path()),
    }

