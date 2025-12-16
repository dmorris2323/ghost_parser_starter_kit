from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st


# -----------------------------
# Paths (read-only)
# -----------------------------
BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"


def _safe_read_text(p: Path) -> str:
    try:
        if not p.exists():
            return "⚠️ File not found."
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"⚠️ Error reading file: {e}"


def _safe_read_json(p: Path) -> dict:
    try:
        if not p.exists():
            return {"error": "file not found"}
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(
    page_title="Ghost Lantern Labs — Demo Shell",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🦉 Ghost Lantern Labs — Demo Dashboard")
st.caption(
    "READ-ONLY • DEMO-SAFE • Assessment is probabilistic and bounded; operator judgment applies."
)

st.sidebar.header("Demo Navigation")

view = st.sidebar.radio(
    "Select View",
    [
        "Commander Brief",
        "Week-3 Operator Summary",
        "Legal Case Snapshot (Shari)",
        "Validation & Gates",
        "Mobile Demo Manifest",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Loaded at: {_utc_now()}")


# -----------------------------
# Commander Brief
# -----------------------------
if view == "Commander Brief":
    st.header("📘 Commander Brief")

    txt = _safe_read_text(BRIEFS_DIR / "commander_brief_latest.txt")
    st.text_area(
        "Commander Brief (Latest)",
        txt,
        height=600,
    )

# -----------------------------
# Operator Summary
# -----------------------------
elif view == "Week-3 Operator Summary":
    st.header("🧭 Week-3 Operator Summary")

    txt = _safe_read_text(BRIEFS_DIR / "week3_operator_summary_latest.txt")
    st.text_area(
        "Operator Summary",
        txt,
        height=400,
    )

# -----------------------------
# Legal Case Snapshot
# -----------------------------
elif view == "Legal Case Snapshot (Shari)":
    st.header("⚖️ Legal Case Snapshot")

    txt = _safe_read_text(BRIEFS_DIR / "legal_case_snapshot_latest.txt")
    st.text_area(
        "Legal Snapshot (Demo / Training)",
        txt,
        height=450,
    )

    st.info(
        "This mirrors legal/collections reasoning. "
        "It does NOT automate decisions. Operator judgment applies."
    )

# -----------------------------
# Validation & Gates
# -----------------------------
elif view == "Validation & Gates":
    st.header("🧪 Validation & Gates")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fusion Core Regression")
        data = _safe_read_json(
            VALIDATION_DIR / "fusion_core_regression_latest.json"
        )
        st.json(data)

    with col2:
        st.subheader("Week-3 Demo Pack Gate")
        data = _safe_read_json(
            VALIDATION_DIR / "week3_demo_pack_gate_latest.json"
        )
        st.json(data)

# -----------------------------
# Mobile Demo Manifest
# -----------------------------
elif view == "Mobile Demo Manifest":
    st.header("📱 Mobile Demo Manifest")

    data = _safe_read_json(
        BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
    )
    st.json(data)

    st.success(
        "This view confirms everything required for mobile / tablet demo is present."
    )


st.markdown("---")
st.caption(
    "Ghost Lantern Labs • Demo Shell • No state changes • No AI execution • No cloud calls"
)


