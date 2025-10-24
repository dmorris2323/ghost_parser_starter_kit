#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ghost Parser GUI
Streamlit-based interface for parsing, fusing, and reporting sensor logs.
"""

import os
import sys
import time
from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Ensure imports resolve ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ghost_parser import parse_lines, load_aois


# ==========================================================
# Function: Report + Downloads Renderer
# ==========================================================
def render_report_and_downloads(df, aois, preset, max_depth_km, min_mag, max_mag):
    """Render chart + one-click Markdown report + CSV/MD download buttons."""

    try:
        if "Match_confidence" in df.columns:
            st.subheader("Match Confidence (Fusion)")
            fig, ax = plt.subplots()
            df["Match_confidence"].plot(
                kind="hist",
                bins=10,
                ax=ax,
                title="Match Confidence Distribution"
            )
            ax.set_xlabel("Confidence (0–100)")
            st.pyplot(fig)
        else:
            st.subheader("Reason Counts (Parser)")
            reason_counts = df["Reasons"].fillna("").replace("", "(none)").value_counts()
            st.bar_chart(reason_counts)
    except Exception as e:
        st.warning(f"Could not render chart: {e}")

    parsed_count = len(df)
    flagged_count = int(df["Flagged"].sum()) if "Flagged" in df.columns else 0
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")

    aoi_keys = ", ".join(list(aois.keys())) if aois else "None"
    preset_line = f"Preset: {preset} | Depth≤{max_depth_km}km | Mag {min_mag}–{max_mag}"

    reasons_top = {}
    if "Reasons" in df.columns:
        reasons_top = df["Reasons"].fillna("").replace("", "(none)").value_counts().to_dict()

    md = []
    md.append(f"# Ghost Parser Report — {now}")
    md.append("")
    md.append("**Run Summary**")
    md.append(f"- Parsed events: **{parsed_count}**")
    md.append(f"- Flagged: **{flagged_count}**")
    md.append(f"- {preset_line}")
    md.append(f"- AOIs: {aoi_keys}")
    md.append("")
    md.append("**Reason counts:**")
    if reasons_top:
        for k, v in reasons_top.items():
            md.append(f"- {k or '(none)'}: {v}")
    else:
        md.append("- (no reason field present)")
    md.append("")

    md.append("**Sample flagged rows (first 5):**")
    md.append("")
    if "Flagged" in df.columns:
        sample = df[df["Flagged"] == True].head(5)
    else:
        sample = df.head(5)
    try:
        if sample.empty:
            md.append("_No flagged rows in sample._")
        else:
            md.append(sample.to_markdown(index=False))
    except Exception:
        md.append("_Markdown table unavailable (install `tabulate`). Showing CSV rows:_")
        md.append(sample.to_csv(index=False))

    md_bytes = "\n".join(md).encode("utf-8")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="parsed_gui.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "📝 Download Report (Markdown)",
            data=md_bytes,
            file_name=f"ghost_parser_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ==========================================================
# Streamlit App Layout
# ==========================================================
st.set_page_config(page_title="Ghost Parser GUI", layout="wide")
st.title("🛰️ Ghost Parser — Operational Parse Console")
st.caption("Upload logs → set thresholds → parse → review flags → download results")

left, right = st.columns(2)

# --- File Uploads ---
with left:
    log_file = st.file_uploader("Upload raw log (.log or .txt)", type=["log", "txt"])
with right:
    aoi_file = st.file_uploader("Upload AOI (.json)", type=["json"])

preset = st.selectbox("Select preset", ["Default", "Seismic", "RF Fusion"])
max_depth_km = st.slider("Max depth (km)", 0.0, 10.0, 2.5, 0.5)
min_mag = st.slider("Min magnitude", 0.0, 10.0, 3.5, 0.5)
max_mag = st.slider("Max magnitude", 0.0, 10.0, 9.5, 0.5)

# --- Parse Action ---
if st.button("🚀 Run Parser"):
    if not log_file:
        st.warning("Please upload a log file first.")
    else:
        with st.spinner("Parsing logs..."):
            lines = log_file.read().decode("utf-8").splitlines()
            aois = load_aois(aoi_file) if aoi_file else {}

            df = parse_lines(lines)
            if df.empty:
                st.error("No valid data parsed.")
            else:
                st.success("Parsing complete ✅")
                st.metric("Parsed events", len(df))
                if "Flagged" in df.columns:
                    st.metric("Flagged", int(df["Flagged"].sum()))

                st.dataframe(df, use_container_width=True, hide_index=True)

                render_report_and_downloads(
                    df=df,
                    aois=aois,
                    preset=preset,
                    max_depth_km=max_depth_km,
                    min_mag=min_mag,
                    max_mag=max_mag,
                )

st.markdown("---")
st.caption("Ghost Lantern Labs © 2025 — Prototype Parser GUI")

