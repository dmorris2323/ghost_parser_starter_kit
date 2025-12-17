# src/obasi_command_center.py
"""
OBASI COMMAND CENTER — MODULE 6D
Live HUD heartbeat + snapshot refresh (demo-safe)
Batman / Iron-Man style ISR Command Center
READ-ONLY • DEMO-LOCKED • ARTIFACT-DRIVEN
"""

from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

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
# Utilities
# ============================
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ts_short() -> str:
    return utc_now().split("T")[1][:8]


def read_txt(p: Path, limit=14000) -> Optional[str]:
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
# Verdict Helpers
# ============================
def _extract_verdict_from_json(obj: Optional[dict]) -> str:
    if not isinstance(obj, dict):
        return "UNKNOWN"
    v = obj.get("verdict") or obj.get("status") or obj.get("result")
    if isinstance(v, str):
        v = v.strip().upper()
        if v in {"PASS", "FAIL", "UNKNOWN"}:
            return v
    return "UNKNOWN"


def _extract_verdict_from_txt(txt: Optional[str]) -> str:
    if not txt:
        return "UNKNOWN"
    t = txt.upper()
    if "VERDICT: PASS" in t:
        return "PASS"
    if "VERDICT: FAIL" in t:
        return "FAIL"
    return "UNKNOWN"


def compute_status() -> dict:
    fusion_json = read_json(VALIDATION / "fusion_core_regression_latest.json")
    fusion_txt = read_txt(VALIDATION / "fusion_core_regression_latest.txt")

    readiness_json = read_json(VALIDATION / "week3_demo_readiness_gate_latest.json")
    readiness_txt = read_txt(VALIDATION / "week3_demo_readiness_gate_latest.txt")

    pack_json = read_json(VALIDATION / "week3_demo_pack_gate_latest.json")

    fusion = _extract_verdict_from_json(fusion_json)
    if fusion == "UNKNOWN":
        fusion = _extract_verdict_from_txt(fusion_txt)

    readiness = _extract_verdict_from_json(readiness_json)
    if readiness == "UNKNOWN":
        readiness = _extract_verdict_from_txt(readiness_txt)

    pack = _extract_verdict_from_json(pack_json)

    if "FAIL" in {fusion, readiness, pack}:
        overall = "DEGRADED"
    elif "UNKNOWN" in {fusion, readiness, pack}:
        overall = "WATCH"
    else:
        overall = "READY"

    return {
        "fusion": fusion,
        "readiness": readiness,
        "pack": pack,
        "overall": overall,
        "demo_lock": is_demo_locked(),
        "evaluated_at": utc_now(),
    }


def verdict_class(v: str) -> str:
    if v == "PASS":
        return "ok"
    if v == "FAIL":
        return "bad"
    return "warn"


