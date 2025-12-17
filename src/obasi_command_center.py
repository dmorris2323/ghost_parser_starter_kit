# src/obasi_command_center.py
"""
OBASI COMMAND CENTER — MODULE 6C
Premium HUD (Batcave / Iron-Man style) + Radar Sweep + Reactive Status Lights
Artifact-driven • Demo-locked • Read-only
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
# Safe Readers
# ============================
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    # sometimes status objects embed status inside dicts
    if isinstance(obj.get("verdict"), dict) and isinstance(obj["verdict"].get("status"), str):
        return obj["verdict"]["status"].strip().upper()
    return "UNKNOWN"


def _extract_verdict_from_txt(txt: Optional[str]) -> str:
    if not txt:
        return "UNKNOWN"
    t = txt.upper()
    # prioritize explicit "VERDICT:" lines
    for needle in ["VERDICT: PASS", "VERDICT: FAIL"]:
        if needle in t:
            return "PASS" if "PASS" in needle else "FAIL"
    # fallback
    if "VERDICT: PASS" in t or "\nPASS\n" in t:
        return "PASS"
    if "VERDICT: FAIL" in t or "\nFAIL\n" in t:
        return "FAIL"
    return "UNKNOWN"


def compute_status() -> dict:
    """
    Read-only status rollup from latest artifacts.
    Never crashes.
    """
    fusion_core = read_json(VALIDATION / "fusion_core_regression_latest.json")
    readiness = read_json(VALIDATION / "week3_demo_readiness_gate_latest.json")
    demo_pack = read_json(VALIDATION / "week3_demo_pack_gate_latest.json")

    # Sometimes only TXT exists for some gates; load best-effort.
    readiness_txt = read_txt(VALIDATION / "week3_demo_readiness_gate_latest.txt")
    fusion_txt = read_txt(VALIDATION / "fusion_core_regression_latest.txt")

    fusion_v = _extract_verdict_from_json(fusion_core)
    if fusion_v == "UNKNOWN":
        fusion_v = _extract_verdict_from_txt(fusion_txt)

    readiness_v = _extract_verdict_from_json(readiness)
    if readiness_v == "UNKNOWN":
        readiness_v = _extract_verdict_from_txt(readiness_txt)

    demo_pack_v = _extract_verdict_from_json(demo_pack)

    # Overall posture
    if "FAIL" in {fusion_v, readiness_v, demo_pack_v}:
        overall = "DEGRADED"
    elif "UNKNOWN" in {fusion_v, readiness_v, demo_pack_v}:
        overall = "WATCH"
    else:
        overall = "READY"

    return {
        "fusion_core_regression": fusion_v,
        "demo_readiness_gate": readiness_v,
        "demo_pack_gate": demo_pack_v if demo_pack_v != "UNKNOWN" else "UNKNOWN",
        "overall": overall,
        "demo_lock": bool(is_demo_locked()),
    }


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
    .boot { text-align:center; margin-top:12%; }
    .title { font-size:3.4rem; letter-spacing:.4em; font-weight:900; }
    .subtitle { color:#8BA3C7; letter-spacing:.18em; margin-top:.5rem; }
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
# HUD Styling + Radar Sweep
# ============================
def hud_css():
    st.markdown("""
    <style>
    :root {
      --cyan: #14F1FF;
      --ink: #05070c;
      --panel: rgba(8,12,22,.75);
      --border: rgba(20,241,255,.35);
      --muted: #8BA3C7;
      --ok: #38f5a3;
      --warn: #ffd36a;
      --bad: #ff5b7a;
    }

    body {
      background:
        radial-gradient(circle at 18% 12%, rgba(20,241,255,0.10), transparent 45%),
        radial-gradient(circle at 82% 18%, rgba(255,91,122,0.07), transparent 45%),
        repeating-linear-gradient(
            0deg,
            rgba(20,241,255,0.05) 0px,
            rgba(20,241,255,0.05) 1px,
            transparent 1px,
            transparent 44px
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
      margin-bottom:1.2rem;
    }

    .status-bar {
      display:flex;
      justify-content:space-between;
      gap:10px;
      padding:.65rem .75rem;
      border:1px solid var(--border);
      border-radius:16px;
      background: rgba(10,15,25,.65);
      margin-bottom:1.2rem;
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
      box-shadow: 0 0 10px rgba(20,241,255,.6);
      animation: blink 2.0s infinite;
    }

    @keyframes blink {
      0% { opacity:.35; transform:scale(.95); }
      50% { opacity:1; transform:scale(1.15); }
      100% { opacity:.35; transform:scale(.95); }
    }

    .dot.ok { background: var(--ok); box-shadow:0 0 12px rgba(56,245,163,.8); }
    .dot.warn { background: var(--warn); box-shadow:0 0 12px rgba(255,211,106,.8); }
    .dot.bad { background: var(--bad); box-shadow:0 0 12px rgba(255,91,122,.8); }
    .dot.neutral { background: var(--cyan); box-shadow:0 0 12px rgba(20,241,255,.8); }

    .panel {
      border:1px solid var(--border);
      border-radius:18px;
      padding:14px;
      background: var(--panel);
      box-shadow:0 0 28px rgba(20,241,255,.08);
      margin-bottom:1rem;
    }

    .panel h3 {
      margin:0 0 .5rem 0;
      color:#E5EEFF;
      letter-spacing:.08em;
    }

    /* Radar widget */
    .radar-wrap {
      position: relative;
      width: 100%;
      height: 220px;
      border-radius: 18px;
      border: 1px solid rgba(20,241,255,.35);
      overflow: hidden;
      background:
        radial-gradient(circle at center, rgba(20,241,255,0.12), transparent 60%),
        radial-gradient(circle at center, rgba(20,241,255,0.10), transparent 42%),
        repeating-radial-gradient(circle at center,
          rgba(20,241,255,0.10) 0px,
          rgba(20,241,255,0.10) 1px,
          transparent 1px,
          transparent 34px
        ),
        rgba(5,7,12,.55);
      box-shadow: 0 0 26px rgba(20,241,255,.08);
    }

    .radar-grid {
      position:absolute; inset:0;
      background:
        linear-gradient(transparent 49%, rgba(20,241,255,.12) 50%, transparent 51%),
        linear-gradient(90deg, transparent 49%, rgba(20,241,255,.12) 50%, transparent 51%);
      opacity:.6;
      mix-blend-mode: screen;
    }

    .radar-sweep {
      position:absolute;
      width: 520px;
      height: 520px;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      border-radius:50%;
      background: conic-gradient(from 0deg,
        rgba(20,241,255,0.0) 0deg,
        rgba(20,241,255,0.0) 300deg,
        rgba(20,241,255,0.12) 330deg,
        rgba(20,241,255,0.45) 350deg,
        rgba(20,241,255,0.0) 360deg
      );
      animation: sweep 3.4s linear infinite;
      filter: blur(.2px);
      opacity: .85;
    }

    @keyframes sweep {
      from { transform: translate(-50%, -50%) rotate(0deg); }
      to { transform: translate(-50%, -50%) rotate(360deg); }
    }

    .radar-label {
      position:absolute;
      left:12px; top:10px;
      color: rgba(20,241,255,.9);
      font-weight: 800;
      letter-spacing:.18em;
      font-size:.85rem;
      text-shadow: 0 0 12px rgba(20,241,255,.2);
    }

    .radar-meta {
      position:absolute;
      right:12px; bottom:10px;
      color: rgba(139,163,199,.95);
      font-size:.80rem;
      letter-spacing:.12em;
    }

    .radar-blip {
      position:absolute;
      width:10px; height:10px;
      border-radius:50%;
      background: rgba(20,241,255,.95);
      box-shadow: 0 0 14px rgba(20,241,255,.7);
      animation: blip 2.7s infinite;
      opacity:.85;
    }
    @keyframes blip {
      0% { transform: scale(.6); opacity:.35; }
      50% { transform: scale(1.4); opacity:1; }
      100% { transform: scale(.6); opacity:.35; }
    }
    </style>
    """, unsafe_allow_html=True)


def verdict_to_class(v: str) -> Tuple[str, str]:
    v = (v or "").strip().upper()
    if v == "PASS":
        return "ok", "PASS"
    if v == "FAIL":
        return "bad", "FAIL"
    return "warn", "UNKNOWN"


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

    status = compute_status()

    fusion_class, fusion_label = verdict_to_class(status["fusion_core_regression"])
    ready_class, ready_label = verdict_to_class(status["demo_readiness_gate"])
    pack_class, pack_label = verdict_to_class(status["demo_pack_gate"])

    overall = status["overall"]
    if overall == "READY":
        overall_class = "ok"
    elif overall == "DEGRADED":
        overall_class = "bad"
    else:
        overall_class = "warn"

    # Status Bar (reactive)
    st.markdown(f"""
    <div class="status-bar">
        <div class="pill"><div class="dot {overall_class}"></div>POSTURE: {overall}</div>
        <div class="pill"><div class="dot {fusion_class}"></div>FUSION CORE: {fusion_label}</div>
        <div class="pill"><div class="dot {ready_class}"></div>READINESS GATE: {ready_label}</div>
        <div class="pill"><div class="dot {pack_class}"></div>DEMO PACK: {pack_label}</div>
        <div class="pill"><div class="dot neutral"></div>DEMO LOCK: {"ON" if status["demo_lock"] else "OFF"}</div>
    </div>
    """, unsafe_allow_html=True)

    if is_demo_locked():
        st.warning(demo_lock_banner())

    # Load artifacts (read-only)
    commander = read_txt(BRIEFS / "commander_brief_latest.txt")
    operator = read_txt(BRIEFS / "week3_operator_summary_latest.txt")
    legal = read_txt(BRIEFS / "legal_case_snapshot_latest.txt")
    readiness_txt = read_txt(VALIDATION / "week3_demo_readiness_gate_latest.txt")

    # HUD Layout
    left, right = st.columns([1.35, 1])

    with left:
        # Radar panel
        st.markdown('<div class="panel"><h3>TACTICAL RADAR</h3></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="radar-wrap">
          <div class="radar-label">OBASI RADAR / SENSOR LATTICE</div>
          <div class="radar-grid"></div>
          <div class="radar-sweep"></div>

          <!-- Blips (static positions for demo feel) -->
          <div class="radar-blip" style="left:18%; top:62%;"></div>
          <div class="radar-blip" style="left:42%; top:28%; animation-delay:.6s;"></div>
          <div class="radar-blip" style="left:68%; top:44%; animation-delay:1.2s;"></div>
          <div class="radar-blip" style="left:78%; top:70%; animation-delay:1.8s;"></div>

          <div class="radar-meta">UTC {utc_now().split('T')[1][:8]} • POSTURE {overall}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="panel"><h3>Commander Brief</h3></div>', unsafe_allow_html=True)
        st.text_area("commander", commander or "Commander brief missing.", height=420)

    with right:
        st.markdown('<div class="panel"><h3>Operator Summary</h3></div>', unsafe_allow_html=True)
        st.text_area("operator", operator or "Operator summary missing.", height=200)

        st.markdown('<div class="panel"><h3>Legal Snapshot</h3></div>', unsafe_allow_html=True)
        st.text_area("legal", legal or "Legal snapshot missing.", height=200)

        st.markdown('<div class="panel"><h3>Demo Readiness Gate</h3></div>', unsafe_allow_html=True)
        st.text_area("readiness", readiness_txt or "Readiness gate missing.", height=260)

    st.caption(f"Last refresh (UTC): {utc_now()} | Repo: {ROOT} | Read-only demo display.")


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

