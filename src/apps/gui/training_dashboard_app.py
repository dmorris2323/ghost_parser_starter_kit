#!/usr/bin/env python3
"""
apps/gui/training_dashboard_app.py

Ghost Lantern Labs – Training Dashboard GUI
-------------------------------------------

Purpose:
    Provide a Streamlit UI for:

        - Training summary tiles (sessions, averages, domain coverage)
        - Confidence-over-time progress chart (with focus filter)
        - Recent sessions table
        - Obasi Training Coach panel (guidance based on trends & coverage)

Inputs:
    - docs/training_sessions_log.json
    - docs/training_instructor_report.json
    - docs/training_mode_brief.json

Usage:
    From repo root:

        streamlit run src/apps/gui/training_dashboard_app.py
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

import streamlit as st
import pandas as pd

# -------------------------------------------------------------------
# Ensure src/ is on sys.path so we can import obasi_training_coach
# -------------------------------------------------------------------

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402


# Resolve base paths
BASE_DIR = SRC_DIR
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
    obasi = build_obasi_training_coach_speech()

    total_sessions = len(sessions)

    # ------------------------------
    # Top metrics row
    # ------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Total Sessions")
        st.metric(label="Logged", value=total_sessions)

    avg_conf = None
    conf_trend = "NO_DATA"
    avg_eng = None
    eng_trend = "NO_DATA"
    domain_counts: Dict[str, int] = {}

    if report:
        progress = report.get("progress_summary", {})
        avg_conf = progress.get("average_confidence")
        conf_trend = progress.get("confidence_trend", "NO_DATA")
        avg_eng = progress.get("average_engagement_chars")
        eng_trend = progress.get("engagement_trend", "NO_DATA")
        domain_counts = progress.get("domain_counts", {}) or {}

    with col2:
        st.subheader("Average Confidence")
        if avg_conf is None:
            st.metric(label="Self-assessed", value="N/A")
        else:
            st.metric(label="Self-assessed", value=f"{avg_conf:.1f} / 100", delta=conf_trend)

    with col3:
        st.subheader("Engagement")
        if avg_eng is None:
            st.metric(label="Chars per session", value="N/A")
        else:
            st.metric(label="Chars per session", value=f"{avg_eng:.0f}", delta=eng_trend)

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

    # ------------------------------
    # Filter + Confidence chart + Domain coverage
    # ------------------------------
    left, right = st.columns([2, 1])

    unique_focuses = sorted({s.get("training_focus", "UNKNOWN") for s in sessions}) if sessions else []
    filter_options = ["All"] + unique_focuses if unique_focuses else ["All"]
    selected_focus = left.selectbox(
        "Filter sessions by training focus",
        filter_options,
        index=0,
    )

    if selected_focus == "All":
        filtered_sessions = sessions
    else:
        filtered_sessions = [
            s for s in sessions if s.get("training_focus", "UNKNOWN") == selected_focus
        ]

    with left:
        st.subheader("Confidence Over Time")
        if not filtered_sessions:
            st.info("No training sessions match this filter yet. Log a session or change the filter.")
        else:
            chart_data = []
            for s in filtered_sessions:
                ts = s.get("timestamp_utc", "")
                conf = _clip_0_100(_fmt_float(s.get("self_confidence", 0.0), 0.0))
                chart_data.append({"timestamp": ts, "self_confidence": conf})
            df = pd.DataFrame(chart_data)
            df = df.set_index("timestamp")
            st.line_chart(df, height=260)

    with right:
        st.subheader("Domain Coverage")
        if domain_counts:
            dom_rows = [{"training_focus": k, "sessions": v} for k, v in domain_counts.items()]
            df_dom = pd.DataFrame(dom_rows)
            st.table(df_dom)
        else:
            st.info("No domain coverage data yet. Log a few sessions to see spread across domains.")

    st.markdown("---")

    # ------------------------------
    # Obasi Coach + Recent Sessions
    # ------------------------------
    coach_col, table_col = st.columns([1, 2])

    with coach_col:
        st.subheader("🦉 Obasi – Training Coach")
        st.markdown(f"**{obasi.get('headline', '')}**")
        st.write(obasi.get("subtext", ""))

        if obasi.get("suggested_next_rep"):
            st.markdown("**Suggested Next Rep**")
            st.code(obasi["suggested_next_rep"])

        if obasi.get("warning_flags"):
            st.markdown("**Watch Items**")
            for w in obasi["warning_flags"]:
                st.warning(w)

        if obasi.get("encouragement"):
            st.markdown("**Encouragement**")
            st.info(obasi["encouragement"])

    with table_col:
        st.subheader("Recent Sessions")
        if not filtered_sessions:
            st.info("No sessions to display under this filter.")
        else:
            recent = filtered_sessions[-10:]
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

