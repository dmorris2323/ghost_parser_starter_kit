# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st

from training_session_store import load_sessions
from training_feedback_store import load_latest_feedback
from operator_certification_mode import compute_certification_status
from command_brief_exporter import export_command_brief

try:
    from training_curve_engine import compute_training_curve
except Exception:
    compute_training_curve = None

try:
    from fusion_validation_harness import load_latest_validation_report
except Exception:
    load_latest_validation_report = None


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center")

    sessions = load_sessions()
    feedback = load_latest_feedback()

    curve = {}
    if compute_training_curve:
        curve = compute_training_curve()

    cert = compute_certification_status(
        sessions=sessions,
        target_difficulty="ADVERSARIAL",
        required_pass_streak=5,
        require_no_safety_flags=True,
    )

    validation = load_latest_validation_report() if load_latest_validation_report else None

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Readiness Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI", curve.get("AGI", 0))
        c2.metric("Slope", curve.get("improvement_slope", 0))
        c3.metric("Difficulty Avg", curve.get("difficulty_weighted_average", 0))
        c4.metric("Volatility", curve.get("volatility_index", 0))

        st.subheader("Certification Status")
        st.json(cert)

    with col2:
        st.subheader("Export Command Brief")
        trainee = st.text_input("Trainee name", value="Ghost")

        if st.button("📄 Generate Command-Grade PDF", type="primary"):
            path = export_command_brief(
                trainee_name=trainee,
                training_curve=curve,
                validation_report=validation,
                certification_status=cert,
                training_feedback=feedback,
            )
            st.success("Brief generated.")
            st.download_button(
                label="Download PDF",
                data=path.read_bytes(),
                file_name=path.name,
                mime="application/pdf",
            )


if __name__ == "__main__":
    main()

