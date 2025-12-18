# src/obasi_command_center.py
# Obasi Command Center — premium demo HUD (Streamlit)
# SAFE: read-only, best-effort, never crashes.

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# Path bootstrap (critical for Streamlit)
# Ensures repo root + src/ are importable even if src/ is not a package.
# -----------------------------
_THIS_FILE = Path(__file__).resolve()
SRC_DIR = _THIS_FILE.parent
REPO_ROOT = SRC_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# -----------------------------
# Optional Demo Lock integration (never required)
# -----------------------------
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:

    def is_demo_locked() -> bool:
        return False

    def demo_lock_banner() -> str:
        return ""

# -----------------------------
# Module 10D: Spectral Owl explain wiring (best-effort)
# If missing, the GUI still runs and shows a safe fallback explanation.
# -----------------------------
try:
    from spectral_owl_explain import (
        explain_installation_threat_map,
        explain_commander_brief,
        explain_legal_snapshot,
    )
except Exception:

    def _fallback_explain(name: str) -> Dict[str, str]:
        return {
            "Status": "Unavailable",
            "Reason": f"{name} explainer module not importable in this environment.",
            "Fix": "Ensure src/spectral_owl_explain.py exists and imports are correct. (GUI will still run.)",
            "Operator note": "Assessment is probabilistic and bounded; operator judgment applies.",
        }

    def explain_installation_threat_map() -> Dict[str, str]:
        return _fallback_explain("Threat Map")

    def explain_commander_brief() -> Dict[str, str]:
        return _fallback_explain("Commander Brief")

    def explain_legal_snapshot() -> Dict[str, str]:
        return _fallback_explain("Legal Snapshot")


DOCS = REPO_ROOT / "docs"
BRIEFS = DOCS / "briefs"
BASE_DEF = DOCS / "base_defense"
VALIDATION = DOCS / "validation"
PACKAGES = DOCS / "packages"


