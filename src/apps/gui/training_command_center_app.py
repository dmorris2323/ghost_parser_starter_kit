# src/apps/gui/training_command_center_app.py
from __future__ import annotations

# --- Streamlit path bootstrap (REQUIRED) ---
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ------------------------------------------

import streamlit as st

from training_session_store import load_sessions
from training_feedback_store import load_latest_feedback
from obasi_training_coach import build_obasi_training_coach_speech

from operator_certification_mode import compute_certification_status

try:
    from training_curve_engine import compute_training_curve
except Exception:
    compute_training_curve = None


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center")
    st.caption("Commander view: curve + volatility + certification readiness.")

    sessions = load_sessions()
    feedback = load_latest_feedback()

    curve = {}
    if compute_training_curve is not None:
        try:
            curve = compute_training_curve()
        except Exception as e:
            st.error(f"training_curve_engine failed: {e}")

    top = st.columns(4)
    top[0].metric("AGI", curve.get("AGI", 0.0))
    top[1].metric("Slope", curve.get("improvement_slope", 0.0))
    top[2].metric("Difficulty Avg", curve.get("difficulty_weighted_average", 0.0))
    top[3].metric("Volatility", curve.get("volatility_index", 0.0))

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("🧭 Next Training Recommendation")
        st.json(feedback)

        st.subheader("🎖️ Certification Readiness")
        target = st.selectbox("Target Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=2)
        streak = st.number_input("Required PASS streak", value=5, min_value=2, max_value=20, step=1)
        cert = compute_certification_status(
            sessions=sessions,
            target_difficulty=target,
            required_pass_streak=int(streak),
            require_no_safety_flags=True,
        )
        st.json(cert)

        st.subheader("🦉 Obasi Coach")
        msg = build_obasi_training_coach_speech(
            trainee_name="Ghost",
            difficulty=curve.get("latest_difficulty", "INTERMEDIATE"),
            AGI=curve.get("AGI", 0.0),
            improvement_slope=curve.get("improvement_slope", 0.0),
            volatility_index=curve.get("volatility_index", 0.0),
        )
        st.text(msg)

    with right:
        st.subheader("Recent Sessions")
        if sessions:
            st.dataframe(list(reversed(sessions))[:25], use_container_width=True)
        else:
            st.info("No sessions logged yet.")


if __name__ == "__main__":
    main()

