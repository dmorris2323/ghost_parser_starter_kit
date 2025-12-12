# training_session_store.py
# Canonical store for War Room + Training Dashboard session logs.

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


DEFAULT_PATH = Path("src/docs/training/training_sessions.json")


def _ensure_store(path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w") as f:
            json.dump({"version": 1, "created_at": datetime.utcnow().isoformat(), "sessions": []}, f, indent=2)


def load_sessions(path: Path = DEFAULT_PATH) -> Dict[str, Any]:
    _ensure_store(path)
    with open(path, "r") as f:
        return json.load(f)


def append_session(session: Dict[str, Any], path: Path = DEFAULT_PATH) -> Dict[str, Any]:
    """
    Appends a training session record.
    Returns { "json_path": ..., "session_id": ... }.
    """
    store = load_sessions(path)
    sessions: List[Dict[str, Any]] = store.get("sessions", [])

    session_id = f"ts_{int(datetime.utcnow().timestamp())}"
    record = {
        "session_id": session_id,
        "recorded_at": datetime.utcnow().isoformat(),
        **session,
    }
    sessions.append(record)

    store["sessions"] = sessions

    with open(path, "w") as f:
        json.dump(store, f, indent=2)

    return {"json_path": str(path), "session_id": session_id}

