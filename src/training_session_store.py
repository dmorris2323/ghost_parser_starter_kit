# src/training_session_store.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # Assumes this file lives in repo_root/src/
    return Path(__file__).resolve().parents[1]


def training_dir() -> Path:
    return _repo_root() / "src" / "docs" / "training"


def sessions_path() -> Path:
    return training_dir() / "training_sessions.json"


@dataclass
class TrainingSession:
    session_id: str
    timestamp_utc: str
    trainee_name: str
    difficulty: str
    scenario_id: str
    pattern_id: Optional[str]
    rubric_scores: Dict[str, float]
    final_score: float
    notes: str = ""
    sis_status: Optional[str] = None
    sps_status: Optional[str] = None
    gate_passed: Optional[bool] = None


def ensure_store() -> None:
    training_dir().mkdir(parents=True, exist_ok=True)
    p = sessions_path()
    if not p.exists():
        p.write_text(json.dumps({"version": 1, "sessions": []}, indent=2))


def load_sessions() -> List[Dict[str, Any]]:
    ensure_store()
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
    ensure_store()
    p = sessions_path()
    p.write_text(json.dumps({"version": 1, "sessions": sessions}, indent=2))


def append_session(session: TrainingSession) -> Dict[str, Any]:
    sessions = load_sessions()
    rec = asdict(session)
    sessions.append(rec)
    write_sessions(sessions)
    return rec


def new_session_id(prefix: str = "S") -> str:
    # readable + collision-safe enough for local store
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}"


def build_session(
    trainee_name: str,
    difficulty: str,
    scenario_id: str,
    final_score: float,
    rubric_scores: Dict[str, float],
    pattern_id: Optional[str] = None,
    notes: str = "",
    sis_status: Optional[str] = None,
    sps_status: Optional[str] = None,
    gate_passed: Optional[bool] = None,
) -> TrainingSession:
    return TrainingSession(
        session_id=new_session_id(),
        timestamp_utc=_utc_now_iso(),
        trainee_name=trainee_name or "Trainee",
        difficulty=(difficulty or "INTERMEDIATE").upper(),
        scenario_id=scenario_id or "DEFAULT",
        pattern_id=pattern_id,
        rubric_scores=rubric_scores or {},
        final_score=float(final_score),
        notes=notes or "",
        sis_status=sis_status,
        sps_status=sps_status,
        gate_passed=gate_passed,
    )

