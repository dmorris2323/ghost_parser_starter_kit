# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from training_session_store import load_sessions, append_session  # noqa: E402
from training_validation_gate import run_training_session_gates  # noqa: E402
from training_curve_engine import compute_training_curve  # noqa: E402
from operator_certification_engine import compute_certification  # noqa: E402


def _load_latest_training_feedback() -> Dict[str, Any]:
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
    st.title("GLL Training Dashboard — Gate + Certification")

    sessions: List[Dict[str, Any]] = load_sessions()
    curve = compute_training_curve()
    certification = compute_certification()
    feedback = _load_latest_training_feedback()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Log a Training Session (Gate-Enforced)")

        trainee_name = st.text_input("Trainee name", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"], index=1)
        score = st.slider("Instructor Score (0–100)", 0, 100, 85)
        scenario_id = st.text_input("Scenario ID (optional)", value="")
        pattern_id = st.text_input("Pattern ID (optional)", value="")
        notes = st.text_area("Notes (optional)", value="", height=80)

        st.caption("Policy: session counts toward AGI only if SIS+SPS PRE and POST gates are GREEN/PASS.")

        if st.button("Append Session (Run Gates)", type="primary"):
            with st.spinner("Running SIS+SPS PRE/POST gates…"):
                pre_gate, post_gate, decision = run_training_session_gates()

            counted_for_agi = bool(decision.get("counted_for_agi", False))
            pre_status = str(decision.get("pre_status", "UNKNOWN"))
            post_status = str(decision.get("post_status", "UNKNOWN"))

            new_session = {
                "trainee_name": trainee_name,
                "difficulty": difficulty,
                "score": float(score),
                "scenario_id": scenario_id,
                "pattern_id": pattern_id,
                "notes": notes,
                "gate_pre_status": pre_status,
                "gate_post_status": post_status,
                "counted_for_agi": counted_for_agi,
            }
            written = append_session(new_session)

            st.success(
                f"Session logged: {written.get('session_id')} | "
                f"PRE={pre_status} POST={post_status} | "
                f"Counted={counted_for_agi}"
            )
            with st.expander("Gate decision details", expanded=not counted_for_agi):
                st.json({"decision": decision, "pre_gate": pre_gate, "post_gate": post_gate})

            st.rerun()

    with right:
        st.subheader("Curve Metrics (COUNTED sessions only)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI", f"{float(curve.get('AGI', 0.0)):.1f}")
        c2.metric("Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
        c3.metric("Difficulty Avg", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
        c4.metric("Volatility", f"{float(curve.get('volatility_index', 0.0)):.2f}")

        st.subheader("🎖️ Operator Certification")
        st.write(f"**Certified level:** `{certification.get('certified_level')}`")
        nxt = certification.get("next_target")
        prog = certification.get("next_target_progress", {}) or {}
        if nxt:
            st.write(
                f"**Next target:** `{nxt}` — "
                f"streak {prog.get('current_streak', 0)}/{prog.get('required', 0)} "
                f"(remaining {prog.get('remaining', 0)})"
            )
        else:
            st.success("Top level achieved. You’re fully certified through ADVERSARIAL.")

        with st.expander("Certification details"):
            st.json(certification)

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

