# apps/gui/mission_scenario_app.py
# War Room Mission Scenario GUI (SAFE) — Module 6 adds Instructor Pack Export.
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st  # noqa: E402

from difficulty_scaling_engine import compute_difficulty_profile  # noqa: E402
from scenario_engine import generate_scenario, grade_scenario_result, rubric_autograde_and_log  # noqa: E402
from aar_generator import build_aar, write_aar_files  # noqa: E402
from instructor_pack_export import export_instructor_packet  # noqa: E402


def _load_json(path: str) -> dict:
    import json
    with open(path, "r") as f:
        return json.load(f)


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
            st.session_state.pop("last_grade", None)
            st.session_state.pop("last_aar", None)
            st.session_state.pop("last_pack", None)

    st.divider()

    scenario = st.session_state.get("scenario")
    if not scenario:
        st.caption("Generate a scenario to begin.")
        return

    st.subheader("Scenario Output")
    st.write(scenario)

    st.divider()
    st.subheader("Scoring")

    grading_mode = st.radio(
        "Scoring mode",
        ["Rubric Auto-Grade (recommended)", "Manual score only"],
        horizontal=True,
        index=0,
    )

    if grading_mode == "Manual score only":
        st.markdown("### Manual Scoring (log a run)")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            score = st.slider("Score (0–100)", 0, 100, 75)
        with c2:
            notes = st.text_input("Notes (short)", value="Ran scenario, identified patterns, wrote summary.")
        with c3:
            trainee = st.text_input("Trainee", value="Ghost")

        if st.button("Log training session (manual)", type="secondary"):
            log = grade_scenario_result(
                scenario_id=scenario["scenario_id"],
                difficulty_used=scenario["difficulty_used"],
                score=float(score),
                notes=notes,
                trainee=trainee,
            )
            st.success(f"Logged. Session ID: {log['session_id']}")
            st.code(log["json_path"])
        return

    # Rubric auto-grade inputs
    st.markdown("### Rubric Auto-Grader (Instructor Mode)")

    left, right = st.columns([1, 1])

    with left:
        trainee = st.text_input("Trainee", value="Ghost")
        called_patterns = st.multiselect(
            "Which patterns do you call?",
            ["drift", "latency", "outage", "storm", "cross"],
            default=["drift"],
        )
        osl = st.selectbox("OSL posture", ["GREEN", "AMBER", "RED"], index=1)
        analyst_notes = st.text_input(
            "Analyst notes (short)",
            value="Validated baseline; cross-checked sensor consistency; cautious confidence."
        )

    with right:
        commander_summary = st.text_area(
            "Commander Summary (target ~5 sentences)",
            height=180,
            value="Observed synthetic anomalies consistent with drift/latency patterns. "
                  "Operational impact is moderate due to reduced confidence in sensor stability. "
                  "Assessment remains likely synthetic sensor behavior rather than a single-point fault. "
                  "Recommend cross-checking sensor baselines and monitoring for escalation or outages. "
                  "Maintain AMBER posture until consistency returns or patterns converge.",
        )

    if st.button("Auto-grade + log session", type="primary"):
        result = rubric_autograde_and_log(
            scenario_json_path=scenario["scenario_json_path"],
            called_patterns=list(called_patterns),
            osl=osl,
            commander_summary=commander_summary,
            analyst_notes=analyst_notes,
            trainee=trainee,
        )
        st.session_state["last_grade"] = result
        st.session_state.pop("last_pack", None)

    last_grade = st.session_state.get("last_grade")
    if last_grade:
        st.success(f"Rubric score: {last_grade['score']}/100")
        st.write("Subscores:", last_grade["subscores"])
        st.write("Instructor feedback:", last_grade["feedback"])
        st.code(last_grade["grade_report"]["json_path"])
        st.code(last_grade["training_log"]["json_path"])

        st.divider()
        st.subheader("Module 5 — AAR Generator")

        if st.button("Generate AAR (one-page)", type="secondary"):
            scenario_packet = _load_json(scenario["scenario_json_path"])
            grade_packet = _load_json(last_grade["grade_report"]["json_path"])

            trainee_payload = {
                "trainee": trainee,
                "called_patterns": list(called_patterns),
                "osl": osl,
                "commander_summary": commander_summary,
                "analyst_notes": analyst_notes,
                "scenario_json_path": scenario["scenario_json_path"],
            }

            aar = build_aar(scenario_packet, grade_packet, trainee_payload)
            paths = write_aar_files(aar)
            st.session_state["last_aar"] = paths
            st.session_state.pop("last_pack", None)

        last_aar = st.session_state.get("last_aar")
        if last_aar:
            st.success("AAR written.")
            st.code(last_aar["json_path"])
            st.code(last_aar["txt_path"])

        st.divider()
        st.subheader("Module 6 — Instructor Pack Export")

        include_optional = st.checkbox("Include optional artifacts (best-effort)", value=True)

        if st.button("Export Instructor Pack (manifest)", type="secondary"):
            grade_json_path = last_grade["grade_report"]["json_path"]
            aar_json_path = (last_aar or {}).get("json_path")

            export = export_instructor_packet(
                scenario_json_path=scenario["scenario_json_path"],
                grade_json_path=grade_json_path,
                aar_json_path=aar_json_path,
                trainee=trainee,
                include_optional_artifacts=include_optional,
            )
            st.session_state["last_pack"] = export

        last_pack = st.session_state.get("last_pack")
        if last_pack:
            st.success("Instructor packet exported.")
            st.code(last_pack["packet_path"])
            st.code(last_pack["latest_path"])


if __name__ == "__main__":
    main()

