# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# ---- Path bootstrap (Streamlit runs from repo root, but we make it bulletproof) ----
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]           # .../parser_starter_kit
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from training_session_store import append_session, load_sessions  # type: ignore
from training_curve_engine import compute_training_curve          # type: ignore
from training_grading_weights import weights_as_dict              # type: ignore
from training_validation_gate import summarize_gate, decide_training_gate  # type: ignore
from obasi_training_coach import build_obasi_training_coach_speech         # type: ignore


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")

    st.title("GLL Training Dashboard")
    st.caption("Difficulty → session log → gates → AGI/slope/volatility (live).")

    # Sidebar controls
    st.sidebar.header("Session Controls")
    trainee_name = st.sidebar.text_input("Trainee name", value="Ghost")
    difficulty = st.sidebar.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
    scenario_id = st.sidebar.text_input("Scenario ID", value="TRAINING_RUN")
    pattern_id = st.sidebar.text_input("Pattern ID (optional)", value="")
    pattern_seed = st.sidebar.number_input("Pattern seed (optional)", value=0, step=1)

    st.sidebar.subheader("Gate Inputs (manual for now)")
    sis_status = st.sidebar.selectbox("SIS status", ["GREEN", "YELLOW", "RED", "UNKNOWN"], index=0)
    sps_status = st.sidebar.selectbox("SPS status", ["GREEN", "YELLOW", "RED", "UNKNOWN"], index=0)
    validation_verdict = st.sidebar.selectbox("Validation verdict", ["PASS", "WARN", "FAIL", "UNKNOWN"], index=0)

    st.sidebar.subheader("Rubric (0–100)")
    accuracy = st.sidebar.slider("Accuracy", 0, 100, 80)
    reasoning = st.sidebar.slider("Reasoning", 0, 100, 75)
    stability = st.sidebar.slider("Stability", 0, 100, 80)
    speed = st.sidebar.slider("Speed", 0, 100, 65)

    # Show difficulty profile
    prof = weights_as_dict(difficulty)
    st.sidebar.markdown("### Difficulty profile")
    st.sidebar.json(prof)

    colA, colB = st.columns([1.2, 1])

    with colA:
        st.subheader("Log a Session")
        clicked = st.button("✅ Log Session & Recompute Curve", use_container_width=True)

        last_result = None
        last_gate_summary = None

        if clicked:
            gate = decide_training_gate(
                sis_status=sis_status,
                sps_status=sps_status,
                validation_verdict=validation_verdict,
            )
            last_gate_summary = summarize_gate(gate)

            last_result = append_session(
                trainee_name=trainee_name,
                difficulty=difficulty,
                rubric={"accuracy": accuracy, "reasoning": reasoning, "stability": stability, "speed": speed},
                scenario_id=scenario_id,
                pattern_id=(pattern_id.strip() or None),
                pattern_seed=(int(pattern_seed) if pattern_seed else None),
                sis_status=sis_status,
                sps_status=sps_status,
                validation_verdict=validation_verdict,
                extra={"ui": "training_dashboard_app"},
            )
            st.success(f"Session stored. Total sessions: {last_result['total_sessions']} | Valid: {last_result['valid_sessions']}")

        # Always recompute curve (safe) so UI shows latest
        curve = compute_training_curve()

        # Metrics row (these keys are guaranteed by your Day 68 curve engine)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("AGI (0–100)", curve["AGI"])
        m2.metric("Improvement slope", curve["improvement_slope"])
        m3.metric("Difficulty-weighted avg", curve["difficulty_weighted_average"])
        m4.metric("Volatility index", curve["volatility_index"])

        st.divider()
        st.subheader("Obasi Coach Panel")

        last_session = (last_result or {}).get("session", {})
        coach_msg = build_obasi_training_coach_speech(
            trainee_name=trainee_name,
            difficulty=difficulty,
            curve=curve,
            last_session=last_session,
            gate_summary=last_gate_summary,
        )
        st.markdown(coach_msg)

    with colB:
        st.subheader("Recent Sessions")
        sessions = load_sessions()
        sessions = list(reversed(sessions))[:20]
        if not sessions:
            st.info("No sessions yet. Log one on the left.")
        else:
            st.dataframe(
                [
                    {
                        "time": s.get("created_at"),
                        "difficulty": s.get("difficulty"),
                        "scenario": s.get("scenario_id"),
                        "valid": s.get("session_valid"),
                        "reason": s.get("invalid_reason"),
                        "accuracy": (s.get("rubric") or {}).get("accuracy"),
                        "reasoning": (s.get("rubric") or {}).get("reasoning"),
                        "stability": (s.get("rubric") or {}).get("stability"),
                        "speed": (s.get("rubric") or {}).get("speed"),
                    }
                    for s in sessions
                ],
                use_container_width=True,
                height=520,
            )


if __name__ == "__main__":
    main()

