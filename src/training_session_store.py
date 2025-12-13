# src/training_session_store.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from training_grading_weights import normalize_difficulty, get_profile
from training_validation_gate import GateDecision, decide_training_gate


DEFAULT_SESSIONS_PATH = Path("src/docs/training/training_sessions.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "updated_at": _utc_now(), "sessions": []}
    try:
        return json.loads(path.read_text())
    except Exception:
        # fail closed: don’t crash training
        return {"version": 1, "updated_at": _utc_now(), "sessions": []}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def load_sessions(path: Path = DEFAULT_SESSIONS_PATH) -> List[Dict[str, Any]]:
    raw = _read_json(path)
    sessions = raw.get("sessions", [])
    return sessions if isinstance(sessions, list) else []


def append_session(
    *,
    trainee_name: str,
    difficulty: str,
    rubric: Dict[str, float],
    scenario_id: str,
    pattern_id: Optional[str] = None,
    pattern_seed: Optional[int] = None,
    sis_status: Optional[str] = None,
    sps_status: Optional[str] = None,
    validation_verdict: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    path: Path = DEFAULT_SESSIONS_PATH,
) -> Dict[str, Any]:
    """
    Stores ONE session entry.
    rubric must include: accuracy, reasoning, stability, speed (0..100).
    Gate is decided here and stored with the session.
    """
    d = normalize_difficulty(difficulty)
    profile = get_profile(d)

    # gate decision
    gate: GateDecision = decide_training_gate(
        sis_status=sis_status,
        sps_status=sps_status,
        validation_verdict=validation_verdict,
    )

    session = {
        "session_id": f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{abs(hash((trainee_name, scenario_id)))%9999:04d}",
        "created_at": _utc_now(),
        "trainee_name": str(trainee_name).strip() or "UNKNOWN",
        "difficulty": d,
        "scenario_id": scenario_id,
        "pattern_id": pattern_id,
        "pattern_seed": pattern_seed,
        "rubric": {
            "accuracy": float(rubric.get("accuracy", 0.0)),
            "reasoning": float(rubric.get("reasoning", 0.0)),
            "stability": float(rubric.get("stability", 0.0)),
            "speed": float(rubric.get("speed", 0.0)),
        },
        "difficulty_profile": {
            "volatility_tolerance": profile.volatility_tolerance,
            "score_multiplier": profile.score_multiplier,
        },
        "gates": gate.to_dict(),
        "session_valid": bool(gate.allowed),
        "invalid_reason": None if gate.allowed else gate.reason,
        "extra": extra or {},
    }

    payload = _read_json(path)
    sessions = payload.get("sessions", [])
    if not isinstance(sessions, list):
        sessions = []
    sessions.append(session)
    payload["version"] = int(payload.get("version", 1))
    payload["updated_at"] = _utc_now()
    payload["sessions"] = sessions
    _write_json(path, payload)

    return {
        "path": str(path),
        "session": session,
        "total_sessions": len(sessions),
        "valid_sessions": len([s for s in sessions if s.get("session_valid")]),
    }

