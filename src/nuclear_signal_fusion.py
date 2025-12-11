#!/usr/bin/env python3
"""
nuclear_signal_fusion.py

Ghost Lantern Labs – Nuclear Signal Fusion Engine
-------------------------------------------------

Purpose:
    Fuse nuclear early-warning context from multiple nuclear/AFTAC-surrounding
    products into a single, commander-readable summary.

    Inputs (if present):
        • src/docs/prelaunch_watchboard.json
        • src/docs/golden_dome_daily_watch.json

    Outputs:
        • src/docs/nuclear_signal_fusion.json
        • src/docs/nuclear_signal_fusion.txt

This module is deliberately heuristic and explainable — no black-box ML.
It is meant to show how GLL thinks about pre-launch nuclear indicators,
Golden Dome readiness, and sector “heat” in a way an AFTAC-style analyst
or commander can actually brief.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"

PRELAUNCH_PATH = DOCS_DIR / "prelaunch_watchboard.json"
DAILY_WATCH_PATH = DOCS_DIR / "golden_dome_daily_watch.json"

OUTPUT_JSON = DOCS_DIR / "nuclear_signal_fusion.json"
OUTPUT_TXT = DOCS_DIR / "nuclear_signal_fusion.txt"


def _safe_load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _extract_prelaunch_signals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull out what we can from the prelaunch watchboard.

    Expected (but not required) keys:
        • overall_alert_level
        • sectors: list of {name, status, notes, anomalies}
    """
    if not data:
        return {
            "present": False,
            "overall_alert_level": "UNKNOWN",
            "hot_sectors": [],
            "total_sectors": 0,
        }

    overall = data.get("overall_alert_level", "UNKNOWN")
    sectors = data.get("sectors") or []

    hot_sectors: List[Dict[str, Any]] = []
    for s in sectors:
        status = str(s.get("status", "")).upper()
        if status in ("WARN", "ELEVATED", "CRITICAL", "ALERT", "HOT"):
            hot_sectors.append(
                {
                    "name": s.get("name", "UNKNOWN"),
                    "status": s.get("status", "UNKNOWN"),
                    "notes": s.get("notes", ""),
                    "anomalies": s.get("anomalies", []),
                }
            )

    return {
        "present": True,
        "overall_alert_level": overall,
        "hot_sectors": hot_sectors,
        "total_sectors": len(sectors),
    }


def _extract_golden_dome_signals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull out usable readiness context from the Golden Dome Daily Watch.

    We don't assume a rigid schema; we look for common nuclear readiness fields.
    """
    if not data:
        return {
            "present": False,
            "readiness_level": "UNKNOWN",
            "drift_status": "UNKNOWN",
            "fusion_trust": None,
        }

    # Try several possible key names to avoid brittleness across versions
    readiness = (
        data.get("golden_dome_readiness")
        or data.get("readiness_level")
        or data.get("golden_dome_status")
        or "UNKNOWN"
    )

    drift = (
        data.get("drift_status")
        or data.get("golden_dome_drift_status")
        or "UNKNOWN"
    )

    fusion_trust = (
        data.get("fusion_trust_score")
        or data.get("fusion_trust")
        or None
    )

    return {
        "present": True,
        "readiness_level": readiness,
        "drift_status": drift,
        "fusion_trust": fusion_trust,
    }


def _assess_overall_risk(prelaunch: Dict[str, Any], dome: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very simple, explainable risk logic.

    Factors:
        • Prelaunch overall alert level and number of hot sectors
        • Golden Dome readiness level and drift
        • Fusion trust (if available)
    """
    reasons: List[str] = []
    level = "LOW"

    # Prelaunch
    alert = str(prelaunch.get("overall_alert_level", "UNKNOWN")).upper()
    hot_sectors = prelaunch.get("hot_sectors", [])
    num_hot = len(hot_sectors)

    if alert in ("CRITICAL", "SEVERE"):
        level = "HIGH"
        reasons.append(f"Prelaunch alert level is {alert}.")
    elif alert in ("ELEVATED", "WARN", "ALERT") and level != "HIGH":
        level = "MEDIUM"
        reasons.append(f"Prelaunch alert level is {alert}.")

    if num_hot >= 3:
        level = "HIGH"
        reasons.append(f"{num_hot} sectors flagged as HOT / WARN.")
    elif 0 < num_hot < 3 and level == "LOW":
        level = "MEDIUM"
        reasons.append(f"{num_hot} sectors showing elevated activity.")

    # Golden Dome readiness
    readiness = str(dome.get("readiness_level", "UNKNOWN")).upper()
    drift_status = str(dome.get("drift_status", "UNKNOWN")).upper()

    if readiness in ("RED", "CRITICAL"):
        level = "HIGH"
        reasons.append(f"Golden Dome readiness is {readiness}.")
    elif readiness in ("AMBER", "YELLOW") and level != "HIGH":
        if level == "LOW":
            level = "MEDIUM"
        reasons.append(f"Golden Dome readiness is {readiness}.")

    if drift_status in ("DEGRADED", "OUT_OF_TOLERANCE"):
        if level == "LOW":
            level = "MEDIUM"
        reasons.append(f"Golden Dome drift reported as {dift_status}.")

    # Fusion trust
    fusion_trust = dome.get("fusion_trust")
    if isinstance(fusion_trust, (int, float)):
        if fusion_trust < 40:
            # Low trust = we should be cautious in either direction
            reasons.append(
                f"Fusion trust score is low ({fusion_trust}). Nuclear picture may be unreliable."
            )

    if not reasons:
        reasons.append("No strong warning indicators detected in current nuclear products.")

    return {
        "risk_level": level,
        "reasons": reasons,
    }


