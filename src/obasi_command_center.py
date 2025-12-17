# src/obasi_command_center.py
"""
OBASI COMMAND CENTER (Module 5B — Visual Elevation Pass)
- Premium HUD styling (Batman/Iron-Man command center)
- READ-ONLY: no mutation, no baselines
- Pulls existing artifacts from docs/briefs and docs/validation

Run:
  streamlit run src/obasi_command_center.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

# Optional demo lock (expected in your repo)
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:  # pragma: no cover
    def is_demo_locked() -> bool:
        return False

    def demo_lock_banner() -> str:
        return "DEMO MODE ACTIVE — READ ONLY\nNo baselines updated. No training. No mutation.\nAssessment is probabilistic and bounded; operator judgment applies."


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BRIEFS = DOCS / "briefs"
VALIDATION = DOCS / "validation"


# ----------------------------
# Helpers
# ----------------------------
def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_json(p: Path) -> dict:
    try:
        return json.loads(_read_text(p) or "{}")
    except Exception:
        return {}


def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _verdict_color(v: str) -> str:
    v = (v or "").strip().upper()
    if v == "PASS":
        return "ok"
    if v == "FAIL":
        return "bad"
    return "warn"


def _pick_verdict(payload: dict) -> str:
    # Try multiple common keys
    for k in ("verdict", "status", "result"):
        if isinstance(payload, dict) and k in payload and isinstance(payload[k], str):
            return payload[k].strip().upper()
    return "UNKNOWN"


def _safe_snip(s: str, max_chars: int = 1200) -> str:
    s = s or ""
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "\n…(truncated)…"


# ----------------------------
# HUD Styling
# ----------------------------
def _inject_hud_css() -> None:
    st.markdown(
        """
<style>
:root{
  --bg0:#070A0F;
  --bg1:#0B1220;
  --bg2:#0E1A2E;
  --panel:#0B1220;
  --panel2:#0A1324;
  --line:#1D2B45;
  --text:#DDE7FF;
  --muted:#8BA3C7;
  --cyan:#14F1FF;
  --cyan2:#00B7FF;
  --amber:#FFB020;
  --red:#FF3B3B;
  --green:#3CFF9A;
  --shadow: 0 12px 40px rgba(0,0,0,.55);
}

/* App background */
.stApp {
  background: radial-gradient(1200px 800px at 15% 20%, rgba(20,241,255,.09), rgba(0,0,0,0) 55%),
              radial-gradient(900px 700px at 85% 30%, rgba(0,183,255,.08), rgba(0,0,0,0) 55%),
              linear-gradient(180deg, var(--bg0), var(--bg1) 30%, var(--bg0));
  color: var(--text);
}

/* Remove wide white margins vibe */
.block-container{
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1250px;
}

/* Hide Streamlit header/footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Title HUD */
.hud-title{
  text-align:center;
  font-weight: 900;
  letter-spacing: .22em;
  text-transform: uppercase;
  font-size: 2.4rem;
  margin: .4rem 0 .25rem 0;
  color: var(--cyan);
  text-shadow: 0 0 18px rgba(20,241,255,.22);
}
.hud-sub{
  text-align:center;
  font-size: .95rem;
  color: var(--muted);
  letter-spacing: .08em;
  margin-bottom: .8rem;
}

/* Banner panel */
.banner{
  border: 1px solid rgba(20,241,255,.35);
  background: linear-gradient(180deg, rgba(20,241,255,.08), rgba(0,0,0,0));
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}
.banner:before{
  content:"";
  position:absolute;
  inset:-80px -60px auto auto;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(20,241,255,.18), rgba(0,0,0,0) 70%);
  filter: blur(2px);
}
.banner .label{
  font-size:.75rem;
  text-transform:uppercase;
  letter-spacing:.18em;
  color: var(--muted);
  margin-bottom: 4px;
}
.banner .msg{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  white-space: pre-wrap;
  color: var(--text);
  line-height: 1.35;
}

/* Chips */
.chips{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 14px 0 18px 0;
}
.chip{
  border: 1px solid rgba(221,231,255,.14);
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(0,0,0,0));
  border-radius: 999px;
  padding: 10px 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
  min-width: 220px;
}
.chip .k{
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .18em;
  color: var(--muted);
}
.chip .v{
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: .04em;
  margin-top: 4px;
}

