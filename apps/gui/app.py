"""
app.py — Ghost Lantern Labs Spectral Dashboard (v4, defensive)

This Streamlit app shows:

- Fusion Trust Score
- Operator Safety Layer
- Sensor Latency
- Fusion Mini-Map
- SOS Overlay
- GLL Readiness
- System Integrity

All imports are defensive so missing modules do NOT crash the GUI.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC = BASE_DIR / "src"


# ----- SAFE LOADERS ----------------------------------------------------------

def _safe_fusion_trust():
    try:
        import sys
        sys.path.insert(0, str(SRC))
        from fusion_trust import compute_trust  # type: ignore
        return compute_trust()
    except Exception as e:
        return {"error": f"fusion_trust unavailable: {e!r}"}


def _safe_osl():
    try:
        import sys
        sys.path.insert(0, str(SRC))
        from operator_safety_layer import compute_osl  # type: ignore
        return compute_osl()
    except Exception as e:
        return {"error": f"operator_safety_layer unavailable: {e!r}"}


def _safe_latency():
    try:
        import sys
        sys.path.insert(0, str(SRC))
        from sensor_latency import compute_latency_report  # type: ignore
        return compute_latency_report()
    except Exception as e:
        return {"status": "no_data", "error": str(e)}


def _safe_minimap():
    try:
        mm = SRC / "gui_minimap.json"
        if not mm.exists():
            return {"status": "no_data", "message": "Run minimap export first."}
        return json.loads(mm.read_text())
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _safe_sos_overlay():
    try:
        sos = SRC / "gui_sos_overlay.json"
        if not sos.exists():
            return {"status": "no_data", "message": "Run SOS overlay export first."}
        return json.loads(sos.read_text())
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _safe_gll_readiness():
    try:
        import sys
        sys.path.insert(0, str(SRC))
        from gll_readiness import compute_gll_readiness  # type: ignore
        return compute_gll_readiness()
    except Exception as e:
        return {"error": f"gll_readiness unavailable: {e!r}"}


def _safe_system_integrity():
    try:
        import sys
        sys.path.insert(0, str(SRC))
        from system_integrity import compute_system_integrity  # type: ignore
        return compute_system_integrity()
    except Exception as e:
        return {"error": f"system_integrity unavailable: {e!r}"}


# ----- STREAMLIT LAYOUT ------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Ghost Lantern Labs — Spectral Dashboard",
        layout="wide",
    )

    st.title("Ghost Lantern Labs — Spectral Dashboard")
    st.caption(f"Base Directory: {BASE_DIR}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fusion Trust Score")
        st.json(_safe_fusion_trust())

        st.subheader("Operator Safety Layer")
        st.json(_safe_osl())

        st.subheader("Sensor Latency")
        st.json(_safe_latency())

        st.subheader("GLL Readiness")
        st.json(_safe_gll_readiness())

    with col2:
        st.subheader("Fusion Mini-Map")
        st.json(_safe_minimap())

        st.subheader("SOS Overlay")
        st.json(_safe_sos_overlay())

        st.subheader("System Integrity")
        st.json(_safe_system_integrity())


if __name__ == "__main__":
    main()

