# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# Ensure repo/src is importable when running streamlit from repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str((REPO_ROOT / "src").resolve())
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from training_session_store import load_sessions, append_session
from training_validation_gate import evaluate_training_gate, gate_to_dict
from training_difficulty_engine import get_profile, compute_weighted_grade
from obasi_training_coach import build_obasi_training_coach_speech

# Optional curve engine (don’t hard-fail if missing)
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
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("GLL Training Dashboard")
    st.caption("Training-only. Uses synthetic data + validation gates. Sessions count toward AGI only when system is GREEN.")

    left, right = st.columns([1, 2])

    with left:
        trainee_name = st.text_input("Trainee name", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        profile = get_profile(difficulty)

        st.subheader("Difficulty expectations")
        st.json(profile)

        st.subheader("Raw scoring (0–1)")
        acc = st.slider("Accuracy", 0.0, 1.0, 0.75, 0.01)
        spd = st.slider("Speed", 0.0, 1.0, 0.65, 0.01)
        trd = st.slider("Tradecraft", 0.0, 1.0, 0.60, 0.01)

        grade = compute_weighted_grade({"accuracy": acc, "speed": spd, "tradecraft": trd}, difficulty)
        st.subheader("Difficulty-weighted grade")
        st.json(grade)

        st.subheader("Validation Gate (counts→AGI only if PASS)")
        gate = evaluate_training_gate(require_all_green=True)
        gate_dict = gate_to_dict(gate)
        st.json({"status": gate.status, "counted_for_agi": gate.counted_for_agi, "message": gate.message})

        if st.button("Log Session"):
            session = {
                "trainee_name": trainee_name,
                "difficulty": difficulty,
                "difficulty_profile": profile,
                "raw_scores": {"accuracy": acc, "speed": spd, "tradecraft": trd},
                "grade": grade,
                "gate": gate_dict,
                "counted_for_agi": bool(gate.counted_for_agi),
            }
            saved = append_session(session)
            st.success(f"Session logged: {saved.get('session_id')} | Counted for AGI: {saved.get('counted_for_agi')}")

    with right:
        sessions = load_sessions()
        curve = _safe_curve()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI (0–100)", curve.get("AGI", 0.0))
        c2.metric("Improvement Slope", curve.get("improvement_slope", 0.0))
        c3.metric("Difficulty-Weighted Avg", curve.get("difficulty_weighted_average", 0.0))
        c4.metric("Volatility Index", curve.get("volatility_index", 0.0))

        st.subheader("Obasi Coach Panel")
        coach_msg = build_obasi_training_coach_speech(
            trainee_name=trainee_name,
            difficulty=difficulty,
            curve=curve,
            sessions=sessions,
            gate=gate_to_dict(evaluate_training_gate(require_all_green=True)),
        )
        st.code(coach_msg)

        st.subheader("Recent Sessions")
        if sessions:
            st.dataframe(list(reversed(sessions))[:25], use_container_width=True)
        else:
            st.info("No sessions yet. Log your first session on the left.")

        st.subheader("Gate Evidence (files seen)")
        st.write(gate_dict.get("files_seen", []))


if __name__ == "__main__":
    main()

