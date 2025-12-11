#!/usr/bin/env python3
"""
gll_training_session_logger.py

Ghost Lantern Labs – Training Session Logger
--------------------------------------------

Purpose:
    Take the existing Training Mode Student Brief and turn it into a
    trackable training session. This module:

        1) Reads docs/training_mode_brief.json (if present).
        2) Prompts the trainee for:
            - name / callsign
            - optional session label or ID
            - self-assessed confidence (0–100)
            - a short summary of what they think is happening
            - key lessons learned
        3) Captures the current nuclear/cyber/joint/fusion snapshot
           from the brief.
        4) Appends a new record to:
            - docs/training_sessions_log.json
            - docs/training_sessions_log.txt

Notes:
    - This is a READ-ONLY consumer of existing artifacts plus a
      training log writer. It does NOT modify any pipeline configs.
    - Safe to run as often as desired – each run appends a new session.

Usage:
    From src/:

        python gll_training_mode_brief.py      # if you haven't run it yet
        python gll_training_session_logger.py  # to log a session
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

TRAINING_BRIEF_JSON = os.path.join(DOCS_DIR, "training_mode_brief.json")
SESSION_LOG_JSON = os.path.join(DOCS_DIR, "training_sessions_log.json")
SESSION_LOG_TXT = os.path.join(DOCS_DIR, "training_sessions_log.txt")


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _fmt_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def _clip_0_100(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 100.0:
        return 100.0
    return x


def _prompt_non_empty(prompt: str) -> str:
    """
    Simple helper to avoid empty strings in key fields.
    """
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Please enter a non-empty value.")


# -------------------------------------------------------------------
# Core logging logic
# -------------------------------------------------------------------

def _load_training_brief() -> Dict[str, Any]:
    data = _safe_read_json(TRAINING_BRIEF_JSON)
    return data if isinstance(data, dict) else {}


def _load_existing_sessions() -> List[Dict[str, Any]]:
    data = _safe_read_json(SESSION_LOG_JSON)
    if isinstance(data, list):
        return data
    return []


def _write_sessions_json(sessions: List[Dict[str, Any]]) -> None:
    with open(SESSION_LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, sort_keys=True)


def _write_sessions_txt(sessions: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Training Session Log")
    lines.append("========================================")
    lines.append(f"Total Sessions: {len(sessions)}")
    lines.append("")

    for i, s in enumerate(sessions, start=1):
        lines.append(f"Session #{i}")
        lines.append("----------")
        lines.append(f"Timestamp (UTC): {s.get('timestamp_utc', 'N/A')}")
        lines.append(f"Trainee:         {s.get('trainee_name', 'N/A')}")
        session_id = s.get("session_id") or "-"
        lines.append(f"Session ID:      {session_id}")
        lines.append(f"Training Focus:  {s.get('training_focus', 'N/A')}")
        lines.append(f"Overall Posture: {s.get('overall_posture', 'N/A')}")
        lines.append("")
        scores = s.get("scores_snapshot", {})
        lines.append("Scores Snapshot:")
        lines.append(f"  Fusion Trust:    {scores.get('fusion_trust_score', 'N/A')} ({scores.get('fusion_posture_level', 'N/A')})")
        lines.append(f"  Nuclear Score:   {scores.get('nuclear_score', 'N/A')} ({scores.get('nuclear_level', 'N/A')})")
        lines.append(f"  Cyber Threat:    {scores.get('cyber_threat_score', 'N/A')} ({scores.get('cyber_posture_level', 'N/A')})")
        lines.append(f"  Joint Readiness: {scores.get('joint_readiness_score', 'N/A')} ({scores.get('joint_readiness_level', 'N/A')})")
        lines.append("")
        lines.append(f"Self-Confidence: {s.get('self_confidence', 'N/A')} / 100")
        lines.append(f"Situation Summary:")
        lines.append(f"  {s.get('situation_summary', '').strip() or '-'}")
        lines.append("")
        lines.append(f"Lessons Learned:")
        lessons = s.get("lessons_learned", "").strip() or "-"
        lines.append(f"  {lessons}")
        lines.append("")
        lines.append("-----")
        lines.append("")

    with open(SESSION_LOG_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def log_training_session() -> Dict[str, Any]:
    """
    Interactive entrypoint to log a single training session.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    brief = _load_training_brief()
    if not brief:
        print("")
        print("WARNING: No training_mode_brief.json found.")
        print("Run gll_training_mode_brief.py first to generate a training scenario.")
        print("")
        # Still allow logging, but with minimal context
    else:
        print("")
        print("Loaded training_mode_brief.json for context.")
        print(f"Training Focus:  {brief.get('training_focus', 'UNKNOWN')}")
        print(f"Overall Posture: {brief.get('overall_posture', 'UNKNOWN')}")
        print("")

    trainee_name = _prompt_non_empty("Enter trainee name / callsign: ")
    session_id = input("Optional session label/ID (press Enter to skip): ").strip()

    # Confidence: we accept numbers, clamp to [0, 100]
    while True:
        raw_conf = input("Self-assessed confidence (0–100): ").strip()
        try:
            conf = _clip_0_100(float(raw_conf))
            break
        except Exception:
            print("Please enter a numeric value between 0 and 100.")

    print("")
    print("In 2–3 sentences, describe what you think is happening in this scenario.")
    situation_summary = input("Situation summary: ").strip()

    print("")
    print("What are the top 1–3 lessons you learned from working this scenario?")
    lessons_learned = input("Lessons learned: ").strip()

    timestamp_utc = datetime.utcnow().isoformat() + "Z"

    # Scores snapshot from brief (if present)
    scores = brief.get("scores", {}) if isinstance(brief, dict) else {}

    session_record: Dict[str, Any] = {
        "timestamp_utc": timestamp_utc,
        "trainee_name": trainee_name,
        "session_id": session_id or None,
        "self_confidence": conf,
        "training_focus": brief.get("training_focus", "UNKNOWN") if brief else "UNKNOWN",
        "overall_posture": brief.get("overall_posture", "UNKNOWN") if brief else "UNKNOWN",
        "scores_snapshot": {
            "fusion_trust_score": _clip_0_100(_fmt_float(scores.get("fusion_trust_score", 0.0), 0.0)),
            "fusion_posture_level": scores.get("fusion_posture_level", "UNKNOWN"),
            "nuclear_score": _clip_0_100(_fmt_float(scores.get("nuclear_score", 0.0), 0.0)),
            "nuclear_level": scores.get("nuclear_level", "UNKNOWN"),
            "cyber_threat_score": _clip_0_100(_fmt_float(scores.get("cyber_threat_score", 0.0), 0.0)),
            "cyber_posture_level": scores.get("cyber_posture_level", "UNKNOWN"),
            "joint_readiness_score": _clip_0_100(_fmt_float(scores.get("joint_readiness_score", 0.0), 0.0)),
            "joint_readiness_level": scores.get("joint_readiness_level", "UNKNOWN"),
        },
        "situation_summary": situation_summary,
        "lessons_learned": lessons_learned,
    }

    # Load, append, write
    sessions = _load_existing_sessions()
    sessions.append(session_record)
    _write_sessions_json(sessions)
    _write_sessions_txt(sessions)

    print("")
    print("Training session logged.")
    print(f"  - JSON log: {os.path.join('docs', 'training_sessions_log.json')}")
    print(f"  - TXT log:  {os.path.join('docs', 'training_sessions_log.txt')}")
    print("")

    return session_record


if __name__ == "__main__":
    log_training_session()

