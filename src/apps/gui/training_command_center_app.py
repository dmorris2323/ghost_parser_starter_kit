import json
import sys
from pathlib import Path

import streamlit as st

# -------------------------------------------------------------------
# PATH FIX (non-negotiable for Streamlit)
# This file lives at: <repo>/src/apps/gui/training_command_center_app.py
# We need: <repo>/src on sys.path so imports like training_curve_engine work.
# -------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]  # .../parser_starter_kit
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Now absolute imports work reliably
from training_curve_engine import compute_training_curve
from training_session_store import load_sessions
from gll_run_gates import run_gates
from command_brief_exporter import export_command_brief

# Obasi coach is optional; never hard-crash if it changes
try:
    from obasi_training_coach import build_obasi_training_coach_speech  # type: ignore
except Exception:
    build_obasi_training_coach_speech = None


def _read_latest_feedback() -> dict:
    p = SRC_DIR / "docs" / "training" / "training_feedback_latest.json"
    try:
        if p.exists():
            obj = json.loads(p.read_text(encoding="utf-8"))
            return obj if isinstance(obj, dict) else {"_non_dict": obj}
    except Exception as e:
        return {"status": "ERROR", "reason": f"{e.__class__.__name__}: {e}"}
    return {"status": "MISSING", "reason": "training_feedback_latest.json not found"}


def _download_button(label: str, path: str, mime: str) -> None:
    p = Path(path)
    if not p.exists():
        st.info(f"{label} not available: {path}")
        return
    st.download_button(label=label, data=p.read_bytes(), file_name=p.name, mime=mime)


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")
    st.title("🦉 GLL Training Command Center")

    # ---- Gates quick view ----
    with st.sidebar:
        st.header("🔒 Gates")
        if st.button("Run PRE gate"):
            st.session_state["pre_gate"] = run_gates(
                gate_type="PRE", context="training_command_center", update_baselines=False
            )

        if st.button("Run POST gate"):
            st.session_state["post_gate"] = run_gates(
                gate_type="POST", context="training_command_center", update_baselines=False
            )

        if "pre_gate" in st.session_state:
            st.json(st.session_state["pre_gate"])
        if "post_gate" in st.session_state:
            st.json(st.session_state["post_gate"])

    # ---- Data ----
    sessions = load_sessions()
    curve = compute_training_curve()
    feedback = _read_latest_feedback()

    col1, col2, col3 = st.columns(3)
    col1.metric("AGI (0–100)", float(curve.get("AGI", 0.0)))
    col2.metric("Improvement slope", float(curve.get("improvement_slope", 0.0)))
    col3.metric("Volatility", float(curve.get("volatility_index", 0.0)))

    st.subheader("Sessions (latest)")
    if sessions:
        st.dataframe(sessions[-25:], use_container_width=True)
    else:
        st.info("No sessions found yet.")

    with st.expander("🧭 Next Training Recommendation", expanded=True):
        st.json(feedback)

    # ---- Obasi coach (optional) ----
    st.subheader("Obasi Coach")
    if build_obasi_training_coach_speech is None:
        st.warning("Obasi coach module unavailable (non-fatal).")
    else:
        try:
            msg = build_obasi_training_coach_speech(
                trainee_name="Ghost",
                training_curve=curve,
                sessions=sessions,
                training_feedback=feedback,
            )
            if isinstance(msg, dict):
                st.json(msg)
            else:
                st.write(str(msg))
        except Exception as e:
            st.warning(f"Coach error (non-fatal): {e.__class__.__name__}: {e}")

    # ---- Export brief ----
    st.subheader("📦 Export Command Brief Packet")
    st.caption("HTML always exports. PDF is optional (only if reportlab is installed).")

    if st.button("Export Brief Packet"):
        st.session_state["export_result"] = export_command_brief(
            title="Ghost Lantern Labs — Command Brief Packet"
        )

    if "export_result" in st.session_state:
        r = st.session_state["export_result"]
        st.json(r)

        paths = r.get("paths", {})
        st.markdown("### Downloads")
        _download_button("Download HTML brief", paths.get("html_latest", ""), "text/html")
        _download_button("Download manifest JSON", paths.get("manifest_latest", ""), "application/json")

        pdf_info = r.get("pdf", {})
        if pdf_info.get("latest_ok", False):
            _download_button("Download PDF brief", paths.get("pdf_latest", ""), "application/pdf")
        else:
            st.info(f"PDF not generated: {pdf_info.get('latest_status', 'unknown')}")

    st.divider()
    st.caption("Command Center is designed to never hard-crash due to optional modules.")


if __name__ == "__main__":
    main()

