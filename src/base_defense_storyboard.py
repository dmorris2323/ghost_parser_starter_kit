"""
base_defense_storyboard.py

Module 30 — Base Defense Storyboard (50x Sprint #2)

Purpose:
- Turn your nuclear/base-defense picture into a simple storyboard
  for commanders and briefings.

It stitches together:
- Installation Threat Map
- Sensor Outage Forecast
- Distributed Readiness Snapshot
- Perimeter Incident Report (if present)

Outputs:
- docs/base_defense_storyboard.json
- docs/base_defense_storyboard.txt
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BASE = Path(__file__).resolve().parent
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)

ITM_FILE = DOCS_DIR / "installation_threat_map.json"
OUTAGE_FILE = DOCS_DIR / "sensor_outage_forecast.json"
DIST_FILE = DOCS_DIR / "distributed_readiness_snapshot.json"
PERIM_FILE = DOCS_DIR / "perimeter_incident_report.json"


def _safe_load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_storyboard() -> Dict[str, Any]:
    ts = datetime.utcnow().isoformat() + "Z"

    itm = _safe_load(ITM_FILE)
    outage = _safe_load(OUTAGE_FILE)
    dist = _safe_load(DIST_FILE)
    perim = _safe_load(PERIM_FILE)

    base_name = itm.get("base_name", "Notional Installation")
    crisis_mode = itm.get("crisis_mode", "OFF")
    fusion_trust = int(itm.get("fusion_trust_score", dist.get("fusion_trust", 80)))
    avg_rel = float(dist.get("avg_reliability", 90.0))
    operator = dist.get("operator", "Unknown Operator")

    # Build storyboard phases: Detection, Assessment, Response, Recovery
    phases: List[Dict[str, Any]] = []

    # Detection
    phases.append(
        {
            "phase": "Detection",
            "summary": "How the base detects incoming threats (drones, gate rams, nuclear signals, cyber spikes).",
            "installation_risk": itm.get("overall_risk", "UNKNOWN"),
            "perimeter_risk": perim.get("perimeter_summary", {}).get("sector_risk", "UNKNOWN"),
            "airspace_risk": perim.get("perimeter_summary", {}).get("airspace_risk", "UNKNOWN"),
            "sensor_outage_global": outage.get("sensors", {}).get("global", {}),
        }
    )

    # Assessment
    phases.append(
        {
            "phase": "Assessment",
            "summary": "How Ghost Lantern Labs fuses and rates the situation.",
            "fusion_trust": fusion_trust,
            "avg_reliability": avg_rel,
            "crisis_mode": crisis_mode,
            "readiness_levels": dist.get("readiness", {}),
        }
    )

    # Response
    phases.append(
        {
            "phase": "Response",
            "summary": "How the wing/group/squadron/team posture based on GLL outputs.",
            "wing_level": dist.get("readiness", {}).get("wing", "UNKNOWN"),
            "group_level": dist.get("readiness", {}).get("group", "UNKNOWN"),
            "squadron_level": dist.get("readiness", {}).get("squadron", "UNKNOWN"),
            "team_level": dist.get("readiness", {}).get("team", "UNKNOWN"),
        }
    )

    # Recovery
    phases.append(
        {
            "phase": "Recovery",
            "summary": "Post-incident learning and reset posture.",
            "operator": operator,
            "notes": "Storyboard is designed to be briefed, recorded, and iterated each day.",
        }
    )

    out: Dict[str, Any] = {
        "generated_at": ts,
        "base_name": base_name,
        "crisis_mode": crisis_mode,
        "fusion_trust": fusion_trust,
        "avg_reliability": avg_rel,
        "operator": operator,
        "phases": phases,
    }

    json_path = DOCS_DIR / "base_defense_storyboard.json"
    txt_path = DOCS_DIR / "base_defense_storyboard.txt"

    json_path.write_text(json.dumps(out, indent=2))

    # Human-readable TXT
    lines: List[str] = [
        "=== BASE DEFENSE STORYBOARD ===",
        f"Generated: {ts}",
        f"Base: {base_name}",
        f"Operator: {operator}",
        f"Crisis Mode: {crisis_mode}",
        f"Fusion Trust: {fusion_trust}",
        f"Average Reliability: {avg_rel:.2f}%",
        "",
    ]

    for p in phases:
        lines.append(f"[{p['phase']}]")
        lines.append(f"  {p['summary']}")
        # Add a few key fields if present
        if p["phase"] == "Detection":
            lines.append(f"  Perimeter Risk     : {p['perimeter_risk']}")
            lines.append(f"  Airspace Risk      : {p['airspace_risk']}")
            g = p.get("sensor_outage_global", {})
            if g:
                lines.append(
                    f"  Outage (Global)    : risk={g.get('outage_risk','UNKNOWN')}, "
                    f"errors={g.get('error_events',0)}"
                )
        elif p["phase"] == "Assessment":
            lines.append(f"  Fusion Trust       : {p['fusion_trust']}")
            lines.append(f"  Avg Reliability    : {p['avg_reliability']}")
            lines.append(f"  Crisis Mode        : {p['crisis_mode']}")
        elif p["phase"] == "Response":
            lines.append(f"  Wing Readiness     : {p.get('wing_level','UNKNOWN')}")
            lines.append(f"  Group Readiness    : {p.get('group_level','UNKNOWN')}")
            lines.append(f"  Squadron Readiness : {p.get('squadron_level','UNKNOWN')}")
            lines.append(f"  Team Readiness     : {p.get('team_level','UNKNOWN')}")
        elif p["phase"] == "Recovery":
            lines.append(f"  Operator           : {p['operator']}")
            lines.append(f"  Notes              : {p['notes']}")
        lines.append("")

    txt_path.write_text("\n".join(lines))

    return {
        "status": "ok",
        "json_path": str(json_path),
        "text_path": str(txt_path),
    }


def main() -> None:
    out = build_storyboard()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

