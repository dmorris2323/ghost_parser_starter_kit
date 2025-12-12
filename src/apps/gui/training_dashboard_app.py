# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str((REPO_ROOT / "src").resolve())
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from training_session_store import append_session, load_sessions
from training_validation_gate import evaluate_training_gate, gate_to_dict
from training_curve_engine import compute_training_curve
from instructor_autograder import auto_grade_session
from obasi_training_coach import build_obasi_training_coach_speech


def main():
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("GLL Training Dashboard")
    st.caption("Difficulty controls expectations + grading weights. Sessions count toward AGI only if integrity gate PASS.")

    left, right = st.columns([1, 2])

    with left:
        trainee = st.text_input("Trainee", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)

        st.subheader("Integrity Gate")
        gate = evaluate_training_gate(require_all_green=True)
        st.json({"status": gate.status, "counted_for_agi": gate.counted_for_agi, "message": gate.message})

        st.subheader("Score Inputs (0–1)")
        acc = st.slider("Accuracy", 0.0, 1.0, 0.75, 0.01)
        spd = st.slider("Speed", 0.0, 1.0, 0.65, 0.01)
        trd = st.slider("Tradecraft", 0.0, 1.0, 0.60, 0.01)

        if st.button("Log Training Session"):
            grade = auto_grade_session(
                trainee_name=trainee,
                difficulty=difficulty,
                raw_scores={"accuracy": acc, "speed": spd, "tradecraft": trd},
            )
            session = {
                "trainee_name": trainee,
                "difficulty": difficulty,
                "session_type": "training",
                "raw_scores": {"accuracy": acc, "speed": spd, "tradecraft": trd},
                "auto_grade": grade,
                "gate": gate_to_dict(gate),
                "counted_for_agi": bool(gate.counted_for_agi),
            }
            saved = append_session(session)
            st.success(
                f"Logged {saved['session_id']} | Passed: {grade.get('passed')} | Counted: {saved.get('counted_for_agi')}"
            )

    with right:
        st.subheader("Live Curve (based on counted sessions)")
        curve = compute_training_curve(difficulty_filter=difficulty)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI (0–100)", f"{curve.get('AGI', 0.0):.1f}")
        c2.metric("Improvement slope", f"{curve.get('improvement_slope', 0.0):.2f}")
        c3.metric("Difficulty-weighted avg", f"{curve.get('difficulty_weighted_average', 0.0):.1f}")
        c4.metric("Volatility index", f"{curve.get('volatility_index', 0.0):.3f}")

        st.subheader("Obasi Coach (Live)")
        coach_msg = build_obasi_training_coach_speech(
            trainee_name=trainee,
            difficulty=difficulty,
            curve=curve,
            gate=gate_to_dict(gate),
        )
        st.text(coach_msg)

        st.subheader("Recent Sessions")
        sessions = load_sessions()
        if sessions:
            st.dataframe(list(reversed(sessions))[:30], use_container_width=True)
        else:
            st.info("No sessions logged yet.")


if __name__ == "__main__":
    main()

