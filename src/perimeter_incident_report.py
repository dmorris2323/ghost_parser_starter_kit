"""
perimeter_incident_report.py

Module 29 — Perimeter Incident Report (50x Sprint #2)

Purpose:
- Fuse installation threat map + sensor outage forecast into a simple
  "Perimeter / Airspace incident" commander report.
- Focused on:
    • Gate rams / perimeter breaches
    • Drone / airspace incursions
    • Sensor stability around those sectors

Inputs (optional, safe if missing):
- docs/installation_threat_map.json
- docs/sensor_outage_forecast.json

Outputs:
- docs/perimeter_incident_report.json
- docs/perimeter_incident_report.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE = Path(__file__).resolve().parent
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)

ITM_FILE = DOCS_DIR / "installation_threat_map.json"
OUTAGE_FILE = DOCS_DIR / "sensor_outage_forecast.json"


@dataclass
class PerimeterSummary:
    sector_risk: str
    airspace_risk: str
    global_sensor_outage_risk: str
    notes: str


@dataclass
class PerimeterIncidentReport:
    generated_at: str
    base_name: str
    crisis_mode: str
    fusion_trust_score: int
    perimeter_summary: PerimeterSummary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "base_name": self.base_name,
            "crisis_mode": self.crisis_mode,
            "fusion_trust_score": self.fusion_trust_score,
            "perimeter_summary": asdict(self.perimeter_summary),
        }


def _safe_load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_perimeter_incident_report() -> Dict[str, Any]:
    ts = datetime.utcnow().isoformat() + "Z"

    itm = _safe_load_json(ITM_FILE)
    outage = _safe_load_json(OUTAGE_FILE)

    base_name = itm.get("base_name", "Notional Installation")
    crisis_mode = itm.get("crisis_mode", "OFF")
    fusion_trust_score = int(itm.get("fusion_trust_score", 80))

    sectors = itm.get("sectors", {})
    per = sectors.get("perimeter", {}) or {}
    air = sectors.get("airspace", {}) or {}

    perimeter_risk = per.get("risk_level", "UNKNOWN")
    airspace_risk = air.get("risk_level", "UNKNOWN")

    outage_sensors = outage.get("sensors", {})
    global_outage = outage_sensors.get("global", {}) or {}
    global_outage_risk = global_outage.get("outage_risk", "LOW")

    notes_parts = []

    if perimeter_risk in {"HIGH", "SEVERE", "CRISIS – FRAGILE"}:
        notes_parts.append("Perimeter shows elevated risk — gate/ground security should be primed.")
    elif perimeter_risk in {"ELEVATED", "CRISIS – STABLE"}:
        notes_parts.append("Perimeter is elevated but stable with current posture.")
    else:
        notes_parts.append("Perimeter is currently assessed as stable.")

    if airspace_risk in {"HIGH", "SEVERE", "CRISIS – FRAGILE"}:
        notes_parts.append("Airspace risk is high — drone incursions / low-alt threats must be watched closely.")
    elif airspace_risk in {"ELEVATED", "CRISIS – STABLE"}:
        notes_parts.append("Airspace is elevated but under control.")
    else:
        notes_parts.append("Airspace threat picture is currently stable.")

    if global_outage_risk == "HIGH":
        notes_parts.append("Sensor outage risk is HIGH — commander should expect potential blind spots.")
    elif global_outage_risk == "MEDIUM":
        notes_parts.append("Some sensor instability detected — plan around moderate blind spots.")
    else:
        notes_parts.append("Sensors appear stable with low outage risk.")

    notes = " ".join(notes_parts)

    summary = PerimeterSummary(
        sector_risk=perimeter_risk,
        airspace_risk=airspace_risk,
        global_sensor_outage_risk=global_outage_risk,
        notes=notes,
    )

    report = PerimeterIncidentReport(
        generated_at=ts,
        base_name=base_name,
        crisis_mode=crisis_mode,
        fusion_trust_score=fusion_trust_score,
        perimeter_summary=summary,
    )

    out = report.to_dict()

    json_path = DOCS_DIR / "perimeter_incident_report.json"
    txt_path = DOCS_DIR / "perimeter_incident_report.txt"

    json_path.write_text(json.dumps(out, indent=2))

    lines = [
        "=== PERIMETER INCIDENT REPORT ===",
        f"Generated: {ts}",
        f"Base: {base_name}",
        f"Crisis Mode: {crisis_mode}",
        f"Fusion Trust Score: {fusion_trust_score}",
        "",
        "Perimeter / Airspace Summary:",
        f"  Perimeter Risk          : {summary.sector_risk}",
        f"  Airspace Risk           : {summary.airspace_risk}",
        f"  Global Sensor Outage    : {summary.global_sensor_outage_risk}",
        "",
        "Commander Notes:",
        f"  {summary.notes}",
    ]
    txt_path.write_text("\n".join(lines))

    return {
        "status": "ok",
        "json_path": str(json_path),
        "text_path": str(txt_path),
    }


def main() -> None:
    out = build_perimeter_incident_report()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