# ============================
# CSS (HUD + Radar retained)
# ============================
def hud_css():
    st.markdown("""
    <style>
    :root {
      --cyan: #14F1FF;
      --ink: #05070c;
      --panel: rgba(8,12,22,.78);
      --border: rgba(20,241,255,.35);
      --muted: #8BA3C7;
      --ok: #38f5a3;
      --warn: #ffd36a;
      --bad: #ff5b7a;
    }

    body {
      background:
        radial-gradient(circle at 15% 10%, rgba(20,241,255,0.10), transparent 45%),
        radial-gradient(circle at 85% 18%, rgba(255,91,122,0.08), transparent 45%),
        repeating-linear-gradient(
            0deg,
            rgba(20,241,255,0.05) 0px,
            rgba(20,241,255,0.05) 1px,
            transparent 1px,
            transparent 42px
        ),
        linear-gradient(180deg, #05070c, #0b1220);
      color: #E5EEFF;
      font-family: ui-monospace, monospace;
    }

    .hud-title {
      text-align:center;
      font-size:2.7rem;
      letter-spacing:.28em;
      font-weight:900;
      color: var(--cyan);
      text-shadow: 0 0 18px rgba(20,241,255,.25);
    }

    .hud-sub {
      text-align:center;
      color: var(--muted);
      letter-spacing:.14em;
      margin-bottom:1.1rem;
    }

    .status-bar {
      display:flex;
      justify-content:space-between;
      gap:10px;
      padding:.6rem .75rem;
      border:1px solid var(--border);
      border-radius:16px;
      background: rgba(10,15,25,.65);
      margin-bottom:1rem;
      box-shadow: 0 0 28px rgba(20,241,255,.06);
    }

    .pill {
      display:flex;
      align-items:center;
      gap:.55rem;
      padding:.35rem .75rem;
      border-radius:999px;
      border:1px solid rgba(20,241,255,.25);
      font-size:.85rem;
      color: var(--cyan);
      background: rgba(5,7,12,.55);
    }

    .dot {
      width:10px;
      height:10px;
      border-radius:50%;
      animation: blink 2.2s infinite;
    }

    @keyframes blink {
      0% { opacity:.35; }
      50% { opacity:1; }
      100% { opacity:.35; }
    }

    .ok { background: var(--ok); box-shadow:0 0 12px rgba(56,245,163,.7); }
    .warn { background: var(--warn); box-shadow:0 0 12px rgba(255,211,106,.7); }
    .bad { background: var(--bad); box-shadow:0 0 12px rgba(255,91,122,.7); }

    .panel {
      border:1px solid var(--border);
      border-radius:18px;
      padding:14px;
      background: var(--panel);
      box-shadow:0 0 26px rgba(20,241,255,.08);
      margin-bottom:.9rem;
    }

    .panel h3 {
      margin:0 0 .4rem 0;
      color:#E5EEFF;
      letter-spacing:.08em;
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
    st.markdown('<div class="hud-sub">LIVE DEMO HUD • READ-ONLY • DEMO-LOCKED</div>', unsafe_allow_html=True)

    # Snapshot refresh control
    if "refresh_tick" not in st.session_state:
        st.session_state.refresh_tick = 0

    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("🔄 SNAPSHOT REFRESH"):
            st.session_state.refresh_tick += 1
            st.toast("Snapshot refreshed (read-only).", icon="🦉")

    with cols[1]:
        auto = st.toggle("⏱ Auto Refresh (10s)", value=True)

    with cols[2]:
        st.caption(f"Last UI refresh: {ts_short()} UTC")

    # Auto refresh heartbeat
    if auto:
        time.sleep(10)
        st.rerun()

    status = compute_status()

    # Status bar
    st.markdown(f"""
    <div class="status-bar">
        <div class="pill"><div class="dot {verdict_class(status['overall'])}"></div>POSTURE: {status['overall']}</div>
        <div class="pill"><div class="dot {verdict_class(status['fusion'])}"></div>FUSION: {status['fusion']}</div>
        <div class="pill"><div class="dot {verdict_class(status['readiness'])}"></div>READINESS: {status['readiness']}</div>
        <div class="pill"><div class="dot {verdict_class(status['pack'])}"></div>DEMO PACK: {status['pack']}</div>
        <div class="pill"><div class="dot warn"></div>DEMO LOCK: {"ON" if status['demo_lock'] else "OFF"}</div>
    </div>
    """, unsafe_allow_html=True)

    if is_demo_locked():
        st.warning(demo_lock_banner())

    # Load artifacts
    commander = read_txt(BRIEFS / "commander_brief_latest.txt")
    operator = read_txt(BRIEFS / "week3_operator_summary_latest.txt")
    legal = read_txt(BRIEFS / "legal_case_snapshot_latest.txt")
    readiness_txt = read_txt(VALIDATION / "week3_demo_readiness_gate_latest.txt")

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown('<div class="panel"><h3>Commander Brief</h3></div>', unsafe_allow_html=True)
        st.text_area("commander", commander or "Missing commander brief.", height=420)

    with right:
        st.markdown('<div class="panel"><h3>Operator Summary</h3></div>', unsafe_allow_html=True)
        st.text_area("operator", operator or "Missing operator summary.", height=180)

        st.markdown('<div class="panel"><h3>Legal Snapshot</h3></div>', unsafe_allow_html=True)
        st.text_area("legal", legal or "Missing legal snapshot.", height=180)

        st.markdown('<div class="panel"><h3>Readiness Gate</h3></div>', unsafe_allow_html=True)
        st.text_area("readiness", readiness_txt or "Missing readiness gate.", height=220)

    st.caption(
        f"Evaluated at {status['evaluated_at']} | "
        f"Artifacts only • No mutation • Operator judgment applies."
    )


# ============================
# Entry
# ============================
def main():
    command_center()


if __name__ == "__main__":
    main()

