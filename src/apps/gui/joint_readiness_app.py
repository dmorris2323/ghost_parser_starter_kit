#!/usr/bin/env python3
"""
apps/gui/joint_readiness_app.py

Ghost Lantern Labs – Joint Readiness Console (Obasi View)
---------------------------------------------------------

Purpose:
    Streamlit dashboard focused on the Joint Readiness stack:

        • Joint Readiness Board (nuclear + base-defense)
        • Joint Risk Register
        • Joint Readiness Integrity Report
        • Obasi voice script for joint readiness

This app is READ-ONLY with respect to the live fusion pipeline. It can
optionally trigger regeneration of the joint readiness artifacts by
calling the existing builder modules.

Usage (from repo root):

    cd /Users/dextermorris/ghost/parser_starter_kit
    streamlit run src/apps/gui/joint_readiness_app.py

This does NOT replace your existing Spectral Dashboard (apps/gui/app.py).
It is a focused console for commanders, AFWERX reviewers, and Shari.
"""

import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

# -------------------------------------------------------------------
# Ensure src/ is on the Python path so imports work correctly
# -------------------------------------------------------------------

# __file__ = .../src/apps/gui/joint_readiness_app.py
# We want SRC_DIR = .../src
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Now these imports resolve from src/
from joint_readiness_board import build_joint_readiness_board
from joint_readiness_scorecard import build_joint_readiness_scorecard
from joint_risk_register import build_joint_risk_register
from joint_readiness_voice_script import build_joint_readiness_voice_script
from joint_readiness_integrity_guard import run_joint_readiness_integrity_guard

# -------------------------------------------------------------------
# Paths & helpers
# -------------------------------------------------------------------

BASE_DIR = SRC_DIR                         # /.../parser_starter_kit/src
DOCS_DIR = os.path.join(BASE_DIR, "docs")  # /.../parser_starter_kit/src/docs


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _fmt_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def _get_joint_artifacts() -> Dict[str, Any]:
    """Load all key joint readiness artifacts from docs/."""
    board = _safe_read_json(os.path.join(DOCS_DIR, "joint_readiness_board.json")) or {}
    risk = _safe_read_json(os.path.join(DOCS_DIR, "joint_risk_register.json")) or {}
    integrity = _safe_read_json(os.path.join(DOCS_DIR, "joint_readiness_integrity_report.json")) or {}
    voice = _safe_read_json(os.path.join(DOCS_DIR, "joint_readiness_voice_script.json")) or {}

    return {
        "board": board,
        "risk": risk,
        "integrity": integrity,
        "voice": voice,
    }


# -------------------------------------------------------------------
# UI helpers
# -------------------------------------------------------------------

def _joint_level_pill(level: str) -> str:
    lvl = (level or "UNKNOWN").upper()
    if lvl == "GREEN":
        return "🟢 GREEN"
    if lvl == "AMBER":
        return "🟡 AMBER"
    if lvl == "RED":
        return "🔴 RED"
    return f"⚪ {lvl}"


def _health_level_emoji(level: str) -> str:
    lvl = (level or "UNKNOWN").upper()
    if lvl == "GREEN":
        return "🛡️ GREEN"
    if lvl == "AMBER":
        return "⚠️ AMBER"
    if lvl == "RED":
        return "❌ RED"
    return f"⚪ {lvl}"


def _render_top_risks(risks: List[Dict[str, Any]]) -> None:
    if not risks:
        st.info("No significant risks recorded in the current Joint Risk Register.")
        return

    for idx, r in enumerate(risks, start=1):
        severity = str(r.get("severity", "MEDIUM")).upper()
        domain = str(r.get("domain", "JOINT")).upper()
        title = str(r.get("title", ""))
        detail = str(r.get("detail", ""))

        if severity == "HIGH":
            badge = "🔴 HIGH"
        elif severity == "MEDIUM":
            badge = "🟡 MEDIUM"
        else:
            badge = "🟢 LOW"

        with st.expander(f"Risk {idx}: {domain} – {title} ({badge})", expanded=(idx == 1)):
            st.write(detail)


