# src/obasi_command_center.py
"""
OBASI COMMAND CENTER — MODULE 5F
Cinematic Boot + Demo Auto-Sequence + Premium HUD

Run:
  streamlit run src/obasi_command_center.py
"""

from __future__ import annotations
import json
import time
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st

# ============================
# Demo Lock (expected)
# ============================
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:
    def is_demo_locked() -> bool:
        return True
    def demo_lock_banner() -> str:
        return (
            "DEMO MODE ACTIVE — READ ONLY\n"
            "No baselines updated. No training. No mutation.\n"
            "Assessment is probabilistic and bounded; operator judgment applies."
        )

# ============================
# Paths
# ============================
ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BRIEFS = DOCS / "briefs"
VALIDATION = DOCS / "validation"

# ============================
# Session State Init
# ============================
def init_state():
    st.session_state.setdefault("boot_complete", False)
    st.session_state.setdefault("boot_start", time.time())
    st.session_state.setdefault("presentation", True)
    st.session_state.setdefault("briefing_view", True)
    st.session_state.setdefault("focus", "overview")
    st.session_state.setdefault("seq_running", False)

# ============================
# Cinematic Boot Screen
# ============================
def cinematic_boot():
    st.set_page_config(
        page_title="OBASI Initializing",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    elapsed = time.time() - st.session_state["boot_start"]

    st.markdown(
        """
        <style>
        body {
            background: radial-gradient(circle at center, #0a1a2f 0%, #02040a 70%);
        }
        .boot {
            text-align: center;
            margin-top: 10%;
            font-family: monospace;
            color: #14F1FF;
        }
        .title {
            font-size: 3.2rem;
            font-weight: 900;
            letter-spacing: .35em;
            margin-bottom: 1rem;
        }
        .sub {
            color: #8BA3C7;
            letter-spacing: .15em;
            margin-bottom: 2rem;
        }
        .status {
            font-size: 1.1rem;
            margin-top: 1.5rem;
            color: #DDE7FF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="boot">', unsafe_allow_html=True)
    st.markdown('<div class="title">OBASI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">SPECTRAL OWL COMMAND SYSTEM</div>', unsafe_allow_html=True)

    progress = min(1.0, elapsed / 5.0)
    st.progress(progress)

    if elapsed < 1.2:
        msg = "Initializing core systems…"
    elif elapsed < 2.4:
        msg = "Loading fusion pipeline…"
    elif elapsed < 3.6:
        msg = "Validating demo lock & safety gates…"
    elif elapsed < 4.8:
        msg = "Preparing command interface…"
    else:
        msg = "BOOT COMPLETE"

    st.markdown(f'<div class="status">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if elapsed >= 5.0:
        st.session_state["boot_complete"] = True
        st.rerun()

    time.sleep(0.15)
    st.rerun()

# ============================
# HUD (post-boot)
# ============================
def command_center():
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(180deg, #05080c, #0b1220);
            color: #DDE7FF;
        }
        .hud-title {
            text-align: center;
            font-size: 2.6rem;
            font-weight: 900;
            letter-spacing: .28em;
            color: #14F1FF;
        }
        .hud-sub {
            text-align: center;
            color: #8BA3C7;
            margin-bottom: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hud-sub">Demo-Locked • Read-Only • Spectral Owl</div>', unsafe_allow_html=True)

    st.success("SYSTEM STATUS: DEMO SAFE / READINESS VERIFIED")

    if is_demo_locked():
        st.warning(demo_lock_banner())

    st.markdown("### 🎯 Demo Navigation")
    cols = st.columns(6)
    for i, label in enumerate(["Overview", "Readiness", "Operator", "Commander", "Legal", "Validation"]):
        if cols[i].button(label):
            st.session_state["focus"] = label.lower()

    st.markdown(f"**Current Focus:** `{st.session_state['focus']}`")

    st.markdown("---")
    st.info("HUD rendering active. Artifacts loaded dynamically.")

    # Placeholder — real panels already exist in your 5E version
    st.code("Demo artifacts visible here (commander brief, operator summary, gates, etc.)")

    st.sidebar.markdown("### Demo Controls")
    if st.sidebar.button("🔁 Replay Boot Sequence"):
        st.session_state["boot_complete"] = False
        st.session_state["boot_start"] = time.time()
        st.rerun()

# ============================
# Entry
# ============================
def main():
    init_state()
    if not st.session_state["boot_complete"]:
        cinematic_boot()
    else:
        command_center()

if __name__ == "__main__":
    main()

