# src/obasi_command_center.py
"""
OBASI COMMAND CENTER — MODULE 6F
Cinematic boot intro + one-button demo execution HUD
READ-ONLY • DEMO-LOCKED • COMMANDER-SAFE
"""

from __future__ import annotations
import json
import subprocess
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
ORCHESTRATOR = ROOT / "src" / "week3_demo_orchestrator.py"

# ============================
# Utilities
# ============================
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_txt(p: Path, limit=12000) -> Optional[str]:
    try:
        if not p.exists():
            return None
        t = p.read_text(encoding="utf-8", errors="replace")
        return t[:limit] + "\n…(truncated)…" if len(t) > limit else t
    except Exception:
        return None

def read_json(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None

# ============================
# Demo Execution
# ============================
def run_demo_orchestrator() -> dict:
    if not ORCHESTRATOR.exists():
        return {
            "verdict": "FAIL",
            "error": "week3_demo_orchestrator.py not found",
            "ran_at": utc_now(),
        }

    try:
        p = subprocess.run(
            ["python", str(ORCHESTRATOR)],
            capture_output=True,
            text=True,
            timeout=90,
        )
        result = {
            "returncode": p.returncode,
            "stdout_tail": p.stdout[-800:],
            "stderr_tail": p.stderr[-800:],
            "ran_at": utc_now(),
        }
    except Exception as e:
        result = {
            "returncode": -1,
            "error": str(e),
            "ran_at": utc_now(),
        }

    summary = read_json(BRIEFS / "week3_demo_orchestrator_latest.json")
    if summary:
        result.update({
            "verdict": summary.get("verdict"),
            "crashes": summary.get("crashes"),
            "failed_steps": summary.get("failed_steps", []),
        })
    else:
        result["verdict"] = "UNKNOWN"

    return result

# ============================
# CSS — HUD + CINEMATIC INTRO
# ============================
def hud_css():
    st.markdown("""
    <style>
    body {
      background: radial-gradient(circle at 20% 10%, rgba(20,241,255,.12), transparent 40%),
                  linear-gradient(180deg, #05070c, #0b1220);
      color: #E5EEFF;
      font-family: ui-monospace, monospace;
    }
    .boot {
      text-align:center;
      margin-top:20vh;
    }
    .boot h1 {
      font-size:3rem;
      letter-spacing:.4em;
      color:#14F1FF;
      margin-bottom:.2em;
    }
    .boot p {
      opacity:.85;
      letter-spacing:.15em;
    }
    .scan {
      margin-top:20px;
      height:4px;
      background: linear-gradient(90deg, transparent, #14F1FF, transparent);
      animation: scan 1.5s infinite;
    }
    @keyframes scan {
      0% {opacity:.2}
      50% {opacity:1}
      100% {opacity:.2}
    }
    .panel {
      border:1px solid rgba(20,241,255,.35);
      border-radius:16px;
      padding:12px;
      background: rgba(8,12,22,.8);
      margin-bottom:10px;
    }
    .title {
      text-align:center;
      font-size:2.6rem;
      letter-spacing:.28em;
      font-weight:900;
      color:#14F1FF;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================
# Cinematic Boot
# ============================
def cinematic_boot():
    hud_css()
    st.markdown(
        """
        <div class="boot">
          <h1>OBASI</h1>
          <p>INTELLIGENCE FUSION SYSTEM</p>
          <div class="scan"></div>
          <br/>
          <p>INITIALIZING SENSOR FUSION</p>
          <p>LOADING BOUNDED ANALYTICS</p>
          <p>ENFORCING DEMO LOCK</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(3.8)
    st.session_state.boot_complete = True
    st.rerun()

# ============================
# Command Center
# ============================
def command_center():
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
    )

    hud_css()

    st.markdown('<div class="title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.caption("One-Button Demo Execution • Read-Only • Demo-Locked")

    if is_demo_locked():
        st.warning(demo_lock_banner())

    if "last_demo_run" not in st.session_state:
        st.session_state.last_demo_run = None

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("▶ RUN FULL WEEK-3 DEMO", type="primary"):
            with st.spinner("Executing demo (read-only)…"):
                st.session_state.last_demo_run = run_demo_orchestrator()
            st.toast("Demo execution complete.", icon="🦉")

    with col2:
        st.caption(f"UTC: {utc_now()}")

    st.markdown('<div class="panel"><h3>Last Demo Telemetry</h3></div>', unsafe_allow_html=True)
    if st.session_state.last_demo_run:
        st.json(st.session_state.last_demo_run, expanded=True)
    else:
        st.info("No demo run executed in this session.")

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="panel"><h3>Commander Brief</h3></div>', unsafe_allow_html=True)
        st.text_area(
            "cmd",
            read_txt(BRIEFS / "commander_brief_latest.txt") or "Missing commander brief.",
            height=360,
        )

    with right:
        st.markdown('<div class="panel"><h3>Operator Summary</h3></div>', unsafe_allow_html=True)
        st.text_area(
            "op",
            read_txt(BRIEFS / "week3_operator_summary_latest.txt") or "Missing operator summary.",
            height=180,
        )

        st.markdown('<div class="panel"><h3>Readiness Gate</h3></div>', unsafe_allow_html=True)
        st.text_area(
            "gate",
            read_txt(VALIDATION / "week3_demo_readiness_gate_latest.txt") or "Missing readiness gate.",
            height=180,
        )

    st.caption("Artifacts only • No mutation • Operator judgment applies.")

# ============================
# Entry
# ============================
def main():
    if "boot_complete" not in st.session_state:
        st.session_state.boot_complete = False

    if not st.session_state.boot_complete:
        cinematic_boot()
    else:
        command_center()

if __name__ == "__main__":
    main()