def build_nuclear_signal_fusion() -> Dict[str, Any]:
    """
    Main entrypoint.

    Returns:
        {
            "json_path": str,
            "txt_path": str,
            "summary": {...}
        }
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    prelaunch_raw = _safe_load_json(PRELAUNCH_PATH)
    dome_raw = _safe_load_json(DAILY_WATCH_PATH)

    prelaunch = _extract_prelaunch_signals(prelaunch_raw)
    dome = _extract_golden_dome_signals(dome_raw)
    overall = _assess_overall_risk(prelaunch, dome)

    fusion_summary: Dict[str, Any] = {
        "inputs": {
            "prelaunch_watchboard_present": prelaunch["present"],
            "golden_dome_daily_watch_present": dome["present"],
            "prelaunch_watchboard_path": str(PRELAUNCH_PATH),
            "golden_dome_daily_watch_path": str(DAILY_WATCH_PATH),
        },
        "prelaunch_signals": prelaunch,
        "golden_dome_signals": dome,
        "overall_assessment": overall,
    }

    # Write JSON
    OUTPUT_JSON.write_text(json.dumps(fusion_summary, indent=2), encoding="utf-8")

    # Write TXT (commander-readable)
    lines: List[str] = []
    lines.append("GLL Nuclear Signal Fusion Summary")
    lines.append("================================")
    lines.append("")
    lines.append(f"Prelaunch watchboard present: {prelaunch['present']}")
    lines.append(f"Golden Dome daily watch present: {dome['present']}")
    lines.append("")
    lines.append("Prelaunch signals:")
    lines.append(f"  Overall alert level: {prelaunch.get('overall_alert_level', 'UNKNOWN')}")
    lines.append(f"  Hot sectors: {len(prelaunch.get('hot_sectors', []))}")
    for hs in prelaunch.get("hot_sectors", []):
        lines.append(
            f"    - {hs.get('name', 'UNKNOWN')} [{hs.get('status', 'UNKNOWN')}]: {hs.get('notes', '')}"
        )
    lines.append("")
    lines.append("Golden Dome signals:")
    lines.append(f"  Readiness level: {dome.get('readiness_level', 'UNKNOWN')}")
    lines.append(f"  Drift status: {dome.get('drift_status', 'UNKNOWN')}")
    lines.append(f"  Fusion trust: {dome.get('fusion_trust', 'N/A')}")
    lines.append("")
    lines.append("Overall assessment:")
    lines.append(f"  Risk level: {overall['risk_level']}")
    lines.append("  Reasons:")
    for r in overall["reasons"]:
        lines.append(f"    - {r}")
    lines.append("")

    OUTPUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return {
        "json_path": str(OUTPUT_JSON),
        "txt_path": str(OUTPUT_TXT),
        "summary": fusion_summary,
    }


if __name__ == "__main__":
    result = build_nuclear_signal_fusion()
    print("Nuclear Signal Fusion written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

