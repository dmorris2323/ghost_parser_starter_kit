from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path) -> Dict[str, Any]:
    """
    Safely read a JSON file. Returns {} on any error.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_distributed_readiness_snapshot() -> Dict[str, Any]:
    """
    Fuse installation threat map + outage posture + avg reliability
    into a single base-defense readiness posture:
      READY / WATCH / STRAPPED
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    threat = _safe_read_json(DOCS_DIR / "installation_threat_map.json")
    outage = _safe_read_json(DOCS_DIR / "sensor_outage_prediction.json")
    reliability = _safe_read_json(DOCS_DIR / "sensor_reliability_report.json")

    threat_status = threat.get("status", "GREEN")
    outage_posture = outage.get("posture", "STABLE")

    try:
        avg_rel = reliability.get("avg_reliability")
    except Exception:
        avg_rel = None

    if avg_rel is None:
        avg_rel = 90.0  # safe default if report missing

    # Simple ruleset for readiness
    if threat_status == "RED" or outage_posture == "AT_RISK" or avg_rel < 85:
        readiness = "STRAPPED"
    elif threat_status == "AMBER" or outage_posture == "WATCH":
        readiness = "WATCH"
    else:
        readiness = "READY"

    return {
        "product_type": "Distributed Readiness Snapshot",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "readiness": readiness,
        "inputs": {
            "installation_threat_status": threat_status,
            "outage_posture": outage_posture,
            "avg_reliability": avg_rel,
        },
    }


def write_distributed_readiness_snapshot() -> str:
    """
    Writes the readiness snapshot to docs/distributed_readiness_snapshot.json
    and returns its path.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    snap = build_distributed_readiness_snapshot()
    out_path = DOCS_DIR / "distributed_readiness_snapshot.json"
    out_path.write_text(json.dumps(snap, indent=2))
    return str(out_path)


if __name__ == "__main__":
    path = write_distributed_readiness_snapshot()
    print(f"Distributed Readiness Snapshot written → {path}")

