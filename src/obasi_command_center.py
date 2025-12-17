# src/obasi_command_center.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BRIEFS = DOCS / "briefs"
VALIDATION = DOCS / "validation"
PACKAGES = DOCS / "packages"
BASE_DEFENSE = DOCS / "base_defense"


# -----------------------------
# Utilities (best-effort only)
# -----------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(p: Path, max_chars: int = 8000) -> str:
    try:
        if not p.exists():
            return ""
        t = p.read_text(encoding="utf-8", errors="replace")
        return t[:max_chars]
    except Exception:
        return ""


def _read_json(p: Path) -> Dict[str, Any]:
    try:
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def _safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def _demo_lock_banner_best_effort() -> str:
    try:
        from demo_lock import is_demo_locked, demo_lock_banner  # type: ignore

        if bool(is_demo_locked()):
            return str(demo_lock_banner())
        return ""
    except Exception:
        return ""


def _first_existing(*paths: Path) -> Optional[Path]:
    for p in paths:
        try:
            if p.exists():
                return p
        except Exception:
            pass
    return None


def _badge(verdict: str) -> Tuple[str, str]:
    v = (verdict or "").upper().strip()
    if v == "PASS":
        return ("PASS", "good")
    if v == "FAIL":
        return ("FAIL", "bad")
    return (v or "UNKNOWN", "warn")


