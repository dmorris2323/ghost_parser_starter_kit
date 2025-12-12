# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from difficulty_scaling_engine import list_difficulties, normalize_difficulty
from instructor_grading_weights import CATEGORIES, score_session, expectation_band, get_weights_for_difficulty
from training_session_store import build_session, append_session, load_sessions
from training_curve_engine import write_training_curve_json
from obasi_training_coach import build_obasi_training_coach_speech


def _metric_row(curve: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI", curve.get("AGI", 0.0))
    c2.metric("Slope", curve.get("improvement_slope", 0.0))
    c3.metric("Difficulty Avg", curve.get("difficulty_weighted_average", 0.0))
    c4.metric("Volatility", curve.get("volatility_index", 0.0))


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("🧭 GLL Training Command Center")
    st.caption("Operator view: select difficulty → run session → log → watch curve move in real time.")

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Operator Controls")
        trainee_name = st.text_input("Operator / Trainee", value="Ghost")
        difficulty = st.selectbox("Difficulty", options=list_difficulties(), index=1)
        scenario_id = st.text_input("Scenario ID", value="WAR_ROOM_DRILL")
        pattern_id = st.text_input("Pattern ID (optional)", value="")

        st.divider()
        st.subheader("Fast Rubric (0–100)")
        weights = get_weights_for_difficulty(difficulty)
        rubric = {}
        for k in CATEGORIES:
            rubric[k] = st.slider(f"{k.replace('_',' ').title()} (wt {weights[k]:.2f})", 0, 100, 75)

        band = expectation_band(difficulty)
        st.info(
            f"Expectations @ {difficulty}: target≈{band['expected_target']} | "
            f"vol tol≈{band['volatility_tolerance']} | scalar={band['weight_scalar']}"
        )

        log_btn = st.button("✅ Run + Log Session")

    with right:
        st.subheader("Curve Snapshot (Live)")
        curve_path, curve = write_training_curve_json(max_sessions=50, only_gated=False)
        _metric_row(curve)

        coach_msg = build_obasi_training_coach_speech(
            trainee_name=trainee_name,
            difficulty=difficulty,
            agi=curve.get("AGI"),
            improvement_slope=curve.get("improvement_slope"),
            volatility_index=curve.get("volatility_index"),
            notes="Command Center ready. Log sessions to drive AGI/slope/volatility.",
        )
        st.text_area("🦉 Obasi Live Guidance", value=coach_msg, height=180)

        st.caption(f"Curve JSON: {curve_path}")

    if log_btn:
        final, breakdown = score_session(rubric, difficulty)
        srec = build_session(
            trainee_name=trainee_name,
            difficulty=normalize_difficulty(difficulty),
            scenario_id=scenario_id,
            final_score=final,
            rubric_scores=breakdown,
            pattern_id=(pattern_id.strip() or None),
            notes="Logged from Training Command Center",
            gate_passed=True,
        )
        append_session(srec)
        curve_path, curve = write_training_curve_json(max_sessions=50, only_gated=False)
        st.success(f"Session logged @ {difficulty}. Final score: {final:.1f}")
        _metric_row(curve)

    st.divider()
    st.subheader("Recent Sessions (latest 10)")
    st.json(list(reversed(load_sessions()[-10:])))


if __name__ == "__main__":
    main()

