from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_base_defense_bundle() -> Dict[str, Any]:
    """
    Build a single JSON bundle for all base-defense outputs:

      - installation_threat_map.json
      - sensor_outage_prediction.json
      - distributed_readiness_snapshot.json
      - perimeter_incident_report.json
      - base_defense_storyboard.json
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    installation_threat = _safe_json(DOCS_DIR / "installation_threat_map.json")
    outage_prediction = _safe_json(DOCS_DIR / "sensor_outage_prediction.json")
    readiness_snapshot = _safe_json(DOCS_DIR / "distributed_readiness_snapshot.json")
    perimeter_incidents = _safe_json(DOCS_DIR / "perimeter_incident_report.json")
    storyboard = _safe_json(DOCS_DIR / "base_defense_storyboard.json")

    bundle = {
        "product_type": "Base Defense Bundle",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "installation_threat_map": installation_threat,
        "sensor_outage_prediction": outage_prediction,
        "distributed_readiness_snapshot": readiness_snapshot,
        "perimeter_incident_report": perimeter_incidents,
        "base_defense_storyboard": storyboard,
    }
    return bundle


def write_base_defense_bundle() -> str:
    """
    Write docs/base_defense_bundle.json and return its path.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    bundle = build_base_defense_bundle()
    out_path = DOCS_DIR / "base_defense_bundle.json"
    out_path.write_text(json.dumps(bundle, indent=2))
    return str(out_path)


if __name__ == "__main__":
    path = write_base_defense_bundle()
    print(f"Base Defense Bundle written → {path}")