/* Status dots */
.dot{
  display:inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  box-shadow: 0 0 16px rgba(255,255,255,.12);
}
.dot.ok{ background: var(--green); box-shadow: 0 0 18px rgba(60,255,154,.25); }
.dot.bad{ background: var(--red);   box-shadow: 0 0 18px rgba(255,59,59,.22); }
.dot.warn{ background: var(--amber); box-shadow: 0 0 18px rgba(255,176,32,.22); }

/* Panel cards */
.panel{
  border: 1px solid rgba(20,241,255,.16);
  background: linear-gradient(180deg, rgba(11,18,32,.92), rgba(7,10,15,.86));
  border-radius: 18px;
  padding: 14px 16px 12px 16px;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}
.panel:after{
  content:"";
  position:absolute;
  inset: 0;
  background: repeating-linear-gradient(
    180deg,
    rgba(255,255,255,.02) 0px,
    rgba(255,255,255,.02) 1px,
    rgba(0,0,0,0) 2px,
    rgba(0,0,0,0) 6px
  );
  opacity: .35;
  pointer-events: none;
}
.panel h3{
  margin: 0 0 10px 0;
  padding: 0;
}
.panel-title{
  display:flex;
  align-items:center;
  gap: 10px;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--text);
}
.panel-title .icon{
  font-size: 1.05rem;
  filter: drop-shadow(0 0 10px rgba(20,241,255,.18));
}
.panel-sub{
  font-size: .82rem;
  color: var(--muted);
  margin-top: 2px;
}

/* Code blocks darker */
.stCodeBlock, pre {
  background: rgba(5,8,12,.65) !important;
  border: 1px solid rgba(221,231,255,.10) !important;
}

/* Expanders premium */
details {
  border-radius: 14px !important;
  border: 1px solid rgba(221,231,255,.12) !important;
  background: rgba(10,19,36,.45) !important;
}

/* Buttons */
.stButton button{
  border-radius: 999px;
  border: 1px solid rgba(20,241,255,.35);
  background: linear-gradient(180deg, rgba(20,241,255,.12), rgba(0,0,0,0));
  color: var(--text);
  box-shadow: 0 12px 30px rgba(0,0,0,.35);
}
.stButton button:hover{
  border: 1px solid rgba(20,241,255,.55);
  transform: translateY(-1px);
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(5,8,12,.88), rgba(7,10,15,.82));
  border-right: 1px solid rgba(20,241,255,.12);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _hud_header() -> None:
    st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hud-sub">Spectral Owl • Week-3 Demo • Read-Only HUD</div>', unsafe_allow_html=True)


