"""
apps/gui/app.py

Ghost Lantern Labs — Spectral Dashboard
Streamlit GUI

Shows:
- Fusion Trust Score (from fusion_trust.compute_trust)
- Operator Safety Layer (from operator_safety_layer.compute_osl)
- Sensor Latency (from sensor_latency.compute_latency_report, if available)
- Fusion Mini-Map (from src/gui_minimap.json)
- SOS Overlay (from src/gui_sos_overlay.json)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

# --- PATH SETUP: ensure `src` is importable ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# --- SAFE IMPORTS ---

# Fusion Trust
try:
    from fusion_trust import compute_trust
except Exception:
    def compute_trust():
        return {
            "fusion_trust": None,
            "factors": {
                "error": "fusion_trust module not available"
            },
        }

# Operator Safety Layer
try:
    from operator_safety_layer import compute_osl
except Exception:
    def compute_osl():
        return {
            "osl_status": "UNKNOWN",
            "trust_score": None,
            "message": "operator_safety_layer module not available",
        }

# Sensor Latency
try:
    from sensor_latency import compute_latency_report
except Exception:
    def compute_latency_report():
        return {"status": "no_data", "message": "sensor_latency module not available"}

# --- FILE PATHS FOR JSON ARTIFACTS ---

MINIMAP_FILE = SRC_DIR / "gui_minimap.json"
SOS_FILE = SRC_DIR / "gui_sos_overlay.json"


def load_gui_minimap():
    """Load minimap JSON from src/gui_minimap.json."""
    if not MINIMAP_FILE.exists():
        return {
            "timestamp": None,
            "map": {},
            "message": "No minimap data found. Run CLI Option 19 first.",
        }
    try:
        return json.loads(MINIMAP_FILE.read_text())
    except Exception:
        return {
            "timestamp": None,
            "map": {},
            "message": "Failed to parse gui_minimap.json",
        }


def load_sos_overlay():
    """Load SOS overlay JSON from src/gui_sos_overlay.json."""
    if not SOS_FILE.exists():
        return {
            "status": "empty",
            "message": "No SOS overlay found. Run CLI Option 20 first.",
        }
    try:
        return json.loads(SOS_FILE.read_text())
    except Exception:
        return {
            "status": "corrupted",
            "message": "Failed to parse gui_sos_overlay.json",
        }


def main():
    st.set_page_config(
        page_title="Ghost Lantern Labs — Spectral Dashboard",
        layout="wide",
    )

    st.title("Ghost Lantern Labs — Spectral Dashboard")

    # Top meta bar
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.write(f"Base Directory: `{BASE_DIR}`")
    with col_meta2:
        st.write(f"Loaded at: {datetime.utcnow().isoformat()}Z")

    # --- ROW 1: Trust + Operator Safety + Latency ---

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Fusion Trust Score")
        trust = compute_trust()
        st.json(trust)

    with col2:
        st.subheader("Operator Safety Layer")
        osl = compute_osl()
        st.json(osl)

    with col3:
        st.subheader("Sensor Latency")
        latency = compute_latency_report()
        st.json(latency)

    st.markdown("---")

    # --- ROW 2: Minimap + SOS Overlay ---

    col4, col5 = st.columns(2)

    with col4:
        st.subheader("Fusion Mini-Map")
        minimap = load_gui_minimap()
        st.json(minimap)

    with col5:
        st.subheader("SOS Overlay")
        sos = load_sos_overlay()
        st.json(sos)


if __name__ == "__main__":
    main()

