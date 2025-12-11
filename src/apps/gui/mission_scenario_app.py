#!/usr/bin/env python3
"""
mission_scenario_app.py

Ghost Lantern Labs – Hybrid Fusion Scenario Trainer
---------------------------------------------------

Impact Module 4 – Mission Scenario Mode (with difficulty levels)

Purpose:
    Streamlit GUI to run the flagship HYBRID_FUSION_01 scenario:

        • Nuclear early-warning
        • Base-defense (drones/perimeter)
        • Cyber/DLP (beaconing)
        • SPS/system integrity awareness

    Supports difficulty tiers:
        • Cadet (beginner)
        • Analyst (intermediate)
        • War Room (advanced)

Workflow:
    1. Trainee enters their name and selects difficulty.
    2. Scenario description and questions are shown.
    3. Trainee makes decisions for each phase.
    4. Engine evaluates decisions and produces:
        - rubric (0–5 per dimension)
        - composite score (0–100)
        - feedback per question
    5. Session is logged in src/docs/training_sessions.json.
    6. Obasi provides coaching based on the resulting score.
"""

from datetime import date
from typing import Dict, Any
from pathlib import Path
import sys

import streamlit as st

# ---------------------------------------------------------------------------
# Make sure src/ is on sys.path so we can import scenario_engine
# ---------------------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parents[2]  # .../src

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from scenario_engine import (  # type: ignore  # noqa: E402
    get_hybrid_scenario_definition,
    evaluate_hybrid_scenario,
    record_hybrid_scenario_session,
)
from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _difficulty_label_to_code(label: str) -> str:
    mapping = {
        "Cadet (Beginner)": "CADET",
        "Analyst (Intermediate)": "ANALYST",
        "War Room (Advanced)": "WAR_ROOM",
    }
    return mapping.get(label, "ANALYST")


def _difficulty_code_to_label(code: str) -> str:
    code = code.upper()
    mapping = {
        "CADET": "Cadet (Beginner)",
        "ANALYST": "Analyst (Intermediate)",
        "WAR_ROOM": "War Room (Advanced)",
    }
    return mapping.get(code, code)


def _build_obasi_message(score: float | None) -> str:
    """
    Thin wrapper in case the coach function signature changes.
    """
    try:
        return build_obasi_training_coach_speech(score)
    except TypeError:
        return build_obasi_training_coach_speech()
    except Exception:
        return (
            "Obasi: Coach channel degraded. Focus on what the score tells you: "
            "what did you miss, and how can you tighten your next run?"
        )


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="GLL – Hybrid Fusion Scenario Trainer",
        layout="wide",
    )

    scenario = get_hybrid_scenario_definition()

    st.title("🦉 Ghost Lantern Labs – Hybrid Fusion Scenario Trainer")
    st.caption(
        "Nuclear + base-defense + cyber fusion training scenario with difficulty levels."
    )

    with st.sidebar:
        st.header("Trainee Setup")
        trainee_name = st.text_input("Trainee name", value="Ghost").strip()
        difficulty_label = st.radio(
            "Difficulty",
            options=[
                "Cadet (Beginner)",
                "Analyst (Intermediate)",
                "War Room (Advanced)",
            ],
            index=1,
        )
        difficulty_code = _difficulty_label_to_code(difficulty_label)

        session_date = st.date_input("Session date", value=date.today())

        st.markdown("---")
        st.caption(
            "Tip: Run multiple reps at higher difficulty to build a visible improvement curve "
            "in the Training Dashboard."
        )

    st.subheader(f"Scenario: {scenario['name']}")
    st.write(scenario["summary"])

    st.markdown("### Phases")
    for phase in scenario["phases"]:
        st.markdown(f"- {phase}")

    st.markdown("---")
    st.subheader("Mission Questions")

    questions = scenario["questions"]

    # Collect decisions from user
    decisions: Dict[str, str] = {}
    for q in questions:
        st.markdown(f"**{q['phase']} – {q['id']}**")
        st.write(q["prompt"])
        choice_keys = list(q["choices"].keys())
        chosen_label = st.radio(
            "Select your decision:",
            options=[f"{k}: {q['choices'][k]}" for k in choice_keys],
            index=0,
            key=f"choice_{q['id']}",
        )
        # Extract key from "KEY: description"
        chosen_key = chosen_label.split(":", 1)[0]
        decisions[q["id"]] = chosen_key
        st.markdown("---")

    run_eval = st.button("Run Scenario Evaluation and Save Session")

    if run_eval:
        if not trainee_name:
            st.error("Trainee name is required.")
            return

        eval_result = evaluate_hybrid_scenario(decisions, difficulty_code)
        session_entry = record_hybrid_scenario_session(
            trainee_name=trainee_name,
            difficulty=difficulty_code,
            eval_result=eval_result,
            session_date=session_date,
        )

        st.success(
            f"Scenario evaluated for {trainee_name} "
            f"({difficulty_label}). Composite score: {eval_result['composite_score']}."
        )

        # Show rubric + score
        st.subheader("Rubric & Score")
        col1, col2 = st.columns(2)
        rubric = eval_result["rubric"]
        with col1:
            st.metric("Composite Score", eval_result["composite_score"])
            st.metric("Analysis Quality (0–5)", rubric["analysis_quality"])
            st.metric("Fusion Thinking (0–5)", rubric["fusion_thinking"])
        with col2:
            st.metric("Nuclear Relevance (0–5)", rubric["nuclear_relevance"])
            st.metric("Reporting Discipline (0–5)", rubric["reporting_discipline"])
            st.text(f"Mode: SCENARIO – {session_entry.get('scenario_type')}")

        # Obasi coaching
        st.subheader("🦉 Obasi – Scenario Coaching")
        st.write(_build_obasi_message(eval_result["composite_score"]))

        # Per-question feedback
        st.subheader("Per-Question Feedback")
        for pq in eval_result["per_question"]:
            st.markdown(f"**{pq['question_id']}**")
            st.write(pq["feedback"])

        st.markdown("---")
        st.caption(
            "Scenario run has been saved into src/docs/training_sessions.json and "
            "will appear in the Training Dashboard as a scenario-type session."
        )
    else:
        st.info(
            "Configure trainee name and difficulty, answer the mission questions, "
            "then click 'Run Scenario Evaluation and Save Session'."
        )


if __name__ == "__main__":
    main()

