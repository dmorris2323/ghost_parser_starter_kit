# src/apps/gui/validation_harness_app.py
from __future__ import annotations

import sys
from pathlib import Path
import json
import streamlit as st

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fusion_validation_harness import run_synthetic_fusion_validation  # type: ignore
from gll_run_gates import run_gates  # type: ignore


def main() -> None:
    st.set_page_config(page_title="GLL Validation Harness", layout="wide")
    st.title("GLL Validation Harness")
    st.caption("Baseline vs Injected • Live deltas • Gate-aware")

    # ── Controls ─────────────────────────────────────────────
    st.sidebar.header("Validation Controls")

    difficulty = st.sidebar.selectbox(
        "Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=2
    )

    pattern_id = st.sidebar.selectbox(
        "Pattern Injection",
        [
            "NONE",
            "CROSS_DOMAIN_CONFUSION",
            "SENSOR_DRIFT",
            "ALERT_FLOOD",
        ],
        index=1,
    )

    seed = st.sidebar.number_input("Base seed", value=42, step=1)
    pattern_seed = st.sidebar.number_input("Pattern seed", value=99, step=1)

    run_clicked = st.sidebar.button("▶ Run Validation", use_container_width=True)

    # ── PRE-GATE ──────────────────────────────────────────────
    st.subheader("PRE-GATE STATUS")

    pre_gate = run_gates(
        gate_type="PRE",
        context="validation_harness_ui",
        update_baselines=False,
        raise_on_fail=False,   # 🔑 UI-safe
    )

    if not pre_gate["ok"]:
        st.error("PRE-GATE FAILED — validation blocked")
        st.code(json.dumps(pre_gate, indent=2), language="json")
        st.stop()
    else:
        st.success("PRE-GATE PASSED")

    # ── Validation Execution ──────────────────────────────────
    if not run_clicked:
        st.info("Configure options and click **Run Validation**.")
        st.stop()

    pattern = None if pattern_id == "NONE" else pattern_id

    with st.spinner("Running synthetic fusion validation…"):
        report = run_synthetic_fusion_validation(
            difficulty=difficulty,
            seed=int(seed),
            pattern_id=pattern,
            pattern_seed=int(pattern_seed) if pattern else None,
        )

    # ── Results ───────────────────────────────────────────────
    st.subheader("Validation Verdict")
    verdict = report.get("verdict", {})
    status = verdict.get("status", "UNKNOWN")

    if status == "PASS":
        st.success(verdict.get("message"))
    elif status == "WARN":
        st.warning(verdict.get("message"))
    else:
        st.error(verdict.get("message"))

    # ── Metrics ───────────────────────────────────────────────
    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown("### Baseline")
        st.json(report.get("baseline_metrics", {}))

    with colB:
        st.markdown("### Injected")
        st.json(report.get("injected_metrics", {}))

    with colC:
        st.markdown("### Δ vs Baseline")
        st.json(report.get("delta_vs_baseline", {}))

    # ── Pattern Details ───────────────────────────────────────
    st.subheader("Pattern Injection")
    st.json(report.get("pattern_injection", {}))

    # ── Real Module Health ────────────────────────────────────
    st.subheader("Real Module Integration")
    st.json(report.get("real_module_attempts", {}))

    # ── Output Paths ──────────────────────────────────────────
    st.subheader("Artifacts")
    st.json(report.get("paths", {}))


if __name__ == "__main__":
    main()

