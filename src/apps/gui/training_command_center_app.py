# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from training_session_store import load_sessions  # noqa: E402
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
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center — Certification + Curve")

    sessions: List[Dict[str, Any]] = load_sessions()
    curve = compute_training_curve()
    certification = compute_certification()
    feedback = _load_latest_training_feedback()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI", f"{float(curve.get('AGI', 0.0)):.1f}")
    c2.metric("Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
    c3.metric("Difficulty Avg", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
    c4.metric("Volatility", f"{float(curve.get('volatility_index', 0.0)):.2f}")

    st.subheader("🎖️ Operator Certification Status")
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
        st.success("Top level achieved. Fully certified through ADVERSARIAL.")

    with st.expander("Certification details"):
        st.json(certification)

    with st.expander("🧭 Next Training Recommendation", expanded=True):
        st.json(feedback if feedback else {"status": "NONE", "message": "No feedback written yet."})

    st.divider()
    st.subheader("Sessions (raw)")
    if sessions:
        st.dataframe(sessions, use_container_width=True, hide_index=True)
    else:
        st.info("No sessions logged yet.")


if __name__ == "__main__":
    main()

