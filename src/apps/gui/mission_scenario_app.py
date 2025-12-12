# src/apps/gui/mission_scenario_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str((REPO_ROOT / "src").resolve())
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from scenario_engine import build_training_scenario
from training_validation_gate import evaluate_training_gate, gate_to_dict
from instructor_autograder import auto_grade_session
from training_session_store import append_session, load_sessions


def main():
    st.set_page_config(page_title="GLL Mission Scenario (Training)", layout="wide")
    st.title("GLL Mission Scenario App (Training)")
    st.caption("Synthetic, training-only scenarios. Difficulty changes inject pressure + grading expectations.")

    left, right = st.columns([1, 2])

    with left:
        trainee = st.text_input("Trainee", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        seed = st.number_input("Scenario seed", min_value=1, max_value=999999, value=99, step=1)

        st.subheader("Integrity Gate (counts → AGI only if PASS)")
        gate = evaluate_training_gate(require_all_green=True)
        st.json({"status": gate.status, "counted_for_agi": gate.counted_for_agi, "message": gate.message})

        st.subheader("Quick Scores (0–1)")
        acc = st.slider("Accuracy", 0.0, 1.0, 0.75, 0.01)
        spd = st.slider("Speed", 0.0, 1.0, 0.65, 0.01)
        trd = st.slider("Tradecraft", 0.0, 1.0, 0.60, 0.01)

        if st.button("Generate Scenario"):
            scenario = build_training_scenario(difficulty=difficulty, seed=int(seed))
            st.session_state["scenario"] = scenario

        if st.button("Log Scenario Session"):
            scenario = st.session_state.get("scenario") or build_training_scenario(difficulty=difficulty, seed=int(seed))
            grade = auto_grade_session(
                trainee_name=trainee,
                difficulty=difficulty,
                raw_scores={"accuracy": acc, "speed": spd, "tradecraft": trd},
            )

            session = {
                "trainee_name": trainee,
                "difficulty": difficulty,
                "session_type": "scenario",
                "scenario": scenario,
                "raw_scores": {"accuracy": acc, "speed": spd, "tradecraft": trd},
                "auto_grade": grade,
                "gate": gate_to_dict(gate),
                "counted_for_agi": bool(gate.counted_for_agi),
            }
            saved = append_session(session)
            st.success(f"Logged {saved.get('session_id')} | Passed: {grade.get('passed')} | Counted: {saved.get('counted_for_agi')}")

    with right:
        scenario = st.session_state.get("scenario")
        if not scenario:
            scenario = build_training_scenario(difficulty=difficulty, seed=int(seed))
            st.session_state["scenario"] = scenario

        st.subheader("Scenario")
        st.json(scenario)

        st.subheader("Timeline")
        st.dataframe(scenario.get("timeline", []), use_container_width=True)

        st.subheader("Recent Sessions")
        sessions = load_sessions()
        if sessions:
            st.dataframe(list(reversed(sessions))[:20], use_container_width=True)
        else:
            st.info("No sessions yet.")


if __name__ == "__main__":
    main()

