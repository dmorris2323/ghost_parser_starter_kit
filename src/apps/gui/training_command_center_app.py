# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from training_session_store import load_sessions  # type: ignore
from training_curve_engine import compute_training_curve  # type: ignore
from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center")
    st.caption("Executive view of training performance + stability.")

    curve = compute_training_curve()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI (0–100)", curve["AGI"])
    c2.metric("Improvement slope", curve["improvement_slope"])
    c3.metric("Difficulty-weighted avg", curve["difficulty_weighted_average"])
    c4.metric("Volatility index", curve["volatility_index"])

    sessions = load_sessions()
    last = sessions[-1] if sessions else {}
    trainee = (last.get("trainee_name") or "Operator")
    difficulty = (last.get("difficulty") or "INTERMEDIATE")

    st.divider()
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Obasi Guidance")
        msg = build_obasi_training_coach_speech(
            trainee_name=trainee,
            difficulty=difficulty,
            curve=curve,
            last_session=last,
            gate_summary=None,
        )
        st.markdown(msg)

    with right:
        st.subheader("Session Feed")
        if not sessions:
            st.info("No sessions yet. Use Training Dashboard to log sessions.")
        else:
            st.dataframe(
                [
                    {
                        "time": s.get("created_at"),
                        "trainee": s.get("trainee_name"),
                        "difficulty": s.get("difficulty"),
                        "scenario": s.get("scenario_id"),
                        "valid": s.get("session_valid"),
                        "reason": s.get("invalid_reason"),
                    }
                    for s in list(reversed(sessions))[:30]
                ],
                use_container_width=True,
                height=520,
            )


if __name__ == "__main__":
    main()

