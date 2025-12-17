# src/obasi_command_center.py
"""
OBASI COMMAND CENTER — MODULE 6A
Cinematic Boot + Premium HUD + Artifact-Driven Panels (best-effort, never crash)

Run:
  streamlit run src/obasi_command_center.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

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
BASE_DEF = DOCS / "base_defense"

# Key artifacts (best-effort reads)
P_COMMANDER_TXT = BRIEFS / "commander_brief_latest.txt"
P_COMMANDER_JSON = BRIEFS / "commander_brief_latest.json"

P_OPERATOR_SUMMARY_TXT = BRIEFS / "week3_operator_summary_latest.txt"
P_LEGAL_TXT = BRIEFS / "legal_case_snapshot_latest.txt"
P_LEGAL_JSON = BRIEFS / "legal_case_snapshot_latest.json"

P_DEMO_NARRATIVE_TXT = BRIEFS / "week3_demo_narrative_latest.txt"
P_DEMO_NARRATIVE_JSON = BRIEFS / "week3_demo_narrative_latest.json"

P_MOBILE_MANIFEST = BRIEFS / "mobile_enjoy_manifest_latest.json"

P_READINESS_JSON = VALIDATION / "week3_demo_readiness_gate_latest.json"
P_READINESS_TXT = VALIDATION / "week3_demo_readiness_gate_latest.txt"

P_FUSION_CORE_JSON = VALIDATION / "fusion_core_regression_latest.json"
P_FUSION_CORE_TXT = VALIDATION / "fusion_core_regression_latest.txt"

P_DEMO_PACK_JSON = VALIDATION / "week3_demo_pack_gate_latest.json"


# ============================
# Helpers (never crash)
# ============================
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path, limit: int = 12000) -> Optional[str]:
    try:
        if not path.exists():
            return None
        txt = path.read_text(encoding="utf-8", errors="replace")
        if len(txt) > limit:
            return txt[:limit] + "\n…(truncated)…"
        return txt
    except Exception:
        return None


def _read_json(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _present(path: Path) -> bool:
    try:
        return path.exists()
    except Exception:
        return False


def _badge(verdict: Optional[str]) -> str:
    if not verdict:
        return "UNKNOWN"
    v = str(verdict).upper()
    if v == "PASS":
        return "✅ PASS"
    if v == "FAIL":
        return "❌ FAIL"
    return f"⚠️ {v}"


def _safe_get(d: Optional[dict], key: str, default: Any = None) -> Any:
    try:
        if isinstance(d, dict):
            return d.get(key, default)
        return default
    except Exception:
        return default


# ============================
# Session State Init
# ============================
def init_state():
    st.session_state.setdefault("boot_complete", False)
    st.session_state.setdefault("boot_start", time.time())
    st.session_state.setdefault("focus", "overview")
    st.session_state.setdefault("presentation", True)
    st.session_state.setdefault("last_refresh_utc", _utc_now_iso())


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
        body { background: radial-gradient(circle at center, #0a1a2f 0%, #02040a 70%); }
        .boot { text-align: center; margin-top: 10%; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #14F1FF; }
        .title { font-size: 3.2rem; font-weight: 900; letter-spacing: .35em; margin-bottom: 1rem; }
        .sub { color: #8BA3C7; letter-spacing: .15em; margin-bottom: 2rem; }
        .status { font-size: 1.05rem; margin-top: 1.5rem; color: #DDE7FF; }
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
        msg = "Warming command display layers…"
    else:
        msg = "BOOT COMPLETE"

    st.markdown(f'<div class="status">{msg}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if elapsed >= 5.0:
        st.session_state["boot_complete"] = True
        st.rerun()

    time.sleep(0.15)
    st.rerun()


# ============================
# Artifact Snapshot
# ============================
@dataclass
class ArtifactBundle:
    commander_txt: Optional[str]
    commander_json: Optional[dict]
    operator_summary_txt: Optional[str]
    legal_txt: Optional[str]
    legal_json: Optional[dict]
    demo_narrative_txt: Optional[str]
    demo_narrative_json: Optional[dict]
    readiness_txt: Optional[str]
    readiness_json: Optional[dict]
    fusion_core_txt: Optional[str]
    fusion_core_json: Optional[dict]
    mobile_manifest: Optional[dict]
    demo_pack_json: Optional[dict]


def load_artifacts() -> ArtifactBundle:
    return ArtifactBundle(
        commander_txt=_read_text(P_COMMANDER_TXT),
        commander_json=_read_json(P_COMMANDER_JSON),
        operator_summary_txt=_read_text(P_OPERATOR_SUMMARY_TXT),
        legal_txt=_read_text(P_LEGAL_TXT),
        legal_json=_read_json(P_LEGAL_JSON),
        demo_narrative_txt=_read_text(P_DEMO_NARRATIVE_TXT),
        demo_narrative_json=_read_json(P_DEMO_NARRATIVE_JSON),
        readiness_txt=_read_text(P_READINESS_TXT),
        readiness_json=_read_json(P_READINESS_JSON),
        fusion_core_txt=_read_text(P_FUSION_CORE_TXT),
        fusion_core_json=_read_json(P_FUSION_CORE_JSON),
        mobile_manifest=_read_json(P_MOBILE_MANIFEST),
        demo_pack_json=_read_json(P_DEMO_PACK_JSON),
    )


# ============================
# Premium HUD Styles
# ============================
def hud_styles():
    st.markdown(
        """
        <style>
        body { background: linear-gradient(180deg, #05080c, #0b1220); color: #DDE7FF; }
        .hud-title { text-align: center; font-size: 2.6rem; font-weight: 900; letter-spacing: .22em; color: #14F1FF; margin-top: .2rem; }
        .hud-sub { text-align: center; color: #8BA3C7; margin-bottom: 1.0rem; letter-spacing: .12em; }
        .panel {
            border: 1px solid rgba(20, 241, 255, 0.25);
            border-radius: 18px;
            padding: 14px 16px;
            background: rgba(6, 10, 18, 0.65);
            box-shadow: 0 0 24px rgba(20,241,255,0.08);
        }
        .panel h3 { margin: 0 0 8px 0; color: #DDE7FF; }
        .muted { color: #8BA3C7; font-size: .9rem; }
        .tag { display: inline-block; padding: 2px 10px; border-radius: 999px; border: 1px solid rgba(20,241,255,.35); color: #14F1FF; font-family: ui-monospace, monospace; font-size: .8rem; }
        .danger { border-color: rgba(255, 76, 76, 0.45) !important; box-shadow: 0 0 24px rgba(255,76,76,0.08) !important; }
        .ok { border-color: rgba(54, 255, 162, 0.35) !important; box-shadow: 0 0 24px rgba(54,255,162,0.08) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, subtitle: str = "", state: str = "neutral"):
    cls = "panel"
    if state == "ok":
        cls += " ok"
    elif state == "danger":
        cls += " danger"
    st.markdown(f'<div class="{cls}"><h3>{title}</h3><div class="muted">{subtitle}</div></div>', unsafe_allow_html=True)


# ============================
# Panels
# ============================
def render_overview(a: ArtifactBundle):
    readiness_verdict = _safe_get(a.readiness_json, "verdict", None)
    fusion_verdict = _safe_get(a.fusion_core_json, "verdict", None)
    demo_pack_verdict = _safe_get(a.demo_pack_json, "verdict", None)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DEMO LOCK", "ON" if is_demo_locked() else "OFF")
    col2.metric("READINESS", _badge(readiness_verdict))
    col3.metric("FUSION CORE", _badge(fusion_verdict))
    col4.metric("DEMO PACK", _badge(demo_pack_verdict))

    st.markdown("---")

    left, right = st.columns([1.2, 1.0])

    with left:
        st.subheader("Commander Brief (latest)")
        if a.commander_txt:
            st.text_area("commander_brief_latest.txt", a.commander_txt, height=360)
        else:
            st.warning("Missing commander brief TXT (docs/briefs/commander_brief_latest.txt)")

    with right:
        st.subheader("Operator Summary (Week-3)")
        if a.operator_summary_txt:
            st.text_area("week3_operator_summary_latest.txt", a.operator_summary_txt, height=170)
        else:
            st.warning("Missing operator summary TXT (docs/briefs/week3_operator_summary_latest.txt)")

        st.subheader("Legal Snapshot (Shari Hook)")
        if a.legal_txt:
            st.text_area("legal_case_snapshot_latest.txt", a.legal_txt, height=170)
        else:
            st.warning("Missing legal snapshot TXT (docs/briefs/legal_case_snapshot_latest.txt)")


def render_readiness(a: ArtifactBundle):
    v = _safe_get(a.readiness_json, "verdict", None)
    st.subheader(f"Week-3 Demo Readiness Gate — {_badge(v)}")

    colA, colB, colC = st.columns(3)
    colA.metric("Crashes", str(_safe_get(a.readiness_json, "crashes", 0)))
    colB.metric("Strict", str(_safe_get(a.readiness_json, "strict", True)))
    colC.metric("Generated (UTC)", str(_safe_get(a.readiness_json, "generated_at_utc", "UNKNOWN")))

    st.markdown("### Gate Report (TXT)")
    if a.readiness_txt:
        st.text_area("week3_demo_readiness_gate_latest.txt", a.readiness_txt, height=360)
    else:
        st.warning("Missing readiness TXT report.")

    violations = _safe_get(a.readiness_json, "violations", [])
    if violations:
        st.markdown("### Violations")
        st.error("\n".join([str(x) for x in violations]))
    else:
        st.success("No violations reported.")


def render_validation(a: ArtifactBundle):
    v = _safe_get(a.fusion_core_json, "verdict", None)
    st.subheader(f"Fusion Core Regression Gate — {_badge(v)}")

    colA, colB, colC = st.columns(3)
    colA.metric("Crashes", str(_safe_get(a.fusion_core_json, "crashes", "UNKNOWN")))
    colB.metric("Generated (UTC)", str(_safe_get(a.fusion_core_json, "generated_at_utc", "UNKNOWN")))
    colC.metric("Missing Artifacts", str(len(_safe_get(a.fusion_core_json, "missing_artifacts", []) or [])))

    st.markdown("### Gate Report (TXT)")
    if a.fusion_core_txt:
        st.text_area("fusion_core_regression_latest.txt", a.fusion_core_txt, height=360)
    else:
        st.warning("Missing fusion core TXT report.")

    st.markdown("### Raw JSON (debug)")
    if a.fusion_core_json:
        st.json(a.fusion_core_json)
    else:
        st.info("fusion_core_regression_latest.json not available.")


def render_commander(a: ArtifactBundle):
    st.subheader("Commander Brief — Full Artifact View")

    c1, c2 = st.columns([1.2, 1.0])
    with c1:
        if a.commander_txt:
            st.text_area("commander_brief_latest.txt", a.commander_txt, height=520)
        else:
            st.warning("Commander brief TXT missing.")

    with c2:
        st.markdown("#### JSON Envelope (best-effort)")
        if a.commander_json:
            st.json(a.commander_json)
        else:
            st.info("Commander brief JSON missing.")

        st.markdown("#### Demo Lock Banner")
        if is_demo_locked():
            st.code(demo_lock_banner())


def render_legal(a: ArtifactBundle):
    st.subheader("Legal Case Snapshot — Shari Demo Hook")

    c1, c2 = st.columns([1.2, 1.0])
    with c1:
        if a.legal_txt:
            st.text_area("legal_case_snapshot_latest.txt", a.legal_txt, height=520)
        else:
            st.warning("Legal snapshot TXT missing.")

    with c2:
        st.markdown("#### JSON (best-effort)")
        if a.legal_json:
            st.json(a.legal_json)
        else:
            st.info("Legal snapshot JSON missing.")

        st.markdown("#### Notes for Demo")
        st.write(
            "- This is a **bounded** legal posture recommendation.\n"
            "- Ambiguity flags show what’s missing (party/jurisdiction).\n"
            "- Demo lock proves this is read-only / safe."
        )


def render_operator(a: ArtifactBundle):
    st.subheader("Operator Panel — Demo Narrative + Summary")

    if a.demo_narrative_txt:
        st.markdown("### Demo Narrative (Commander-safe)")
        st.text_area("week3_demo_narrative_latest.txt", a.demo_narrative_txt, height=240)
    else:
        st.warning("Demo narrative TXT missing.")

    if a.operator_summary_txt:
        st.markdown("### Operator Summary (10-second read)")
        st.text_area("week3_operator_summary_latest.txt", a.operator_summary_txt, height=180)
    else:
        st.warning("Operator summary TXT missing.")

    st.markdown("### Mobile Enjoy Manifest (what to open on iPhone)")
    if a.mobile_manifest:
        st.json(a.mobile_manifest)
    else:
        st.info("mobile_enjoy_manifest_latest.json missing.")


def render_artifact_map():
    st.subheader("Artifact Map (paths + presence)")
    rows = [
        ("Commander Brief TXT", str(P_COMMANDER_TXT), _present(P_COMMANDER_TXT)),
        ("Commander Brief JSON", str(P_COMMANDER_JSON), _present(P_COMMANDER_JSON)),
        ("Operator Summary TXT", str(P_OPERATOR_SUMMARY_TXT), _present(P_OPERATOR_SUMMARY_TXT)),
        ("Legal Snapshot TXT", str(P_LEGAL_TXT), _present(P_LEGAL_TXT)),
        ("Legal Snapshot JSON", str(P_LEGAL_JSON), _present(P_LEGAL_JSON)),
        ("Demo Narrative TXT", str(P_DEMO_NARRATIVE_TXT), _present(P_DEMO_NARRATIVE_TXT)),
        ("Readiness Gate JSON", str(P_READINESS_JSON), _present(P_READINESS_JSON)),
        ("Fusion Core Gate JSON", str(P_FUSION_CORE_JSON), _present(P_FUSION_CORE_JSON)),
        ("Mobile Enjoy Manifest", str(P_MOBILE_MANIFEST), _present(P_MOBILE_MANIFEST)),
        ("Demo Pack Gate", str(P_DEMO_PACK_JSON), _present(P_DEMO_PACK_JSON)),
    ]
    for name, path, ok in rows:
        st.write(f"{'✅' if ok else '❌'} **{name}** — `{path}`")


# ============================
# Main HUD
# ============================
def command_center():
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
    )

    hud_styles()

    st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hud-sub">Demo-Locked • Read-Only • Artifact-Driven</div>', unsafe_allow_html=True)

    # Sidebar controls
    st.sidebar.markdown("## ⚙️ Controls")
    if st.sidebar.button("🔁 Replay Boot"):
        st.session_state["boot_complete"] = False
        st.session_state["boot_start"] = time.time()
        st.rerun()

    if st.sidebar.button("♻️ Refresh Artifacts"):
        st.session_state["last_refresh_utc"] = _utc_now_iso()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧭 Navigation")
    focus = st.sidebar.radio(
        "Panel",
        ["Overview", "Readiness", "Validation", "Commander", "Operator", "Legal", "Artifact Map"],
        index=0,
    )
    st.session_state["focus"] = focus.lower()

    # Demo lock banner
    if is_demo_locked():
        st.warning(demo_lock_banner())

    # Load artifacts
    a = load_artifacts()

    # Main render
    if st.session_state["focus"] == "overview":
        render_overview(a)
    elif st.session_state["focus"] == "readiness":
        render_readiness(a)
    elif st.session_state["focus"] == "validation":
        render_validation(a)
    elif st.session_state["focus"] == "commander":
        render_commander(a)
    elif st.session_state["focus"] == "operator":
        render_operator(a)
    elif st.session_state["focus"] == "legal":
        render_legal(a)
    elif st.session_state["focus"] == "artifact map":
        render_artifact_map()

    st.caption(f"Last refresh (UTC): {st.session_state.get('last_refresh_utc','UNKNOWN')} | Repo: {ROOT}")


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