def _render_integrity_checks(checks: List[Dict[str, Any]]) -> None:
    if not checks:
        st.info("No integrity checks recorded. Run the integrity guard to populate this view.")
        return

    for r in checks:
        status = str(r.get("status", "OK")).upper()
        component = str(r.get("component", "unknown"))
        message = str(r.get("message", ""))

        if status == "ERROR":
            icon = "❌"
        elif status == "WARN":
            icon = "⚠️"
        else:
            icon = "✅"

        st.write(f"{icon} **{component}** – {message}")


def _render_voice_segments(voice: Dict[str, Any]) -> None:
    segments = voice.get("segments")
    full_script = voice.get("full_script")

    if not isinstance(segments, dict) or not full_script:
        st.warning("Joint readiness voice script not available. Run the voice script generator first.")
        return

    st.write("**Voice Profile:**", voice.get("voice_profile", "Unknown"))
    st.caption(f"Generated at (UTC): {voice.get('generated_at', 'unknown')}")

    with st.expander("Full Obasi Script (Joint Readiness)", expanded=True):
        st.write(full_script)

    with st.expander("Script Segments", expanded=False):
        for name in [
            "opening",
            "joint_summary",
            "nuclear_summary",
            "base_defense_summary",
            "top_risks",
            "closing",
        ]:
            text = segments.get(name)
            if text:
                st.markdown(f"**{name.replace('_', ' ').title()}**")
                st.write(text)
                st.markdown("---")


