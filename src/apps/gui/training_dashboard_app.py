# apps/gui/training_dashboard_app.py
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st  # noqa: E402

from training_session_store import load_sessions, append_session  # noqa: E402
from training_curve_engine import compute_training_curve  # noqa: E402
from difficulty_scaling_engine import compute_difficulty_profile  # noqa: E402
from apps.gui.obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402


def main():
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("📈 GLL Training Dashboard")
    st.caption("SAFE training telemetry + scenario scoring. Tracks your curve and recommends difficulty.")

    prof = compute_difficulty_profile()
    rec = prof["recommendation"]["recommended_level"]

    curve = compute_training_curve()
    store = load_sessions()
    sessions = store.get("sessions", [])

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Training Curve")
        if curve["session_count"] == 0:
            st.warning("No training sessions logged yet.")
        else:
            st.line_chart(curve["scores"])

        st.metric("AGI (0–100)", curve["agi"])
        st.metric("Average Score", curve["average_score"])
        st.metric("Volatility Index", curve["volatility_index"])
        st.metric("Sessions", curve["session_count"])

    with right:
        st.subheader("Difficulty Recommendation")
        st.info(f"Recommended: **{rec}**")
        st.write(prof["recommendation"]["rationale"])

        st.subheader("Obasi Coach Panel")
        msg = build_obasi_training_coach_speech(
            trainee_name="Ghost",
            difficulty=rec,
            agi=curve["agi"],
            avg_score=curve["average_score"],
            volatility=curve["volatility_index"],
            message_mode="coach",
        )
        st.text_area("Obasi", value=msg, height=160)

    st.divider()

    st.subheader("Log a Training Session (Manual)")
    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])

    with c1:
        score = st.slider("Score", 0, 100, 75)
    with c2:
        mode = st.selectbox("Difficulty mode", ["Auto", "Manual"])
    with c3:
        notes = st.text_input("Notes", value="Manual rep logged.")
    with c4:
        trainee = st.text_input("Trainee", value="Ghost")

    difficulty_used = rec
    if mode == "Manual":
        difficulty_used = st.selectbox("Override difficulty", ["CADET", "ANALYST", "SENIOR", "EXPERT"], index=1)

    if st.button("Log session", type="primary"):
        log = append_session(
            {
                "score": float(score),
                "difficulty": difficulty_used,
                "trainee": trainee,
                "notes": notes[:500],
                "source": "training_dashboard_manual",
            }
        )
        st.success(f"Logged session: {log['session_id']}")
        st.code(log["json_path"])
        st.rerun()

    st.divider()
    st.subheader("Recent Sessions")
    if sessions:
        for s in sessions[-10:][::-1]:
            st.write(s)
    else:
        st.caption("No sessions yet.")


if __name__ == "__main__":
    main()

