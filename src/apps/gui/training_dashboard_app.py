#!/usr/bin/env python3
"""
training_dashboard_app.py

Ghost Lantern Labs – Training Dashboard
---------------------------------------

Impact Module 2 – Instructor Mode + Rubric Engine

Purpose:
    Turns GLL into a real ISR/cyber training tool:

    • Trainee View:
        - Shows recent training sessions for a given trainee.
        - Displays score trend.
        - Surfaces Obasi coach guidance tied to the latest score.

    • Instructor Mode:
        - Allows instructors to log new evaluations using a rubric.
        - Stores all sessions in docs/training_sessions.json.
        - Computes composite scores and trends.
        - Exposes quick stats (average score, last N sessions, per-trainee list).

Design constraints:
    - No external network access.
    - All data persisted locally under src/docs/.
    - Read/write only to JSON in docs/.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime, date
import json

import streamlit as st

from obasi_training_coach import build_obasi_training_coach_speech


# ---------------------------------------------------------------------------
# Paths and storage
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]  # .../parser_starter_kit/src
DOCS_DIR = BASE_DIR / "docs"
SESSIONS_PATH = DOCS_DIR / "training_sessions.json"


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def _load_sessions() -> List[Dict[str, Any]]:
    """
    Load all training sessions from JSON. Returns [] if not present or invalid.
    Each session is a dict with:
        - id
        - trainee_name
        - scenario
        - session_date (ISO)
        - created_at (ISO)
        - rubric:
            * analysis_quality
            * fusion_thinking
            * nuclear_relevance
            * reporting_discipline
        - composite_score (0–100)
    """
    if not SESSIONS_PATH.exists():
        return []
    try:
        data = json.loads(SESSIONS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def _save_sessions(sessions: List[Dict[str, Any]]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_PATH.write_text(json.dumps(sessions, indent=2), encoding="utf-8")


def _next_session_id(sessions: List[Dict[str, Any]]) -> int:
    if not sessions:
        return 1
    return max(int(s.get("id", 0) or 0) for s in sessions) + 1


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def _compute_composite_score(
    analysis_quality: int,
    fusion_thinking: int,
    nuclear_relevance: int,
    reporting_discipline: int,
) -> float:
    """
    Weighted composite score (0–100).
    Weighting reflects ISR/nuclear priorities.
    """
    # 0–5 sliders mapped into 0–100 with weights
    weights = {
        "analysis_quality": 0.30,
        "fusion_thinking": 0.30,
        "nuclear_relevance": 0.25,
        "reporting_discipline": 0.15,
    }

    total = (
        analysis_quality * weights["analysis_quality"]
        + fusion_thinking * weights["fusion_thinking"]
        + nuclear_relevance * weights["nuclear_relevance"]
        + reporting_discipline * weights["reporting_discipline"]
    )
    # scale 0–5 → 0–100
    return round((total / 5.0) * 100.0, 1)


def _filter_by_trainee(
    sessions: List[Dict[str, Any]],
    trainee_name: str,
) -> List[Dict[str, Any]]:
    name_low = trainee_name.strip().lower()
    return [
        s for s in sessions
        if str(s.get("trainee_name", "")).strip().lower() == name_low
    ]


def _compute_overall_stats(
    sessions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not sessions:
        return {
            "count": 0,
            "avg_score": None,
            "latest_score": None,
        }

    scores = [float(s.get("composite_score", 0.0) or 0.0) for s in sessions]
    avg_score = sum(scores) / len(scores)
    latest_score = scores[-1]

    return {
        "count": len(sessions),
        "avg_score": round(avg_score, 1),
        "latest_score": round(latest_score, 1),
    }


def _get_all_trainee_names(sessions: List[Dict[str, Any]]) -> List[str]:
    names = sorted(
        {str(s.get("trainee_name", "")).strip() for s in sessions if s.get("trainee_name", "").strip()}
    )
    return names


# ---------------------------------------------------------------------------
# Obasi coach integration
# ---------------------------------------------------------------------------

def _build_obasi_message(latest_score: float | None) -> str:
    """
    Call Obasi training coach in a way that works whether the underlying
    function expects a score parameter or not. This preserves compatibility
    with earlier implementations.
    """
    try:
        # Preferred: pass score context
        return build_obasi_training_coach_speech(latest_score)
    except TypeError:
        # Fallback: signature without arguments
        return build_obasi_training_coach_speech()
    except Exception:
        return "Obasi coach is temporarily unavailable, but keep training and reviewing your last sessions."


# ---------------------------------------------------------------------------
# UI – Trainee View
# ---------------------------------------------------------------------------

def _render_trainee_view(sessions: List[Dict[str, Any]]) -> None:
    st.header("🎯 Trainee View")

    if not sessions:
        st.info(
            "No training sessions have been logged yet. "
            "Ask an instructor to record your first evaluation in Instructor Mode."
        )
        return

    trainee_names = _get_all_trainee_names(sessions)
    selected_name = st.selectbox(
        "Select trainee name",
        options=trainee_names,
        index=0,
    )

    trainee_sessions = _filter_by_trainee(sessions, selected_name)
    stats = _compute_overall_stats(trainee_sessions)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", stats["count"])
    with col2:
        st.metric("Average Score", stats["avg_score"] if stats["avg_score"] is not None else "—")
    with col3:
        st.metric("Latest Score", stats["latest_score"] if stats["latest_score"] is not None else "—")

    # Obasi coach message
    st.subheader("🦉 Obasi – Training Coach")
    msg = _build_obasi_message(stats["latest_score"])
    st.write(msg)

    # Trend chart
    if trainee_sessions:
        st.subheader("Score Trend")
        scores = [s.get("composite_score", 0.0) for s in trainee_sessions]
        labels = [s.get("session_date", f"#{s.get('id', '?')}") for s in trainee_sessions]
        chart_data = {
            "session": list(range(1, len(scores) + 1)),
            "score": scores,
        }
        st.line_chart(chart_data, x="session", y="score")

    # Recent sessions table
    st.subheader("Recent Sessions")
    recent = trainee_sessions[-10:]
    if recent:
        table_rows = []
        for s in recent:
            table_rows.append({
                "ID": s.get("id"),
                "Date": s.get("session_date"),
                "Scenario": s.get("scenario"),
                "Score": s.get("composite_score"),
                "Analysis": s.get("rubric", {}).get("analysis_quality"),
                "Fusion": s.get("rubric", {}).get("fusion_thinking"),
                "Nuclear": s.get("rubric", {}).get("nuclear_relevance"),
                "Reporting": s.get("rubric", {}).get("reporting_discipline"),
            })
        st.dataframe(table_rows, use_container_width=True)
    else:
        st.info("No sessions found yet for this trainee.")


# ---------------------------------------------------------------------------
# UI – Instructor Mode
# ---------------------------------------------------------------------------

def _render_instructor_mode(
    sessions: List[Dict[str, Any]],
) -> Tuple[bool, List[Dict[str, Any]]]:
    st.header("🧑‍🏫 Instructor Mode – Rubric & Evaluation")

    st.markdown(
        "Use this panel to **record training evaluations** for ISR/cyber trainees. "
        "All evaluations are saved to `src/docs/training_sessions.json`."
    )

    with st.form("new_evaluation"):
        col_basic1, col_basic2 = st.columns(2)
        with col_basic1:
            trainee_name = st.text_input("Trainee name", value="Ghost")
            scenario = st.text_input(
                "Scenario / Exercise Name",
                value="Nuclear Early Warning – Pre-Launch Pattern",
            )
        with col_basic2:
            session_date = st.date_input("Session date", value=date.today())

        st.markdown("### Rubric (0–5)")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            analysis_quality = st.slider(
                "Analysis Quality (0–5)",
                min_value=0,
                max_value=5,
                value=3,
            )
            fusion_thinking = st.slider(
                "Fusion Thinking (0–5)",
                min_value=0,
                max_value=5,
                value=3,
            )
        with col_r2:
            nuclear_relevance = st.slider(
                "Nuclear/ISR Relevance (0–5)",
                min_value=0,
                max_value=5,
                value=3,
            )
            reporting_discipline = st.slider(
                "Reporting Discipline (0–5)",
                min_value=0,
                max_value=5,
                value=3,
            )

        submitted = st.form_submit_button("Save Evaluation")

    updated = False

    if submitted:
        if not trainee_name.strip():
            st.error("Trainee name is required.")
        else:
            composite = _compute_composite_score(
                analysis_quality,
                fusion_thinking,
                nuclear_relevance,
                reporting_discipline,
            )

            new_sessions = list(sessions)
            new_id = _next_session_id(new_sessions)
            new_sessions.append(
                {
                    "id": new_id,
                    "trainee_name": trainee_name.strip(),
                    "scenario": scenario.strip(),
                    "session_date": session_date.strftime("%Y-%m-%d"),
                    "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "rubric": {
                        "analysis_quality": analysis_quality,
                        "fusion_thinking": fusion_thinking,
                        "nuclear_relevance": nuclear_relevance,
                        "reporting_discipline": reporting_discipline,
                    },
                    "composite_score": composite,
                }
            )
            _save_sessions(new_sessions)
            updated = True
            sessions = new_sessions

            st.success(
                f"Saved evaluation for {trainee_name.strip()} "
                f"with composite score {composite}."
            )

    st.subheader("Training Overview")

    stats_all = _compute_overall_stats(sessions)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", stats_all["count"])
    with col2:
        st.metric("Average Score (All)", stats_all["avg_score"] if stats_all["avg_score"] is not None else "—")
    with col3:
        st.metric("Latest Score (All)", stats_all["latest_score"] if stats_all["latest_score"] is not None else "—")

    if sessions:
        st.subheader("Recent Evaluations (Last 15)")
        recent = sessions[-15:]
        table_rows = []
        for s in recent:
            table_rows.append(
                {
                    "ID": s.get("id"),
                    "Trainee": s.get("trainee_name"),
                    "Date": s.get("session_date"),
                    "Scenario": s.get("scenario"),
                    "Score": s.get("composite_score"),
                }
            )
        st.dataframe(table_rows, use_container_width=True)

        # Per-trainee averages
        st.subheader("Per-Trainee Averages")
        names = _get_all_trainee_names(sessions)
        per_rows = []
        for name in names:
            ts = _filter_by_trainee(sessions, name)
            st_stats = _compute_overall_stats(ts)
            per_rows.append(
                {
                    "Trainee": name,
                    "Sessions": st_stats["count"],
                    "Avg Score": st_stats["avg_score"],
                    "Latest Score": st_stats["latest_score"],
                }
            )
        st.dataframe(per_rows, use_container_width=True)
    else:
        st.info("No evaluations logged yet.")

    return updated, sessions


# ---------------------------------------------------------------------------
# Main Streamlit entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="GLL – Training Dashboard",
        layout="wide",
    )

    st.title("🦉 Ghost Lantern Labs – Training Dashboard")
    st.caption(
        "ISR / nuclear / cyber-fusion training tool for trainees and instructors."
    )

    sessions = _load_sessions()

    mode = st.sidebar.radio(
        "Mode",
        options=["Trainee View", "Instructor Mode"],
        index=0,
    )

    if mode == "Trainee View":
        _render_trainee_view(sessions)
    else:
        updated, sessions = _render_instructor_mode(sessions)
        # If updated, we could optionally refresh views, but Streamlit already
        # reruns the script on interaction.

    st.markdown("---")
    st.caption(
        "GLL Training Dashboard – Data is stored locally in src/docs/training_sessions.json. "
        "This tool is for training and education only, not operational ISR decisions."
    )


if __name__ == "__main__":
    main()

