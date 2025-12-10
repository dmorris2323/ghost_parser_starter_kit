"""
apps/gui/app.py

Ghost Lantern Labs — Spectral Dashboard
Stable version with:
  - Fusion Trust Score
  - Operator Safety Layer
  - Sensor Latency
  - Fusion Minimap
  - SOS Overlay
  - Daily Mission Brief (text)

Reads core analytics from src/ and JSON artifacts written by CLI tools.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# --- Resolve paths and make sure /src is importable ---
ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# --- Safe imports from src/ ---
from fusion_trust import compute_trust  # type: ignore
from operator_safety_layer import compute_osl  # type: ignore
from sensor_latency import compute_latency_report  # type: ignore

# --- Files for minimap, SOS, mission brief ---
MINIMAP_FILE = SRC_DIR / "gui_minimap.json"
SOS_FILE = SRC_DIR / "gui_sos_overlay.json"
BRIEF_TXT_FILE = SRC_DIR / "docs" / "daily_mission_brief.txt"


def load_gui_minimap():
    """Load GUI minimap JSON if present, else safe stub."""
    if not MINIMAP_FILE.exists():
        return {
            "timestamp": None,
            "map": {},
            "message": "No minimap data found. Run fusion_minimap_overlay export."
        }
    try:
        return json.loads(MINIMAP_FILE.read_text())
    except Exception as e:
        return {
            "timestamp": None,
            "map": {},
            "error": f"Failed to load minimap: {e!r}",
        }


def load_sos_overlay():
    """Load SOS overlay JSON if present, else safe stub."""
    if not SOS_FILE.exists():
        return {
            "status": "empty",
            "message": "No SOS overlay found. Run spectral_sos_overlay export.",
        }
    try:
        return json.loads(SOS_FILE.read_text())
    except Exception as e:
        return {
            "status": "corrupted",
            "message": f"Failed to load SOS overlay: {e!r}",
        }


def load_brief_text():
    """Load daily mission brief text for quick reference."""
    if not BRIEF_TXT_FILE.exists():
        return "No daily mission brief found. Run mission_brief_html.py / daily_mission_brief.py."
    try:
        return BRIEF_TXT_FILE.read_text()
    except Exception as e:
        return f"[ERROR] Failed to load mission brief: {e!r}"


def main():
    st.set_page_config(page_title="Ghost Lantern Labs — Spectral Dashboard", layout="wide")

    st.title("Ghost Lantern Labs — Spectral Dashboard")

    st.caption(f"Base Directory: {ROOT}")
    st.caption(f"Loaded at: {datetime.now(timezone.utc).isoformat()}")

    col1, col2 = st.columns(2)

    # --- Fusion Trust + OSL ---
    with col1:
        st.subheader("Fusion Trust Score")
        try:
            trust = compute_trust()
            st.json(trust)
        except Exception as e:
            st.error(f"Fusion Trust failed: {e!r}")

    with col2:
        st.subheader("Operator Safety Layer")
        try:
            osl = compute_osl()
            st.json(osl)
        except Exception as e:
            st.error(f"OSL failed: {e!r}")

    # --- Sensor Latency ---
    st.subheader("Sensor Latency")
    try:
        st.json(compute_latency_report())
    except Exception as e:
        st.error(f"Latency report failed: {e!r}")

    # --- Fusion Minimap ---
    st.subheader("Fusion Mini-Map")
    minimap = load_gui_minimap()
    st.json(minimap)

    # --- SOS Overlay ---
    st.subheader("SOS Overlay")
    sos = load_sos_overlay()
    st.json(sos)

    # --- Daily Mission Brief (Text) ---
    st.subheader("Daily Mission Brief (Text)")
    brief_text = load_brief_text()
    st.text(brief_text)


if __name__ == "__main__":
    main()

