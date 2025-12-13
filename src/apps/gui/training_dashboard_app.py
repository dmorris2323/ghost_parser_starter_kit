# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

# --- Streamlit path bootstrap (REQUIRED) ---
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # .../parser_starter_kit
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ------------------------------------------

import streamlit as st

from training_session_store import load_sessions, append_session
from training_feedback_store import load_latest_feedback
from obasi_training_coach import build_obasi_training_coach_speech

try:
    from training_curve_engine import compute_training_curve
except Exception:
    compute_training_curve = None


def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")

    st.title("GLL Training Dashboard")
    st.caption("Sessions, progress curve, and next-step recommendations (read-only).")

    sessions = load_sessions()
    feedback = load_latest_feedback()

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("Log a Training Session")
        trainee = st.text_input("Trainee name", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        score = st.number_input("Score", value=75.0, step=1.0)
        max_score = st.number_input("Max score", value=100.0, step=1.0)
        notes = st.text_area("Notes", value="", height=80)

        if st.button("Append Session", type="primary"):
            s = append_session(
                trainee_name=trainee,
                difficulty=difficulty,
                score=_safe_float(score),
                max_score=_safe_float(max_score, 100.0),
                notes=notes,
            )
            st.success("Session appended.")
            st.json(s)
            st.rerun()

        st.divider()
        st.subheader("🧭 Next Training Recommendation")
        st.json(feedback)

    with right:
        st.subheader("Progress Metrics")

        curve = {}
        if compute_training_curve is not None:
            try:
                curve = compute_training_curve()
            except Exception as e:
                st.error(f"training_curve_engine failed: {e}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI", curve.get("AGI", 0.0))
        c2.metric("Slope", curve.get("improvement_slope", 0.0))
        c3.metric("Difficulty Avg", curve.get("difficulty_weighted_average", 0.0))
        c4.metric("Volatility", curve.get("volatility_index", 0.0))

        st.divider()
        st.subheader("🦉 Obasi Coach")

        msg = build_obasi_training_coach_speech(
            trainee_name=trainee if "trainee" in locals() else "Ghost",
            difficulty=curve.get("latest_difficulty", "INTERMEDIATE"),
            AGI=curve.get("AGI", 0.0),
            improvement_slope=curve.get("improvement_slope", 0.0),
            volatility_index=curve.get("volatility_index", 0.0),
        )
        st.text(msg)

        st.divider()
        st.subheader("Sessions")
        st.write(f"Total sessions: {len(sessions)}")
        if sessions:
            st.dataframe(sessions, use_container_width=True)
        else:
            st.info("No sessions logged yet.")


if __name__ == "__main__":
    main()

