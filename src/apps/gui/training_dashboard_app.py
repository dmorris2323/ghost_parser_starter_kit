# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure src/ imports work when streamlit runs from repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from difficulty_scaling_engine import list_difficulties, get_profile, normalize_difficulty
from instructor_grading_weights import CATEGORIES, score_session, expectation_band, get_weights_for_difficulty
from training_session_store import build_session, append_session, load_sessions
from training_curve_engine import write_training_curve_json
from obasi_training_coach import build_obasi_training_coach_speech


def _metric_row(curve: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI (0–100)", curve.get("AGI", 0.0))
    c2.metric("Slope", curve.get("improvement_slope", 0.0))
    c3.metric("Difficulty Avg", curve.get("difficulty_weighted_average", 0.0))
    c4.metric("Volatility", curve.get("volatility_index", 0.0))


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("🎯 GLL Training Dashboard")
    st.caption("Tracks sessions → rubric score → difficulty weighting → AGI / slope / volatility. Synthetic/training-safe.")

    with st.sidebar:
        st.header("Session Controls")
        trainee_name = st.text_input("Trainee name", value="Ghost")
        difficulty = st.selectbox("Difficulty", options=list_difficulties(), index=1)
        scenario_id = st.text_input("Scenario ID", value="WARGAME_SYNTH")
        pattern_id = st.text_input("Pattern ID (optional)", value="")
        notes = st.text_area("Notes (optional)", value="", height=90)

        st.divider()
        st.subheader("Instructor Rubric (0–100 each)")
        weights = get_weights_for_difficulty(difficulty)
        rubric = {}
        for k in CATEGORIES:
            label = f"{k.replace('_',' ').title()} (wt {weights[k]:.2f})"
            rubric[k] = st.slider(label, 0, 100, 75)

        band = expectation_band(difficulty)
        st.divider()
        st.subheader("Difficulty Expectations")
        st.write(
            {
                "expected_min": band["expected_min"],
                "expected_target": band["expected_target"],
                "expected_max": band["expected_max"],
                "volatility_tolerance": band["volatility_tolerance"],
                "weight_scalar": band["weight_scalar"],
            }
        )

        commit_now = st.button("✅ Log Session (counts immediately)")

    # Current curve
    curve_path, curve = write_training_curve_json(max_sessions=50, only_gated=False)
    _metric_row(curve)

    # Obasi guidance
    coach_msg = build_obasi_training_coach_speech(
        trainee_name=trainee_name,
        difficulty=difficulty,
        agi=curve.get("AGI"),
        improvement_slope=curve.get("improvement_slope"),
        volatility_index=curve.get("volatility_index"),
        sis_status=None,
        sps_status=None,
        notes="Training dashboard active. Log a session to move the curve.",
    )
    st.text_area("🦉 Obasi Coach (live)", value=coach_msg, height=160)

    st.divider()
    st.subheader("Log a new session")

    if commit_now:
        final, breakdown = score_session(rubric, difficulty)
        srec = build_session(
            trainee_name=trainee_name,
            difficulty=normalize_difficulty(difficulty),
            scenario_id=scenario_id,
            final_score=final,
            rubric_scores=breakdown,
            pattern_id=(pattern_id.strip() or None),
            notes=notes,
            # gates can be wired later; for now, leave None/True as you choose
            gate_passed=True,
        )
        append_session(srec)

        # recompute curve immediately
        curve_path, curve = write_training_curve_json(max_sessions=50, only_gated=False)

        st.success(f"Session logged. Final score: {final:.1f}")
        _metric_row(curve)

    st.divider()
    st.subheader("Recent sessions (latest 12)")
    sessions = load_sessions()[-12:]
    sessions = list(reversed(sessions))
    st.json(sessions)

    st.caption(f"Curve JSON written to: {curve_path}")


if __name__ == "__main__":
    main()

