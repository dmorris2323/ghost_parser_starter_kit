#!/usr/bin/env python3
"""
apps/gui/app.py

Ghost Lantern Labs – Spectral Command Center (Command Center Edition)
---------------------------------------------------------------------

This is the primary GUI for Ghost Lantern Labs. It presents a
commander-focused view of:

    • Fusion Trust and overall readiness
    • Nuclear / Golden Dome posture
    • Base-defense situation
    • Defensive cyber intelligence (DCIM)
    • Minimap + SOS overlays
    • Daily mission brief (text)

Design goals:
    - Dark, ISR-style command aesthetic
    - Card-based layout for key scores
    - Tabs for nuclear/base-defense, cyber intel, visual overlays, and brief
    - Robust: degrades gracefully when some docs are missing

This app does NOT alter the fusion pipeline or external systems.
It is a read-only visualization layer over the docs/ artifacts.
"""

import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

# -------------------------------------------------------------------
# Path setup – ensure src/ is on the Python path
# -------------------------------------------------------------------

# __file__ = .../src/apps/gui/app.py
SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

BASE_DIR = SRC_DIR
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# Try to import an aggregate dashboard builder if it exists
try:
    from spectral_dashboard_api import build_dashboard_bundle  # type: ignore
except Exception:
    build_dashboard_bundle = None  # type: ignore


# -------------------------------------------------------------------
# Helpers to safely read docs
# -------------------------------------------------------------------

