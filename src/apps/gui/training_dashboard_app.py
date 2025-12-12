from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import streamlit as st


# Ensure repo/src is importable when running streamlit from repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from difficulty_scaling_engine import explain_difficulty, list_difficulties  # noqa: E402
from instructor_autograder import grade_session  # noqa: E402
from obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402
from training_curve_engine import compute_training_curve  # noqa: E402
from training_session_store import append_session, load_sessions  # noqa: E402


st.set_page_config(page_title="GLL Training Dashboard", layout="wide")


def _ui_rubric_inputs() -> Dict[str, float]:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        accuracy = st.slider("Accuracy", 0, 100, 75)
    with c2:
        discipline = st.slider("Discipline", 0, 100, 75)
    with c3:
        procedure = st.slider("Procedure", 0, 100, 75)
    with c4:
        timeliness = st.slider("Timeliness", 0, 100, 70)
    with c5:
        comms_clarity = st.slider("Comms clarity", 0, 100, 75)
    return {
        "accuracy": float(accuracy),
        "discipline": float(discipline),
        "procedure": float(procedure),
        "timeliness": float(timeliness),
        "comms_clarity": float(comms_clarity),
    }


def main() -> None:
    st.title("🦉 GLL Training Dashboard")
    st.caption("Difficulty-aware session logging + live AGI / slope / volatility updates.")

    with st.sidebar:
        st.header("Controls")
        trainee_name = st.text_input("Trainee name", value="Ghost")

        difficulty = st.selectbox("Difficulty", options=list_difficulties(), index=1)
        d_name, d_desc = explain_difficulty(difficulty)
        st.info(f"**{d_name}** — {d_desc}")

        gate_green = st.checkbox("SIS/SPS Gate GREEN (counts toward AGI)", value=True)
        notes = st.text_area("Notes (optional)", value="", height=100)

    st.subheader("Rubric inputs (0–100)")
    rubric = _ui_rubric_inputs()

    # Live grading preview
    result = grade_session(
        difficulty=difficulty,
        accuracy=rubric["accuracy"],
        timeliness=rubric["timeliness"],
        discipline=rubric["discipline"],
        comms_clarity=rubric["comms_clarity"],
        procedure=rubric["procedure"],
        gate_green=gate_green,
    )

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Auto-grade (preview)")
        st.metric("Score", result["score"])
        st.metric("Pass threshold", result["score_floor"])
        st.metric("Passed", "YES" if result["passed"] else "NO")
        st.metric("Counts toward AGI", "YES" if result["counted"] else "NO")
        st.json({"weights": result["grader_weights"], "inputs": result["inputs"]})

    with right:
        st.subheader("Obasi coach (preview)")
        coach_msg = build_obasi_training_coach_speech(
            trainee_name=trainee_name,
            difficulty=difficulty,
            agi=0,  # will be replaced after logging / curve compute
            improvement_slope=0,
            volatility_index=0,
            notes=("Gate GREEN" if gate_green else "Gate RED") + (f" | {notes}" if notes else ""),
        )
        st.text_area("Coach message", value=coach_msg, height=240)

    st.divider()

    colA, colB, colC = st.columns([1, 1, 2])
    with colA:
        if st.button("✅ Log session", use_container_width=True):
            stored = append_session(
                {
                    "difficulty": result["difficulty"],
                    "score": result["score"],
                    "passed": result["passed"],
                    "gate_green": result["gate_green"],
                    "counted": result["counted"],
                    "grader_weights": result["grader_weights"],
                    "rubric_inputs": result["inputs"],
                    "trainee_name": trainee_name,
                    "notes": notes,
                }
            )
            curve = compute_training_curve()
            st.success(f"Session logged: {stored.get('session_id')} | Counted: {stored.get('counted')}")
            st.session_state["curve"] = curve

    with colB:
        if st.button("🔄 Recompute curve", use_container_width=True):
            curve = compute_training_curve()
            st.session_state["curve"] = curve
            st.info("Curve recomputed.")

    with colC:
        curve = st.session_state.get("curve") or compute_training_curve()
        st.subheader("Training curve (live)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI (0–100)", curve.get("AGI", 0.0))
        c2.metric("Slope", curve.get("improvement_slope", 0.0))
        c3.metric("Volatility", curve.get("volatility_index", 0.0))
        c4.metric("Diff-weighted avg", curve.get("difficulty_weighted_average", 0.0))

    st.divider()
    st.subheader("Recent sessions")
    sessions = load_sessions()
    sessions = list(reversed(sessions))[:10]
    if not sessions:
        st.write("No sessions logged yet.")
        return

    for s in sessions:
        st.write(
            f"- **{s.get('session_id')}** | {s.get('created_at')} | "
            f"{s.get('difficulty')} | score={s.get('score')} | counted={s.get('counted')}"
        )


if __name__ == "__main__":
    main()