# -----------------------------
# HUD styles + animated radar
# -----------------------------
def _inject_hud_css() -> None:
    st.markdown(
        """
<style>
/* --- Base --- */
:root{
  --bg0:#05070c;
  --bg1:#0a1221;
  --panel: rgba(10,16,30,0.70);
  --line: rgba(90,220,255,0.18);
  --line2: rgba(90,220,255,0.10);
  --glow: rgba(90,220,255,0.28);
  --text: rgba(230,245,255,0.92);
  --muted: rgba(190,220,240,0.72);
  --accent: rgba(90,220,255,0.95);
  --good: rgba(120,255,190,0.95);
  --bad: rgba(255,130,130,0.95);
  --warn: rgba(255,210,130,0.95);
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
}
html, body, [class*="css"]  { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }
.stApp{
  background:
    radial-gradient(1100px 700px at 20% 10%, rgba(90,220,255,0.10), transparent 60%),
    radial-gradient(900px 700px at 95% 20%, rgba(120,255,190,0.06), transparent 55%),
    radial-gradient(900px 700px at 20% 90%, rgba(255,210,130,0.04), transparent 55%),
    linear-gradient(180deg, var(--bg0), var(--bg1));
  color: var(--text);
}
/* tighten default paddings */
.block-container { padding-top: 1.2rem; padding-bottom: 1.5rem; max-width: 1400px; }
/* Hide Streamlit chrome */
header[data-testid="stHeader"]{background:transparent;}
div[data-testid="stToolbar"]{visibility:hidden; height:0px;}
/* HUD panels */
.hud-panel{
  border:1px solid var(--line);
  background: var(--panel);
  box-shadow: 0 0 0 1px rgba(90,220,255,0.06) inset, 0 18px 60px rgba(0,0,0,0.45);
  border-radius: 16px;
  padding: 14px 14px;
  position: relative;
  overflow:hidden;
}
.hud-panel:before{
  content:"";
  position:absolute; inset:0;
  background: radial-gradient(900px 220px at 20% 0%, rgba(90,220,255,0.07), transparent 62%);
  pointer-events:none;
}
.hud-title{
  font-weight:900; letter-spacing:1px; text-transform:uppercase;
  font-size:12px; color: rgba(235,250,255,0.92);
}
.hud-sub{
  font-family: var(--mono);
  font-size:11px; color: var(--muted);
}
.hud-kpi{
  border:1px solid var(--line2);
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(0,0,0,0.22);
}
.hud-kpi .k{ font-size:11px; color: var(--muted); text-transform:uppercase; letter-spacing:.6px; }
.hud-kpi .v{ font-family: var(--mono); font-size:12px; color: rgba(230,245,255,0.90); margin-top:6px; }
.badge{
  font-family: var(--mono);
  font-size:11px;
  padding: 6px 10px;
  border-radius: 999px;
  border:1px solid var(--line);
  background: rgba(0,0,0,0.25);
  color: var(--muted);
  display:inline-block;
}
.badge.good{ color: var(--good); border-color: rgba(120,255,190,0.28); }
.badge.bad{ color: var(--bad); border-color: rgba(255,130,130,0.28); }
.badge.warn{ color: var(--warn); border-color: rgba(255,210,130,0.28); }
.mono{
  font-family: var(--mono);
  font-size: 12px;
  color: rgba(230,245,255,0.88);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
/* Buttons */
.stButton>button{
  border-radius: 14px !important;
  border: 1px solid rgba(90,220,255,0.22) !important;
  background: rgba(0,0,0,0.25) !important;
  color: rgba(230,245,255,0.92) !important;
  box-shadow: 0 0 24px rgba(90,220,255,0.08);
}
.stButton>button:hover{
  border-color: rgba(90,220,255,0.45) !important;
  box-shadow: 0 0 32px rgba(90,220,255,0.14);
}
/* Tabs */
.stTabs [data-baseweb="tab"]{
  background: rgba(0,0,0,0.18);
  border: 1px solid rgba(90,220,255,0.12);
  border-radius: 12px;
  padding: 8px 12px;
  margin-right: 8px;
}
.stTabs [aria-selected="true"]{
  border-color: rgba(90,220,255,0.35);
  box-shadow: 0 0 26px rgba(90,220,255,0.10);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _radar_widget(height_px: int = 360) -> None:
    """
    Pure CSS/HTML animated radar. Always available (doesn't depend on artifacts).
    """
    html = f"""
<div style="width:100%;height:{height_px}px;">
  <style>
    .radar-wrap{{
      height:{height_px}px;
      border-radius: 16px;
      border: 1px solid rgba(90,220,255,0.18);
      background: radial-gradient(circle at 50% 50%, rgba(90,220,255,0.12), rgba(0,0,0,0.25) 60%, rgba(0,0,0,0.35));
      box-shadow: 0 0 0 1px rgba(90,220,255,0.06) inset, 0 18px 60px rgba(0,0,0,0.35);
      position: relative;
      overflow:hidden;
    }}
    .radar-grid{{
      position:absolute; inset:0;
      background:
        radial-gradient(circle, rgba(90,220,255,0.14) 1px, transparent 1px),
        radial-gradient(circle, rgba(90,220,255,0.10) 1px, transparent 1px);
      background-size: 60px 60px, 120px 120px;
      opacity: 0.35;
      mix-blend-mode: screen;
    }}
    .radar-rings{{
      position:absolute; inset:-10%;
      background:
        radial-gradient(circle at 50% 50%,
          transparent 0%,
          transparent 18%,
          rgba(90,220,255,0.12) 18.2%,
          transparent 18.6%,
          transparent 36%,
          rgba(90,220,255,0.10) 36.2%,
          transparent 36.6%,
          transparent 54%,
          rgba(90,220,255,0.08) 54.2%,
          transparent 54.6%,
          transparent 72%,
          rgba(90,220,255,0.06) 72.2%,
          transparent 72.6%,
          transparent 100%);
      opacity: 0.9;
    }}
    .radar-sweep{{
      position:absolute;
      inset:-40%;
      background: conic-gradient(
        from 0deg,
        rgba(90,220,255,0.00) 0deg,
        rgba(90,220,255,0.00) 290deg,
        rgba(90,220,255,0.10) 320deg,
        rgba(90,220,255,0.28) 345deg,
        rgba(90,220,255,0.00) 360deg
      );
      animation: spin 2.8s linear infinite;
      filter: blur(0.2px);
    }}
    .radar-fade{{
      position:absolute; inset:0;
      background: radial-gradient(circle at 50% 50%, rgba(0,0,0,0.0), rgba(0,0,0,0.35) 70%, rgba(0,0,0,0.55) 100%);
      pointer-events:none;
    }}
    .blip{{
      position:absolute;
      width: 8px; height: 8px;
      border-radius: 999px;
      background: rgba(120,255,190,0.95);
      box-shadow: 0 0 18px rgba(120,255,190,0.30), 0 0 3px rgba(120,255,190,0.65);
      opacity: 0;
      animation: ping 3.6s ease-in-out infinite;
    }}
    .b1{{ left: 22%; top: 34%; animation-delay: .3s; }}
    .b2{{ left: 64%; top: 28%; animation-delay: 1.1s; background: rgba(90,220,255,0.95); box-shadow: 0 0 18px rgba(90,220,255,0.25), 0 0 3px rgba(90,220,255,0.60);}}
    .b3{{ left: 58%; top: 68%; animation-delay: 2.0s; background: rgba(255,210,130,0.95); box-shadow: 0 0 18px rgba(255,210,130,0.22), 0 0 3px rgba(255,210,130,0.55);}}
    .b4{{ left: 36%; top: 74%; animation-delay: 2.7s; }}
    .crosshair{{
      position:absolute; inset:0;
      background:
        linear-gradient(to right, transparent 49.7%, rgba(90,220,255,0.14) 49.9%, rgba(90,220,255,0.14) 50.1%, transparent 50.3%),
        linear-gradient(to bottom, transparent 49.7%, rgba(90,220,255,0.14) 49.9%, rgba(90,220,255,0.14) 50.1%, transparent 50.3%);
      opacity: 0.45;
      mix-blend-mode: screen;
    }}
    .label{{
      position:absolute;
      left: 12px; top: 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
      font-size: 11px;
      color: rgba(190,220,240,0.78);
      letter-spacing: .5px;
      text-transform: uppercase;
      user-select:none;
    }}
    .label b{{ color: rgba(90,220,255,0.95); text-shadow: 0 0 14px rgba(90,220,255,0.30); }}
    .footer{{
      position:absolute; left: 12px; bottom: 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
      font-size: 10px;
      color: rgba(190,220,240,0.66);
      user-select:none;
    }}
    @keyframes spin {{
      from {{ transform: rotate(0deg); }}
      to   {{ transform: rotate(360deg); }}
    }}
    @keyframes ping {{
      0%   {{ transform: scale(0.5); opacity: 0; }}
      12%  {{ opacity: 0.95; }}
      35%  {{ opacity: 0.12; transform: scale(2.2); }}
      100% {{ opacity: 0; transform: scale(2.8); }}
    }}
  </style>
  <div class="radar-wrap">
    <div class="label"><b>RADAR</b> // LIVE SWEEP</div>
    <div class="radar-grid"></div>
    <div class="radar-rings"></div>
    <div class="crosshair"></div>
    <div class="radar-sweep"></div>
    <div class="blip b1"></div>
    <div class="blip b2"></div>
    <div class="blip b3"></div>
    <div class="blip b4"></div>
    <div class="radar-fade"></div>
    <div class="footer">demo-safe • visual only • no attribution</div>
  </div>
</div>
"""
    components.html(html, height=height_px + 10)


# -----------------------------
# Artifact selectors
# -----------------------------
def _artifact_paths() -> Dict[str, Path]:
    return {
        "orchestrator_txt": BRIEFS / "week3_demo_orchestrator_latest.txt",
        "orchestrator_json": BRIEFS / "week3_demo_orchestrator_latest.json",
        "readiness_txt": VALIDATION / "week3_demo_readiness_gate_latest.txt",
        "readiness_json": VALIDATION / "week3_demo_readiness_gate_latest.json",
        "commander_txt": BRIEFS / "commander_brief_latest.txt",
        "commander_json": BRIEFS / "commander_brief_latest.json",
        "narrative_txt": BRIEFS / "week3_demo_narrative_latest.txt",
        "legal_txt": BRIEFS / "legal_case_snapshot_latest.txt",
        "legal_json": BRIEFS / "legal_case_snapshot_latest.json",
        "ops_summary_txt": BRIEFS / "week3_operator_summary_latest.txt",
        "mobile_manifest_json": BRIEFS / "mobile_enjoy_manifest_latest.json",
        "install_threat_txt": BASE_DEFENSE / "installation_threat_map_latest.txt",
        "install_threat_json": BASE_DEFENSE / "installation_threat_map_latest.json",
        "cloud_package_manifest": PACKAGES / "week3_cloud_demo_package_manifest_latest.json",
    }


# -----------------------------
# App
# -----------------------------
def main() -> int:
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _inject_hud_css()

    banner = _demo_lock_banner_best_effort()

    # Header
    st.markdown(
        f"""
<div class="hud-panel" style="padding:16px 16px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
    <div>
      <div class="hud-title" style="font-size:14px;color:rgba(90,220,255,0.95);text-shadow:0 0 16px rgba(90,220,255,0.30);">
        OBASI // COMMAND CENTER
      </div>
      <div class="hud-sub">Week-3 Demo War Room • demo-safe • read-only posture</div>
    </div>
    <div class="hud-sub" style="text-align:right;">
      generated_at_utc: <span style="font-family:var(--mono);">{_utc_now_iso()}</span><br/>
      safety: <span style="font-family:var(--mono);">Assessment is probabilistic and bounded; operator judgment applies.</span>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if banner:
        st.markdown(
            f"""
<div class="hud-panel" style="margin-top:10px;border-color:rgba(255,210,130,0.22);">
  <div class="hud-title">DEMO LOCK</div>
  <div class="mono">{banner}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    paths = _artifact_paths()

    orch = _read_json(paths["orchestrator_json"])
    readiness = _read_json(paths["readiness_json"])
    cloud = _read_json(paths["cloud_package_manifest"])

    orch_verdict, orch_cls = _badge(str(orch.get("verdict", "UNKNOWN")))
    read_verdict, read_cls = _badge(str(readiness.get("verdict", "UNKNOWN")))
    cloud_verdict, cloud_cls = _badge(str(cloud.get("verdict", "UNKNOWN")))

    # Layout columns
    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        st.markdown(
            f"""
<div class="hud-panel">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div class="hud-title">TACTICAL RADAR</div>
    <div class="badge {orch_cls}">Orchestrator: {orch_verdict}</div>
  </div>
  <div class="hud-sub" style="margin-top:6px;">Premium HUD radar sweep (visual). This is what you were missing.</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        _radar_widget(height_px=380)

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        # Quick KPIs
        missing = cloud.get("required_missing", [])
        st.markdown(
            f"""
<div class="hud-panel">
  <div class="hud-title">STATUS SNAPSHOT</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
    <div class="hud-kpi">
      <div class="k">Readiness Gate</div>
      <div class="v"><span class="badge {read_cls}">{read_verdict}</span></div>
    </div>
    <div class="hud-kpi">
      <div class="k">Cloud Package</div>
      <div class="v"><span class="badge {cloud_cls}">{cloud_verdict}</span>  missing={len(missing) if isinstance(missing,list) else "UNK"}</div>
    </div>
    <div class="hud-kpi">
      <div class="k">Installation Threat Map</div>
      <div class="v">{'OK' if paths['install_threat_txt'].exists() else 'MISSING'} • {_safe_rel(paths['install_threat_txt'])}</div>
    </div>
    <div class="hud-kpi">
      <div class="k">Mobile Manifest</div>
      <div class="v">{'OK' if paths['mobile_manifest_json'].exists() else 'MISSING'} • {_safe_rel(paths['mobile_manifest_json'])}</div>
    </div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        tabs = st.tabs(
            [
                "Commander Brief",
                "Demo Narrative",
                "Legal Snapshot",
                "Installation Threat Map",
                "Readiness / Orchestrator",
                "Cloud Package",
            ]
        )

        def panel(title: str, body: str, badge_text: str = "", badge_cls: str = "warn") -> None:
            b = f'<span class="badge {badge_cls}">{badge_text}</span>' if badge_text else ""
            st.markdown(
                f"""
<div class="hud-panel">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div class="hud-title">{title}</div>
    {b}
  </div>
  <div class="mono" style="margin-top:10px;">{body if body else "Unavailable."}</div>
</div>
                """,
                unsafe_allow_html=True,
            )

        with tabs[0]:
            txt = _read_text(paths["commander_txt"], max_chars=12000)
            panel("COMMANDER BRIEF (latest)", txt, "bounded", "good" if "Assessment is probabilistic" in txt else "warn")

        with tabs[1]:
            txt = _read_text(paths["narrative_txt"], max_chars=12000)
            panel("WEEK-3 DEMO NARRATIVE (latest)", txt, "demo-safe", "good")

        with tabs[2]:
            txt = _read_text(paths["legal_txt"], max_chars=12000)
            panel("LEGAL CASE SNAPSHOT (latest)", txt, "demo-lock" if "DEMO MODE ACTIVE" in txt else "check", "good" if "DEMO MODE ACTIVE" in txt else "warn")

        with tabs[3]:
            txt = _read_text(paths["install_threat_txt"], max_chars=12000)
            panel("INSTALLATION THREAT MAP (latest)", txt, "artifact", "good" if txt else "bad")

        with tabs[4]:
            orch_txt = _read_text(paths["orchestrator_txt"], max_chars=9000)
            read_txt = _read_text(paths["readiness_txt"], max_chars=9000)
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            panel("WEEK-3 ORCHESTRATOR", orch_txt, f"verdict {orch_verdict}", orch_cls)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            panel("READINESS GATE", read_txt, f"verdict {read_verdict}", read_cls)

        with tabs[5]:
            cloud_txt = json.dumps(_read_json(paths["cloud_package_manifest"]), indent=2)
            panel("CLOUD DEMO PACKAGE MANIFEST", cloud_txt, f"verdict {cloud_verdict}", cloud_cls)

    # Footer actions
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("Open docs/briefs folder (Mac)", use_container_width=True):
            # best-effort only
            try:
                import subprocess
                subprocess.run(["open", str(BRIEFS)], check=False)
            except Exception:
                pass
    with c2:
        if st.button("Open docs/validation folder (Mac)", use_container_width=True):
            try:
                import subprocess
                subprocess.run(["open", str(VALIDATION)], check=False)
            except Exception:
                pass
    with c3:
        if st.button("Open docs/packages folder (Mac)", use_container_width=True):
            try:
                import subprocess
                subprocess.run(["open", str(PACKAGES)], check=False)
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

