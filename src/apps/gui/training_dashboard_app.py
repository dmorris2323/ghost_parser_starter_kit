from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure repo root/src is importable regardless of streamlit cwd
ROOT = Path(__file__).resolve().parents[3]  # .../src/apps/gui -> repo root
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from training_session_store import load_sessions, append_session
from operator_certification_engine import compute_certification, highest_certified_track
from training_policy import can_log_difficulty, get_expectations, normalize_difficulty
from training_curve_engine import compute_training_curve
from training_feedback_engine import recommend_next_training, write_latest_feedback


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
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")

    st.title("🧠 GLL Training Dashboard")
    st.caption("Gate-enforced sessions • Difficulty policy • Certification tracks • AGI curve (GREEN-only)")

    sessions = load_sessions()
    cert = compute_certification(sessions)
    certified_track = highest_certified_track(cert)
    curve = compute_training_curve()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("🎯 Certification Status")
        st.json(cert)

        st.subheader("📈 Training Curve (GREEN-only)")
        cols = st.columns(4)
        cols[0].metric("AGI (0–100)", curve.get("AGI", 0.0))
        cols[1].metric("Improvement Slope", curve.get("improvement_slope", 0.0))
        cols[2].metric("Difficulty-Weighted Avg", curve.get("difficulty_weighted_average", 0.0))
        cols[3].metric("Volatility Index", curve.get("volatility_index", 0.0))

    with right:
        st.subheader("🧪 Log Training Session")
        st.caption("Only GREEN sessions count toward AGI. Difficulty must respect certification (+1 rule).")

        requested = st.selectbox(
            "Difficulty",
            ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"],
            index=0,
        )
        requested = normalize_difficulty(requested)

        allowed = can_log_difficulty(requested_difficulty=requested, certified_track=certified_track)
        exp = get_expectations(requested)

        st.info(
            f"**Instructor expectations for {requested}:** "
            f"min_score={exp['min_score']} • "
            f"weights: accuracy={exp['grader_weight_accuracy']} process={exp['grader_weight_process']}\n\n"
            f"{exp['notes']}"
        )

        if not allowed:
            st.error(
                f"Blocked: You are certified at **{certified_track}**. "
                f"You can log only current or next track."
            )

        gate_status = st.selectbox("Gate status (SIS+SPS)", ["GREEN", "YELLOW", "RED", "UNKNOWN"], index=0)
        score = st.slider("Session Score (0–100)", 0, 100, 75)
        notes = st.text_area("Notes", value="", height=120)

        if st.button("✅ Append Session", disabled=not allowed):
            sess = append_session(
                difficulty=requested,
                gate_status=gate_status,
                score=float(score),
                notes=notes,
                tags=["TRAINING"],
            )
            st.success(f"Session appended: {sess['session_id']}")

            # Recompute curve and write recommendation (recorded, not enforced)
            sessions2 = load_sessions()
            curve2 = compute_training_curve()
            fb = recommend_next_training(
                training_curve=curve2,
                current_difficulty=requested,
                validation_verdict="PASS",
                sessions=sessions2,
            )
            write_latest_feedback(fb)
            st.toast("Training recommendation updated (read-only).", icon="🧭")

    st.divider()

    st.subheader("🧾 Sessions (normalized schema)")
    if sessions:
        table = []
        for s in sessions[-50:]:
            table.append({
                "created_at": s.get("created_at"),
                "session_id": s.get("session_id"),
                "difficulty": s.get("difficulty"),
                "gate_status": s.get("gate_status"),
                "score": s.get("score"),
                "notes": s.get("notes", "")[:80],
            })
        st.dataframe(table, use_container_width=True)
    else:
        st.warning("No sessions yet.")

    st.subheader("🧭 Next Training Recommendation (read-only)")
    fb_latest = _load_latest_training_feedback()
    if fb_latest:
        st.json(fb_latest)
    else:
        st.info("No recommendation written yet. Append a session to generate one.")


if __name__ == "__main__":
    main()

