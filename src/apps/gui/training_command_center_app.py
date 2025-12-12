from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from difficulty_scaling_engine import explain_difficulty, list_difficulties  # noqa: E402
from instructor_autograder import grade_session  # noqa: E402
from obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402
from training_curve_engine import compute_training_curve  # noqa: E402
from training_session_store import append_session, load_sessions  # noqa: E402


st.set_page_config(page_title="GLL Training Command Center", layout="wide")


def main() -> None:
    st.title("🛰️ GLL Training Command Center")
    st.caption("Live difficulty control → session log → auto-grade → curve metrics.")

    with st.sidebar:
        st.header("Operator Controls")
        trainee_name = st.text_input("Trainee", value="Ghost")
        difficulty = st.selectbox("Difficulty", options=list_difficulties(), index=1)
        d_name, d_desc = explain_difficulty(difficulty)
        st.info(f"**{d_name}** — {d_desc}")
        gate_green = st.checkbox("SIS/SPS Gate GREEN (counts)", value=True)

    topL, topR = st.columns([2, 1])

    with topL:
        st.subheader("Mission performance inputs (0–100)")
        a1, a2, a3 = st.columns(3)
        with a1:
            accuracy = st.slider("Accuracy", 0, 100, 75)
            procedure = st.slider("Procedure", 0, 100, 75)
        with a2:
            discipline = st.slider("Discipline", 0, 100, 75)
            timeliness = st.slider("Timeliness", 0, 100, 70)
        with a3:
            comms = st.slider("Comms clarity", 0, 100, 75)
            notes = st.text_area("Notes", value="", height=120)

        preview = grade_session(
            difficulty=difficulty,
            accuracy=float(accuracy),
            timeliness=float(timeliness),
            discipline=float(discipline),
            comms_clarity=float(comms),
            procedure=float(procedure),
            gate_green=gate_green,
        )

        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Score", preview["score"])
        b2.metric("Threshold", preview["score_floor"])
        b3.metric("Passed", "YES" if preview["passed"] else "NO")
        b4.metric("Counts", "YES" if preview["counted"] else "NO")

        st.json({"weights": preview["grader_weights"], "inputs": preview["inputs"]})

        if st.button("✅ Log session to curve", use_container_width=True):
            append_session(
                {
                    "difficulty": preview["difficulty"],
                    "score": preview["score"],
                    "passed": preview["passed"],
                    "gate_green": preview["gate_green"],
                    "counted": preview["counted"],
                    "grader_weights": preview["grader_weights"],
                    "rubric_inputs": preview["inputs"],
                    "trainee_name": trainee_name,
                    "notes": notes,
                }
            )
            curve = compute_training_curve()
            st.session_state["curve"] = curve
            st.success("Logged session and recomputed curve.")

    with topR:
        curve = st.session_state.get("curve") or compute_training_curve()
        st.subheader("Curve telemetry")
        st.metric("AGI", curve.get("AGI", 0.0))
        st.metric("Slope", curve.get("improvement_slope", 0.0))
        st.metric("Volatility", curve.get("volatility_index", 0.0))
        st.metric("Diff-weighted avg", curve.get("difficulty_weighted_average", 0.0))

        st.subheader("Obasi Live Coach")
        msg = build_obasi_training_coach_speech(
            trainee_name=trainee_name,
            difficulty=difficulty,
            agi=curve.get("AGI", 0.0),
            improvement_slope=curve.get("improvement_slope", 0.0),
            volatility_index=curve.get("volatility_index", 0.0),
            notes=("Gate GREEN" if gate_green else "Gate RED"),
        )
        st.text_area("Coach", value=msg, height=260)

    st.divider()
    st.subheader("Recent sessions")
    sessions = load_sessions()
    for s in list(reversed(sessions))[:12]:
        st.write(
            f"- **{s.get('session_id')}** | {s.get('created_at')} | "
            f"{s.get('difficulty')} | score={s.get('score')} | counted={s.get('counted')}"
        )


if __name__ == "__main__":
    main()

