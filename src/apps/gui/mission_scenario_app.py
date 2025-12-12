# apps/gui/mission_scenario_app.py
# War Room Mission Scenario GUI (SAFE)
import sys
from pathlib import Path

# Ensure src is on path when running streamlit from repo root
SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st  # noqa: E402

from difficulty_scaling_engine import compute_difficulty_profile  # noqa: E402
from scenario_engine import generate_scenario, grade_scenario_result  # noqa: E402


def main():
    st.set_page_config(page_title="GLL War Room – Mission Scenarios", layout="wide")
    st.title("🛰️ GLL War Room – Mission Scenario Engine")
    st.caption("SAFE synthetic-only training scenarios. No real-world signatures.")

    prof = compute_difficulty_profile()
    rec = prof["recommendation"]["recommended_level"]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Difficulty")
        mode = st.radio("Difficulty mode", ["Auto (recommended)", "Manual override"], horizontal=True)
        difficulty = rec
        if mode == "Manual override":
            difficulty = st.selectbox("Choose difficulty", ["CADET", "ANALYST", "SENIOR", "EXPERT"], index=1)

        st.info(f"Recommended: **{rec}**")

    with col2:
        st.subheader("Generate Scenario")
        seed = st.number_input("Seed (optional)", min_value=0, value=0, step=1)
        use_seed = st.checkbox("Use seed", value=False)

        if st.button("Generate mission scenario", type="primary"):
            result = generate_scenario(difficulty=difficulty, seed=int(seed) if use_seed else None)
            st.session_state["scenario"] = result

    st.divider()

    scenario = st.session_state.get("scenario")
    if scenario:
        st.subheader("Scenario Output")
        st.write(scenario)

        st.markdown("### Trainee Scoring (log a run)")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            score = st.slider("Score (0–100)", 0, 100, 75)
        with c2:
            notes = st.text_input("Notes (short)", value="Ran scenario, identified patterns, wrote summary.")
        with c3:
            trainee = st.text_input("Trainee", value="Ghost")

        if st.button("Log training session", type="secondary"):
            log = grade_scenario_result(
                scenario_id=scenario["scenario_id"],
                difficulty_used=scenario["difficulty_used"],
                score=float(score),
                notes=notes,
                trainee=trainee,
            )
            st.success(f"Logged. Session ID: {log['session_id']}")
            st.code(log["json_path"])


if __name__ == "__main__":
    main()

