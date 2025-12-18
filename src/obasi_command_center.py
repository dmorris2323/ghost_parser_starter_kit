# src/obasi_command_center.py
from __future__ import annotations

import streamlit as st
from pathlib import Path
from datetime import datetime, timezone

# -----------------------------
# Local imports (safe + explicit)
# -----------------------------
from spectral_owl_explain import (
    explain_installation_threat_map,
    explain_commander_brief,
    explain_legal_snapshot,
)

# -----------------------------
# Helpers
# -----------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Obasi Command Center",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Minimal CSS (safe)
# -----------------------------
st.markdown(
    """
    <style>
    body {
        background-color: #0b0e14;
        color: #e6e6e6;
    }
    .panel {
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 1rem;
        background-color: #0f172a;
        margin-bottom: 1rem;
    }
    .owl-drawer {
        border: 1px solid #2563eb;
        border-radius: 10px;
        padding: 1rem;
        background: linear-gradient(180deg, #020617, #020617);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 🦉 Owl drawer state (REQUIRED)
# -----------------------------
if "owl_drawer" not in st.session_state:
    st.session_state["owl_drawer"] = {
        "title": "",
        "sections": {},
    }

# -----------------------------
# Layout
# -----------------------------
left_col, right_col = st.columns([2.5, 1.5])

# ============================================================
# LEFT — MAIN PANELS
# ============================================================
with left_col:

    st.markdown("## 🛰️ Obasi Command Center")
    st.caption(
        f"Read-only • Bounded outputs • Operator judgment applies • generated_at_utc: {_utc_now_iso()}"
    )

    # -----------------------------
    # Installation Threat Map Panel
    # -----------------------------
    with st.container():
        st.markdown("### 📡 Installation Threat Map")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write("Zone-based risk snapshot (bounded scoring).")
        if st.button(
            "🦉 Explain Radar / Threat Map",
            use_container_width=True,
            key="owl_explain_radar_main",
        ):
            st.session_state["owl_drawer"] = {
                "title": "Radar / Threat Map",
                "sections": explain_installation_threat_map(),
            }
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # Commander Brief Panel
    # -----------------------------
    with st.container():
        st.markdown("### 🧾 Commander Brief")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write("Executive summary: what changed, why it matters, posture.")
        if st.button(
            "🦉 Explain Commander Brief",
            use_container_width=True,
            key="owl_explain_commander_main",
        ):
            st.session_state["owl_drawer"] = {
                "title": "Commander Brief",
                "sections": explain_commander_brief(),
            }
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # Legal Snapshot Panel
    # -----------------------------
    with st.container():
        st.markdown("### ⚖️ Legal Snapshot (Demo)")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write("Bounded legal triage — ambiguity-first posture.")
        if st.button(
            "🦉 Explain Legal Snapshot",
            use_container_width=True,
            key="owl_explain_legal_main",
        ):
            st.session_state["owl_drawer"] = {
                "title": "Legal Snapshot",
                "sections": explain_legal_snapshot(),
            }
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# RIGHT — 🦉 SPECTRAL OWL DRAWER
# ============================================================
with right_col:
    st.markdown("## 🦉 Spectral Owl")
    st.markdown("<div class='owl-drawer'>", unsafe_allow_html=True)

    drawer = st.session_state.get("owl_drawer", {})
    title = drawer.get("title", "").strip()
    sections = drawer.get("sections", {}) or {}

    if not title:
        st.caption("Click an 🦉 Explain button to open analysis.")
    else:
        st.markdown(f"**Target:** {title}")

        order = [
            "headline",
            "summary",
            "confidence",
            "recommended_posture",
            "what_we_know",
            "what_we_do_not_know",
            "assumptions",
            "uncertainties",
            "operator_actions",
            "notice",
        ]

        for key in order:
            if key in sections:
                st.markdown(f"**{key.replace('_', ' ').title()}**")
                st.write(sections[key])

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# Footer
# ============================================================
st.caption(
    "DEMO MODE ACTIVE — READ ONLY • No baselines updated • Assessment is probabilistic and bounded."
)

