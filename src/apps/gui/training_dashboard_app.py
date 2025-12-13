# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

# --- Streamlit path bootstrap (REQUIRED) ---
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ------------------------------------------

import streamlit as st

from training_session_store import load_sessions, append_session
from training_feedback_store import load_latest_feedback
from obasi_training_coach import build_obasi_training_coach_speech

from difficulty_profiles import as_dict as difficulty_as_dict
from instructor_grader import grade_session
from operator_certification_mode import compute_certification_status

try:
    from training_curve_engine import compute_training_curve
except Exception:
    compute_training_curve = None


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("GLL Training Dashboard")
    st.caption("Difficulty-aware training + grading + certification (training-safe).")

    sessions = load_sessions()
    feedback = load_latest_feedback()

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("Log a Training Session")
        trainee = st.text_input("Trainee name", value="Ghost")

        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        dmeta = difficulty_as_dict(difficulty)

        with st.expander("🎚️ Difficulty Expectations + Grader Weights", expanded=True):
            st.json(dmeta)

        score = st.number_input("Score", value=75.0, step=1.0)
        max_score = st.number_input("Max score", value=100.0, step=1.0)

        procedure_ok = st.checkbox("Procedure OK", value=True)
        safety_ok = st.checkbox("Safety OK", value=True)
        explanation_quality = st.slider("Explanation Quality (0..1)", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        notes = st.text_area("Notes", value="", height=90)

        if st.button("Append Session", type="primary"):
            # record the session (store also captures the extra rubric fields)
            s = append_session(
                trainee_name=trainee,
                difficulty=difficulty,
                score=float(score),
                max_score=float(max_score),
                notes=notes,
                procedure_ok=procedure_ok,
                safety_ok=safety_ok,
                explanation_quality=float(explanation_quality),
            )

            g = grade_session(
                difficulty=difficulty,
                score=float(score),
                max_score=float(max_score),
                procedure_ok=procedure_ok,
                safety_ok=safety_ok,
                explanation_quality=float(explanation_quality),
            )

            st.success("Session appended + graded.")
            st.json({"session": s, "grade": g})
            st.rerun()

        st.divider()
        st.subheader("🧭 Next Training Recommendation")
        st.json(feedback)

        st.divider()
        st.subheader("🎖️ Operator Certification Mode (training)")
        target = st.selectbox("Target Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=2)
        streak = st.number_input("Required PASS streak", value=5, min_value=2, max_value=20, step=1)
        require_no_safety = st.checkbox("Require NO safety flags", value=True)

        cert = compute_certification_status(
            sessions=sessions,
            target_difficulty=target,
            required_pass_streak=int(streak),
            require_no_safety_flags=require_no_safety,
        )
        st.json(cert)

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
            trainee_name=trainee,
            difficulty=curve.get("latest_difficulty", difficulty),
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