# -------------------------------------------------------------------
# Main render
# -------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="GLL – Joint Readiness Console",
        page_icon="🦉",
        layout="wide",
    )

    st.title("🦉 Ghost Lantern Labs – Joint Readiness Console")
    st.caption(
        "Joint nuclear + base-defense readiness view for commanders, AFWERX reviewers, and Shari. "
        "Powered by Ghost Lantern Labs' nuclear/AFTAC and base-defense stacks."
    )

    # Sidebar controls
    st.sidebar.header("Console Controls")

    st.sidebar.markdown(
        "This console visualizes existing joint readiness artifacts from `src/docs/`.\n\n"
        "Use the button below to rebuild the joint readiness products from the latest inputs."
    )

    if st.sidebar.button("🔁 Rebuild joint readiness products"):
        with st.spinner("Rebuilding joint readiness products..."):
            build_joint_readiness_board()
            build_joint_readiness_scorecard()
            build_joint_risk_register()
            build_joint_readiness_voice_script()
            run_joint_readiness_integrity_guard()
        st.sidebar.success("Joint readiness products rebuilt.")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Tip:** Run your underlying generators (nuclear early warning, "
        "installation threat map, outage predictor, distributed readiness, "
        "base defense storyboard) regularly from `ghost_cli.py` or via the "
        "individual modules to keep this console fresh."
    )

    artifacts = _get_joint_artifacts()
    board = artifacts["board"]
    risk = artifacts["risk"]
    integrity = artifacts["integrity"]
    voice = artifacts["voice"]

    # -----------------------------
    # Topline: joint + health
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    jr_score = _fmt_float(board.get("joint_readiness_score"), 0.0)
    jr_level = str(board.get("joint_readiness_level", "UNKNOWN"))
    generated_at = board.get("generated_at", datetime.utcnow().isoformat() + "Z")

    with col1:
        st.metric(
            label="Joint Readiness Score",
            value=f"{jr_score:.1f} / 100",
            delta=_joint_level_pill(jr_level),
        )
        st.caption(f"Latest joint readiness snapshot · Generated (UTC): {generated_at}")

    health_score = _fmt_float(integrity.get("health_score"), 0.0)
    health_level = str(integrity.get("health_level", "UNKNOWN"))

    with col2:
        st.metric(
            label="Integrity Health Score",
            value=f"{health_score:.1f} / 100",
            delta=_health_level_emoji(health_level),
        )
        st.caption("Structural health of the joint readiness stack.")

    risks_list: List[Dict[str, Any]] = []
    if isinstance(risk.get("risks"), list):
        risks_list = [r for r in risk["risks"] if isinstance(r, dict)]

    with col3:
        high_count = sum(1 for r in risks_list if str(r.get("severity", "")).upper() == "HIGH")
        med_count = sum(1 for r in risks_list if str(r.get("severity", "")).upper() == "MEDIUM")
        st.metric(
            label="Tracked Joint Risks",
            value=f"{len(risks_list)} total",
            delta=f"🔴 {high_count} HIGH · 🟡 {med_count} MED",
        )
        st.caption("Risks spanning nuclear, base-defense, sensors, fusion, and overall joint posture.")

    st.markdown("---")

    # -----------------------------
    # Nuclear + base-defense detail
    # -----------------------------

    st.subheader("Nuclear & Base-Defense Posture")

    nuclear = board.get("nuclear", {}) or {}
    base_def = board.get("base_defense", {}) or {}
    outage = board.get("outage", {}) or {}
    dist = board.get("distributed_readiness", {}) or {}

    n_level = str(nuclear.get("level", "UNKNOWN"))
    n_score = _fmt_float(nuclear.get("score"), 0.0)
    n_vol = _fmt_float(nuclear.get("volatility_index"), 0.0)
    n_drift_conf = _fmt_float(nuclear.get("drift_confidence"), 0.0)
    n_align = str(nuclear.get("alignment", "UNKNOWN"))

    b_level = str(base_def.get("level", "UNKNOWN"))
    b_score = _fmt_float(base_def.get("score"), 0.0)
    b_sectors = int(base_def.get("sectors", 0))

    o_risk = _fmt_float(outage.get("outage_risk_score"), 0.0)
    o_crit = int(outage.get("critical_sensors_at_risk", 0))

    d_fusion = _fmt_float(dist.get("fusion_trust_score"), 0.0)
    d_rel = _fmt_float(dist.get("average_reliability"), 0.0)
    d_units = int(dist.get("units_tracked", 0))

    nc1, nc2 = st.columns(2)

    with nc1:
        st.markdown("#### Nuclear Early Warning")
        st.metric("Nuclear Early-Warning Score", f"{n_score:.1f} / 100", help="Higher = more nuclear pressure.")
        st.write(f"**Level:** {n_level}")
        st.write(f"**Temporal Volatility:** {n_vol:.1f} / 100")
        st.write(f"**Drift Confidence:** {n_drift_conf:.1f} / 100")
        st.write(f"**Alignment:** {n_align}")

    with nc2:
        st.markdown("#### Base Defense & Fusion Health")
        st.metric("Base Threat Score", f"{b_score:.1f} / 100", help="Higher = more perimeter/airspace pressure.")
        st.write(f"**Base Threat Level:** {b_level}")
        st.write(f"**Sectors Tracked:** {b_sectors}")
        st.write(f"**Sensor Outage Risk:** {o_risk:.1f} / 100")
        st.write(f"**Critical Sensors at Risk:** {o_crit}")
        st.write(f"**Fusion Trust Score:** {d_fusion:.1f} / 100")
        st.write(f"**Avg Sensor Reliability:** {d_rel:.1f} / 100")
        st.write(f"**Units / Elements Tracked:** {d_units}")

    st.markdown("---")

    # -----------------------------
    # Top risks
    # -----------------------------

    st.subheader("Top Joint Risks")
    _render_top_risks(risks_list)

    st.markdown("---")

    # -----------------------------
    # Obasi voice script
    # -----------------------------

    st.subheader("Obasi – Joint Readiness Voice Script")

    if not voice:
        st.warning(
            "No joint readiness voice script found. Click 'Rebuild joint readiness products' in the sidebar "
            "or run joint_readiness_voice_script.py from the CLI."
        )
    else:
        _render_voice_segments(voice)

    st.markdown("---")

    # -----------------------------
    # Integrity report detail
    # -----------------------------

    st.subheader("Integrity Guard – Joint Stack Health")

    checks = integrity.get("checks")
    if not isinstance(checks, list):
        st.warning(
            "No integrity checks found. Run joint_readiness_integrity_guard.py or click 'Rebuild joint readiness products'."
        )
    else:
        _render_integrity_checks(checks)

    st.markdown("---")
    st.caption(
        "Ghost Lantern Labs · Joint Nuclear / Base-Defense Readiness Console · "
        "Built for nuclear, ISR, and base-defense mission owners."
    )


if __name__ == "__main__":
    main()

