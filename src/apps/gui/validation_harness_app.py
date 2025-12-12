# src/apps/gui/validation_harness_app.py
from __future__ import annotations

import sys
from pathlib import Path
import json
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = str((REPO_ROOT / "src").resolve())
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from fusion_validation_harness import run_synthetic_fusion_validation


def main():
    st.set_page_config(
        page_title="GLL Validation Harness",
        layout="wide",
    )

    st.title("GLL Validation Harness — Live Delta Viewer")
    st.caption(
        "Synthetic-only validation. Safe for training, demos, and instructor review."
    )

    # -------------------------------
    # Controls
    # -------------------------------
    with st.sidebar:
        st.header("Scenario Controls")

        difficulty = st.selectbox(
            "Difficulty",
            ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"],
            index=1,
        )

        pattern = st.selectbox(
            "Pattern Injection",
            [
                "NONE",
                "CROSS_DOMAIN_CONFUSION",
                "SIGNAL_DRIFT",
                "FALSE_POSITIVE_STORM",
            ],
            index=0,
        )

        seed = st.number_input("Random Seed", min_value=1, max_value=9999, value=42)

        run_btn = st.button("Run Validation")

    # -------------------------------
    # Execution
    # -------------------------------
    if not run_btn:
        st.info("Configure difficulty and pattern injection, then run validation.")
        return

    pattern_id = None if pattern == "NONE" else pattern

    with st.spinner("Running synthetic validation…"):
        report = run_synthetic_fusion_validation(
            difficulty=difficulty,
            seed=int(seed),
            pattern_id=pattern_id,
            pattern_seed=int(seed),
        )

    # -------------------------------
    # Summary
    # -------------------------------
    verdict = report.get("verdict", {})
    st.subheader("Verdict")
    st.metric(
        "Status",
        verdict.get("status", "UNKNOWN"),
        verdict.get("message", ""),
    )

    # -------------------------------
    # Metrics
    # -------------------------------
    st.subheader("Baseline vs Injected Metrics")

    base = report.get("baseline_metrics", {})
    inj = report.get("injected_metrics", {})
    delta = report.get("delta_vs_baseline", {})

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Trust Proxy",
        f"{inj.get('trust_proxy', 0):.2f}",
        f"{delta.get('trust_proxy_delta', 0):+.2f}",
    )

    col2.metric(
        "Risk Score",
        f"{inj.get('risk_score', 0):.2f}",
        f"{delta.get('risk_score_delta', 0):+.2f}",
    )

    col3.metric(
        "Total Alerts",
        inj.get("alerts", {}).get("total", 0),
        delta.get("alerts_delta", {}).get("total", 0),
    )

    # -------------------------------
    # Alert Breakdown
    # -------------------------------
    st.subheader("Alert Pressure Change")

    alerts_delta = delta.get("alerts_delta", {})
    st.json(alerts_delta)

    # -------------------------------
    # Pattern Details
    # -------------------------------
    if pattern_id:
        st.subheader("Injected Pattern Details")
        st.json(report.get("pattern_injection", {}))

    # -------------------------------
    # Raw Report (Expandable)
    # -------------------------------
    with st.expander("Full Validation Report (JSON)"):
        st.json(report)


if __name__ == "__main__":
    main()