# -----------------------------
# Helpers (best-effort, no crash)
# -----------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text_best_effort(p: Path, max_chars: int = 60_000) -> str:
    try:
        if not p.exists():
            return ""
        t = p.read_text(encoding="utf-8", errors="ignore")
        if len(t) > max_chars:
            return t[:max_chars] + "\n\n[TRUNCATED]"
        return t
    except Exception:
        return ""


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def _present(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _file_card(label: str, p: Path, kind: str = "txt") -> None:
    ok = _present(p)
    cols = st.columns([2, 1, 1, 2])
    with cols[0]:
        st.write(f"**{label}**")
        st.caption(str(p))
    with cols[1]:
        st.write("✅" if ok else "—")
    with cols[2]:
        st.write(kind.upper())
    with cols[3]:
        if ok:
            try:
                data = p.read_text(encoding="utf-8", errors="ignore")
                st.download_button("Download", data, file_name=p.name, use_container_width=True)
            except Exception:
                st.write("")


def _hud_css() -> str:
    return """
<style>
html, body, [class*="css"]  {
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}
.stApp {
  background: radial-gradient(1200px 800px at 15% 10%, rgba(0, 255, 209, 0.10), rgba(0,0,0,0)),
              radial-gradient(900px 600px at 85% 0%, rgba(255, 77, 166, 0.08), rgba(0,0,0,0)),
              linear-gradient(180deg, #05070b 0%, #05060a 40%, #02030a 100%);
  color: #d6f7ff;
}
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(2,10,18,0.96), rgba(3,6,14,0.96));
  border-right: 1px solid rgba(0, 255, 209, 0.20);
}
section[data-testid="stSidebar"] * { color: #d6f7ff; }

.hud-card {
  border: 1px solid rgba(0, 255, 209, 0.22);
  background: linear-gradient(180deg, rgba(7, 16, 30, 0.55), rgba(3, 6, 14, 0.55));
  box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset, 0 16px 40px rgba(0,0,0,0.45);
  border-radius: 16px;
  padding: 14px 14px 10px 14px;
}
.hud-title {
  font-size: 14px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: rgba(214, 247, 255, 0.85);
  margin-bottom: 6px;
}
.hud-kpi {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 0.02em;
  margin: 0;
}
.hud-sub {
  font-size: 12px;
  color: rgba(214, 247, 255, 0.70);
  margin-top: -2px;
}
.hud-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(0,255,209,0.35), rgba(255,77,166,0.18), rgba(0,0,0,0));
  margin: 10px 0 8px 0;
}
.stButton > button {
  border-radius: 12px !important;
  border: 1px solid rgba(0, 255, 209, 0.30) !important;
  background: linear-gradient(180deg, rgba(0, 255, 209, 0.10), rgba(0, 255, 209, 0.03)) !important;
  color: #d6f7ff !important;
  font-weight: 700 !important;
}
.stButton > button:hover {
  border: 1px solid rgba(255, 77, 166, 0.35) !important;
  background: linear-gradient(180deg, rgba(255, 77, 166, 0.14), rgba(0, 255, 209, 0.06)) !important;
}
details {
  border: 1px solid rgba(0, 255, 209, 0.18) !important;
  border-radius: 14px !important;
  background: rgba(0,0,0,0.18) !important;
}
pre, code {
  background: rgba(0,0,0,0.32) !important;
  border: 1px solid rgba(0, 255, 209, 0.15) !important;
}
.hud-header {
  border: 1px solid rgba(0,255,209,0.22);
  background: linear-gradient(90deg, rgba(0,255,209,0.08), rgba(255,77,166,0.06), rgba(0,0,0,0));
  border-radius: 18px;
  padding: 14px 16px;
  margin-bottom: 14px;
}
.hud-header h1 { font-size: 24px; margin: 0; letter-spacing: .06em; }
.hud-header p {
  margin: 2px 0 0 0;
  color: rgba(214, 247, 255, 0.72);
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.hud-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,255,209,0.35);
  background: rgba(0,255,209,0.08);
  font-size: 11px;
  letter-spacing: .10em;
  text-transform: uppercase;
  color: rgba(214,247,255,0.88);
}
</style>
"""


def _radar_widget_html(size_px: int = 280) -> str:
    s = int(size_px)
    return f"""
<div style="display:flex; align-items:center; justify-content:center;">
  <div style="
    width:{s}px; height:{s}px; border-radius:50%;
    border:1px solid rgba(0,255,209,0.35);
    background:
      radial-gradient(circle at center, rgba(0,255,209,0.12), rgba(0,0,0,0) 60%),
      repeating-radial-gradient(circle at center, rgba(0,255,209,0.18) 0 1px, rgba(0,0,0,0) 1px 22px),
      repeating-linear-gradient(0deg, rgba(0,255,209,0.10) 0 1px, rgba(0,0,0,0) 1px 22px),
      repeating-linear-gradient(90deg, rgba(0,255,209,0.10) 0 1px, rgba(0,0,0,0) 1px 22px);
    box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset, 0 18px 50px rgba(0,0,0,0.55);
    position:relative;
    overflow:hidden;
  ">
    <div style="
      position:absolute; inset:-20%;
      background: conic-gradient(from 0deg, rgba(0,255,209,0.0) 0 70%, rgba(0,255,209,0.22) 82%, rgba(0,255,209,0.0) 100%);
      animation: spin 2.8s linear infinite;
      "></div>

    <div style="position:absolute; width:8px; height:8px; border-radius:50%; background:rgba(255,77,166,0.75); left:68%; top:38%;
                box-shadow:0 0 14px rgba(255,77,166,0.8); animation:pulse 1.6s ease-in-out infinite;"></div>
    <div style="position:absolute; width:6px; height:6px; border-radius:50%; background:rgba(0,255,209,0.85); left:28%; top:62%;
                box-shadow:0 0 12px rgba(0,255,209,0.8); animation:pulse 1.9s ease-in-out infinite;"></div>
    <div style="position:absolute; width:5px; height:5px; border-radius:50%; background:rgba(0,255,209,0.7); left:44%; top:24%;
                box-shadow:0 0 10px rgba(0,255,209,0.6); animation:pulse 2.3s ease-in-out infinite;"></div>

    <div style="position:absolute; inset:0; border-radius:50%;
      background: radial-gradient(circle at center, rgba(0,0,0,0) 0 55%, rgba(0,0,0,0.18) 70%, rgba(0,0,0,0.55) 100%);
      pointer-events:none;"></div>
  </div>
</div>

<style>
@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
@keyframes pulse {{
  0%, 100% {{ transform: scale(1); opacity: .65; }}
  50% {{ transform: scale(1.35); opacity: 1; }}
}}
</style>
"""


def _sidebar_explain(title: str, payload: Dict[str, str]) -> None:
    st.sidebar.markdown(f"## 🦉 {title}")
    if is_demo_locked():
        st.sidebar.warning(demo_lock_banner())
    for k, v in payload.items():
        st.sidebar.markdown(f"**{k}**")
        st.sidebar.write(v)


def main() -> int:
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_hud_css(), unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="hud-header">
  <span class="hud-badge">OBASI • COMMAND CENTER</span>
  <h1>Ghost Lantern Labs — Demo War Room</h1>
  <p>Read-only • Bounded outputs • Operator judgment applies • generated_at_utc: {_utc_now_iso()}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    commander_txt = BRIEFS / "commander_brief_latest.txt"
    commander_json = BRIEFS / "commander_brief_latest.json"
    operator_summary = BRIEFS / "week3_operator_summary_latest.txt"
    legal_txt = BRIEFS / "legal_case_snapshot_latest.txt"
    legal_json = BRIEFS / "legal_case_snapshot_latest.json"
    threat_map_txt = BASE_DEF / "installation_threat_map_latest.txt"
    threat_map_json = BASE_DEF / "installation_threat_map_latest.json"
    mobile_manifest = BRIEFS / "mobile_enjoy_manifest_latest.json"
    demo_orchestrator_txt = BRIEFS / "week3_demo_orchestrator_latest.txt"
    demo_readiness_txt = VALIDATION / "week3_demo_readiness_gate_latest.txt"

    commander_head = "\n".join(_read_text_best_effort(commander_txt).splitlines()[:40])
    operator_head = "\n".join(_read_text_best_effort(operator_summary).splitlines()[:18])
    legal_head = "\n".join(_read_text_best_effort(legal_txt).splitlines()[:28])
    readiness_head = "\n".join(_read_text_best_effort(demo_readiness_txt).splitlines()[:32])
    orchestrator_head = "\n".join(_read_text_best_effort(demo_orchestrator_txt).splitlines()[:28])

    threat_j = _read_json_best_effort(threat_map_json) or {}
    posture = str(threat_j.get("posture", "UNKNOWN"))
    band = str(threat_j.get("overall_risk_band", threat_j.get("overall_band", "UNKNOWN")))
    max_score = str(threat_j.get("max_risk_score", "N/A"))

    # Sidebar quick actions
    st.sidebar.markdown("### System")
    st.sidebar.write(f"**Demo lock:** {'✅ ON' if is_demo_locked() else 'OFF'}")
    if is_demo_locked():
        st.sidebar.info(demo_lock_banner())

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Explainers")
    if st.sidebar.button("🦉 Explain Radar / Threat Map", use_container_width=True):
        _sidebar_explain("Threat Map Explanation", explain_installation_threat_map())
    if st.sidebar.button("🦉 Explain Commander Brief", use_container_width=True):
        _sidebar_explain("Commander Brief Explanation", explain_commander_brief())
    if st.sidebar.button("🦉 Explain Legal Snapshot", use_container_width=True):
        _sidebar_explain("Legal Snapshot Explanation", explain_legal_snapshot())

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Artifacts (downloads)")
    _file_card("Commander Brief (TXT)", commander_txt, "txt")
    _file_card("Commander Brief (JSON)", commander_json, "json")
    _file_card("Week-3 Operator Summary (TXT)", operator_summary, "txt")
    _file_card("Legal Snapshot (TXT)", legal_txt, "txt")
    _file_card("Legal Snapshot (JSON)", legal_json, "json")
    _file_card("Threat Map (TXT)", threat_map_txt, "txt")
    _file_card("Threat Map (JSON)", threat_map_json, "json")
    _file_card("Mobile Enjoy Manifest (JSON)", mobile_manifest, "json")

    left, mid, right = st.columns([1.0, 1.25, 1.0], gap="large")

    with left:
        st.markdown('<div class="hud-card">', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">Radar / Installation Threat Map</div>', unsafe_allow_html=True)
        components.html(_radar_widget_html(280), height=310)
        st.markdown('<div class="hud-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="hud-kpi">{band}</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="hud-sub">posture: {posture} • max_risk_score: {max_score}</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Open Threat Map (TXT)", use_container_width=True):
                st.code(_read_text_best_effort(threat_map_txt), language="text")
        with col_b:
            if st.button("Open Threat Map (JSON)", use_container_width=True):
                st.json(_read_json_best_effort(threat_map_json) or {})

        st.markdown("</div>", unsafe_allow_html=True)

    with mid:
        st.markdown('<div class="hud-card">', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">Commander Brief</div>', unsafe_allow_html=True)

        top_cols = st.columns([1, 1, 1])
        with top_cols[0]:
            if st.button("🦉 Explain Commander Brief", use_container_width=True):
                _sidebar_explain("Commander Brief Explanation", explain_commander_brief())
        with top_cols[1]:
            if st.button("Open Brief (TXT)", use_container_width=True):
                st.code(_read_text_best_effort(commander_txt), language="text")
        with top_cols[2]:
            if st.button("Open Brief (JSON)", use_container_width=True):
                st.json(_read_json_best_effort(commander_json) or {})

        with st.expander("Preview (head)", expanded=True):
            if commander_head.strip():
                st.code(commander_head, language="text")
            else:
                st.info("Commander brief not found yet. Generate docs/briefs/commander_brief_latest.*")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="hud-card">', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">Shari Demo • Legal Snapshot</div>', unsafe_allow_html=True)

        rcols = st.columns([1, 1])
        with rcols[0]:
            if st.button("🦉 Explain Legal Snapshot", use_container_width=True):
                _sidebar_explain("Legal Snapshot Explanation", explain_legal_snapshot())
        with rcols[1]:
            if st.button("Open Legal Snapshot (TXT)", use_container_width=True):
                st.code(_read_text_best_effort(legal_txt), language="text")

        with st.expander("Preview (head)", expanded=True):
            if legal_head.strip():
                st.code(legal_head, language="text")
            else:
                st.info("Legal snapshot not found yet. Run: python src/legal_case_snapshot.py")

        st.markdown('<div class="hud-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">Week-3 Operator Summary</div>', unsafe_allow_html=True)
        if operator_head.strip():
            st.code(operator_head, language="text")
        else:
            st.info("Operator summary not found yet. Run: python src/week3_operator_summary.py")

        st.markdown('<div class="hud-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">Demo Readiness / Orchestrator</div>', unsafe_allow_html=True)

        with st.expander("Readiness Gate (head)", expanded=False):
            if readiness_head.strip():
                st.code(readiness_head, language="text")
            else:
                st.info("Readiness gate not found yet. Run: python src/week3_demo_readiness_gate.py")

        with st.expander("Orchestrator (head)", expanded=False):
            if orchestrator_head.strip():
                st.code(orchestrator_head, language="text")
            else:
                st.info("Orchestrator output not found yet. Run: python src/week3_demo_orchestrator.py")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div style="margin-top:14px; padding:10px 12px; border-radius:14px;
            border:1px solid rgba(0,255,209,0.18);
            background: rgba(0,0,0,0.18); color: rgba(214,247,255,0.80);">
  <b>Operator note:</b> This is a demo GUI. It reads existing artifacts and does not mutate baselines.
  <span style="opacity:.8;">Assessment is probabilistic and bounded; operator judgment applies.</span>
</div>
""",
        unsafe_allow_html=True,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

