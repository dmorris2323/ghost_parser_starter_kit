"""
daily_mission_brief.py — Clean, Defensive Mission Brief Builder (v4)

This rebuilds the daily mission brief in a defensive way,
using your existing modules WHEN AVAILABLE, but never crashing
if something is missing.

Outputs:
- docs/daily_mission_brief.txt (text brief)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DOCS = Path(__file__).resolve().parent / "docs"


# ---- SAFE HELPERS -----------------------------------------------------------

def _safe_pipeline_health() -> Any:
    try:
        from pipeline_health import evaluate_pipeline_health  # type: ignore
        return evaluate_pipeline_health()
    except Exception:
        return "Pipeline health module unavailable."


def _safe_sensor_readiness() -> str:
    try:
        from sensor_readiness_brief import build_readiness_brief  # type: ignore
        return build_readiness_brief()
    except Exception:
        return "Sensor readiness module unavailable."


def _safe_sensor_reliability() -> Any:
    try:
        from sensor_reliability import compute_reliability_summary  # type: ignore
        return compute_reliability_summary()
    except Exception:
        return "Sensor reliability module unavailable."


def _safe_reliability_trend() -> Any:
    try:
        from reliability_trend import compute_trend  # type: ignore
        return compute_trend()
    except Exception:
        return {"trend": "no_data"}


def _safe_fusion_trust() -> Any:
    try:
        from fusion_trust import compute_trust  # type: ignore
        return compute_trust()
    except Exception:
        return "Fusion trust engine unavailable."


def _safe_osl() -> Any:
    try:
        from operator_safety_layer import compute_osl  # type: ignore
        return compute_osl()
    except Exception:
        return "Operator Safety Layer unavailable."


def _safe_latency() -> Any:
    try:
        from sensor_latency import compute_latency_report  # type: ignore
        return compute_latency_report()
    except Exception:
        return {"status": "no_data"}


def _safe_drift() -> Any:
    try:
        from golden_dome_drift import compute_drift  # type: ignore
        return compute_drift()
    except Exception:
        return {"status": "no_data"}


def _safe_nuclear_snapshot() -> Any:
    try:
        from golden_dome_snapshot import build_snapshot  # type: ignore
        return build_snapshot()
    except Exception:
        return "Nuclear readiness snapshot unavailable."


def _safe_crisis_status() -> str:
    try:
        from crisis_mode_flag import status as crisis_status  # type: ignore
        return crisis_status()
    except Exception:
        return "UNKNOWN"


def _safe_operator() -> str:
    try:
        from operator_identity import get_identity  # type: ignore
        return get_identity()
    except Exception:
        return "Unknown Operator"


def _safe_gll_readiness() -> Dict[str, Any] | str:
    try:
        from gll_readiness import compute_gll_readiness  # type: ignore
        return compute_gll_readiness()
    except Exception:
        return "GLL readiness module unavailable."


def _safe_system_integrity() -> Dict[str, Any] | str:
    try:
        from system_integrity import compute_system_integrity  # type: ignore
        return compute_system_integrity()
    except Exception:
        return "System integrity module unavailable."


# ---- CORE BRIEF -------------------------------------------------------------

def build_mission_brief() -> str:
    lines: list[str] = []

    operator = _safe_operator()
    crisis = _safe_crisis_status()

    lines.append("=== GHOST LANTERN LABS — DAILY MISSION BRIEF ===")
    lines.append(f"Operator: {operator}")
    lines.append(f"Crisis Mode: {crisis}")
    lines.append("")

    # Pipeline health
    lines.append("=== PIPELINE HEALTH ===")
    ph = _safe_pipeline_health()
    if isinstance(ph, dict):
        lines.append(json.dumps(ph, indent=2))
    else:
        lines.append(str(ph))
    lines.append("")

    # Sensor readiness
    lines.append("=== SENSOR READINESS BRIEF ===")
    sr = _safe_sensor_readiness()
    lines.append(str(sr))
    lines.append("")

    # Sensor reliability
    lines.append("=== SENSOR RELIABILITY SUMMARY ===")
    rel = _safe_sensor_reliability()
    if isinstance(rel, dict):
        lines.append(json.dumps(rel, indent=2))
    else:
        lines.append(str(rel))
    lines.append("")

    # Reliability trend
    lines.append("=== RELIABILITY TREND ===")
    trend = _safe_reliability_trend()
    if isinstance(trend, dict):
        lines.append(json.dumps(trend, indent=2))
    else:
        lines.append(str(trend))
    lines.append("")

    # Fusion trust
    lines.append("=== FUSION TRUST SCORE ===")
    ft = _safe_fusion_trust()
    if isinstance(ft, dict):
        lines.append(json.dumps(ft, indent=2))
    else:
        lines.append(str(ft))
    lines.append("")

    # Operator Safety Layer
    lines.append("=== OPERATOR SAFETY LAYER ===")
    osl = _safe_osl()
    if isinstance(osl, dict):
        lines.append(json.dumps(osl, indent=2))
    else:
        lines.append(str(osl))
    lines.append("")

    # Sensor latency
    lines.append("=== SENSOR LATENCY ===")
    lat = _safe_latency()
    if isinstance(lat, dict):
        lines.append(json.dumps(lat, indent=2))
    else:
        lines.append(str(lat))
    lines.append("")

    # Golden Dome Drift
    lines.append("=== GOLDEN DOME DRIFT ===")
    drift = _safe_drift()
    if isinstance(drift, dict):
        lines.append(json.dumps(drift, indent=2))
    else:
        lines.append(str(drift))
    lines.append("")

    # Nuclear readiness
    lines.append("=== NUCLEAR READINESS SNAPSHOT ===")
    nuke = _safe_nuclear_snapshot()
    if isinstance(nuke, dict):
        lines.append(json.dumps(nuke, indent=2))
    else:
        lines.append(str(nuke))
    lines.append("")

    # GLL readiness
    lines.append("=== GLL READINESS SCORE ===")
    gllr = _safe_gll_readiness()
    if isinstance(gllr, dict):
        lines.append(json.dumps(gllr, indent=2))
    else:
        lines.append(str(gllr))
    lines.append("")

    # System integrity
    lines.append("=== SYSTEM INTEGRITY ===")
    integ = _safe_system_integrity()
    if isinstance(integ, dict):
        lines.append(json.dumps(integ, indent=2))
    else:
        lines.append(str(integ))
    lines.append("")

    return "\n".join(lines)


def write_daily_brief(path: str | Path = "docs/daily_mission_brief.txt") -> str:
    DOCS.mkdir(parents=True, exist_ok=True)
    txt = build_mission_brief()
    p = DOCS / Path(path).name
    p.write_text(txt)
    return str(p)


if __name__ == "__main__":
    print(write_daily_brief())

