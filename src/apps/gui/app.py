"""
app.py (Spectral Command Center – Stable)

Purpose:
- Keep Spectral Dashboard functional even when some subsystems are missing.
- Provide Training Curve tiles + quick rep runner so difficulty can be switched live
  and AGI/slope/volatility update immediately.

Run (from repo root):
  cd /Users/dextermorris/ghost/parser_starter_kit
  streamlit run src/apps/gui/app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

_THIS = Path(__file__).resolve()
_SRC = _THIS.parents[2]  # .../src
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from difficulty_scaling_engine import VALID_DIFFICULTIES, profiles_summary  # noqa: E402
from training_curve_engine import compute_training_curve  # noqa: E402
from training_session_store import append_training_session  # noqa: E402
from scenario_engine import generate_scenario  # noqa: E402
from instructor_rubric_autograder import auto_grade_scenario  # noqa: E402

try:
    from obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402
except Exception:
    def build_obasi_training_coach_speech(*args: Any, **kwargs: Any) -> str:
        return "Obasi coach unavailable."


def main() -> None:
    st.set_page_config(page_title="GLL Spectral Command Center", layout="wide")
    st.title("GLL Spectral Command Center")
    st.caption("Nuclear / ISR / Base Defense + Training Mode (Synthetic-safe)")

    tabs = st.tabs(["Command Center", "Training Tile", "Outputs", "Profiles"])

    with tabs[0]:
        _render_command_center()

    with tabs[1]:
        _render_training_tile()

    with tabs[2]:
        _render_outputs_panel()

    with tabs[3]:
        st.subheader("Difficulty Profiles (Source of Truth)")
        st.json(profiles_summary())


def _render_command_center() -> None:
    st.subheader("Core Readiness Snapshot")

    # If you have existing JSON bundles, we show them when present — but never hard-fail.
    bundle = _read_json_if_exists(_repo_root() / "outputs" / "spectral_dashboard.json")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Fusion Trust", _safe_metric(bundle, ["fusion_trust", "fusion_trust_score"], default="—"))
    with col2:
        st.metric("OSL", _safe_metric(bundle, ["osl", "operator_safety_layer", "osl_status"], default="—"))
    with col3:
        st.metric("Crisis Mode", _safe_metric(bundle, ["crisis_mode", "crisis_mode_flag"], default="—"))

    st.markdown("---")
    st.subheader("Training Curve (Live)")
    curve = compute_training_curve()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI (0–100)", f"{float(curve.get('AGI', 0.0)):.1f}")
    c2.metric("Improvement Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
    c3.metric("Difficulty-Weighted Avg", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
    c4.metric("Volatility Index", f"{float(curve.get('volatility_index', 0.0)):.2f}")

    coach = build_obasi_training_coach_speech(
        trainee_name="Ghost",
        difficulty=str(curve.get("last_session", {}).get("difficulty", "INTERMEDIATE")),
        agi=float(curve.get("AGI", 0.0)),
        improvement_slope=float(curve.get("improvement_slope", 0.0)),
        volatility_index=float(curve.get("volatility_index", 0.0)),
        last_score=float(curve.get("last_session", {}).get("score", 0.0) or 0.0),
        difficulty_weighted_average=float(curve.get("difficulty_weighted_average", 0.0)),
        notes="Command Center view. Use Training Tile to run reps.",
    )
    st.code(coach, language="text")


def _render_training_tile() -> None:
    st.subheader("Quick Training Rep (updates AGI live)")
    st.caption("This is a lightweight runner. Full training workflow is in training_dashboard_app.py.")

    left, right = st.columns([1, 2])

    with left:
        difficulty = st.selectbox("Difficulty", list(VALID_DIFFICULTIES), index=1)
        seed = st.number_input("Seed", min_value=0, max_value=999999, value=11, step=1)

        pattern_id = st.selectbox(
            "Pattern Injection (optional)",
            ["NONE", "CROSS_DOMAIN_CONFUSION", "SATURATION_PRESSURE", "SENSOR_SPOOF_LIKE", "COMMS_DEGRADATION"],
            index=0,
        )
        pat = None if pattern_id == "NONE" else pattern_id

        st.markdown("**Rubric inputs (0–100)**")
        summary_quality = st.slider("Situation Awareness", 0, 100, 70)
        evidence_quality = st.slider("Evidence Handling", 0, 100, 70)
        decision_quality = st.slider("Decision Quality", 0, 100, 70)
        communication = st.slider("Communication", 0, 100, 70)
        discipline = st.slider("Discipline Under Pressure", 0, 100, 70)

        if st.button("Run Quick Rep", use_container_width=True):
            scenario = generate_scenario(
                difficulty=difficulty,
                seed=int(seed),
                pattern_id=pat,
                pattern_seed=int(seed) if pat else None,
                write=True,
            )

            trainee_inputs = {
                "summary_quality": summary_quality,
                "evidence_quality": evidence_quality,
                "decision_quality": decision_quality,
                "communication": communication,
                "discipline": discipline,
            }

            grade = auto_grade_scenario(
                difficulty=difficulty,
                trainee_inputs=trainee_inputs,
                scenario=scenario,
                rubric_weights=None,
            )

            append_training_session(
                difficulty=difficulty,
                score=float(grade["final_score"]),
                scenario_id=grade.get("scenario_id"),
                rubric=grade,
                notes="Quick rep from Command Center tile",
            )

            # Recompute curve immediately
            curve = compute_training_curve()
            st.success("Saved. Curve updated.")
            st.json({"grade": grade, "curve": curve, "scenario_paths": scenario.get("paths", {})})

    with right:
        st.subheader("Live Curve")
        curve = compute_training_curve()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI (0–100)", f"{float(curve.get('AGI', 0.0)):.1f}")
        c2.metric("Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
        c3.metric("DWA", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
        c4.metric("Volatility", f"{float(curve.get('volatility_index', 0.0)):.2f}")

        st.caption(f"Sessions: {curve.get('total_sessions', 0)}")


def _render_outputs_panel() -> None:
    st.subheader("Common Output Files (read-only)")
    candidates = [
        _repo_root() / "outputs" / "spectral_dashboard.json",
        _repo_root() / "src" / "docs" / "training" / "training_curve_latest.json",
        _repo_root() / "src" / "docs" / "training" / "training_sessions.json",
        _repo_root() / "src" / "docs" / "scenarios" / "scenario_latest.json",
    ]
    for p in candidates:
        st.markdown(f"**{p}**")
        if p.exists():
            if p.suffix.lower() == ".json":
                st.json(_read_json_if_exists(p) or {"error": "Could not read JSON"})
            else:
                st.code(p.read_text()[:4000], language="text")
        else:
            st.info("Not found yet.")


def _repo_root() -> Path:
    # .../src/apps/gui/app.py -> parents[3] = repo root
    return Path(__file__).resolve().parents[3]


def _read_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text())
    except Exception:
        return None


def _safe_metric(bundle: Optional[Dict[str, Any]], keys: list[str], default: str = "—") -> str:
    if not bundle:
        return default
    for k in keys:
        if k in bundle:
            return str(bundle.get(k))
    # Try nested common blocks
    for k in keys:
        for block_key in ("summary", "tiles", "readiness", "status"):
            blk = bundle.get(block_key)
            if isinstance(blk, dict) and k in blk:
                return str(blk.get(k))
    return default


if __name__ == "__main__":
    main()

