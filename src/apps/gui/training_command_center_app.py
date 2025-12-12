# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str((REPO_ROOT / "src").resolve())
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from training_curve_engine import compute_training_curve
from training_validation_gate import evaluate_training_gate, gate_to_dict
from training_session_store import load_sessions
from obasi_training_coach import build_obasi_training_coach_speech


def main():
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center")
    st.caption("Switch difficulty live. Watch AGI + slope + volatility respond as sessions accumulate.")

    top = st.columns([1, 1, 2])

    with top[0]:
        trainee = st.text_input("Trainee", value="Ghost")
    with top[1]:
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
    with top[2]:
        gate = evaluate_training_gate(require_all_green=True)
        st.metric("Integrity Gate", gate.status, "Counted" if gate.counted_for_agi else "Not counted")
        st.caption(gate.message)

    curve = compute_training_curve(difficulty_filter=difficulty)

    row = st.columns(4)
    row[0].metric("AGI (0–100)", f"{curve.get('AGI', 0.0):.1f}")
    row[1].metric("Slope", f"{curve.get('improvement_slope', 0.0):.2f}")
    row[2].metric("Weighted Avg", f"{curve.get('difficulty_weighted_average', 0.0):.1f}")
    row[3].metric("Volatility", f"{curve.get('volatility_index', 0.0):.3f}")

    st.subheader("Obasi Live Guidance")
    msg = build_obasi_training_coach_speech(
        trainee_name=trainee,
        difficulty=difficulty,
        curve=curve,
        gate=gate_to_dict(gate),
    )
    st.text(msg)

    st.subheader("Session Feed")
    sessions = load_sessions()
    if sessions:
        st.dataframe(list(reversed(sessions))[:50], use_container_width=True)
    else:
        st.info("No sessions yet. Log sessions from the Training Dashboard.")


if __name__ == "__main__":
    main()

