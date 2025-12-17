from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

# ============================
# CONFIG
# ============================

BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

ARTIFACTS = {
    "Commander Brief (TXT)": BRIEFS_DIR / "commander_brief_latest.txt",
    "Operator Summary": BRIEFS_DIR / "week3_operator_summary_latest.txt",
    "Demo Narrative": BRIEFS_DIR / "week3_demo_narrative_latest.txt",
    "Legal Case Snapshot": BRIEFS_DIR / "legal_case_snapshot_latest.txt",
    "Mobile Manifest": BRIEFS_DIR / "mobile_enjoy_manifest_latest.json",
    "Fusion Core Regression": VALIDATION_DIR / "fusion_core_regression_latest.json",
    "Demo Readiness Gate": VALIDATION_DIR / "week3_demo_readiness_gate_latest.json",
}

# ============================
# UTILS
# ============================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return "⚠️ Artifact missing or unreadable."

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"error": "Artifact missing or unreadable."}

# ============================
# STREAMLIT PAGE CONFIG
# ============================

st.set_page_config(
    page_title="OBASI COMMAND CENTER",
    layout="wide",
)

# ============================
# STYLING — BATMAN / IRON MAN HUD
# ============================

st.markdown(
    """
    <style>
    body {
        background-color: #0b0f14;
        color: #e0f7fa;
    }
    .hud-title {
        font-size: 42px;
        font-weight: 800;
        color: #00e5ff;
        text-align: center;
        letter-spacing: 2px;
    }
    .hud-sub {
        text-align: center;
        color: #90caf9;
        margin-bottom: 20px;
    }
    .hud-panel {
        border: 1px solid #00e5ff33;
        border-radius: 10px;
        padding: 15px;
        background: linear-gradient(145deg, #0f1720, #05080c);
        box-shadow: 0 0 12px #00e5ff22;
        margin-bottom: 15px;
    }
    .demo-lock {
        border: 2px solid #ff1744;
        color: #ff1744;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================
# HEADER
# ============================

st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hud-sub">Spectral Owl • Week-3 Demo • Read-Only</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="demo-lock">
    DEMO MODE ACTIVE — READ ONLY<br/>
    No baselines updated • No training • No mutation<br/>
    Assessment is probabilistic and bounded; operator judgment applies.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"Generated at (UTC): {utc_now()}")

# ============================
# STATUS BAR
# ============================

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("SYSTEM STATUS", "PASS")
with col_b:
    st.metric("MODE", "DEMO LOCKED")
with col_c:
    st.metric("ENVIRONMENT", "LOCAL HUD")

st.divider()

# ============================
# MAIN PANELS
# ============================

left, right = st.columns(2)

with left:
    st.markdown("### 🧠 Commander View")
    for name in [
        "Commander Brief (TXT)",
        "Demo Narrative",
        "Operator Summary",
        "Legal Case Snapshot",
    ]:
        with st.container():
            st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.text(read_text(ARTIFACTS[name]))
            st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("### 🛡️ System & Validation")
    for name in [
        "Fusion Core Regression",
        "Demo Readiness Gate",
        "Mobile Manifest",
    ]:
        with st.container():
            st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.json(read_json(ARTIFACTS[name]))
            st.markdown("</div>", unsafe_allow_html=True)

# ============================
# FOOTER
# ============================

st.divider()
st.caption(
    "OBASI — Spectral Owl Command Interface | Ghost Lantern Labs | Demo-Safe HUD"
)

