#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ghost Parser GUI
Streamlit-based interface for parsing, fusing, and reporting sensor logs.
"""

import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime
import io
import time
import os
import sys

# allow ghost_parser imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ghost_parser import parse_lines, load_aois


# UI SETUP
st.set_page_config(page_title="Ghost Parser GUI", layout="wide")
st.title("🛰️ Ghost Parser — Operational Console")
st.caption("Upload logs → parse → analyze → brief → export")


# INPUT PANELS
left, right = st.columns(2)

with left:
    st.subheader("Log Input")
    log_file = st.file_uploader(
        "Upload seismic/RF log (.log/.txt)",
        type=["log", "txt"],
        key="log_file_upload"
    )

    text_area = st.text_area("Or paste raw lines", height=150)

with right:
    st.subheader("AOI Input (optional)")
    aoi_file = st.file_uploader("Upload AOI JSON", type=["json"], key="aoi_file_upload")
    if aoi_file:
        try:
            aois = json.loads(aoi_file.getvalue().decode("utf-8"))
            st.success(f"Loaded {len(aois)} AOI areas")
        except Exception as e:
            st.error(f"AOI load error: {e}")
            aois = {}
    else:
        aois = {}


# THRESHOLDS
left2, right2 = st.columns(2)

with left2:
    preset = st.selectbox("Threshold Preset", ["Default", "Strict", "Loose"], key="preset")
with right2:
    max_depth_km = st.number_input("Max Depth (km)", value=2.5, step=0.1, min_value=0.0, key="max_depth_km")
    min_mag      = st.number_input("Min Magnitude", value=3.5, step=0.1, min_value=0.0, key="min_mag")
    max_mag      = st.number_input("Max Magnitude", value=6.5, step=0.1, min_value=0.0, key="max_mag")


# RUN BUTTON
run_parse = st.button("🚀 Run Parser", use_container_width=True)


# MAIN EXECUTION
if run_parse:

    # load text lines
    if log_file:
        lines = log_file.getvalue().decode("utf-8").splitlines()
    elif text_area.strip():
        lines = text_area.splitlines()
    else:
        st.warning("Upload a log or paste text before running.")
        st.stop()

    with st.spinner("Parsing logs..."):
        rows = parse_lines(lines, aois, max_depth_km, min_mag, max_mag)
        df = pd.DataFrame(rows)

    if df.empty:
        st.warning("No valid rows parsed.")
        st.stop()

    # METRICS
    flagged_count = int(df.get("Flagged", False).astype(bool).sum())
    st.metric("Parsed events", len(df))
    st.metric("Flagged", flagged_count)

    st.dataframe(df, use_container_width=True, hide_index=True)
    from src.fusion_aoi import fuse_with_aoi

    if st.button("🔬 Run AOI Fusion Check"):
        try:
            with st.spinner("Running AOI Fusion..."):
                fusion_df = fuse_with_aoi("parsed_gui.csv", "aoi.json")
                st.success(f"Fusion complete — {fusion_df['Fused'].sum()} AOI hits.")
                st.dataframe(fusion_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Fusion step failed: {e}")


    # AUTO-CHART BLOCK
    try:
        if "Match_confidence" in df.columns and df["Match_confidence"].notna().any():
            st.subheader("Match Confidence Distribution")
            fig, ax = plt.subplots()
            df["Match_confidence"].astype(float).plot(kind="hist", bins=10, ax=ax)
            ax.set_xlabel("Confidence (0–100)")
            st.pyplot(fig)
        else:
            st.subheader("Reason Counts (Parser)")
            reason_counts = (
                df.get("Reasons", pd.Series([], dtype=str))
                  .fillna("")
                  .replace("", "(none)")
                  .value_counts()
            )
            st.bar_chart(reason_counts)
    except Exception as e:
        st.warning(f"Chart skipped: {e}")


    # MARKDOWN REPORT + EXPORTS
    try:
        parsed_count = len(df)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")
        aoi_keys = ", ".join(list(aois.keys())) if aois else "None"

        md = []
        md.append("Ghost Lantern Labs — Operational Parse Report")
        md.append(f"# Run at {now}")
        md.append("")
        md.append("**Run Summary**")
        md.append(f"- Parsed events: **{parsed_count}**")
        md.append(f"- Flagged: **{flagged_count}**")
        md.append(f"- AOIs: {aoi_keys}")
        md.append("")

        md.append("**Sample Flagged Rows**")
        sample = df[df.get("Flagged", False) == True].head(5)
        if sample.empty:
            md.append("_No flagged rows in sample._")
        else:
            md.append(sample.to_markdown(index=False))

        md_bytes = "\n".join(md).encode("utf-8")

        csv_bytes = df.to_csv(index=False).encode("utf-8")

        jsonl_buf = io.BytesIO()
        for _, r in df.iterrows():
            jsonl_buf.write((json.dumps(r.to_dict()) + "\n").encode("utf-8"))
        jsonl_bytes = jsonl_buf.getvalue()

        c1, c2, c3 = st.columns(3)
        c1.download_button(
            "📝 Report (Markdown)",
            data=md_bytes, file_name="ghost_report.md",
            mime="text/markdown", use_container_width=True
        )
        c2.download_button(
            "⬇️ Parsed CSV",
            data=csv_bytes, file_name="parsed.csv",
            mime="text/csv", use_container_width=True
        )
        c3.download_button(
            "⬇️ Parsed JSONL",
            data=jsonl_bytes, file_name="parsed.jsonl",
            mime="application/json", use_container_width=True
        )

    except Exception as e:
        st.warning(f"Report export skipped: {e}")


st.markdown("---")
st.caption("© 2025 Ghost Lantern Labs — Prototype Operational Console")