def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _fmt_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def _clip_0_100(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 100.0:
        return 100.0
    return x


# -------------------------------------------------------------------
# Data loaders – pull from docs/ in a tolerant way
# -------------------------------------------------------------------

def _load_golden_dome_watch() -> Dict[str, Any]:
    path = os.path.join(DOCS_DIR, "golden_dome_daily_watch.json")
    data = _safe_read_json(path)
    return data if isinstance(data, dict) else {}


def _load_defensive_cyber_intel() -> Dict[str, Any]:
    path = os.path.join(DOCS_DIR, "defensive_cyber_intel_report.json")
    data = _safe_read_json(path)
    return data if isinstance(data, dict) else {}


def _load_joint_readiness_board() -> Dict[str, Any]:
    path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    data = _safe_read_json(path)
    return data if isinstance(data, dict) else {}


def _load_minimap_overlay() -> Dict[str, Any]:
    path = os.path.join(DOCS_DIR, "gui_minimap.json")
    data = _safe_read_json(path)
    return data if isinstance(data, dict) else {}


def _load_sos_overlay() -> Dict[str, Any]:
    path = os.path.join(DOCS_DIR, "gui_sos_overlay.json")
    data = _safe_read_json(path)
    return data if isinstance(data, dict) else {}


def _load_daily_brief_text() -> Optional[str]:
    # Prefer text. If not present, try HTML and strip minimally.
    txt = _safe_read_text(os.path.join(DOCS_DIR, "daily_mission_brief.txt"))
    if txt:
        return txt
    html = _safe_read_text(os.path.join(DOCS_DIR, "daily_mission_brief.html"))
    return html


def _load_dashboard_bundle() -> Dict[str, Any]:
    """
    Optional use of spectral_dashboard_api.build_dashboard_bundle().
    If unavailable, we fall back to direct doc loading.
    """
    if build_dashboard_bundle is None:
        return {}
    try:
        bundle = build_dashboard_bundle()
        return bundle if isinstance(bundle, dict) else {}
    except Exception:
        return {}


# -------------------------------------------------------------------
# Styling – Command Center Edition
# -------------------------------------------------------------------

def _inject_css() -> None:
    st.markdown(
        """
        <style>
        /* Global dark theme tweaks */
        body, .stApp {
            background-color: #05060a;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        /* GLL card styling */
        .gll-card {
            background: linear-gradient(135deg, #111827 0%, #020617 60%, #111827 100%);
            border-radius: 18px;
            padding: 1.0rem 1.2rem;
            border: 1px solid #1f2937;
            box-shadow: 0 0 25px rgba(15, 23, 42, 0.8);
        }

        .gll-card h3, .gll-card h4 {
            color: #e5e7eb;
            margin-bottom: 0.25rem;
        }

        .gll-metric-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #9ca3af;
        }

        .gll-metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #e5e7eb;
        }

        .gll-metric-sub {
            font-size: 0.85rem;
            color: #9ca3af;
        }

        .gll-badge {
            display: inline-block;
            padding: 0.1rem 0.5rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background-color: #111827;
            border: 1px solid #1f2937;
            color: #9ca3af;
        }

        .gll-badge-red {
            border-color: #b91c1c;
            color: #fecaca;
        }

        .gll-badge-amber {
            border-color: #f59e0b;
            color: #fcd34d;
        }

        .gll-badge-green {
            border-color: #16a34a;
            color: #bbf7d0;
        }

        .gll-section-title {
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #9ca3af;
        }

        .gll-json-box {
            background-color: #020617;
            border-radius: 12px;
            padding: 0.75rem;
            border: 1px solid #1f2937;
            font-family: "SF Mono", ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 0.75rem;
            color: #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _posture_badge(level: str) -> str:
    lvl = (level or "UNKNOWN").upper()
    if lvl == "GREEN":
        return '<span class="gll-badge gll-badge-green">🟢 GREEN</span>'
    if lvl == "AMBER":
        return '<span class="gll-badge gll-badge-amber">🟡 AMBER</span>'
    if lvl == "RED":
        return '<span class="gll-badge gll-badge-red">🔴 RED</span>'
    return f'<span class="gll-badge">⚪ {lvl}</span>'


# -------------------------------------------------------------------
# Main UI
# -------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="GLL – Spectral Command Center",
        page_icon="🦉",
        layout="wide",
    )

    _inject_css()

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.25rem;">
            <div style="font-size:1.7rem;">🦉</div>
            <div>
                <div style="font-size:0.8rem;letter-spacing:0.18em;text-transform:uppercase;color:#9ca3af;">
                    Ghost Lantern Labs
                </div>
                <div style="font-size:1.6rem;font-weight:600;color:#e5e7eb;">
                    Spectral Command Center
                </div>
            </div>
        </div>
        <div style="font-size:0.85rem;color:#9ca3af;margin-bottom:1rem;">
            Nuclear / ISR / Base-Defense / Cyber Fusion – Operator Console
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Optionally pull a prebuilt bundle (if available)
    bundle = _load_dashboard_bundle()

    golden = _load_golden_dome_watch()
    dcim = _load_defensive_cyber_intel()
    joint = _load_joint_readiness_board()
    minimap = _load_minimap_overlay()
    sos = _load_sos_overlay()
    brief_text = _load_daily_brief_text()

    # ----------------------------------------------------------------
    # TOP METRICS – FUSION, NUCLEAR, CYBER, JOINT
    # ----------------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    # Fusion trust from Golden Dome daily watch if present
    fusion_trust_score = _fmt_float(
        golden.get("fusion_trust_score", golden.get("fusion_trust", 0.0)),
        0.0,
    )
    fusion_level = str(golden.get("fusion_posture_level", "UNKNOWN"))

    with col1:
        st.markdown('<div class="gll-card">', unsafe_allow_html=True)
        st.markdown('<div class="gll-metric-label">Fusion Trust</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="gll-metric-value">{fusion_trust_score:.1f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="gll-metric-sub">Pipeline confidence · {_posture_badge(fusion_level)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Nuclear early warning from Golden Dome daily watch (if present)
    nuclear_score = _fmt_float(
        golden.get("nuclear_pressure_score", golden.get("nuclear_score", 0.0)),
        0.0,
    )
    nuclear_level = str(golden.get("nuclear_level", golden.get("golden_dome_level", "UNKNOWN")))

    with col2:
        st.markdown('<div class="gll-card">', unsafe_allow_html=True)
        st.markdown('<div class="gll-metric-label">Nuclear Early Warning</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="gll-metric-value">{nuclear_score:.1f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="gll-metric-sub">Golden Dome posture · {_posture_badge(nuclear_level)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Cyber threat from DCIM
    cyber_score = _clip_0_100(_fmt_float(dcim.get("cyber_threat_score", 0.0), 0.0))
    cyber_level = str(dcim.get("cyber_posture_level", "UNKNOWN"))

    with col3:
        st.markdown('<div class="gll-card">', unsafe_allow_html=True)
        st.markdown('<div class="gll-metric-label">Defensive Cyber Intel</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="gll-metric-value">{cyber_score:.1f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="gll-metric-sub">DCIM posture · {_posture_badge(cyber_level)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Joint readiness from joint_readiness_board.json
    jr_score = _fmt_float(joint.get("joint_readiness_score", 0.0), 0.0)
    jr_level = str(joint.get("joint_readiness_level", "UNKNOWN"))

    with col4:
        st.markdown('<div class="gll-card">', unsafe_allow_html=True)
        st.markdown('<div class="gll-metric-label">Joint Readiness</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="gll-metric-value">{jr_score:.1f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="gll-metric-sub">Nuclear + base-defense · {_posture_badge(jr_level)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ----------------------------------------------------------------
    # TABS – Nuclear/Base-Defense, Cyber Intel, Minimap/SOS, Brief
    # ----------------------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Nuclear & Base-Defense",
            "Cyber Intelligence (DCIM)",
            "Minimap & SOS Overlay",
            "Daily Mission Brief",
        ]
    )

    # ---------------------- TAB 1: Nuclear & Base-Defense -------------------
    with tab1:
        st.markdown('<div class="gll-section-title">Nuclear / Golden Dome Posture</div>', unsafe_allow_html=True)
        st.write("")

        nc1, nc2 = st.columns(2)

        with nc1:
            st.markdown('<div class="gll-card">', unsafe_allow_html=True)
            st.markdown("#### Nuclear Snapshot", unsafe_allow_html=True)

            if golden:
                gd_level = golden.get("golden_dome_level", nuclear_level)
                gd_drift = _fmt_float(golden.get("drift_index", golden.get("drift_score", 0.0)), 0.0)
                gd_vol = _fmt_float(golden.get("temporal_volatility", 0.0), 0.0)
                gd_msg = golden.get("summary", "No nuclear summary supplied.")

                st.write(f"**Golden Dome Level:** {_posture_badge(str(gd_level))}", unsafe_allow_html=True)
                st.write(f"**Drift Index:** {gd_drift:.1f}")
                st.write(f"**Temporal Volatility:** {gd_vol:.1f}")
                st.write("")
                st.write("**Analyst Note:**")
                st.write(gd_msg)
            else:
                st.info(
                    "No golden_dome_daily_watch.json found. Run the Golden Dome Daily Watch tool "
                    "from ghost_cli.py to populate this section."
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with nc2:
            st.markdown('<div class="gll-card">', unsafe_allow_html=True)
            st.markdown("#### Base-Defense Storyboard (Summary)", unsafe_allow_html=True)

            storyboard = _safe_read_json(os.path.join(DOCS_DIR, "base_defense_storyboard.json"))
            if isinstance(storyboard, dict):
                phases = storyboard.get("phases", [])
                if isinstance(phases, list) and phases:
                    for p in phases:
                        if not isinstance(p, dict):
                            continue
                        name = str(p.get("name", "Phase")).title()
                        summary = str(p.get("summary", ""))
                        st.markdown(f"**{name}**")
                        st.write(summary)
                        st.markdown("---")
                else:
                    st.write("Base-defense storyboard is present but has no phases.")
            else:
                st.info(
                    "No base_defense_storyboard.json found. Run the Base Defense Storyboard tool "
                    "from ghost_cli.py to populate this section."
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------- TAB 2: Cyber Intelligence -----------------------
    with tab2:
        st.markdown('<div class="gll-section-title">Defensive Cyber Intelligence (DCIM)</div>', unsafe_allow_html=True)
        st.write("")

        if not dcim:
            st.warning(
                "No defensive_cyber_intel_report.json found. Run the Defensive Cyber Intelligence "
                "Module (DCIM) from ghost_cli.py to populate this section."
            )
        else:
            c1, c2 = st.columns([2, 1])

            with c1:
                st.markdown('<div class="gll-card">', unsafe_allow_html=True)
                st.markdown("#### Cyber Threat Summary", unsafe_allow_html=True)

                score = _clip_0_100(_fmt_float(dcim.get("cyber_threat_score", 0.0), 0.0))
                level = _posture_badge(str(dcim.get("cyber_posture_level", "UNKNOWN")))
                confidence = _clip_0_100(_fmt_float(dcim.get("confidence", 0.0), 0.0))

                st.write(f"**Threat Score:** {score:.1f} / 100")
                st.write(f"**Posture Level:** {level}", unsafe_allow_html=True)
                st.write(f"**Assessment Confidence:** {confidence:.1f} / 100")
                st.write("")
                st.write("**MITRE ATT&CK–style Tactics Suspected:**")
                mitre = dcim.get("mitre_tactics_suspected", [])
                if isinstance(mitre, list) and mitre:
                    for t in mitre:
                        st.write(f"- {t}")
                else:
                    st.write("- None confidently indicated.")
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="gll-card">', unsafe_allow_html=True)
                st.markdown("#### Category Scores", unsafe_allow_html=True)
                cats = dcim.get("category_scores", {}) or {}
                st.write(f"- **Beaconing / C2 suspicion:** {cats.get('beaconing_score', 0):.1f}")
                st.write(f"- **Auth & identity anomalies:** {cats.get('auth_anomaly_score', 0):.1f}")
                st.write(f"- **Inbound threat pressure:** {cats.get('inbound_threat_score', 0):.1f}")
                st.write(f"- **Sensor tampering signals:** {cats.get('tamper_score', 0):.1f}")
                st.write(f"- **Config / posture drift:** {cats.get('config_drift_score', 0):.1f}")
                st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------- TAB 3: Minimap & SOS ---------------------------
    with tab3:
        st.markdown('<div class="gll-section-title">Fusion Minimap & SOS Overlay</div>', unsafe_allow_html=True)
        st.write("")

        mc1, mc2 = st.columns(2)

        with mc1:
            st.markdown('<div class="gll-card">', unsafe_allow_html=True)
            st.markdown("#### Fusion Minimap Snapshot", unsafe_allow_html=True)
            if minimap:
                st.markdown('<div class="gll-json-box">', unsafe_allow_html=True)
                st.json(minimap)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(
                    "No gui_minimap.json found. Run the fusion minimap export from ghost_cli.py "
                    "to populate this section."
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with mc2:
            st.markdown('<div class="gll-card">', unsafe_allow_html=True)
            st.markdown("#### SOS Overlay", unsafe_allow_html=True)
            if sos:
                st.markdown('<div class="gll-json-box">', unsafe_allow_html=True)
                st.json(sos)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(
                    "No gui_sos_overlay.json found. Run the SOS overlay export from ghost_cli.py "
                    "to populate this section."
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------- TAB 4: Daily Mission Brief ---------------------
    with tab4:
        st.markdown('<div class="gll-section-title">Daily Mission Brief</div>', unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="gll-card">', unsafe_allow_html=True)
        if brief_text:
            st.markdown("#### Current Daily Mission Brief", unsafe_allow_html=True)
            st.text(brief_text)
        else:
            st.info(
                "No daily mission brief found. Run the daily mission brief generator from ghost_cli.py "
                "to populate this section."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # Footer
    # ----------------------------------------------------------------
    st.markdown("---")
    st.caption(
        "Ghost Lantern Labs · Spectral Command Center · Nuclear / ISR / Base-Defense / Defensive Cyber Intelligence"
    )


if __name__ == "__main__":
    main()

