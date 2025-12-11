#!/usr/bin/env python3
"""
obasi_training_coach.py

Ghost Lantern Labs – Obasi Training Coach
-----------------------------------------

Purpose:
    Provide a lightweight "Obasi" coaching summary for Training Mode.

    Reads:
        - docs/training_instructor_report.json (if present)
        - docs/training_mode_brief.json (if present)

    Returns:
        A small dict of coaching lines for the UI, including:
            - headline
            - subtext
            - suggested_next_rep
            - warning_flags
            - encouragement

    This does NOT modify any pipeline configs or core analysis.
"""

import json
import os
from typing import Any, Dict, Optional


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

INSTRUCTOR_JSON = os.path.join(DOCS_DIR, "training_instructor_report.json")
BRIEF_JSON = os.path.join(DOCS_DIR, "training_mode_brief.json")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _normalize_focus(focus: str) -> str:
    focus = (focus or "UNKNOWN").upper()
    if focus == "NUCLEAR_EARLY_WARNING":
        return "Nuclear Early Warning"
    if focus == "DEFENSIVE_CYBER_INTEL":
        return "Defensive Cyber Intel"
    if focus == "JOINT_BASE_DEFENSE":
        return "Joint/Base Defense"
    if focus == "GENERAL_FUSION":
        return "General Fusion"
    return focus.title() if focus else "Unknown"


def build_obasi_training_coach_speech() -> Dict[str, Any]:
    """
    Build a coaching payload based on instructor report + latest brief.
    Safe to call even if no data is present.
    """
    instructor = _safe_read_json(INSTRUCTOR_JSON)
    brief = _safe_read_json(BRIEF_JSON)

    if not instructor:
        # No training has really started yet
        return {
            "agent": "Obasi",
            "mode": "training_coach",
            "headline": "No reps logged yet.",
            "subtext": (
                "We have the range, the simulators, and the instruments — but no sorties flown. "
                "Run a Training Mode brief, log a session, and we’ll start tracking your curve."
            ),
            "suggested_next_rep": (
                "Step 1: python gll_training_mode_brief.py\n"
                "Step 2: python gll_training_session_logger.py\n"
                "Then re-run the Training Dashboard."
            ),
            "warning_flags": [],
            "encouragement": (
                "Every great crew starts at zero hours. What matters is that you start flying reps."
            ),
        }

    progress = instructor.get("progress_summary", {}) or {}

    total_sessions = progress.get("total_sessions", 0)
    avg_conf = progress.get("average_confidence", None)
    conf_trend = (progress.get("confidence_trend") or "NO_DATA").upper()
    eng_trend = (progress.get("engagement_trend") or "NO_DATA").upper()
    domain_counts = progress.get("domain_counts", {}) or {}

    latest_focus_raw = (brief or {}).get("training_focus", "UNKNOWN")
    latest_posture = (brief or {}).get("overall_posture", "UNKNOWN")
    latest_focus = _normalize_focus(latest_focus_raw)

    # Headline
    if total_sessions == 0:
        headline = "No reps logged yet."
    elif total_sessions < 3:
        headline = f"Early reps logged – {total_sessions} sortie(s) on the board."
    else:
        headline = f"{total_sessions} training sorties logged – trend is forming."

    # Trend summary
    trend_bits = []
    if conf_trend == "INCREASING":
        trend_bits.append("Your self-confidence trend is climbing – you’re starting to trust your read.")
    elif conf_trend == "DECREASING":
        trend_bits.append("Self-confidence is drifting down – time to tighten fundamentals and checklists.")
    elif conf_trend == "STABLE":
        trend_bits.append("Confidence is steady – now push for more depth and precision in each rep.")
    else:
        trend_bits.append("Not enough data yet for a confidence trend – keep logging sessions.")

    if eng_trend == "INCREASING":
        trend_bits.append("Your written reasoning is getting denser – good sign of analytic maturity.")
    elif eng_trend == "DECREASING":
        trend_bits.append("Engagement is thinning out – don’t cut corners on your written logic.")
    elif eng_trend == "STABLE":
        trend_bits.append("Engagement is steady – aim for one strong paragraph per rep minimum.")

    # Domain coverage
    dom_notes = []
    if domain_counts:
        sorted_domains = sorted(domain_counts.items(), key=lambda kv: kv[1], reverse=True)
        top_dom, top_count = sorted_domains[0]
        top_dom_label = _normalize_focus(top_dom)
        dom_notes.append(f"Most of your reps so far are in: {top_dom_label} ({top_count} session(s)).")

        all_expected = [
            "NUCLEAR_EARLY_WARNING",
            "DEFENSIVE_CYBER_INTEL",
            "JOINT_BASE_DEFENSE",
            "GENERAL_FUSION",
        ]
        missing = [d for d in all_expected if d not in domain_counts]
        if missing:
            pretty_missing = ", ".join(_normalize_focus(d) for d in missing)
            dom_notes.append(f"Under-trained domains: {pretty_missing}. Build at least one rep in each.")
    else:
        dom_notes.append("No domain spread yet – start with at least one rep in nuclear, cyber, and joint/base defense.")

    suggested_next_rep = (
        f"Next rep: run a {latest_focus} scenario and write a tight paragraph that explains why "
        f"the posture is {latest_posture}."
    )

    warning_flags = []
    if conf_trend == "DECREASING":
        warning_flags.append("Confidence trending down – schedule a fundamentals-focused rep (intel cycle, I&W, drift).")
    if eng_trend == "DECREASING":
        warning_flags.append("Engagement dropping – require yourself to write at least 4–5 full sentences per scenario.")
    if total_sessions >= 5 and len(domain_counts) == 1:
        warning_flags.append("You’re over-concentrated in one domain – spread reps across nuclear, cyber, and base-defense.")

    if total_sessions == 0:
        encouragement = (
            "Obasi: \"The first sortie is the most important. After that, we’re just refining the pattern.\""
        )
    elif conf_trend == "INCREASING":
        encouragement = (
            "Obasi: \"Good – your instincts are calibrating. Keep logging reps and don’t get sloppy on your write-ups.\""
        )
    elif conf_trend == "DECREASING":
        encouragement = (
            "Obasi: \"This is where real analysts are forged – stay in the seat, work the fundamentals, and keep flying the scenario.\""
        )
    else:
        encouragement = (
            "Obasi: \"Consistency beats bursts. One solid, honest rep per day will change who you are as an analyst.\""
        )

    subtext = " ".join(trend_bits + dom_notes)

    return {
        "agent": "Obasi",
        "mode": "training_coach",
        "headline": headline,
        "subtext": subtext,
        "suggested_next_rep": suggested_next_rep,
        "warning_flags": warning_flags,
        "encouragement": encouragement,
        "latest_focus": latest_focus,
        "latest_posture": latest_posture,
        "total_sessions": total_sessions,
    }


if __name__ == "__main__":
    payload = build_obasi_training_coach_speech()
    print("Obasi Training Coach payload:")
    print(json.dumps(payload, indent=2))

