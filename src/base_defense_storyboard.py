from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path) -> Dict[str, Any]:
    """
    Safely read a JSON file, returning {} on any failure.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_base_defense_storyboard() -> Dict[str, Any]:
    """
    Fuse base-defense artifacts into a commander-readable storyboard:
      - installation_threat_map.json
      - sensor_outage_prediction.json
      - distributed_readiness_snapshot.json
      - perimeter_incident_report.json (module 41)
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    threat = _safe_read_json(DOCS_DIR / "installation_threat_map.json")
    outage = _safe_read_json(DOCS_DIR / "sensor_outage_prediction.json")
    dist = _safe_read_json(DOCS_DIR / "distributed_readiness_snapshot.json")
    perimeter = _safe_read_json(DOCS_DIR / "perimeter_incident_report.json")

    threat_status = threat.get("status", "GREEN")
    outage_posture = outage.get("posture", "STABLE")
    readiness = dist.get("readiness", "READY")

    total_incidents = perimeter.get("total_events", 0)
    sector_counts = perimeter.get("sector_counts", {})
    pattern_counts = perimeter.get("pattern_counts", {})

    storyline = []

    storyline.append("Base-Defense Storyboard")
    storyline.append("-----------------------")
    storyline.append(f"Installation threat status: {threat_status}")
    storyline.append(f"Outage posture            : {outage_posture}")
    storyline.append(f"Distributed readiness     : {readiness}")
    storyline.append("")
    storyline.append(f"Total perimeter incidents recorded: {total_incidents}")
    storyline.append("")

    if sector_counts:
        storyline.append("Sector pressure profile:")
        for sector, count in sorted(sector_counts.items()):
            storyline.append(f"  - {sector}: {count} events")
        storyline.append("")
    else:
        storyline.append("Sector pressure profile: no events logged.")
        storyline.append("")

    if pattern_counts:
        storyline.append("Incident pattern summary:")
        for pattern, count in sorted(pattern_counts.items()):
            storyline.append(f"  - {pattern}: {count}")
        storyline.append("")
    else:
        storyline.append("Incident pattern summary: no pattern data.")
        storyline.append("")

    storyline.append("Commanders' Bottom Line:")
    if readiness == "STRAPPED":
        storyline.append(
            "  • Base-defense posture is STRAPPED — prioritize mitigation now."
        )
    elif readiness == "WATCH":
        storyline.append(
            "  • Base-defense posture is WATCH — elevated risk, maintain vigilance."
        )
    else:
        storyline.append(
            "  • Base-defense posture is READY — normal ops with heightened awareness."
        )

    if threat_status == "RED":
        storyline.append("  • Installation threat map indicates RED sectors under pressure.")
    elif threat_status == "AMBER":
        storyline.append("  • AMBER sectors show localized pressure; monitor closely.")

    if outage_posture in ("WATCH", "AT_RISK"):
        storyline.append(
            "  • Sensor outage posture is elevated — confirm redundancy and backups."
        )

    storyboard = {
        "product_type": "Base Defense Storyboard",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "installation_threat_status": threat_status,
            "outage_posture": outage_posture,
            "readiness": readiness,
            "total_perimeter_incidents": total_incidents,
        },
        "storyboard_lines": storyline,
    }
    return storyboard


def write_base_defense_storyboard() -> Dict[str, str]:
    """
    Write JSON + TXT storyboard files.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_base_defense_storyboard()

    json_path = DOCS_DIR / "base_defense_storyboard.json"
    txt_path = DOCS_DIR / "base_defense_storyboard.txt"

    json_path.write_text(json.dumps(data, indent=2))
    txt_path.write_text("\n".join(data["storyboard_lines"]) + "\n")

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_base_defense_storyboard()
    print("Base Defense Storyboard written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

