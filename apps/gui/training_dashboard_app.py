#!/usr/bin/env python3
"""
apps/gui/training_dashboard_app.py

Ghost Lantern Labs – Training Dashboard GUI
-------------------------------------------

Purpose:
    Provide a Streamlit UI for:

        - Training summary tiles (sessions, averages, domain coverage)
        - Simple progress chart (self-confidence over time)
        - Quick view of latest training focus and posture

Inputs:
    - docs/training_sessions_log.json
    - docs/training_instructor_report.json (if already generated)
    - docs/training_mode_brief.json (optional, for extra context)

Usage:
    From repo root:

        streamlit run src/apps/gui/training_dashboard_app.py
"""

import json
import os
from typing import Any, Dict, List, Optional

import streamlit as st
import pandas as pd


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

SESSIONS_JSON = os.path.join(DOCS_DIR, "training_sessions_log.json")
INSTRUCTOR_JSON = os.path.join(DOCS_DIR, "training_instructor_report.json")
BRIEF_JSON = os.path.join(DOCS_DIR, "training_mode_brief.json")


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


# -------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------

def load_sessions() -> List[Dict[str, Any]]:
    data = _safe_read_json(SESSIONS_JSON)
    if isinstance(data, list):
        # Sort by timestamp for chart
        def _ts(s: Dict[str, Any]) -> str:
            return str(s.get("timestamp_utc", ""))
        return sorted(data, key=_ts)
    return []


def load_instructor_report() -> Dict[str, Any]:
    data = _safe_read_json(INSTRUCTOR_JSON)
    return data if isinstance(data, dict) else {}


def load_latest_brief() -> Dict[str, Any]:
    data = _safe_read_json(BRIEF_JSON)
    return data if isinstance(data, dict) else {}


# -------------------------------------------------------------------
# Streamlit App
# -------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="GLL Training Dashboard",
        layout="wide",
    )

    st.title("🧠 GLL Training Dashboard")
    st.caption(
        "Ghost Lantern Labs – Training Mode overview for trainees and instructors."
    )

    sessions = load_sessions()
    report = load_instructor_report()
    brief = load_latest_brief()

    total_sessions = len(sessions)

    # Top-level status
    col1, col2, col3, col4 = st.columns(4)

    # Total sessions tile
    with col1:
        st.subheader("Total Sessions")
        st.metric(label="Logged", value=total_sessions)

    # Average confidence
    avg_conf = None
    conf_trend = "NO_DATA"
    if report:
        progress = report.get("progress_summary", {})
        avg_conf = progress.get("average_confidence")
        conf_trend = progress.get("confidence_trend", "NO_DATA")
    with col2:
        st.subheader("Average Confidence")
        if avg_conf is None:
            st.metric(label="Self-assessed", value="N/A")
        else:
            st.metric(label="Self-assessed", value=f"{avg_conf:.1f} / 100", delta=conf_trend)

    # Engagement
    avg_eng = None
    eng_trend = "NO_DATA"
    if report:
        progress = report.get("progress_summary", {})
        avg_eng = progress.get("average_engagement_chars")
        eng_trend = progress.get("engagement_trend", "NO_DATA")
    with col3:
        st.subheader("Engagement")
        if avg_eng is None:
            st.metric(label="Chars per session", value="N/A")
        else:
            st.metric(label="Chars per session", value=f"{avg_eng:.0f}", delta=eng_trend)

    # Latest posture
    latest_focus = brief.get("training_focus", "UNKNOWN") if brief else "UNKNOWN"
    latest_posture = brief.get("overall_posture", "UNKNOWN") if brief else "UNKNOWN"
    with col4:
        st.subheader("Latest Scenario")
        st.metric(
            label="Focus / Posture",
            value=f"{latest_focus}",
            delta=f"Posture: {latest_posture}",
        )

    st.markdown("---")

    # Progress chart & domain coverage
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Confidence Over Time")
        if not sessions:
            st.info("No training sessions logged yet. Run the Training Session Logger first.")
        else:
            # Build DataFrame for chart
            chart_data = []
            for s in sessions:
                ts = s.get("timestamp_utc", "")
                conf = _clip_0_100(_fmt_float(s.get("self_confidence", 0.0), 0.0))
                chart_data.append({"timestamp": ts, "self_confidence": conf})
            df = pd.DataFrame(chart_data)
            df = df.set_index("timestamp")
            st.line_chart(df, height=260)

    with right:
        st.subheader("Domain Coverage")
        if report:
            progress = report.get("progress_summary", {})
            dom_counts = progress.get("domain_counts", {})
            if dom_counts:
                dom_rows = [{"training_focus": k, "sessions": v} for k, v in dom_counts.items()]
                df_dom = pd.DataFrame(dom_rows)
                st.table(df_dom)
            else:
                st.info("No domain coverage data yet.")
        else:
            st.info("Run the Instructor Mode report once to populate domain coverage.")

    st.markdown("---")

    # Recent sessions table
    st.subheader("Recent Sessions")
    if not sessions:
        st.info("No sessions to display.")
    else:
        # Show most recent 10
        recent = sessions[-10:]
        rows = []
        for s in recent:
            scores = s.get("scores_snapshot", {})
            rows.append(
                {
                    "Time (UTC)": s.get("timestamp_utc", ""),
                    "Trainee": s.get("trainee_name", ""),
                    "Focus": s.get("training_focus", ""),
                    "Posture": s.get("overall_posture", ""),
                    "Confidence": _clip_0_100(_fmt_float(s.get("self_confidence", 0.0), 0.0)),
                    "Nuclear Score": scores.get("nuclear_score", ""),
                    "Cyber Score": scores.get("cyber_threat_score", ""),
                    "Joint Score": scores.get("joint_readiness_score", ""),
                }
            )
        df_recent = pd.DataFrame(rows)
        st.dataframe(df_recent, use_container_width=True)


if __name__ == "__main__":
    main()

