#!/usr/bin/env python3
"""
gll_training_instructor_mode.py

Ghost Lantern Labs – Instructor Mode & Progress Report
------------------------------------------------------

Purpose:
    Provide an instructor-facing view over GLL training sessions:

    1) Read:
         - docs/training_sessions_log.json (session history)
         - docs/training_mode_brief.json (latest brief, if present)

    2) For each session:
         - Capture posture & score snapshot (already stored in session)
         - Derive engagement (length of answers)
         - Preserve self-assessed confidence
         - Suggest instructor focus areas

    3) Across all sessions:
         - Compute:
             * total sessions
             * time span
             * average confidence
             * confidence trend (increasing / decreasing / stable)
             * engagement trend
             * domain coverage by training_focus

    4) Output:
         - docs/training_instructor_report.json
         - docs/training_instructor_report.txt

Notes:
    - This does NOT try to autograde "correctness".
      It provides heuristics and context to help a human instructor.
    - Read-only with respect to core pipeline configuration.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

SESSIONS_JSON = os.path.join(DOCS_DIR, "training_sessions_log.json")
TRAINING_BRIEF_JSON = os.path.join(DOCS_DIR, "training_mode_brief.json")
INSTRUCTOR_JSON = os.path.join(DOCS_DIR, "training_instructor_report.json")
INSTRUCTOR_TXT = os.path.join(DOCS_DIR, "training_instructor_report.txt")


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


def _engagement_level(text_len: int) -> str:
    """
    Very simple engagement heuristic:
        - < 80 chars   -> LOW
        - 80–200 chars -> MEDIUM
        - > 200 chars  -> HIGH
    """
    if text_len <= 0:
        return "NONE"
    if text_len < 80:
        return "LOW"
    if text_len < 200:
        return "MEDIUM"
    return "HIGH"


def _trend_label(first_half_avg: float, second_half_avg: float, eps: float = 3.0) -> str:
    """
    Compare averages of first vs second half.
    eps is a deadband in score units.
    """
    delta = second_half_avg - first_half_avg
    if delta > eps:
        return "INCREASING"
    if delta < -eps:
        return "DECREASING"
    return "STABLE"


# -------------------------------------------------------------------
# Core analysis
# -------------------------------------------------------------------

def _load_sessions() -> List[Dict[str, Any]]:
    data = _safe_read_json(SESSIONS_JSON)
    if isinstance(data, list):
        # Sort by timestamp if possible
        def _ts(s: Dict[str, Any]) -> str:
            return str(s.get("timestamp_utc", ""))
        return sorted(data, key=_ts)
    return []


def _load_latest_brief() -> Dict[str, Any]:
    data = _safe_read_json(TRAINING_BRIEF_JSON)
    return data if isinstance(data, dict) else {}


def _analyze_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute per-session notes + aggregate progress metrics.
    """
    total = len(sessions)
    if total == 0:
        return {
            "total_sessions": 0,
            "time_span": None,
            "average_confidence": None,
            "confidence_trend": "NO_DATA",
            "average_engagement": None,
            "engagement_trend": "NO_DATA",
            "domain_counts": {},
            "session_summaries": [],
        }

    # Time span
    first_ts = sessions[0].get("timestamp_utc")
    last_ts = sessions[-1].get("timestamp_utc")

    # Domain / confidence / engagement
    confidences: List[float] = []
    engagements: List[float] = []
    domain_counts: Dict[str, int] = {}

    session_summaries: List[Dict[str, Any]] = []

    for idx, s in enumerate(sessions, start=1):
        tfocus = str(s.get("training_focus", "UNKNOWN"))
        domain_counts[tfocus] = domain_counts.get(tfocus, 0) + 1

        conf = _clip_0_100(_fmt_float(s.get("self_confidence", 0.0), 0.0))
        confidences.append(conf)

        summary_text = (s.get("situation_summary") or "").strip()
        lessons_text = (s.get("lessons_learned") or "").strip()
        engaged_chars = len(summary_text) + len(lessons_text)
        engagements.append(engaged_chars)

        eng_level = _engagement_level(engaged_chars)

        scores = s.get("scores_snapshot", {})
        nuclear_score = _clip_0_100(_fmt_float(scores.get("nuclear_score", 0.0), 0.0))
        nuclear_level = str(scores.get("nuclear_level", "UNKNOWN"))
        cyber_score = _clip_0_100(_fmt_float(scores.get("cyber_threat_score", 0.0), 0.0))
        cyber_level = str(scores.get("cyber_posture_level", "UNKNOWN"))
        joint_score = _clip_0_100(_fmt_float(scores.get("joint_readiness_score", 0.0), 0.0))
        joint_level = str(scores.get("joint_readiness_level", "UNKNOWN"))

        # Very simple instructor suggestion
        instr_focus: List[str] = []
        if nuclear_score >= 70.0 or nuclear_level.upper() in ("RED", "AMBER"):
            instr_focus.append("Reinforce nuclear drift/volatility interpretation.")
        if cyber_score >= 70.0 or cyber_level.upper() in ("RED", "AMBER"):
            instr_focus.append("Review cyber threat vectors and DCIM reading.")
        if joint_score <= 40.0 or joint_level.upper() == "RED":
            instr_focus.append("Discuss joint/base-defense readiness implications.")
        if eng_level in ("LOW", "NONE"):
            instr_focus.append("Encourage deeper written reasoning (more detail).")

        session_summaries.append(
            {
                "session_index": idx,
                "timestamp_utc": s.get("timestamp_utc"),
                "trainee_name": s.get("trainee_name"),
                "session_id": s.get("session_id"),
                "training_focus": tfocus,
                "overall_posture": s.get("overall_posture", "UNKNOWN"),
                "self_confidence": conf,
                "engagement_chars": engaged_chars,
                "engagement_level": eng_level,
                "instructor_suggestions": instr_focus,
            }
        )

    # Aggregate confidence / engagement
    avg_conf = sum(confidences) / len(confidences) if confidences else None
    avg_eng_chars = sum(engagements) / len(engagements) if engagements else None

    # Trends (if enough data)
    if len(confidences) >= 4:
        half = len(confidences) // 2
        c_first = sum(confidences[:half]) / max(half, 1)
        c_second = sum(confidences[half:]) / max(len(confidences) - half, 1)
        conf_trend = _trend_label(c_first, c_second)
    else:
        conf_trend = "INSUFFICIENT_DATA"

    if len(engagements) >= 4:
        half = len(engagements) // 2
        e_first = sum(engagements[:half]) / max(half, 1)
        e_second = sum(engagements[half:]) / max(len(engagements) - half, 1)
        eng_trend = _trend_label(e_first, e_second)
    else:
        eng_trend = "INSUFFICIENT_DATA"

    return {
        "total_sessions": total,
        "time_span": {
            "first_session_utc": first_ts,
            "last_session_utc": last_ts,
        },
        "average_confidence": round(avg_conf, 1) if avg_conf is not None else None,
        "confidence_trend": conf_trend,
        "average_engagement_chars": round(avg_eng_chars, 1) if avg_eng_chars is not None else None,
        "engagement_trend": eng_trend,
        "domain_counts": domain_counts,
        "session_summaries": session_summaries,
    }


