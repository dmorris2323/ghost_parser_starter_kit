from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# Ensure src/ is importable when running streamlit from repo root
ROOT = Path(__file__).resolve().parents[3]  # .../parser_starter_kit
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from training_session_store import load_sessions, append_session
from training_curve_engine import compute_training_curve
from training_feedback_engine import recommend_next_training, write_latest_feedback


st.set_page_config(page_title="GLL Training Dashboard", layout="wide")


def _safe_str(x, default=""):
    try:
        return str(x)
    except Exception:
        return default


def _call_obasi(payload: dict) -> str:
    """
    Defensive adapter: obasi_training_coach may have different signatures.
    Always returns a STRING for display.
    """
    try:
        import inspect
        import obasi_training_coach as coach

        fn = getattr(coach, "build_obasi_training_coach_speech", None)
        if fn is None:
            return "Obasi coach module not available."

        sig = inspect.signature(fn)
        # If it takes kwargs, pass payload. If it takes none, call bare.
        if len(sig.parameters) == 0:
            res = fn()
        else:
            res = fn(**payload)

        if isinstance(res, str):
            return res
        if isinstance(res, dict):
            # render dict as readable text
            return "\n".join([f"- {k}: {res[k]}" for k in res.keys()])
        return _safe_str(res, "Obasi coach generated an unsupported response.")
    except Exception as e:
        return f"Obasi coach unavailable: {e.__class__.__name__}: {e}"


def main():
    st.title("🦉 GLL Training Dashboard")

    sessions = load_sessions()

    colA, colB = st.columns([1, 1])
    with colA:
        st.subheader("Log a Training Session (Synthetic / Safe)")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        verdict = st.selectbox("Validation Verdict", ["PASS", "WARN", "FAIL"], index=0)
        score = st.slider("Session Score (0–100)", 0, 100, 75)
        pattern = st.text_input("Pattern ID (optional)", value="").strip() or None
        notes = st.text_area("Notes", value="", height=90)

        if st.button("✅ Append Session"):
            # This session append is "raw". Gate enforcement can be added later at the logging point.
            s = append_session(
                {
                    "difficulty": difficulty,
                    "verdict": verdict,
                    "score": float(score),
                    "pattern_id": pattern,
                    "notes": notes,
                    # default until gate wiring is added at logging time
                    "counts_toward_agi": True,
                }
            )
            st.success(f"Appended session: {s['session_id']}")

    with colB:
        st.subheader("Live Curve + Recommendation")
        curve = compute_training_curve()
        st.metric("AGI (0–100)", curve["AGI"])
        st.metric("Improvement slope", curve["improvement_slope"])
        st.metric("Volatility index", curve["volatility_index"])
        st.metric("Counted sessions", curve["counted_sessions"])

        fb = recommend_next_training(
            training_curve=curve,
            current_difficulty="INTERMEDIATE",
            validation_verdict="PASS",
        )
        write_latest_feedback(fb)

        with st.expander("🧭 Next Training Recommendation", expanded=True):
            st.json(fb)

        with st.expander("🦉 Obasi Coach", expanded=True):
            msg = _call_obasi(
                {
                    "trainee_name": "Ghost",
                    "agi": curve["AGI"],
                    "slope": curve["improvement_slope"],
                    "volatility": curve["volatility_index"],
                    "counted_sessions": curve["counted_sessions"],
                }
            )
            st.write(msg)

    st.divider()
    st.subheader("Sessions (Normalized)")

    # Render stable table (no KeyError)
    rows = []
    for s in sessions:
        rows.append(
            {
                "session_id": s.get("session_id", ""),
                "timestamp": s.get("timestamp", ""),
                "difficulty": s.get("difficulty", ""),
                "score": s.get("score", 0.0),
                "verdict": s.get("verdict", ""),
                "counts_toward_agi": s.get("counts_toward_agi", False),
                "pattern_id": s.get("pattern_id", None),
            }
        )
    st.dataframe(rows, use_container_width=True)


if __name__ == "__main__":
    main()