def _banner_block(text: str) -> None:
    st.markdown(
        f"""
<div class="banner">
  <div class="label">DEMO SAFETY / READ-ONLY</div>
  <div class="msg">{text}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _chips(system_status: str, mode: str, env: str, generated_at: str) -> None:
    sys_class = _verdict_color(system_status)
    st.markdown(
        f"""
<div class="chips">
  <div class="chip">
    <div class="k">System Status</div>
    <div class="v"><span class="dot {sys_class}"></span>{system_status}</div>
  </div>
  <div class="chip">
    <div class="k">Mode</div>
    <div class="v">{mode}</div>
  </div>
  <div class="chip">
    <div class="k">Environment</div>
    <div class="v">{env}</div>
  </div>
  <div class="chip">
    <div class="k">Generated (UTC)</div>
    <div class="v" style="font-size:1.05rem;font-weight:800;">{generated_at}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _panel_open(title: str, subtitle: str = "", icon: str = "◈") -> None:
    st.markdown(
        f"""
<div class="panel">
  <div class="panel-title"><span class="icon">{icon}</span>{title}</div>
  <div class="panel-sub">{subtitle}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# Load artifacts
# ----------------------------
def load_artifacts() -> dict:
    # Expected "latest" files (your current output convention)
    paths = {
        "commander_txt": BRIEFS / "commander_brief_latest.txt",
        "commander_json": BRIEFS / "commander_brief_latest.json",
        "operator_txt": BRIEFS / "week3_operator_summary_latest.txt",
        "legal_txt": BRIEFS / "legal_case_snapshot_latest.txt",
        "legal_json": BRIEFS / "legal_case_snapshot_latest.json",
        "narrative_txt": BRIEFS / "week3_demo_narrative_latest.txt",
        "mobile_manifest": BRIEFS / "mobile_enjoy_manifest_latest.json",
        "fusion_reg_json": VALIDATION / "fusion_core_regression_latest.json",
        "fusion_reg_txt": VALIDATION / "fusion_core_regression_latest.txt",
        "demo_gate_json": VALIDATION / "week3_demo_readiness_gate_latest.json",
        "demo_gate_txt": VALIDATION / "week3_demo_readiness_gate_latest.txt",
        "demo_pack_gate_json": VALIDATION / "week3_demo_pack_gate_latest.json",
    }

    res = {"paths": {k: str(v) for k, v in paths.items()}, "present": {}, "payloads": {}}

    for k, p in paths.items():
        res["present"][k] = _exists(p)

    # Read JSON payloads
    for k in ("commander_json", "legal_json", "mobile_manifest", "fusion_reg_json", "demo_gate_json", "demo_pack_gate_json"):
        p = paths[k]
        res["payloads"][k] = _read_json(p) if _exists(p) else {}

    # Read text payloads
    for k in ("commander_txt", "operator_txt", "legal_txt", "narrative_txt", "fusion_reg_txt", "demo_gate_txt"):
        p = paths[k]
        res["payloads"][k] = _read_text(p) if _exists(p) else ""

    # Determine system status
    demo_gate = res["payloads"].get("demo_gate_json", {}) or {}
    verdict = _pick_verdict(demo_gate)
    if verdict == "UNKNOWN":
        # fall back: fusion regression
        verdict = _pick_verdict(res["payloads"].get("fusion_reg_json", {}) or {})
    res["system_status"] = verdict if verdict else "UNKNOWN"

    res["generated_at_utc"] = _now_utc_iso()
    res["demo_locked"] = bool(is_demo_locked())
    return res


# ----------------------------
# UI
# ----------------------------
def main() -> int:
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_hud_css()
    _hud_header()

    data = load_artifacts()

    # Banner: always show for demo posture
    banner = demo_lock_banner() if data["demo_locked"] else "READ-ONLY HUD\nAssessment is probabilistic and bounded; operator judgment applies."
    _banner_block(banner.replace("\n", "<br/>"))

    # Chips
    sys_status = data.get("system_status", "UNKNOWN")
    mode = "DEMO LOCKED" if data.get("demo_locked") else "READ ONLY"
    env = "LOCAL HUD"
    gen = data.get("generated_at_utc", _now_utc_iso())
    _chips(sys_status, mode, env, gen)

    # Sidebar controls (pure UI)
    st.sidebar.markdown("### Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (demo)", value=False)
    refresh_secs = st.sidebar.slider("Refresh interval (seconds)", 5, 60, 15, step=5)
    compact = st.sidebar.checkbox("Compact text (less whitespace)", value=True)
    show_json = st.sidebar.checkbox("Show JSON panels", value=True)
    show_paths = st.sidebar.checkbox("Show artifact paths (operator only)", value=False)

    if st.sidebar.button("Refresh Now"):
        st.rerun()

    if auto_refresh:
        st.sidebar.caption("Auto-refresh enabled.")
        st.markdown(
            f"""
<script>
setTimeout(function() {{
  window.location.reload();
}}, {int(refresh_secs)*1000});
</script>
            """,
            unsafe_allow_html=True,
        )

    if show_paths:
        with st.sidebar.expander("Artifact Paths", expanded=False):
            st.code(json.dumps(data["paths"], indent=2), language="json")

    # Layout columns
    left, right = st.columns(2, gap="large")

    # ----------------------------
    # Commander View (Left)
    # ----------------------------
    with left:
        st.markdown("### 🧠 Commander View")
        st.caption("Bounded, commander-safe outputs. No inference beyond available artifacts.")

        # Commander Brief
        commander_txt = data["payloads"].get("commander_txt", "")
        if commander_txt:
            st.markdown("#### Commander Brief (TXT)")
            st.code(_safe_snip(commander_txt, 2600) if compact else commander_txt, language="markdown")
        else:
            st.warning("Commander brief not found (docs/briefs/commander_brief_latest.txt). Run the orchestrator once.")

        # Demo Narrative
        narrative_txt = data["payloads"].get("narrative_txt", "")
        with st.expander("Week-3 Demo Narrative (Commander-Safe)", expanded=True):
            if narrative_txt:
                st.code(_safe_snip(narrative_txt, 3200) if compact else narrative_txt, language="markdown")
            else:
                st.info("Demo narrative not found yet (docs/briefs/week3_demo_narrative_latest.txt).")

        # Legal Snapshot
        legal_txt = data["payloads"].get("legal_txt", "")
        with st.expander("Legal Case Snapshot (Demo / Training)", expanded=False):
            if legal_txt:
                st.code(_safe_snip(legal_txt, 3200) if compact else legal_txt, language="markdown")
            else:
                st.info("Legal snapshot not found yet (docs/briefs/legal_case_snapshot_latest.txt).")

        # Operator summary (useful in commander view during demo)
        operator_txt = data["payloads"].get("operator_txt", "")
        with st.expander("Operator Summary (Week-3)", expanded=False):
            if operator_txt:
                st.code(_safe_snip(operator_txt, 2400) if compact else operator_txt, language="markdown")
            else:
                st.info("Operator summary not found yet (docs/briefs/week3_operator_summary_latest.txt).")

    # ----------------------------
    # System & Validation (Right)
    # ----------------------------
    with right:
        st.markdown("### 🛡️ System & Validation")
        st.caption("Gate status, regression posture, and demo readiness proof.")

        # Demo readiness gate
        demo_gate_json = data["payloads"].get("demo_gate_json", {}) or {}
        dg_verdict = _pick_verdict(demo_gate_json)
        dg_class = _verdict_color(dg_verdict)
        st.markdown(
            f"""
<div class="panel" style="margin-bottom: 14px;">
  <div class="panel-title"><span class="icon">⛓️</span>Demo Readiness Gate</div>
  <div class="panel-sub"><span class="dot {dg_class}"></span>Verdict: <b>{dg_verdict}</b></div>
</div>
            """,
            unsafe_allow_html=True,
        )

        demo_gate_txt = data["payloads"].get("demo_gate_txt", "")
        with st.expander("Readiness Gate (TXT)", expanded=False):
            if demo_gate_txt:
                st.code(_safe_snip(demo_gate_txt, 3600) if compact else demo_gate_txt, language="markdown")
            else:
                st.info("Readiness gate TXT not found (docs/validation/week3_demo_readiness_gate_latest.txt).")

        # Fusion core regression
        fusion_reg = data["payloads"].get("fusion_reg_json", {}) or {}
        fr_verdict = _pick_verdict(fusion_reg)
        fr_class = _verdict_color(fr_verdict)
        st.markdown(
            f"""
<div class="panel" style="margin-bottom: 14px;">
  <div class="panel-title"><span class="icon">🧪</span>Fusion Core Regression</div>
  <div class="panel-sub"><span class="dot {fr_class}"></span>Verdict: <b>{fr_verdict}</b></div>
</div>
            """,
            unsafe_allow_html=True,
        )

        fusion_reg_txt = data["payloads"].get("fusion_reg_txt", "")
        with st.expander("Fusion Regression (TXT)", expanded=False):
            if fusion_reg_txt:
                st.code(_safe_snip(fusion_reg_txt, 3600) if compact else fusion_reg_txt, language="markdown")
            else:
                st.info("Fusion regression TXT not found (docs/validation/fusion_core_regression_latest.txt).")

        # Mobile manifest
        mobile_manifest = data["payloads"].get("mobile_manifest", {}) or {}
        with st.expander("Mobile Enjoy Manifest (JSON)", expanded=False):
            if mobile_manifest:
                st.json(mobile_manifest)
            else:
                st.info("Mobile manifest not found (docs/briefs/mobile_enjoy_manifest_latest.json).")

        # Optional JSON panels
        if show_json:
            with st.expander("Commander Brief (JSON envelope)", expanded=False):
                cmd_json = data["payloads"].get("commander_json", {}) or {}
                if cmd_json:
                    st.json(cmd_json)
                else:
                    st.info("Commander brief JSON not found (docs/briefs/commander_brief_latest.json).")

            with st.expander("Legal Snapshot (JSON)", expanded=False):
                leg_json = data["payloads"].get("legal_json", {}) or {}
                if leg_json:
                    st.json(leg_json)
                else:
                    st.info("Legal snapshot JSON not found (docs/briefs/legal_case_snapshot_latest.json).")

    # Footer cue (cinematic but factual)
    st.markdown("---")
    st.caption("OBASI HUD • Demo-Locked • Read-Only • Operator judgment applies.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

