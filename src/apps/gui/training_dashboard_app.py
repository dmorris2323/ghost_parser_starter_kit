# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

# Ensure src/ is on sys.path no matter where Streamlit executes from
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from training_session_store import load_sessions, append_session  # noqa: E402
from obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402


def _safe_curve() -> Dict[str, Any]:
    try:
        from training_curve_engine import compute_training_curve  # type: ignore

        curve = compute_training_curve()
        return curve if isinstance(curve, dict) else {}
    except Exception:
        return {}


def _load_latest_training_feedback() -> Dict[str, Any]:
    # Read-only; safe if file missing
    try:
        import json

        p = Path("src") / "docs" / "training" / "training_feedback_latest.json"
        if not p.exists():
            return {}
        raw = json.loads(p.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("GLL Training Dashboard")

    sessions: List[Dict[str, Any]] = load_sessions()
    curve = _safe_curve()
    feedback = _load_latest_training_feedback()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Log a Training Session")

        trainee_name = st.text_input("Trainee name", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"], index=1)
        score = st.slider("Instructor Score (0–100)", 0, 100, 85)
        scenario_id = st.text_input("Scenario ID (optional)", value="")
        pattern_id = st.text_input("Pattern ID (optional)", value="")
        notes = st.text_area("Notes (optional)", value="", height=80)

        # Gate status: you said sessions already log with gate status.
        # We keep this simple: instructor supplies current gate status for now.
        # (Gate-enforced sessions is a separate module; we won't break your app here.)
        gate_pre_status = st.selectbox("Gate (PRE) status", ["GREEN", "YELLOW", "RED", "UNKNOWN"], index=0)
        gate_post_status = st.selectbox("Gate (POST) status", ["GREEN", "YELLOW", "RED", "UNKNOWN"], index=0)
        counted_for_agi = st.checkbox("Counts toward AGI", value=(gate_pre_status == "GREEN" and gate_post_status == "GREEN"))

        if st.button("Append Session", type="primary"):
            new_session = {
                "trainee_name": trainee_name,
                "difficulty": difficulty,
                "score": float(score),
                "scenario_id": scenario_id,
                "pattern_id": pattern_id,
                "notes": notes,
                "gate_pre_status": gate_pre_status,
                "gate_post_status": gate_post_status,
                "counted_for_agi": counted_for_agi,
            }
            written = append_session(new_session)
            st.success(f"Session logged: {written.get('session_id')}")
            st.rerun()

    with right:
        st.subheader("Curve Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI", f"{float(curve.get('AGI', 0.0)):.1f}")
        c2.metric("Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
        c3.metric("Difficulty Avg", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
        c4.metric("Volatility", f"{float(curve.get('volatility_index', 0.0)):.2f}")

        st.subheader("Obasi Coach (Stable)")
        coach_msg = build_obasi_training_coach_speech(
            trainee_name="Ghost",
            difficulty=str(curve.get("current_difficulty", "UNKNOWN")),
            gate_status="GREEN",
            curve=curve,
            sessions=sessions,
            training_feedback=feedback,
        )
        st.code(coach_msg)

        with st.expander("🧭 Next Training Recommendation", expanded=True):
            st.json(feedback if feedback else {"status": "NONE", "message": "No feedback written yet."})

    st.divider()
    st.subheader("Sessions")
    if sessions:
        st.dataframe(sessions, use_container_width=True, hide_index=True)
    else:
        st.info("No sessions logged yet.")


if __name__ == "__main__":
    main()

