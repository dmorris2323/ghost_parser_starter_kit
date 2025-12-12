# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str((REPO_ROOT / "src").resolve())
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from training_session_store import load_sessions
from training_validation_gate import evaluate_training_gate, gate_to_dict
from training_difficulty_engine import get_profile
from obasi_training_coach import build_obasi_training_coach_speech

try:
    from training_curve_engine import compute_training_curve
except Exception:
    compute_training_curve = None  # type: ignore


def _safe_curve() -> dict:
    if compute_training_curve is None:
        return {"AGI": 0.0, "improvement_slope": 0.0, "difficulty_weighted_average": 0.0, "volatility_index": 0.0}
    try:
        return compute_training_curve()
    except Exception:
        return {"AGI": 0.0, "improvement_slope": 0.0, "difficulty_weighted_average": 0.0, "volatility_index": 0.0}


def main():
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center")
    st.caption("Live training posture + integrity gating + coach guidance.")

    top1, top2, top3 = st.columns([1, 1, 2])

    with top1:
        trainee_name = st.text_input("Trainee", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        st.json(get_profile(difficulty))

    with top2:
        gate = evaluate_training_gate(require_all_green=True)
        st.subheader("Gate Status")
        st.metric("Gate", gate.status)
        st.metric("Counts toward AGI", "YES" if gate.counted_for_agi else "NO")
        st.write(gate.message)

    with top3:
        curve = _safe_curve()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI", curve.get("AGI", 0.0))
        c2.metric("Slope", curve.get("improvement_slope", 0.0))
        c3.metric("DW Avg", curve.get("difficulty_weighted_average", 0.0))
        c4.metric("Volatility", curve.get("volatility_index", 0.0))

    st.divider()

    left, right = st.columns([2, 2])

    with left:
        st.subheader("Obasi Coach")
        sessions = load_sessions()
        msg = build_obasi_training_coach_speech(
            trainee_name=trainee_name,
            difficulty=difficulty,
            curve=curve,
            sessions=sessions,
            gate=gate_to_dict(gate),
        )
        st.code(msg)

    with right:
        st.subheader("Sessions (latest 25)")
        sessions = load_sessions()
        if sessions:
            st.dataframe(list(reversed(sessions))[:25], use_container_width=True)
        else:
            st.info("No sessions logged yet.")

        st.subheader("Gate Files Seen")
        st.write(gate_to_dict(gate).get("files_seen", []))


if __name__ == "__main__":
    main()

