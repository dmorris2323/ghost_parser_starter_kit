"""
validation_harness_app.py

GLL Validation Harness (Operator UI)
- Live controls: difficulty + seed + optional pattern injection
- Runs fusion_validation_harness.run_synthetic_fusion_validation()
- Displays: baseline metrics, injected metrics, delta_vs_baseline, verdict
- Handles gate failures as readable signals (no engine logic changes)

Run from repo root:
  streamlit run src/apps/gui/validation_harness_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

# --- Ensure imports work when Streamlit runs from repo root ---
REPO_ROOT = Path(__file__).resolve().parents[3]  # .../parser_starter_kit
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fusion_validation_harness import run_synthetic_fusion_validation  # noqa: E402
from apps.gui.shared_gate_utils import parse_gate_runtime_error  # noqa: E402


DIFFICULTIES = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"]

# Keep this list conservative; users can type custom patterns too.
KNOWN_PATTERNS = [
    "NONE",
    "CROSS_DOMAIN_CONFUSION",
    "SENSOR_DROP_AND_SPIKE",
    "COMMS_DEGRADATION",
    "NOISE_FLOOD",
    "LOW_SLOW_DRIFT",
]


def _safe_get(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def _render_metric_block(title: str, metrics: Optional[Dict[str, Any]]) -> None:
    st.subheader(title)
    if not isinstance(metrics, dict):
        st.info("No metrics found.")
        return

    trust = metrics.get("trust_proxy")
    risk = metrics.get("risk_score")
    alerts = metrics.get("alerts", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("Trust Proxy", f"{trust:.2f}" if isinstance(trust, (int, float)) else str(trust))
    col2.metric("Risk Score", f"{risk:.2f}" if isinstance(risk, (int, float)) else str(risk))
    col3.metric("Alerts (Total)", str(_safe_get(alerts, "total", default="—")))

    with st.expander("Alert breakdown", expanded=False):
        st.json(alerts)


def _render_delta_block(delta: Optional[Dict[str, Any]]) -> None:
    st.subheader("Delta vs Baseline")
    if not isinstance(delta, dict):
        st.info("No delta_vs_baseline found.")
        return

    t = delta.get("trust_proxy_delta")
    r = delta.get("risk_score_delta")
    alerts_delta = delta.get("alerts_delta", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Δ Trust", f"{t:+.2f}" if isinstance(t, (int, float)) else str(t))
    col2.metric("Δ Risk", f"{r:+.2f}" if isinstance(r, (int, float)) else str(r))
    col3.metric("Δ Crit", str(_safe_get(alerts_delta, "crit", default="—")))
    col4.metric("Δ High", str(_safe_get(alerts_delta, "high", default="—")))

    with st.expander("Delta detail", expanded=False):
        st.json(delta)


def _call_validation(
    *,
    difficulty: str,
    seed: int,
    pattern_id: Optional[str],
    pattern_seed: int,
) -> Dict[str, Any]:
    """
    Calls the validation harness with a small compatibility fallback:
    If signature mismatches across iterations, we retry with fewer args.
    """
    kwargs: Dict[str, Any] = {"difficulty": difficulty, "seed": seed}
    if pattern_id and pattern_id.upper() != "NONE":
        kwargs["pattern_id"] = pattern_id
        kwargs["pattern_seed"] = pattern_seed

    try:
        return run_synthetic_fusion_validation(**kwargs)
    except TypeError:
        # Fallback: older harness might not accept pattern_seed
        if "pattern_seed" in kwargs:
            kwargs.pop("pattern_seed", None)
            return run_synthetic_fusion_validation(**kwargs)
        raise


def main() -> None:
    st.set_page_config(page_title="GLL Validation Harness", layout="wide")
    st.title("🧪 GLL Validation Harness (Operator UI)")
    st.caption("Safe: synthetic telemetry only. Gate failures are shown as signals (not crashes).")

    with st.sidebar:
        st.header("Run Controls")

        difficulty = st.selectbox("Difficulty", DIFFICULTIES, index=1)
        seed = st.number_input("Seed", min_value=0, max_value=999999, value=99, step=1)

        st.divider()
        st.subheader("Pattern Injection (Optional)")
        pattern_pick = st.selectbox("Pattern", KNOWN_PATTERNS, index=0)

        custom_pattern = st.text_input(
            "Custom pattern_id (optional)",
            value="",
            help="If provided, overrides the dropdown selection.",
        ).strip()

        pattern_id = custom_pattern or pattern_pick
        pattern_seed = st.number_input("Pattern seed", min_value=0, max_value=999999, value=99, step=1)

        st.divider()
        run_btn = st.button("▶ Run Validation", type="primary", use_container_width=True)

    if not run_btn:
        st.info("Set controls and click **Run Validation**.")
        return

    # --- Run ---
    with st.spinner("Running validation harness (this may take a few seconds)..."):
        try:
            report = _call_validation(
                difficulty=str(difficulty).upper(),
                seed=int(seed),
                pattern_id=str(pattern_id).upper() if pattern_id else None,
                pattern_seed=int(pattern_seed),
            )
        except RuntimeError as e:
            info = parse_gate_runtime_error(e)
            if info:
                st.error(f"❌ {info.gate_type}-GATE FAILED for context: **{info.context}**")
                st.code(info.message)
                if info.report_path:
                    st.warning(f"Open this integrity report and fix issues before re-running:\n\n`{info.report_path}`")
                else:
                    st.warning("Gate failure did not include a report path. Check docs/integrity for the latest run_gate_* file.")
                st.stop()
            # Not a gate error — surface raw
            st.exception(e)
            st.stop()
        except Exception as e:
            st.exception(e)
            st.stop()

    # --- Render summary ---
    verdict = report.get("verdict", {})
    status = verdict.get("status", "UNKNOWN")
    msg = verdict.get("message", "")

    if status in {"PASS", "OK"}:
        st.success(f"✅ Verdict: {status} — {msg}")
    elif status in {"WARN"}:
        st.warning(f"⚠️ Verdict: {status} — {msg}")
    else:
        st.error(f"❌ Verdict: {status} — {msg}")

    # --- Metrics blocks ---
    colA, colB = st.columns(2)
    with colA:
        _render_metric_block("Baseline Metrics", report.get("baseline_metrics"))
    with colB:
        _render_metric_block("Injected Metrics", report.get("injected_metrics"))

    _render_delta_block(report.get("delta_vs_baseline"))

    # --- Key details ---
    with st.expander("Inputs / Paths", expanded=False):
        st.json(report.get("inputs", {}))
        st.json(report.get("paths", {}))

    with st.expander("Pattern Injection Details", expanded=False):
        st.json(report.get("pattern_injection", {}))

    with st.expander("Gate Results (if present in report)", expanded=False):
        gates = report.get("gates") or report.get("gate_results") or {}
        st.json(gates)

    with st.expander("Full Validation Report (JSON)", expanded=False):
        st.json(report)

    # Optional: make it easy to copy the latest report path quickly
    latest_json = _safe_get(report, "paths", "json_latest", default="")
    if isinstance(latest_json, str) and latest_json:
        st.caption(f"Latest report: `{latest_json}`")


if __name__ == "__main__":
    main()

