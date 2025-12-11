#!/usr/bin/env python3
"""
training_dashboard_app.py

Ghost Lantern Labs – Training Dashboard v2
-----------------------------------------

Purpose:
    Provide a training cockpit for:
        • Trainee progress (AGI – Analyst Growth Index)
        • Difficulty-weighted improvement
        • Scenario vs. exercise balance
        • Recent session history
        • Obasi-style coaching based on real performance

This app is meant for:
    - Ghost (self-training)
    - Instructors / Shari
    - Future schoolhouse / SBIR demos
"""

import sys
from pathlib import Path
import json
from typing import List, Dict, Any

import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# Ensure src/ is on the Python path so we can import engines
# ------------------------------------------------------------
SRC_DIR = Path(__file__).resolve().parents[2]  # .../parser_starter_kit/src
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DOCS_DIR = SRC_DIR / "docs"
SESSIONS_PATH = DOCS_DIR / "training_sessions.json"

# Core engine
from training_curve_engine import compute_training_curve


# ------------------------------------------------------------
# Data loading helpers
# ------------------------------------------------------------

def load_sessions() -> List[Dict[str, Any]]:
    if not SESSIONS_PATH.exists():
        return []
    try:
        data = json.loads(SESSIONS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def summarize_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute simple summary stats for the dashboard."""
    if not sessions:
        return {
            "total": 0,
            "scenario_count": 0,
            "exercise_count": 0,
            "avg_score": 0.0,
            "avg_scenario_score": 0.0,
            "avg_exercise_score": 0.0,
        }

    total = len(sessions)
    scenario_scores = []
    exercise_scores = []
    all_scores = []

    for s in sessions:
        score = s.get("composite_score")
        if score is None:
            continue
        all_scores.append(score)
        mode = (s.get("mode") or "").upper()
        if mode == "SCENARIO":
            scenario_scores.append(score)
        elif mode == "EXERCISE":
            exercise_scores.append(score)

    def _avg(lst: List[float]) -> float:
        return round(sum(lst) / len(lst), 2) if lst else 0.0

    return {
        "total": total,
        "scenario_count": len(scenario_scores),
        "exercise_count": len(exercise_scores),
        "avg_score": _avg(all_scores),
        "avg_scenario_score": _avg(scenario_scores),
        "avg_exercise_score": _avg(exercise_scores),
    }


def build_recent_sessions_table(sessions: List[Dict[str, Any]], limit: int = 10) -> pd.DataFrame:
    """Return a DataFrame of the most recent N sessions."""
    if not sessions:
        return pd.DataFrame(columns=["date", "mode", "difficulty", "score", "scenario_type"])

    # Sort by date if available
    def _key(s):
        return s.get("session_date") or s.get("timestamp") or ""

    sessions_sorted = sorted(sessions, key=_key, reverse=True)[:limit]

    rows = []
    for s in sessions_sorted:
        rows.append({
            "date": s.get("session_date") or s.get("timestamp") or "",
            "mode": s.get("mode") or "",
            "difficulty": s.get("difficulty") or "",
            "score": s.get("composite_score"),
            "scenario_type": s.get("scenario_type") or "",
        })

    return pd.DataFrame(rows)


def build_score_series(sessions: List[Dict[str, Any]]) -> pd.DataFrame:
    """Build a simple series of scores over time for plotting."""
    if not sessions:
        return pd.DataFrame(columns=["index", "score"])

    def _key(s):
        return s.get("session_date") or s.get("timestamp") or ""

    sessions_sorted = sorted(sessions, key=_key)
    scores = []
    for idx, s in enumerate(sessions_sorted, start=1):
        score = s.get("composite_score")
        if score is None:
            continue
        scores.append({"index": idx, "score": score})

    if not scores:
        return pd.DataFrame(columns=["index", "score"])

    return pd.DataFrame(scores)


# ------------------------------------------------------------
# Obasi-style coaching logic (local)
# ------------------------------------------------------------

def build_obasi_message(curve: Dict[str, Any], summary: Dict[str, Any]) -> str:
    """
    Build an Obasi-style coaching message based on AGI, slope, volatility, and session count.
    This is kept local to avoid tight coupling to any specific Obasi helper signature.
    """
    AGI = curve.get("AGI", 0)
    slope = curve.get("improvement_slope", 0)
    volatility = curve.get("volatility_index", 0)
    total_sessions = summary.get("total", 0)

    if total_sessions == 0:
        base = (
            "Ghost, no runs are on the board yet. Start with a CADET difficulty scenario. "
            "Take your time, think clearly, and focus on clean answers before you worry about speed."
        )
    elif AGI >= 80 and slope > 0:
        base = (
            "Ghost, your curve is strong and trending up. You're in the hunt. "
            "Start mixing in harder scenarios, tighter time boxes, and more multi-domain fusion "
            "(nuclear, cyber, and base-defense in the same run)."
        )
    elif AGI >= 50 and slope >= 0:
        base = (
            "Ghost, you're improving and building a solid base. "
            "Keep running ANALYST difficulty missions and do short self-debriefs after each one: "
            "What did you see, what did you miss, and what would you brief a commander?"
        )
    elif AGI < 50 and slope >= 0:
        base = (
            "Ghost, you're trending upward from a low baseline. That's fine. "
            "Stay in CADET and lower ANALYST missions, slow down, and focus on getting the logic right. "
            "The curve will steepen as your reps stack."
        )
    else:
        base = (
            "Ghost, your performance is unstable or drifting down. "
            "Pause on difficulty increases. Re-run a few past missions, compare your answers, and look "
            "for recurring blind spots. Stabilize first, then push again."
        )

    # Add a small volatility note
    if volatility > 20:
        vol_note = (
            " Your score volatility is high. That means some runs are great and some fall apart. "
            "Tighten your process: same warmup, same note style, same checklist going into each mission."
        )
    else:
        vol_note = (
            " Your volatility is under control. Now it's about stacking consistent, high-quality reps."
        )

    return f"🦉 Obasi: {base}{vol_note}"


# ------------------------------------------------------------
# Streamlit app
# ------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="GLL Training Dashboard",
        layout="wide",
    )

    st.title("🛰️ Ghost Lantern Labs – Training Dashboard")

    sessions = load_sessions()
    curve = compute_training_curve()
    summary = summarize_sessions(sessions)
    recent_df = build_recent_sessions_table(sessions, limit=10)
    series_df = build_score_series(sessions)

    # ---------------- Top metrics row ----------------
    st.subheader("📈 Analyst Growth Metrics")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AGI (0–100)", curve.get("AGI", 0))
    m2.metric("Improvement Slope", curve.get("improvement_slope", 0))
    m3.metric("Diff-Weighted Avg", curve.get("difficulty_weighted_average", 0))
    m4.metric("Volatility Index", curve.get("volatility_index", 0))

    st.markdown("---")

    # ---------------- Summary row ----------------
    st.subheader("📊 Session Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sessions", summary["total"])
    c2.metric("Scenario Sessions", summary["scenario_count"])
    c3.metric("Exercise Sessions", summary["exercise_count"])
    c4.metric("Average Score", summary["avg_score"])

    c5, c6 = st.columns(2)
    c5.metric("Avg Scenario Score", summary["avg_scenario_score"])
    c6.metric("Avg Exercise Score", summary["avg_exercise_score"])

    st.markdown("---")

    # ---------------- Obasi coaching + curve ----------------
    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("🦉 Obasi Coach Panel")
        if summary["total"] == 0:
            st.info(
                "No training sessions logged yet. Run a scenario or exercise from the "
                "Mission Scenario Trainer or Training Dashboard to start your curve."
            )
        else:
            message = build_obasi_message(curve, summary)
            st.info(message)

    with right:
        st.subheader("Progress Curve")
        if series_df.empty:
            st.write("No score data available yet.")
        else:
            st.line_chart(series_df.set_index("index")["score"])

    st.markdown("---")

    # ---------------- Recent sessions table ----------------
    st.subheader("📜 Recent Sessions (Last 10)")

    if recent_df.empty:
        st.write("No training sessions have been recorded yet.")
    else:
        st.dataframe(
            recent_df,
            use_container_width=True,
        )


if __name__ == "__main__":
    main()

