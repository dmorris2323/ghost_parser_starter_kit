"""
src/apps/gui/training_dashboard_app.py

Robust Training Dashboard:
- Tolerates multiple versions of obasi_training_coach import/signatures.
- Never crashes if coach returns dict/None/other types.
- Uses operator= instead of trainee_name= for broad compatibility.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Any, Dict, Callable

import streamlit as st

_THIS = Path(__file__).resolve()
_SRC = _THIS.parents[2]  # .../src
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Local GLL imports (must exist in src/)
from difficulty_scaling_engine import VALID_DIFFICULTIES, profiles_summary, normalize_difficulty  # noqa: E402
from scenario_engine import generate_scenario  # noqa: E402
from instructor_rubric_autograder import auto_grade_scenario  # noqa: E402
from training_session_store import append_training_session, load_sessions  # noqa: E402
from training_curve_engine import compute_training_curve  # noqa: E402


def _load_obasi() -> Callable[..., Any]:
    """
    Try to import whatever obasi_training_coach Streamlit resolves.
    Return a callable that never raises at import time.
    """
    try:
        from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore
        return build_obasi_training_coach_speech
    except Exception:
        def _fallback(*args: Any, **kwargs: Any) -> str:
            return "Obasi coach unavailable (import failed)."
        return _fallback


build_obasi_training_coach_speech = _load_obasi()


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")
    st.title("GLL Training Dashboard")
    st.caption("Instructor Mode + Live Difficulty Scaling (Synthetic-only training data)")

    with st.expander("Difficulty Profiles (source of truth)", expanded=False):
        st.json(profiles_summary())

    left, right = st.columns([1, 2])

    with left:
        st.subheader("Run a Training Rep")

        difficulty = st.selectbox("Difficulty", list(VALID_DIFFICULTIES), index=1)
        seed = st.number_input("Seed", min_value=0, max_value=999999, value=7, step=1)

        pattern_id = st.selectbox(
            "Pattern Injection (optional)",
            ["NONE", "CROSS_DOMAIN_CONFUSION", "SATURATION_PRESSURE", "SENSOR_SPOOF_LIKE", "COMMS_DEGRADATION"],
            index=0,
        )
        pattern_seed = st.number_input("Pattern Seed", min_value=0, max_value=999999, value=seed, step=1)

        st.markdown("---")
        st.subheader("Instructor Rubric Inputs (0–100)")
        summary_quality = st.slider("Situation Awareness", 0, 100, 72)
        evidence_quality = st.slider("Evidence Handling", 0, 100, 70)
        decision_quality = st.slider("Decision Quality", 0, 100, 68)
        communication = st.slider("Communication", 0, 100, 75)
        discipline = st.slider("Discipline Under Pressure", 0, 100, 66)

        notes = st.text_area("Instructor Notes", value="")

        if st.button("Run Rep → Grade → Save Session", use_container_width=True):
            pat = None if pattern_id == "NONE" else pattern_id
            scenario = generate_scenario(
                difficulty=difficulty,
                seed=int(seed),
                pattern_id=pat,
                pattern_seed=int(pattern_seed) if pat else None,
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

            save = append_training_session(
                difficulty=difficulty,
                score=float(grade["final_score"]),
                scenario_id=grade.get("scenario_id"),
                rubric=grade,
                notes=notes,
            )

            curve = compute_training_curve()

            st.success("Session saved + curve recomputed.")
            st.json(
                {
                    "saved": {"path": save["json_path"], "total_sessions": save["total_sessions"]},
                    "grade": grade,
                    "curve": curve,
                    "scenario_paths": scenario.get("paths", {}),
                }
            )

    with right:
        st.subheader("Live Training Curve")

        curve = compute_training_curve()
        _render_curve_tiles(curve)

        st.markdown("---")
        st.subheader("Session History")
        sessions_payload = load_sessions()
        sessions = sessions_payload.get("sessions", [])
        if not sessions:
            st.info("No sessions yet. Run a rep to start your curve.")
        else:
            rows = []
            for s in sessions[-50:]:
                rows.append(
                    {
                        "ts_utc": s.get("ts_utc"),
                        "difficulty": s.get("difficulty"),
                        "weight": s.get("difficulty_weight"),
                        "score": s.get("score"),
                        "scenario_id": s.get("scenario_id"),
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

            scores = [float(s.get("score", 0.0)) for s in sessions]
            st.line_chart(scores, height=220)

        st.markdown("---")
        st.subheader("Obasi Coach Panel")
        coach = _build_obasi_message(curve=curve, sessions=sessions)
        st.code(coach, language="text")


def _render_curve_tiles(curve: Dict[str, Any]) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AGI (0–100)", f"{float(curve.get('AGI', 0.0)):.1f}")
    col2.metric("Improvement Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
    col3.metric("Difficulty-Weighted Avg", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
    col4.metric("Volatility Index", f"{float(curve.get('volatility_index', 0.0)):.2f}")

    last = curve.get("last_session", {}) or {}
    st.caption(
        f"Last session: {last.get('ts_utc','—')} | {last.get('difficulty','—')} "
        f"(w={last.get('difficulty_weight','—')}) | score={last.get('score','—')}"
    )


def _as_text(x: Any) -> str:
    """Force any return type into a readable string."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, (dict, list)):
        try:
            return json.dumps(x, indent=2)
        except Exception:
            return str(x)
    return str(x)


def _build_obasi_message(curve: Dict[str, Any], sessions: list[dict]) -> str:
    last_score = 0.0
    last_diff = "INTERMEDIATE"
    if sessions:
        last_score = float(sessions[-1].get("score", 0.0))
        last_diff = str(sessions[-1].get("difficulty", "INTERMEDIATE"))

    payload = dict(
        # Use operator= for max compatibility with older coach modules
        operator="Ghost",
        difficulty=normalize_difficulty(last_diff),
        agi=float(curve.get("AGI", 0.0)),
        improvement_slope=float(curve.get("improvement_slope", 0.0)),
        volatility_index=float(curve.get("volatility_index", 0.0)),
        last_score=last_score,
        difficulty_weighted_average=float(curve.get("difficulty_weighted_average", 0.0)),
        notes="One rep at a time. Build consistency. Then raise difficulty.",
    )

    # Try kwargs call
    try:
        out = build_obasi_training_coach_speech(**payload)
        out_txt = _as_text(out).strip()
        if out_txt:
            return out_txt
    except TypeError:
        pass
    except Exception:
        pass

    # Fallback: call with no args (older coach versions)
    try:
        base = build_obasi_training_coach_speech()
    except Exception:
        base = "Obasi coach unavailable."

    base_txt = _as_text(base).strip() or "Obasi coach unavailable."

    # Append metrics ourselves (always safe)
    metrics = (
        "\n\n[Metrics]\n"
        f"Operator: {payload['operator']}\n"
        f"Difficulty: {payload['difficulty']}\n"
        f"AGI: {payload['agi']:.1f}\n"
        f"Slope: {payload['improvement_slope']:.2f}\n"
        f"Volatility: {payload['volatility_index']:.2f}\n"
        f"Last score: {payload['last_score']:.1f}\n"
        f"DWA: {payload['difficulty_weighted_average']:.1f}\n"
    )
    return base_txt + metrics


if __name__ == "__main__":
    main()

