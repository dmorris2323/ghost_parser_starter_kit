# src/obasi_command_center.py
"""
OBASI COMMAND CENTER — MODULE 6B
Premium HUD (Batcave / Iron-Man style)
Artifact-driven • Demo-locked • Read-only
"""

from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import streamlit as st

# ============================
# Demo Lock
# ============================
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:
    def is_demo_locked(): return True
    def demo_lock_banner():
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
# Safe Readers
# ============================
def read_txt(p: Path, limit=12000) -> Optional[str]:
    try:
        if not p.exists(): return None
        t = p.read_text(encoding="utf-8", errors="replace")
        return t[:limit] + "\n…(truncated)…" if len(t) > limit else t
    except Exception:
        return None

def read_json(p: Path) -> Optional[dict]:
    try:
        if not p.exists(): return None
        return json.loads(p.read_text())
    except Exception:
        return None

def utc_now():
    return datetime.now(timezone.utc).isoformat()

# ============================
# Cinematic Boot
# ============================
def cinematic_boot():
    st.set_page_config(
        page_title="OBASI INITIALIZING",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    elapsed = time.time() - st.session_state["boot_start"]

    st.markdown("""
    <style>
    body {
        background:
        radial-gradient(circle at center, rgba(20,241,255,0.08), transparent 55%),
        repeating-linear-gradient(
            0deg,
            rgba(20,241,255,0.06) 0px,
            rgba(20,241,255,0.06) 1px,
            transparent 1px,
            transparent 40px
        ),
        #05070c;
        color: #14F1FF;
        font-family: ui-monospace, monospace;
    }
    .boot {
        text-align:center;
        margin-top:12%;
    }
    .title {
        font-size:3.4rem;
        letter-spacing:.4em;
        font-weight:900;
    }
    .subtitle {
        color:#8BA3C7;
        letter-spacing:.18em;
        margin-top:.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="boot">', unsafe_allow_html=True)
    st.markdown('<div class="title">OBASI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">SPECTRAL OWL COMMAND SYSTEM</div>', unsafe_allow_html=True)

    progress = min(1.0, elapsed / 5.0)
    st.progress(progress)

    if elapsed < 1.5:
        msg = "Powering fusion core…"
    elif elapsed < 3.0:
        msg = "Synchronizing intelligence lattice…"
    elif elapsed < 4.5:
        msg = "Validating demo safety envelope…"
    else:
        msg = "SYSTEM READY"

    st.markdown(f"<p>{msg}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if elapsed >= 5.0:
        st.session_state["boot_complete"] = True
        st.rerun()

    time.sleep(0.15)
    st.rerun()

# ============================
# HUD Styling
# ============================
def hud_css():
    st.markdown("""
    <style>
    body {
        background:
        linear-gradient(180deg, #05070c, #0b1220);
        color: #E5EEFF;
    }

    .hud-title {
        text-align:center;
        font-size:2.7rem;
        letter-spacing:.28em;
        font-weight:900;
        color:#14F1FF;
    }

    .hud-sub {
        text-align:center;
        color:#8BA3C7;
        letter-spacing:.14em;
        margin-bottom:1.2rem;
    }

    .status-bar {
        display:flex;
        justify-content:space-around;
        padding:.6rem;
        border:1px solid rgba(20,241,255,.35);
        border-radius:14px;
        background:rgba(10,15,25,.65);
        margin-bottom:1.2rem;
    }

    .status-pill {
        padding:.3rem .9rem;
        border-radius:999px;
        border:1px solid rgba(20,241,255,.4);
        font-size:.85rem;
        color:#14F1FF;
        animation:pulse 2.5s infinite;
    }

    @keyframes pulse {
        0% { box-shadow:0 0 4px rgba(20,241,255,.4); }
        50% { box-shadow:0 0 14px rgba(20,241,255,.8); }
        100% { box-shadow:0 0 4px rgba(20,241,255,.4); }
    }

    .panel {
        border:1px solid rgba(20,241,255,.35);
        border-radius:18px;
        padding:14px;
        background:rgba(8,12,22,.75);
        box-shadow:0 0 28px rgba(20,241,255,.08);
        margin-bottom:1rem;
    }

    .panel h3 {
        margin:0 0 .5rem 0;
        color:#E5EEFF;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================
# Main Command Center
# ============================
def command_center():
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
    )

    hud_css()

    st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hud-sub">DEMO-LOCKED • READ-ONLY • ISR-GRADE</div>', unsafe_allow_html=True)

    # Status Bar
    st.markdown("""
    <div class="status-bar">
        <div class="status-pill">SYSTEM READY</div>
        <div class="status-pill">DEMO LOCK: ON</div>
        <div class="status-pill">FUSION STABLE</div>
        <div class="status-pill">NO MUTATION</div>
    </div>
    """, unsafe_allow_html=True)

    if is_demo_locked():
        st.warning(demo_lock_banner())

    # Load artifacts
    commander = read_txt(BRIEFS / "commander_brief_latest.txt")
    operator = read_txt(BRIEFS / "week3_operator_summary_latest.txt")
    legal = read_txt(BRIEFS / "legal_case_snapshot_latest.txt")
    readiness = read_txt(VALIDATION / "week3_demo_readiness_gate_latest.txt")

    col1, col2 = st.columns([1.25, 1])

    with col1:
        st.markdown('<div class="panel"><h3>Commander Brief</h3></div>', unsafe_allow_html=True)
        st.text_area("commander", commander or "Commander brief missing.", height=420)

    with col2:
        st.markdown('<div class="panel"><h3>Operator Summary</h3></div>', unsafe_allow_html=True)
        st.text_area("operator", operator or "Operator summary missing.", height=180)

        st.markdown('<div class="panel"><h3>Legal Snapshot</h3></div>', unsafe_allow_html=True)
        st.text_area("legal", legal or "Legal snapshot missing.", height=180)

    st.markdown('<div class="panel"><h3>Demo Readiness Gate</h3></div>', unsafe_allow_html=True)
    st.text_area("readiness", readiness or "Readiness gate missing.", height=240)

    st.caption(f"Last refresh (UTC): {utc_now()} | Repo: {ROOT}")

# ============================
# Entry
# ============================
def main():
    st.session_state.setdefault("boot_complete", False)
    st.session_state.setdefault("boot_start", time.time())

    if not st.session_state["boot_complete"]:
        cinematic_boot()
    else:
        command_center()

if __name__ == "__main__":
    main()

