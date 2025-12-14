from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from training_session_store import load_sessions
from training_curve_engine import compute_training_curve


def _load_latest_training_feedback() -> dict:
    p = Path("src") / "docs" / "training" / "training_feedback_latest.json"
    if not p.exists():
        return {}
    try:
        import json
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("🛰️ GLL Training Command Center")
    st.caption("Command view: curve + stability + latest recommendation (read-only)")

    sessions = load_sessions()
    curve = compute_training_curve()
    fb = _load_latest_training_feedback()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI", curve.get("AGI", 0.0))
    c2.metric("Slope", curve.get("improvement_slope", 0.0))
    c3.metric("Weighted Avg", curve.get("difficulty_weighted_average", 0.0))
    c4.metric("Volatility", curve.get("volatility_index", 0.0))

    st.divider()

    left, right = st.columns([1, 1])
    with left:
        st.subheader("🧭 Next Training Recommendation")
        if fb:
            st.json(fb)
        else:
            st.info("No recommendation yet. Use Training Dashboard to append a session.")

    with right:
        st.subheader("🧾 Recent Sessions (last 20)")
        if sessions:
            rows = []
            for s in sessions[-20:]:
                rows.append({
                    "created_at": s.get("created_at"),
                    "difficulty": s.get("difficulty"),
                    "gate_status": s.get("gate_status"),
                    "score": s.get("score"),
                    "session_id": s.get("session_id"),
                })
            st.dataframe(rows, use_container_width=True)
        else:
            st.warning("No sessions found.")


if __name__ == "__main__":
    main()

