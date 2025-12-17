from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from demo_lock import is_demo_locked, demo_lock_banner

BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

# Artifacts (best-effort)
P_COMMANDER_TXT = BRIEFS_DIR / "commander_brief_latest.txt"
P_OPERATOR_SUMMARY = BRIEFS_DIR / "week3_operator_summary_latest.txt"
P_LEGAL_TXT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
P_NARRATIVE = BRIEFS_DIR / "week3_demo_narrative_latest.txt"
P_SHARI_PACKET_TXT = BRIEFS_DIR / "week3_shari_demo_packet_latest.txt"
P_MOBILE_MANIFEST = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"

P_READINESS_TXT = VALIDATION_DIR / "week3_demo_readiness_gate_latest.txt"
P_REGRESSION_TXT = VALIDATION_DIR / "fusion_core_regression_latest.txt"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_txt_best_effort(p: Path, default: str = "Unavailable.", max_chars: int = 120000) -> str:
    try:
        if not p.exists():
            return default
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return default


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _present(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _status_badge(present: bool) -> str:
    return "🟢 READY" if present else "🔴 MISSING"


def _hud_css() -> str:
    # Dark, high-contrast “command center” aesthetic (no external assets)
    return """
<style>
:root {
  --bg0: #06080d;
  --bg1: #0b1020;
  --panel: rgba(12, 18, 34, 0.75);
  --panel2: rgba(10, 14, 24, 0.85);
  --line: rgba(76, 255, 226, 0.18);
  --glow: rgba(76, 255, 226, 0.25);
  --text: rgba(234, 244, 255, 0.95);
  --muted: rgba(234, 244, 255, 0.70);
  --warn: rgba(255, 201, 77, 0.95);
  --bad: rgba(255, 90, 90, 0.95);
  --ok: rgba(120, 255, 205, 0.95);
}

/* Page background grid */
.stApp {
  background:
    radial-gradient(1200px 700px at 10% 10%, rgba(76,255,226,0.10), transparent 55%),
    radial-gradient(900px 600px at 90% 15%, rgba(120,200,255,0.08), transparent 55%),
    linear-gradient(180deg, var(--bg0), var(--bg1));
  color: var(--text);
}

.block-container { padding-top: 1.1rem; }

.hud-header {
  border: 1px solid var(--line);
  background: linear-gradient(135deg, rgba(76,255,226,0.07), rgba(120,200,255,0.05));
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 0 40px rgba(0,0,0,0.35);
}

.hud-title {
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0;
  font-size: 20px;
}

.hud-sub {
  margin: 6px 0 0 0;
  color: var(--muted);
  font-size: 13px;
}

.hud-pill {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(12,18,34,0.7);
  color: var(--text);
  font-size: 12px;
  margin-right: 8px;
}

.panel {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 0 30px rgba(0,0,0,0.30);
}

.panel-title {
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
}

.kpi {
  border: 1px solid rgba(76,255,226,0.22);
  background: var(--panel2);
  border-radius: 14px;
  padding: 12px 12px;
}

.kpi .label {
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.kpi .value {
  font-size: 22px;
  font-weight: 800;
}

.divider {
  height: 1px;
  background: var(--line);
  margin: 10px 0;
}

.monospace {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12.5px;
  white-space: pre-wrap;
  color: var(--text);
}

.badge-ok { color: var(--ok); font-weight: 800; }
.badge-warn { color: var(--warn); font-weight: 800; }
.badge-bad { color: var(--bad); font-weight: 800; }

.scanline {
  position: relative;
  overflow: hidden;
}
.scanline:after {
  content: "";
  position: absolute;
  top: -40%;
  left: -10%;
  width: 120%;
  height: 60%;
  background: linear-gradient(90deg, transparent, rgba(76,255,226,0.06), transparent);
  transform: rotate(6deg);
  animation: sweep 5.5s ease-in-out infinite;
}
@keyframes sweep {
  0% { transform: translateY(-10%) rotate(6deg); opacity: 0.0; }
  20% { opacity: 0.65; }
  50% { transform: translateY(220%) rotate(6deg); opacity: 0.30; }
  100% { transform: translateY(220%) rotate(6deg); opacity: 0.0; }
}
</style>
"""


def main() -> None:
    st.set_page_config(
        page_title="GLL | Obasi Command Center (Demo)",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_hud_css(), unsafe_allow_html=True)

    # HEADER
    demo_locked = is_demo_locked()
    lock_text = "DEMO LOCK: ON (READ-ONLY)" if demo_locked else "DEMO LOCK: OFF"
    lock_class = "badge-ok" if demo_locked else "badge-warn"

    st.markdown(
        f"""
<div class="hud-header scanline">
  <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px;">
    <div>
      <div class="hud-title">OBASI COMMAND CENTER — GHOST LANTERN LABS</div>
      <div class="hud-sub">Futuristic demo shell • bounded outputs • survivable without perfect inputs • generated_at_utc: {_utc_now_iso()}</div>
      <div style="margin-top:10px;">
        <span class="hud-pill"><span class="{lock_class}">{lock_text}</span></span>
        <span class="hud-pill">MODE: WEEK-3 DEMO</span>
        <span class="hud-pill">RULE: operator judgment applies</span>
      </div>
    </div>
    <div style="text-align:right; min-width:260px;">
      <div class="hud-sub" style="margin:0;">Spectral Owl: <span class="badge-ok">ONLINE</span></div>
      <div class="hud-sub" style="margin:0;">Integrity: <span class="badge-ok">GATED</span></div>
      <div class="hud-sub" style="margin:0;">Demo Readiness: <span class="badge-ok">TARGET = PASS</span></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if demo_locked:
        st.info(demo_lock_banner())

    st.sidebar.markdown("### Demo Controls")
    st.sidebar.caption("This UI is read-only. It only renders the latest artifacts.")
    show_previews = st.sidebar.toggle("Show previews", value=True)
    max_chars = st.sidebar.slider("Max text length", 2000, 60000, 20000, step=1000)

    st.sidebar.markdown("### Quick Launch")
    st.sidebar.code(
        "streamlit run src/week3_demo_gui.py\n"
        "python src/week3_shari_demo_packet.py\n"
        "python src/week3_demo_readiness_gate.py",
        language="bash",
    )

    # KPI ROW
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="kpi"><div class="label">Commander Brief</div>'
                    f'<div class="value">{_status_badge(_present(P_COMMANDER_TXT))}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi"><div class="label">Legal Snapshot</div>'
                    f'<div class="value">{_status_badge(_present(P_LEGAL_TXT))}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi"><div class="label">Readiness Gate</div>'
                    f'<div class="value">{_status_badge(_present(P_READINESS_TXT))}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi"><div class="label">Mobile Enjoy Manifest</div>'
                    f'<div class="value">{_status_badge(_present(P_MOBILE_MANIFEST))}</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # MAIN TABS
    tabs = st.tabs(
        [
            "🛰️ Commander Brief",
            "⚖️ Legal Snapshot (Shari Hook)",
            "✅ Operator Summary",
            "🧪 Demo Readiness Gate",
            "📦 Shari Demo Packet",
            "📱 Mobile Enjoy Mode",
            "🧭 Demo Narrative",
        ]
    )

    # Tab 1 — Commander Brief
    with tabs[0]:
        st.markdown("<div class='panel'><div class='panel-title'>Commander Brief (bounded)</div>", unsafe_allow_html=True)
        txt = _read_txt_best_effort(P_COMMANDER_TXT, default="Commander brief not found.", max_chars=max_chars)
        st.markdown(f"<div class='monospace'>{txt}</div></div>", unsafe_allow_html=True)

    # Tab 2 — Legal Snapshot
    with tabs[1]:
        st.markdown("<div class='panel'><div class='panel-title'>Legal Case Snapshot (demo / training)</div>", unsafe_allow_html=True)
        txt = _read_txt_best_effort(P_LEGAL_TXT, default="Legal snapshot not found.", max_chars=max_chars)
        st.markdown(f"<div class='monospace'>{txt}</div></div>", unsafe_allow_html=True)

    # Tab 3 — Operator Summary
    with tabs[2]:
        st.markdown("<div class='panel'><div class='panel-title'>Operator Summary (10-second PASS)</div>", unsafe_allow_html=True)
        txt = _read_txt_best_effort(P_OPERATOR_SUMMARY, default="Operator summary not found.", max_chars=max_chars)
        st.markdown(f"<div class='monospace'>{txt}</div></div>", unsafe_allow_html=True)

    # Tab 4 — Readiness Gate
    with tabs[3]:
        st.markdown("<div class='panel'><div class='panel-title'>Week-3 Demo Readiness Gate (proof)</div>", unsafe_allow_html=True)
        txt = _read_txt_best_effort(P_READINESS_TXT, default="Readiness gate not found.", max_chars=max_chars)
        st.markdown(f"<div class='monospace'>{txt}</div></div>", unsafe_allow_html=True)

        if show_previews:
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='panel'><div class='panel-title'>Fusion Core Regression (supporting evidence)</div>", unsafe_allow_html=True)
            reg = _read_txt_best_effort(P_REGRESSION_TXT, default="Regression report not found.", max_chars=max_chars)
            st.markdown(f"<div class='monospace'>{reg}</div></div>", unsafe_allow_html=True)

    # Tab 5 — Shari Demo Packet
    with tabs[4]:
        st.markdown("<div class='panel'><div class='panel-title'>Shari Demo Packet (checklist + talking points)</div>", unsafe_allow_html=True)
        txt = _read_txt_best_effort(P_SHARI_PACKET_TXT, default="Packet not found. Run: python src/week3_shari_demo_packet.py", max_chars=max_chars)
        st.markdown(f"<div class='monospace'>{txt}</div></div>", unsafe_allow_html=True)

    # Tab 6 — Mobile Enjoy Mode
    with tabs[5]:
        st.markdown("<div class='panel'><div class='panel-title'>Mobile Enjoy Manifest (read-only paths)</div>", unsafe_allow_html=True)
        manifest = _read_json_best_effort(P_MOBILE_MANIFEST)
        if manifest is None:
            st.markdown("<div class='monospace'>Manifest not found. Run CLI option 76 to generate it.</div></div>", unsafe_allow_html=True)
        else:
            st.json(manifest)
            st.markdown("</div>", unsafe_allow_html=True)

    # Tab 7 — Demo Narrative
    with tabs[6]:
        st.markdown("<div class='panel'><div class='panel-title'>Demo Narrative Control</div>", unsafe_allow_html=True)
        txt = _read_txt_best_effort(P_NARRATIVE, default="Narrative not found.", max_chars=max_chars)
        st.markdown(f"<div class='monospace'>{txt}</div></div>", unsafe_allow_html=True)

    # Footer “Obasi” vibe
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='panel'><div class='panel-title'>Obasi Signal</div>"
        "<div class='monospace'>"
        "OBASI // WATCHFLOOR ONLINE\n"
        "RULES: bounded statements • no attribution • operator judgment applies\n"
        "DEMO: read-only • no baselines • no training • no mutation\n"
        "</div></div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

