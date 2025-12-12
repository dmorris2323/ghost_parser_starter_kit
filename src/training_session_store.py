"""
training_session_store.py

Persistent store for training sessions.
Difficulty is first-class and enforced via training_config.
"""

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List

from difficulty_control_engine import get_difficulty_profile
from training_config import effective_difficulty, load_training_config

STORE_PATH = Path("src/docs/training/training_sessions.json")
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_sessions() -> List[Dict[str, Any]]:
    if not STORE_PATH.exists():
        return []
    try:
        data = json.loads(STORE_PATH.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def append_training_session(session: Dict[str, Any], gate: bool = True) -> Dict[str, Any]:
    sessions = load_sessions()

    requested = session.get("difficulty", "INTERMEDIATE")
    enforced = effective_difficulty(requested)
    profile = get_difficulty_profile(enforced)

    cfg = load_training_config()
    source = "manual"
    if cfg.get("instructor_lock"):
        source = "locked"
    if session.get("difficulty_source"):
        source = str(session.get("difficulty_source"))

    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "difficulty": profile.name,
        "difficulty_source": source,
        "mode": session.get("mode", "training"),
        "score": float(session.get("score", 0.0)),
        "notes": (session.get("notes") or "").strip(),
        "grading_expectation": profile.grading_expectation,
    }

    sessions.append(record)
    STORE_PATH.write_text(json.dumps(sessions, indent=2))

    return {
        "count": len(sessions),
        "difficulty": profile.name,
        "difficulty_source": source,
        "path": str(STORE_PATH),
    }

