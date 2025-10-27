#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ghost Parser GUI
Streamlit-based interface for parsing, fusing, and reporting sensor logs.
"""

import json
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

# --- INPUTS ---
left, right = st.columns(2)
with left:
    log_file  = st.file_uploader("Raw log", type=["log","txt"], key="raw_log")
    raw_text  = st.text_area("...or paste lines", height=160, key="raw_text")
with right:
    aoi_file  = st.file_uploader("AOI (aoi.json) [optional]", type=["json"], key="aoi_json")
    max_depth_km = st.number_input("Max depth (km)", value=2.5, step=0.1, min_value=0.0, key="max_depth_km")
    min_mag      = st.number_input("Min magnitude",  value=3.5, step=0.1, min_value=0.0, key="min_mag")
    max_mag      = st.number_input("Max magnitude",  value=6.5, step=0.1, min_value=0.0, key="max_mag")
    run_parse    = st.button("🚀 Run Parser", type="primary", use_container_width=True)

# --- COLLECT LINES (outside the button so they're available when you click it) ---
lines = []
if log_file is not None:
    try:
        lines = log_file.getvalue().decode("utf-8", errors="ignore").splitlines()
    except Exception as e:
        st.error(f"Could not read log file: {e}")
elif raw_text.strip():
    lines = raw_text.splitlines()

# --- SAFE AOI LOAD (outside the button so aois is always defined) ---
aois = {}
if aoi_file is not None:
    try:
        aois = json.loads(aoi_file.getvalue().decode("utf-8"))
        st.success(f"Loaded {len(aois)} AOI boxes")
    except Exception as e:
        st.error(f"AOI load error: {e}")
        aois = {}

# --- RUN PARSER ---
if run_parse:
    if not lines:
        st.warning("Please upload a log file or paste lines first.")
    else:
        with st.spinner("Parsing logs..."):
            rows = parse_lines(lines, aois, max_depth_km, min_mag, max_mag)
            df = pd.DataFrame(rows)

            # --- Display metrics ---
            flagged_count = int(df["Flagged"].astype(bool).sum()) if "Flagged" in df.columns else 0
            st.metric("Parsed events", len(df))
            st.metric("Flagged", flagged_count)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # --- Quick chart (auto-switch) ---
            try:
                if "Match_confidence" in df.columns and df["Match_confidence"].notna().any():
                    st.subheader("Match Confidence (Fusion)")
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots()
                    df["Match_confidence"].astype(float).plot(
                        kind="hist", bins=10, ax=ax, title="Match Confidence Distribution"
                    )
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
                    if len(reason_counts) > 0:
                        st.bar_chart(reason_counts)
                    else:
                        st.caption("No reasons to chart yet.")
            except Exception as e:
                st.warning(f"Chart skipped: {e}")

            # --- Safe default for preset (if not defined earlier) ---
            preset = st.session_state.get("preset", "Default")

            # --- Generate report and downloads ---
            render_report_and_downloads(
                df=df,
                aois=aois,
                preset=preset,
                max_depth_km=max_depth_km,
                min_mag=min_mag,
                max_mag=max_mag,
            )

# --- FOOTER ---
st.markdown("---")
st.caption("Ghost Lantern Labs © 2025 — Prototype Parser GUI")

