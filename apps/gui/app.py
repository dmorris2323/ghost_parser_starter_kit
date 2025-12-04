"""
app.py — Ghost Lantern Labs GUI
Includes: Minimap Loader, SOS Loader, Cross-Sensor Loader,
Golden Dome Readiness Tile, and all dashboard panels.
"""

import streamlit as st
import json
from pathlib import Path

# =========================
# LOADERS
# =========================

# --- Minimap Loader ---
MINIMAP_FILE = Path(__file__).resolve().parent.parent.parent / "src/gui_minimap.json"

def load_gui_minimap():
    if not MINIMAP_FILE.exists():
        return {"map": {}, "timestamp": None}
    try:
        return json.loads(MINIMAP_FILE.read_text())
    except:
        return {"map": {}, "timestamp": None}


# --- SOS Loader ---
SOS_FILE = Path(__file__).resolve().parent.parent.parent / "src/gui_sos_overlay.json"

def load_sos_overlay():
    if not SOS_FILE.exists():
        return {"status": "empty", "data": {}}
    try:
        return json.loads(SOS_FILE.read_text())
    except:
        return {"status": "corrupted", "data": {}}


# --- Cross-Sensor Loader ---
CROSS_SENSOR_FILE = Path(__file__).resolve().parent.parent.parent / "src/docs/cross_sensor_report.txt"

def load_cross_sensor():
    if CROSS_SENSOR_FILE.exists():
        try:
            return CROSS_SENSOR_FILE.read_text()
        except:
            return "Cross-sensor report corrupted."
    return "No cross-sensor report found. Run Option 25."


# --- Golden Dome Tile ---
from golden_dome_tile import build_golden_dome_tile


# =========================
# GUI RENDER
# =========================

def main():
    st.title("Ghost Lantern Labs — Spectral Owl Dashboard")

    # =========================
    # MINIMAP PANEL
    # =========================
    st.header("Sensor Minimap")
    minimap = load_gui_minimap()
    st.json(minimap)

    # =========================
    # SOS OVERLAY PANEL
    # =========================
    st.header("Spectral SOS Overlay")
    sos = load_sos_overlay()
    st.json(sos)

    # =========================
    # CROSS-SENSOR PANEL
    # =========================
    st.header("Cross-Sensor Validation")
    cross = load_cross_sensor()
    st.text(cross)

    # =========================
    # GOLDEN DOME READINESS TILE
    # =========================
    st.header("Golden Dome Readiness")

    # Example static values — GUI dynamically updates once backend stats exist.
    tile = build_golden_dome_tile(
        reliability=92.5,
        agreement=88.0,
        profile="Ghost Analyst"
    )

    st.json(tile)

    st.success("GUI rendering complete.")


if __name__ == "__main__":
    main()

