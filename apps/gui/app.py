"""
apps/gui/app.py

Streamlit GUI for Ghost Lantern Labs.

Panels:
- Main: Daily Mission Brief (text)
- Sidebar: Minimap, SOS Overlay, Sensor Reliability, Sensor Drift, Cross-Sensor Report
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

# --- PATH SETUP ---
APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent.parent
SRC = ROOT / "src"
DOCS = SRC / "docs"

MINIMAP_FILE = SRC / "gui_minimap.json"
SOS_FILE = SRC / "gui_sos_overlay.json"
RELIABILITY_FILE = DOCS / "reliability_report.txt"
DRIFT_FILE = DOCS / "drift_report.txt"
CROSS_SENSOR_FILE = DOCS / "cross_sensor_report.txt"
TEXT_BRIEF_FILE = DOCS / "daily_mission_brief.txt"
HTML_BRIEF_FILE = DOCS / "daily_mission_brief.html"


# --- LOADERS ---


def load_gui_minimap():
    if not MINIMAP_FILE.exists():
        return {"map": {}, "timestamp": None}
    try:
        return json.loads(MINIMAP_FILE.read_text())
    except Exception:
        return {"map": {}, "timestamp": None}


def load_sos_overlay():
    if not SOS_FILE.exists():
        return {"status": "empty", "data": {}}
    try:
        return json.loads(SOS_FILE.read_text())
    except Exception:
        return {"status": "corrupted", "data": {}}


def _load_text_file(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    try:
        return path.read_text().strip()
    except Exception:
        return fallback


def load_reliability():
    return _load_text_file(
        RELIABILITY_FILE,
        "Reliability report not generated yet. Run sensor_reliability.py.",
    )


def load_drift():
    return _load_text_file(
        DRIFT_FILE,
        "Drift report not generated yet. Run sensor_drift_predictor.py.",
    )


def load_cross_sensor():
    return _load_text_file(
        CROSS_SENSOR_FILE,
        "No cross-sensor report found. Run Option 25 in ghost_cli.",
    )


def load_text_brief():
    """
    Prefer the plain text mission brief. If missing, fall back to HTML stripped.
    """
    if TEXT_BRIEF_FILE.exists():
        return TEXT_BRIEF_FILE.read_text()
    # fallback: if HTML exists, at least show raw HTML as text
    if HTML_BRIEF_FILE.exists():
        return HTML_BRIEF_FILE.read_text()
    return "No daily mission brief found. Run daily_mission_brief.py and mission_brief_html.py."


# --- STREAMLIT UI ---


def main() -> None:
    st.set_page_config(
        page_title="Ghost Lantern Labs – Spectral Dashboard",
        layout="wide",
    )

    st.title("Ghost Lantern Labs – Spectral Dashboard")

    # Main layout: two columns (wide main, narrow sidebar)
    col_main, col_side = st.columns([3, 2])

    # MAIN PANEL: Mission Brief
    with col_main:
        st.subheader("Daily Mission Brief")
        brief_text = load_text_brief()
        st.text_area(
            label="Core Mission Brief (read-only)",
            value=brief_text,
            height=500,
        )

    # SIDEBAR PANEL: Minimap, SOS, Reliability, Drift, Cross-Sensor
    with col_side:
        st.subheader("Fusion Mini-Map")
        minimap = load_gui_minimap()
        if not minimap.get("map"):
            st.info(
                "No minimap data found.\n\nRun:\n"
                "  python src/fusion_minimap_overlay.py\n"
                "or use CLI option 19 to export minimap."
            )
        else:
            st.json(minimap)

        st.subheader("SOS Overlay")
        sos = load_sos_overlay()
        if sos.get("status") in ("empty", "corrupted"):
            st.info(
                "No SOS overlay found.\n\nRun:\n"
                "  python src/spectral_sos_overlay.py\n"
                "or use CLI option 20 to export the situation summary."
            )
        else:
            st.json(sos)

        st.subheader("Sensor Reliability")
        st.text(load_reliability())

        st.subheader("Sensor Drift Prediction")
        st.text(load_drift())

        st.subheader("Cross-Sensor Validation")
        st.text(load_cross_sensor())


if __name__ == "__main__":
    main()

