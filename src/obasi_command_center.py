# src/obasi_command_center.py
from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# Path bootstrap (critical for Streamlit)
# -----------------------------
_THIS_FILE = Path(__file__).resolve()
SRC_DIR = _THIS_FILE.parent
REPO_ROOT = SRC_DIR.parent

# Ensure src/ is importable as a top-level module location
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# -----------------------------
# Spectral Owl explainers (Module 10C)
# -----------------------------
from spectral_owl_explain import (
    explain_installation_threat_map,
    explain_commander_brief,
    explain_legal_snapshot,
)

# -----------------------------
# Repo paths
# -----------------------------
BRIEFS_DIR = REPO_ROOT / "docs" / "briefs"
VALIDATION_DIR = REPO_ROOT / "docs" / "validation"
BASEDEF_DIR = REPO_ROOT / "docs" / "base_defense"


# -----------------------------
# UI config
# -----------------------------
st.set_page_config(
    page_title="Obasi Command Center — Ghost Lantern Labs",
    page_icon="🦉",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text_best_effort(p: Path) -> str:
    try:
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_json_best_effort(p: Path) -> Dict[str, Any]:
    try:
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def _badge(label: str, value: str, tone: str = "neutral") -> str:
    tone_map = {
        "ok": "#22c55e",
        "warn": "#f59e0b",
        "bad": "#ef4444",
        "neutral": "#60a5fa",
        "muted": "#94a3b8",
    }
    c = tone_map.get(tone, tone_map["neutral"])
    return f"""
    <div style="display:inline-flex; gap:8px; align-items:center; padding:8px 10px; border-radius:12px;
                border:1px solid rgba(148,163,184,0.25); background: rgba(2,6,23,0.55);">
        <span style="font-size:12px; color:#94a3b8;">{label}</span>
        <span style="font-weight:700; color:{c};">{value}</span>
    </div>
    """


def _apply_hud_css() -> None:
    st.markdown(
        """
<style>
/* --- Obasi HUD Theme (Batman/Iron-Man vibe) --- */
:root {
  --bg0: #050814;
  --bg1: #0b1024;
  --glass: rgba(2, 6, 23, 0.55);
  --line: rgba(148,163,184,0.18);
  --text: rgba(226,232,240,0.92);
  --muted: rgba(148,163,184,0.86);
  --accent: rgba(56,189,248,0.95);
  --accent2: rgba(34,197,94,0.95);
  --danger: rgba(239,68,68,0.95);
  --warn: rgba(245,158,11,0.95);
}

/* page background */
.stApp {
  background: radial-gradient(1200px 600px at 25% 10%, rgba(56,189,248,0.10), transparent 55%),
              radial-gradient(1000px 700px at 80% 30%, rgba(34,197,94,0.08), transparent 55%),
              radial-gradient(900px 600px at 55% 80%, rgba(239,68,68,0.05), transparent 60%),
              linear-gradient(180deg, var(--bg0), var(--bg1));
  color: var(--text);
}

/* top padding tighten */
.block-container { padding-top: 1.25rem; }

/* sidebar styling */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(2,6,23,0.80), rgba(2,6,23,0.55));
  border-right: 1px solid var(--line);
}

/* cards */
.hud-card {
  border: 1px solid var(--line);
  background: var(--glass);
  border-radius: 18px;
  padding: 16px 16px 12px 16px;
  box-shadow: 0 0 0 1px rgba(56,189,248,0.05) inset, 0 18px 40px rgba(0,0,0,0.35);
}

/* section title */
.hud-title {
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 12px;
  color: rgba(56,189,248,0.92);
  margin-bottom: 10px;
}

/* subtle grid lines */
.hud-grid {
  position: relative;
}
.hud-grid:before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(148,163,184,0.06) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148,163,184,0.06) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: radial-gradient(circle at 20% 25%, black 0%, transparent 55%);
  pointer-events: none;
  border-radius: 18px;
}

/* buttons */
div.stButton > button {
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(56,189,248,0.25) !important;
  background: rgba(2,6,23,0.55) !important;
  color: rgba(226,232,240,0.95) !important;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 0.65rem 0.9rem;
}
div.stButton > button:hover {
  border: 1px solid rgba(56,189,248,0.55) !important;
  box-shadow: 0 0 0 1px rgba(56,189,248,0.08) inset, 0 14px 30px rgba(0,0,0,0.40);
}

/* expanders */
details {
  border: 1px solid var(--line) !important;
  background: rgba(2,6,23,0.45) !important;
  border-radius: 14px !important;
}
summary {
  color: rgba(226,232,240,0.92) !important;
}

/* metric text */
[data-testid="stMetricValue"] { color: rgba(226,232,240,0.96) !important; }
[data-testid="stMetricLabel"] { color: rgba(148,163,184,0.90) !important; }

</style>
        """,
        unsafe_allow_html=True,
    )


def _hud_card(title: str, body_html: str) -> None:
    st.markdown(
        f"""
<div class="hud-card hud-grid">
  <div class="hud-title">{title}</div>
  {body_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def _tone_for_band(band: str) -> str:
    b = (band or "").strip().upper()
    if b in {"LOW", "GREEN", "OK"}:
        return "ok"
    if b in {"GUARDED", "ELEVATED", "AMBER", "YELLOW"}:
        return "warn"
    if b in {"HIGH", "CRITICAL", "RED"}:
        return "bad"
    return "neutral"


def _sidebar_explain(title: str, sections: Dict[str, str]) -> None:
    st.sidebar.markdown(f"## 🦉 {title}")
    # show in stable order if present
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
    for k in order:
        if k in sections:
            st.sidebar.markdown(f"**{k.replace('_',' ').title()}**")
            st.sidebar.write(sections.get(k, ""))


# -----------------------------
# Radar widget (visual only)
# -----------------------------
def _radar_html(size: int = 280) -> str:
    # Pure HTML/CSS radar sweep (no JS libs). Demo-safe.
    return f"""
<div style="width:{size}px; height:{size}px; margin:auto; border-radius:50%;
            background:
              radial-gradient(circle at center, rgba(56,189,248,0.10) 0%, rgba(56,189,248,0.04) 55%, rgba(56,189,248,0.02) 70%, rgba(2,6,23,0.55) 100%),
              repeating-radial-gradient(circle at center, rgba(56,189,248,0.10) 0 1px, transparent 1px 26px),
              repeating-linear-gradient(0deg, rgba(56,189,248,0.08) 0 1px, transparent 1px 28px),
              repeating-linear-gradient(90deg, rgba(56,189,248,0.08) 0 1px, transparent 1px 28px);
            border: 1px solid rgba(56,189,248,0.25);
            box-shadow: 0 0 0 1px rgba(56,189,248,0.05) inset, 0 18px 40px rgba(0,0,0,0.35);
            position: relative; overflow:hidden;">
  <div style="position:absolute; inset:0; border-radius:50%;
              background: conic-gradient(from 0deg, rgba(56,189,248,0.00), rgba(56,189,248,0.00), rgba(56,189,248,0.35), rgba(56,189,248,0.00));
              animation: sweep 2.4s linear infinite;"></div>

  <!-- blips -->
  <div style="position:absolute; left:60%; top:35%; width:8px; height:8px; border-radius:50%;
              background: rgba(34,197,94,0.90); box-shadow: 0 0 12px rgba(34,197,94,0.60);"></div>
  <div style="position:absolute; left:32%; top:58%; width:6px; height:6px; border-radius:50%;
              background: rgba(245,158,11,0.90); box-shadow: 0 0 10px rgba(245,158,11,0.55);"></div>
  <div style="position:absolute; left:48%; top:72%; width:5px; height:5px; border-radius:50%;
              background: rgba(56,189,248,0.90); box-shadow: 0 0 10px rgba(56,189,248,0.55);"></div>

  <div style="position:absolute; inset:12px; border-radius:50%; border:1px dashed rgba(56,189,248,0.20);"></div>
  <div style="position:absolute; inset:44px; border-radius:50%; border:1px dashed rgba(56,189,248,0.18);"></div>

  <div style="position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
              width:6px; height:6px; border-radius:50%; background: rgba(56,189,248,0.95); box-shadow:0 0 14px rgba(56,189,248,0.65);"></div>
</div>

<style>
@keyframes sweep {{
  0% {{ transform: rotate(0deg); opacity: 0.9; }}
  100% {{ transform: rotate(360deg); opacity: 0.9; }}
}}
</style>
"""


def _load_installation_threat_map_txt() -> str:
    # Prefer docs/base_defense path; fallback to briefs if your pipeline writes elsewhere
    candidates = [
        BASEDEF_DIR / "installation_threat_map_latest.txt",
        BRIEFS_DIR / "installation_threat_map_latest.txt",
    ]
    for p in candidates:
        t = _read_text_best_effort(p)
        if t.strip():
            return t
    return ""


def _load_commander_brief_txt() -> str:
    return _read_text_best_effort(BRIEFS_DIR / "commander_brief_latest.txt")


def _load_legal_snapshot_txt() -> str:
    return _read_text_best_effort(BRIEFS_DIR / "legal_case_snapshot_latest.txt")


def _load_demo_orchestrator_status() -> Dict[str, Any]:
    return _read_json_best_effort(BRIEFS_DIR / "week3_demo_orchestrator_latest.json")


def _load_demo_readiness_gate_txt() -> str:
    return _read_text_best_effort(VALIDATION_DIR / "week3_demo_readiness_gate_latest.txt")


def _heat_zone_table_from_threat_map_text(txt: str) -> List[Tuple[str, float, str, str]]:
    """
    Very light parsing of your threat map text format:
      zones:
      - NORTH: risk_score=12.0 band=LOW notes=...
    Returns list of (zone, risk_score, band, notes)
    """
    out: List[Tuple[str, float, str, str]] = []
    if not txt.strip():
        return out

    lines = [ln.strip() for ln in txt.splitlines()]
    in_zones = False
    for ln in lines:
        if ln.lower().startswith("zones:"):
            in_zones = True
            continue
        if not in_zones:
            continue
        if ln.startswith("what_we_can_say:") or ln.startswith("what_we_cannot_say:"):
            break
        if ln.startswith("- "):
            item = ln[2:].strip()
            # expected: "NORTH: risk_score=12.0 band=LOW notes=Routine activity."
            if ":" in item:
                zone, rest = item.split(":", 1)
                zone = zone.strip()
                risk_score = 0.0
                band = ""
                notes = rest.strip()
                try:
                    # pull risk_score=
                    if "risk_score=" in rest:
                        rs_part = rest.split("risk_score=", 1)[1]
                        rs_str = rs_part.split()[0].strip()
                        rs_str = rs_str.replace("band=", "").replace("notes=", "")
                        # Sometimes it's "12.0" or "12.0"
                        risk_score = float(rs_str.split(" ")[0].split("band=")[0].strip().replace(",", ""))
                except Exception:
                    risk_score = 0.0
                try:
                    if "band=" in rest:
                        band = rest.split("band=", 1)[1].split()[0].strip()
                except Exception:
                    band = ""
                # notes best effort
                try:
                    if "notes=" in rest:
                        notes = rest.split("notes=", 1)[1].strip()
                except Exception:
                    notes = rest.strip()
                out.append((zone, risk_score, band, notes))
    return out


def _risk_to_color_name(score: float) -> str:
    # No custom colors in charts; we use text labels and emojis only
    if score >= 70:
        return "🟥"
    if score >= 45:
        return "🟧"
    if score >= 20:
        return "🟨"
    return "🟩"


def main() -> int:
    _apply_hud_css()

    # -----------------------------
    # Header
    # -----------------------------
    st.markdown(
        f"""
<div class="hud-card">
  <div style="display:flex; justify-content:space-between; align-items:flex-end; gap:16px;">
    <div>
      <div style="font-size:28px; font-weight:900; letter-spacing:0.02em;">
        🦉 OBASI COMMAND CENTER
      </div>
      <div style="color: rgba(148,163,184,0.92); margin-top:4px;">
        Read-only • Bounded outputs • Operator judgment applies • generated_at_utc: {_utc_now_iso()}
      </div>
    </div>
    <div style="display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end;">
      {_badge("MODE", "DEMO / READ-ONLY", "warn")}
      {_badge("PROFILE", "OPS", "neutral")}
      {_badge("SYSTEM", "LOCAL", "muted")}
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # -----------------------------
    # Sidebar: System quick actions + explanation drawer
    # -----------------------------
    st.sidebar.markdown("### ⚙️ Demo Controls")
    st.sidebar.caption("These buttons do not mutate baselines. They read existing artifacts only.")

    if st.sidebar.button("🔄 Rerun Demo Orchestrator (local)", use_container_width=True, key="sb_rerun_orchestrator"):
        st.sidebar.warning("This UI does not execute subprocesses. Run it from terminal:")
        st.sidebar.code("python src/week3_demo_orchestrator.py")

    if st.sidebar.button("✅ Check Demo Readiness Gate", use_container_width=True, key="sb_check_readiness"):
        st.sidebar.code("python src/week3_demo_readiness_gate.py")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🦉 Spectral Owl Explanation")
    st.sidebar.caption("Click an Explain button in any panel to populate this drawer.")

    # -----------------------------
    # Layout columns
    # -----------------------------
    left, mid, right = st.columns([1.05, 1.2, 1.05], gap="large")

    # =====================================================
    # LEFT: Radar + Installation Threat Map
    # =====================================================
    with left:
        _hud_card("Radar / Threat Map", "<div></div>")
        components.html(_radar_html(300), height=320)

        threat_txt = _load_installation_threat_map_txt()
        if threat_txt.strip():
            with st.expander("📡 Installation Threat Map (latest)", expanded=True):
                st.code(threat_txt, language="text")
        else:
            st.info("No installation threat map text found yet (expected in docs/base_defense).")

        # Explain button (unique key)
        if st.button("🦉 Explain Radar / Threat Map", use_container_width=True, key="owl_explain_radar_main"):
            _sidebar_explain("Radar / Threat Map", explain_installation_threat_map())

        # Mini “heat” table (safe, no charts)
        zones = _heat_zone_table_from_threat_map_text(threat_txt)
        if zones:
            st.markdown("#### 🔥 Zone Heat (bounded)")
            rows = []
            for (z, score, band, notes) in zones:
                rows.append(
                    {
                        "Zone": z,
                        "Heat": _risk_to_color_name(score),
                        "Risk Score": score,
                        "Band": band,
                        "Notes": notes,
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

    # =====================================================
    # MIDDLE: Commander Brief + Orchestrator Status
    # =====================================================
    with mid:
        orch = _load_demo_orchestrator_status()
        verdict = str(orch.get("verdict", "UNKNOWN"))
        crashes = int(orch.get("crashes", 0) or 0)
        failed = orch.get("failed_steps", []) or []
        tone = "ok" if verdict == "PASS" else "bad" if verdict == "FAIL" else "neutral"

        st.markdown(
            f"""
<div class="hud-card">
  <div class="hud-title">Demo Orchestrator Status</div>
  <div style="display:flex; gap:10px; flex-wrap:wrap;">
    {_badge("VERDICT", verdict, tone)}
    {_badge("CRASHES", str(crashes), "bad" if crashes else "ok")}
    {_badge("FAILED_STEPS", str(len(failed)), "bad" if failed else "ok")}
  </div>
  <div style="margin-top:12px; color: rgba(148,163,184,0.95); font-size:13px;">
    This is your one-button demo health check. If FAIL: fix first failing step, rerun orchestrator.
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        cmd_txt = _load_commander_brief_txt()
        if cmd_txt.strip():
            with st.expander("🧾 Commander Brief (latest)", expanded=True):
                st.code(cmd_txt, language="text")
        else:
            st.warning("Commander brief not found yet: docs/briefs/commander_brief_latest.txt")

        # Explain button (unique key)
        if st.button("🦉 Explain Commander Brief", use_container_width=True, key="owl_explain_commander_main"):
            _sidebar_explain("Commander Brief", explain_commander_brief())

        st.write("")
        gate_txt = _load_demo_readiness_gate_txt()
        if gate_txt.strip():
            with st.expander("✅ Demo Readiness Gate (latest)", expanded=False):
                st.code(gate_txt, language="text")

    # =====================================================
    # RIGHT: Legal Snapshot + Explain + Quick Links
    # =====================================================
    with right:
        _hud_card("Shari Hook / Legal Snapshot", "<div style='color: rgba(148,163,184,0.95); font-size:13px;'>Demo-safe triage artifact for exec storytelling.</div>")

        legal_txt = _load_legal_snapshot_txt()
        if legal_txt.strip():
            with st.expander("⚖️ Legal Case Snapshot (latest)", expanded=True):
                st.code(legal_txt, language="text")
        else:
            st.warning("Legal snapshot not found yet: docs/briefs/legal_case_snapshot_latest.txt")

        # Explain button (unique key)
        if st.button("🦉 Explain Legal Snapshot", use_container_width=True, key="owl_explain_legal_main"):
            _sidebar_explain("Legal Snapshot", explain_legal_snapshot())

        st.write("")
        _hud_card(
            "Quick Artifact Links (local paths)",
            f"""
<div style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas; font-size:12px; color: rgba(148,163,184,0.95); line-height:1.6;">
docs/briefs/commander_brief_latest.txt<br/>
docs/briefs/week3_operator_summary_latest.txt<br/>
docs/briefs/legal_case_snapshot_latest.txt<br/>
docs/briefs/week3_demo_narrative_latest.txt<br/>
docs/briefs/mobile_enjoy_manifest_latest.json<br/>
docs/validation/week3_demo_readiness_gate_latest.txt<br/>
docs/packages/week3_cloud_demo_package_latest.zip
</div>
            """,
        )

    st.write("")
    st.caption("Obasi Command Center is read-only. It visualizes the latest artifacts already generated by your Week-3/Week-7 modules.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

