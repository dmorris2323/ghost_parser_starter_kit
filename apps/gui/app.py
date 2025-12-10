"""
Ghost Lantern Labs — Spectral Dashboard (Streamlit)
---------------------------------------------------
Shows:
  • Fusion Trust Score
  • Operator Safety Layer
  • Sensor Latency
  • Fusion Mini-Map
  • SOS Overlay
  • Adversary Pattern Engine
  • Daily Mission Brief (text)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

# --- Path setup so we can import from src/ cleanly ---
BASE = Path(__file__).resolve().parent.parent.parent  # /parser_starter_kit
SRC = BASE / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# --- Core analytics imports from src/ ---
from fusion_trust import compute_trust
from operator_safety_layer import compute_osl
from sensor_latency import compute_latency_report
from adversary_pattern_engine import analyze_patterns

# --- File paths for overlays / brief ---
MINIMAP_FILE = SRC / "gui_minimap.json"
SOS_FILE = SRC / "gui_sos_overlay.json"
BRIEF_FILE = SRC / "docs" / "daily_mission_brief.txt"


# ---------------------------
# Helper loaders
# ---------------------------
def load_gui_minimap():
    """Safe loader for GUI minimap JSON."""
    if not MINIMAP_FILE.exists():
        return {"map": {}, "timestamp": None, "status": "no_data"}

    try:
        return json.loads(MINIMAP_FILE.read_text())
    except Exception as e:
        return {
            "map": {},
            "timestamp": None,
            "status": f"error_parsing_minimap: {e!r}",
        }


def load_sos_overlay():
    """Safe loader for SOS overlay JSON."""
    if not SOS_FILE.exists():
        return {"status": "no_data", "message": "No SOS overlay found."}

    try:
        return json.loads(SOS_FILE.read_text())
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error parsing SOS overlay: {e!r}",
        }


def load_daily_brief_text():
    """Safe loader for text daily mission brief."""
    if not BRIEF_FILE.exists():
        return "No daily mission brief found. Run daily_mission_brief.py."

    try:
        return BRIEF_FILE.read_text()
    except Exception as e:
        return f"[ERROR] Could not read daily_mission_brief.txt: {e!r}"


# ---------------------------
# Streamlit layout
# ---------------------------
def main():
    st.set_page_config(page_title="Ghost Lantern Labs — Spectral Dashboard", layout="wide")

    st.title("Ghost Lantern Labs — Spectral Dashboard")

    st.text(f"Base Directory: {BASE}")
    st.text(f"Loaded at: {datetime.now(timezone.utc).isoformat()}")

    st.markdown("---")

    # --- Top row: Trust + OSL + Latency ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Fusion Trust Score")
        try:
            st.json(compute_trust())
        except Exception as e:
            st.error(f"Fusion Trust failed: {e!r}")

    with col2:
        st.subheader("Operator Safety Layer")
        try:
            st.json(compute_osl())
        except Exception as e:
            st.error(f"OSL failed: {e!r}")

    with col3:
        st.subheader("Sensor Latency")
        try:
            st.json(compute_latency_report())
        except Exception as e:
            st.error(f"Latency report failed: {e!r}")

    st.markdown("---")

    # --- Second row: Minimap + SOS Overlay ---
    col4, col5 = st.columns(2)

    with col4:
        st.subheader("Fusion Mini-Map")
        st.json(load_gui_minimap())

    with col5:
        st.subheader("SOS Overlay")
        st.json(load_sos_overlay())

    st.markdown("---")

    # --- Adversary Pattern Engine ---
    st.subheader("Adversary Pattern Engine")
    try:
        st.json(analyze_patterns())
    except Exception as e:
        st.error(f"Adversary pattern engine failed: {e!r}")

    st.markdown("---")

    # --- Daily brief text at the bottom ---
    st.subheader("Daily Mission Brief (Text)")
    st.text(load_daily_brief_text())


if __name__ == "__main__":
    main()

