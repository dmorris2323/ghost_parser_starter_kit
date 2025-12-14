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
from obasi_training_coach import build_obasi_training_coach_speech  # noqa: E402
from crisis_mode_flag import read_crisis_mode, set_crisis_mode  # noqa: E402


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        import json

        if not path.exists():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _safe_curve() -> Dict[str, Any]:
    try:
        from training_curve_engine import compute_training_curve  # type: ignore

        curve = compute_training_curve()
        return curve if isinstance(curve, dict) else {}
    except Exception:
        return {}


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("GLL Training Command Center")

    sessions: List[Dict[str, Any]] = load_sessions()
    curve = _safe_curve()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("System Status")

        cm = read_crisis_mode()
        st.json(cm)

        enable = st.checkbox("CRISIS MODE (ON)", value=(cm.get("crisis_mode") == "ON"))
        reason = st.text_input("Reason", value=str(cm.get("reason", "operator_action")))
        if st.button("Apply Crisis Mode"):
            written = set_crisis_mode(enabled=enable, reason=reason, operator="Ghost")
            st.success(f"Updated: {written.get('crisis_mode')}")
            st.rerun()

        st.subheader("Curve Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AGI", f"{float(curve.get('AGI', 0.0)):.1f}")
        c2.metric("Slope", f"{float(curve.get('improvement_slope', 0.0)):.2f}")
        c3.metric("Difficulty Avg", f"{float(curve.get('difficulty_weighted_average', 0.0)):.1f}")
        c4.metric("Volatility", f"{float(curve.get('volatility_index', 0.0)):.2f}")

        st.subheader("Obasi Coach (Stable)")
        coach_msg = build_obasi_training_coach_speech(
            trainee_name="Ghost",
            difficulty=str(curve.get("current_difficulty", "UNKNOWN")),
            gate_status="GREEN",
            curve=curve,
            sessions=sessions,
            training_feedback=_load_json(Path("src") / "docs" / "training" / "training_feedback_latest.json"),
        )
        st.code(coach_msg)

    with right:
        st.subheader("Latest Validation Report")
        report = _load_json(Path("src") / "docs" / "validation" / "fusion_validation_report.json")
        if report:
            st.json(report)
        else:
            st.info("No validation report found yet: src/docs/validation/fusion_validation_report.json")

        st.subheader("Command Brief Export (Optional)")
        st.caption("If reportlab isn't installed, this will show a safe warning instead of crashing.")
        if st.button("Export Command Brief PDF"):
            try:
                # Lazy import so missing reportlab never kills the UI
                from command_brief_exporter import export_command_brief  # type: ignore

                out = export_command_brief()
                st.success(f"Exported: {out}")
            except Exception as e:
                st.warning(f"PDF export unavailable: {e.__class__.__name__}: {e}")

    st.divider()
    st.subheader("Recent Sessions")
    if sessions:
        st.dataframe(sessions[-25:], use_container_width=True, hide_index=True)
    else:
        st.info("No sessions logged yet.")


if __name__ == "__main__":
    main()

