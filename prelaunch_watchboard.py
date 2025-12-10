#!/usr/bin/env python3
"""
prelaunch_watchboard.py

Day 66 – Ghost Lantern Labs
Pre-Launch Early Warning Hardening – Option C

This module builds a robust "Pre-Launch ISR Watchboard" that fuses:

- Pre-launch signal analysis (from prelaunch_signals_analyzer)
- Crisis mode flag (if available)
- Basic nuclear readiness context (if available)

Outputs (defensive, commander-grade):
    docs/prelaunch_watchboard.json
    docs/prelaunch_watchboard.txt

The JSON schema is stable and explainable:

{
  "generated_at": "...",
  "early_warning_score": float (0–100),
  "early_warning_level": "STEADY" | "TENSE" | "ALERT" | "CRITICAL",
  "crisis_mode": bool,
  "sensor_concurrence_score": float,
  "ems_spike_score": float,
  "latency_risk_score": float,
  "pattern_anomaly_score": float,
  "signals": [...],
  "rationale": [...],
  "inputs_present": {...}
}

This is designed to degrade gracefully if upstream artifacts are missing.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from prelaunch_signals_analyzer import analyze_prelaunch_signals

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

CRISIS_FLAG_LOCATIONS = [
    os.path.join(BASE_DIR, "config", "crisis_mode_flag.txt"),
    os.path.join(DOCS_DIR, "crisis_mode_flag.txt"),
]


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _load_crisis_flag() -> bool:
    """
    Reads crisis_mode flag from known locations.
    If not found, returns False.
    """
    for path in CRISIS_FLAG_LOCATIONS:
        txt = _safe_read_text(path)
        if txt is None:
            continue
        val = txt.strip().lower()
        if "on" in val or "true" in val or val == "1":
            return True
        if "off" in val or "false" in val or val == "0":
            return False
    return False


def _determine_level(score: float, crisis_on: bool) -> str:
    """
    Map an overall pre-launch signal score plus crisis flag to a 4-level ladder.
    """

    # Score-only mapping
    if score < 20.0:
        base_level = "STEADY"
    elif score < 45.0:
        base_level = "TENSE"
    elif score < 70.0:
        base_level = "ALERT"
    else:
        base_level = "CRITICAL"

    # Crisis flag can bump one notch up
    if crisis_on and base_level == "TENSE":
        return "ALERT"
    if crisis_on and base_level == "ALERT":
        return "CRITICAL"
    return base_level


def build_prelaunch_watchboard() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    # Core signal analysis
    signal_picture = analyze_prelaunch_signals()
    crisis_on = _load_crisis_flag()

    early_warning_score = signal_picture.get("overall_signal_score", 0.0)
    level = _determine_level(early_warning_score, crisis_on)

    rationale: List[str] = []
    rationale.append(
        f"Composite pre-launch signal score: {early_warning_score:.1f}/100 (crisis_mode={crisis_on})."
    )

    # Provide human-readable rationales derived from individual scores
    sensor_conc = signal_picture.get("sensor_concurrence_score", 0.0)
    ems_spike = signal_picture.get("ems_spike_score", 0.0)
    latency_risk = signal_picture.get("latency_risk_score", 0.0)
    pattern_anom = signal_picture.get("pattern_anomaly_score", 0.0)

    if sensor_conc > 0.0:
        rationale.append(
            f"Multi-sensor concurrence indicators contribute ~{sensor_conc:.1f}/100 to pre-launch pressure."
        )
    if ems_spike > 0.0:
        rationale.append(
            f"EMS/RF anomalies contribute ~{ems_spike:.1f}/100 to pre-launch pressure."
        )
    if latency_risk > 0.0:
        rationale.append(
            f"Sensor latency risk contributes ~{latency_risk:.1f}/100 to pre-launch uncertainty."
        )
    if pattern_anom > 0.0:
        rationale.append(
            f"Adversary pattern anomalies contribute ~{pattern_anom:.1f}/100 to pre-launch concern."
        )

    if not rationale:
        rationale.append("No meaningful pre-launch signals detected from available artifacts.")

    watchboard: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "early_warning_score": early_warning_score,
        "early_warning_level": level,
        "crisis_mode": crisis_on,
        "sensor_concurrence_score": sensor_conc,
        "ems_spike_score": ems_spike,
        "latency_risk_score": latency_risk,
        "pattern_anomaly_score": pattern_anom,
        "signals": signal_picture.get("signals", []),
        "rationale": rationale,
        "inputs_present": signal_picture.get("inputs_present", {}),
    }

    # Write JSON
    json_path = os.path.join(DOCS_DIR, "prelaunch_watchboard.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(watchboard, f_json, indent=2, sort_keys=True)

    # Write Text
    txt_lines: List[str] = []
    txt_lines.append("GLL Pre-Launch ISR Watchboard")
    txt_lines.append("================================")
    txt_lines.append(f"Generated at (UTC): {watchboard['generated_at']}")
    txt_lines.append("")
    txt_lines.append(f"Early Warning Level: {level}")
    txt_lines.append(f"Early Warning Score: {early_warning_score:.1f}/100")
    txt_lines.append(f"Crisis Mode: {'ON' if crisis_on else 'OFF'}")
    txt_lines.append("")
    txt_lines.append("Inputs Present:")
    for name, present in watchboard["inputs_present"].items():
        txt_lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    txt_lines.append("")
    txt_lines.append("Rationale:")
    for line in rationale:
        txt_lines.append(f"  - {line}")
    txt_lines.append("")
    txt_lines.append("Signals:")
    if watchboard["signals"]:
        for sig in watchboard["signals"]:
            txt_lines.append(f"  • {sig.get('name', 'unknown')} [{sig.get('severity', 'UNKNOWN')}]")
            txt_lines.append(f"      {sig.get('rationale', '').strip()}")
    else:
        txt_lines.append("  [No distinct pre-launch signals identified]")

    txt_path = os.path.join(DOCS_DIR, "prelaunch_watchboard.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(txt_lines))

    return watchboard


if __name__ == "__main__":
    wb = build_prelaunch_watchboard()
    print("Pre-Launch ISR Watchboard generated:")
    print(f"  - {os.path.join('docs', 'prelaunch_watchboard.json')}")
    print(f"  - {os.path.join('docs', 'prelaunch_watchboard.txt')}")

