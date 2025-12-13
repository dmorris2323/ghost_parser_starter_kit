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

st.set_page_config(page_title="GLL Training Command Center", layout="wide")


def main():
    st.title("🎛️ GLL Training Command Center")

    curve = compute_training_curve()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI", curve["AGI"])
    c2.metric("Slope", curve["improvement_slope"])
    c3.metric("Difficulty-W Avg", curve["difficulty_weighted_average"])
    c4.metric("Volatility", curve["volatility_index"])

    st.divider()
    st.subheader("Most Recent Sessions")

    sessions = load_sessions()
    sessions = list(reversed(sessions))[:12]

    st.dataframe(
        [
            {
                "session_id": s.get("session_id", ""),
                "timestamp": s.get("timestamp", ""),
                "difficulty": s.get("difficulty", ""),
                "score": s.get("score", 0.0),
                "verdict": s.get("verdict", ""),
                "counts_toward_agi": s.get("counts_toward_agi", False),
                "pattern_id": s.get("pattern_id", None),
            }
            for s in sessions
        ],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()