def build_instructor_report() -> Dict[str, Any]:
    """
    Main entrypoint: analyze sessions and write instructor report.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    sessions = _load_sessions()
    brief = _load_latest_brief()
    progress = _analyze_sessions(sessions)

    generated_at = datetime.utcnow().isoformat() + "Z"

    payload: Dict[str, Any] = {
        "module": "gll_training_instructor_mode",
        "generated_at": generated_at,
        "progress_summary": progress,
        "latest_training_focus": brief.get("training_focus", "UNKNOWN"),
        "latest_overall_posture": brief.get("overall_posture", "UNKNOWN"),
        "latest_scores": brief.get("scores", {}),
    }

    # JSON
    with open(INSTRUCTOR_JSON, "w", encoding="utf-8") as f_json:
        json.dump(payload, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Instructor Mode Report")
    lines.append("==========================================")
    lines.append(f"Generated at (UTC): {generated_at}")
    lines.append("")
    lines.append("Progress Overview")
    lines.append("-----------------")

    total = progress.get("total_sessions", 0)
    lines.append(f"Total sessions logged: {total}")

    span = progress.get("time_span") or {}
    lines.append(f"First session UTC: {span.get('first_session_utc', 'N/A')}")
    lines.append(f"Last session UTC:  {span.get('last_session_utc', 'N/A')}")
    lines.append("")

    lines.append(f"Average self-confidence: {progress.get('average_confidence', 'N/A')}")
    lines.append(f"Confidence trend:        {progress.get('confidence_trend', 'N/A')}")
    lines.append("")
    lines.append(
        f"Average engagement (chars in summary+lessons): "
        f"{progress.get('average_engagement_chars', 'N/A')}"
    )
    lines.append(f"Engagement trend:        {progress.get('engagement_trend', 'N/A')}")
    lines.append("")

    lines.append("Domain Coverage (by training_focus)")
    lines.append("-----------------------------------")
    domain_counts = progress.get("domain_counts", {})
    if domain_counts:
        for dom, count in domain_counts.items():
            lines.append(f"- {dom}: {count} session(s)")
    else:
        lines.append("- No sessions logged yet.")
    lines.append("")

    # Latest brief snapshot
    lines.append("Latest Brief Snapshot")
    lines.append("----------------------")
    lines.append(f"Latest training focus:  {payload.get('latest_training_focus', 'N/A')}")
    lines.append(f"Latest overall posture: {payload.get('latest_overall_posture', 'N/A')}")
    scores = payload.get("latest_scores") or {}
    if scores:
        lines.append("Latest key scores:")
        lines.append(f"  Fusion trust:   {scores.get('fusion_trust_score', 'N/A')} "
                     f"({scores.get('fusion_posture_level', 'N/A')})")
        lines.append(f"  Nuclear score:  {scores.get('nuclear_score', 'N/A')} "
                     f"({scores.get('nuclear_level', 'N/A')})")
        lines.append(f"  Cyber threat:   {scores.get('cyber_threat_score', 'N/A')} "
                     f"({scores.get('cyber_posture_level', 'N/A')})")
        lines.append(f"  Joint readiness:{scores.get('joint_readiness_score', 'N/A')} "
                     f"({scores.get('joint_readiness_level', 'N/A')})")
    else:
        lines.append("No latest scores available (no training_mode_brief.json).")
    lines.append("")

    lines.append("Recent Sessions (most recent last)")
    lines.append("----------------------------------")
    if not progress.get("session_summaries"):
        lines.append("No sessions to display.")
    else:
        for s in progress["session_summaries"]:
            lines.append(f"Session #{s['session_index']} – {s.get('timestamp_utc', 'N/A')}")
            lines.append(f"  Trainee:         {s.get('trainee_name', 'N/A')}")
            lines.append(f"  Session ID:      {s.get('session_id', 'N/A')}")
            lines.append(f"  Training focus:  {s.get('training_focus', 'N/A')}")
            lines.append(f"  Overall posture: {s.get('overall_posture', 'N/A')}")
            lines.append(f"  Confidence:      {s.get('self_confidence', 'N/A')} / 100")
            lines.append(f"  Engagement:      {s.get('engagement_level', 'N/A')} "
                         f"({s.get('engagement_chars', 0)} chars)")
            suggestions = s.get("instructor_suggestions") or []
            if suggestions:
                lines.append("  Instructor notes:")
                for note in suggestions:
                    lines.append(f"    - {note}")
            else:
                lines.append("  Instructor notes: (none – healthy baseline)")
            lines.append("")

    with open(INSTRUCTOR_TXT, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return payload


if __name__ == "__main__":
    report = build_instructor_report()
    print("Instructor Mode report generated:")
    print(f"  - {os.path.join('docs', 'training_instructor_report.json')}")
    print(f"  - {os.path.join('docs', 'training_instructor_report.txt')}")
    print("")
    print(json.dumps(report, indent=2))

