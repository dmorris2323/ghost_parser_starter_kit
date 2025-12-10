#!/usr/bin/env python3
"""
early_warning_scorecard.py

Day 66 – Ghost Lantern Labs
Pre-Launch Early Warning Hardening – Option C

Builds a simple, commander-facing Early Warning Scorecard derived from:
    docs/prelaunch_watchboard.json

This is meant to be printed, screenshotted, or dropped into a brief.
It does NOT change upstream logic – it is a thin presentation layer.

Output:
    docs/early_warning_scorecard.txt
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def build_early_warning_scorecard() -> str:
    os.makedirs(DOCS_DIR, exist_ok=True)

    watchboard_path = os.path.join(DOCS_DIR, "prelaunch_watchboard.json")
    wb = _safe_read_json(watchboard_path)

    now_utc = datetime.utcnow().isoformat() + "Z"
    lines: List[str] = []
    lines.append("GLL Early Warning Scorecard")
    lines.append("================================")
    lines.append(f"Generated at (UTC): {now_utc}")
    lines.append("")

    if not isinstance(wb, dict):
        lines.append("No prelaunch_watchboard.json available.")
        lines.append("Run `prelaunch_watchboard.py` first.")
        out_path = os.path.join(DOCS_DIR, "early_warning_scorecard.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return out_path

    level = wb.get("early_warning_level", "UNKNOWN")
    score = wb.get("early_warning_score", 0.0)
    crisis = wb.get("crisis_mode", False)
    sensor_conc = wb.get("sensor_concurrence_score", 0.0)
    ems_spike = wb.get("ems_spike_score", 0.0)
    latency_risk = wb.get("latency_risk_score", 0.0)
    pattern_anom = wb.get("pattern_anomaly_score", 0.0)
    inputs_present = wb.get("inputs_present", {})
    rationale = wb.get("rationale", [])
    signals = wb.get("signals", [])

    lines.append("1. Early Warning Posture")
    lines.append("-------------------------")
    lines.append(f"  Level: {level}")
    lines.append(f"  Score: {score:.1f}/100")
    lines.append(f"  Crisis Mode: {'ON' if crisis else 'OFF'}")
    lines.append("")

    lines.append("2. Contributing Factors")
    lines.append("------------------------")
    lines.append(f"  Multi-Sensor Concurrence Score: {sensor_conc:.1f}/100")
    lines.append(f"  EMS / RF Spike Score:          {ems_spike:.1f}/100")
    lines.append(f"  Sensor Latency Risk Score:     {latency_risk:.1f}/100")
    lines.append(f"  Pattern Anomaly Score:         {pattern_anom:.1f}/100")
    lines.append("")

    lines.append("3. Inputs Present")
    lines.append("-----------------")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    if not inputs_present:
        lines.append("  [No input presence map available]")
    lines.append("")

    lines.append("4. Rationale Summary")
    lines.append("---------------------")
    if rationale:
        for r in rationale:
            lines.append(f"  - {r}")
    else:
        lines.append("  [No rationale entries available]")
    lines.append("")

    lines.append("5. Signals Overview")
    lines.append("-------------------")
    if signals:
        for sig in signals:
            name = sig.get("name", "unknown")
            sev = sig.get("severity", "UNKNOWN")
            rat = sig.get("rationale", "").strip()
            lines.append(f"  • {name} [{sev}]")
            if rat:
                lines.append(f"      {rat}")
    else:
        lines.append("  [No distinct signals recorded in watchboard]")
    lines.append("")

    out_path = os.path.join(DOCS_DIR, "early_warning_scorecard.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path


if __name__ == "__main__":
    path = build_early_warning_scorecard()
    print("Early Warning Scorecard generated:")
    print(f"  - {path}")

