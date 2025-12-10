from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"


def _safe_load_reliability_log() -> Dict[str, float]:
    """
    Load sensor_reliability_log.csv if it exists.
    Expected columns: sensor,name,reliability
    Returns: {sensor_name: reliability_float}
    """
    log_file = DATA_DIR / "sensor_reliability_log.csv"
    if not log_file.exists():
        return {}

    results: Dict[str, float] = {}
    try:
        with log_file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("sensor") or row.get("name")
                rel = row.get("reliability")
                if not name or not rel:
                    continue
                try:
                    results[name] = float(rel)
                except ValueError:
                    continue
    except Exception:
        return {}
    return results


def compute_outage_risk() -> Dict[str, Any]:
    """
    Computes an outage risk band (LOW / MEDIUM / HIGH) per sensor
    based on reliability scores.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    rel = _safe_load_reliability_log()

    risks: Dict[str, Dict[str, Any]] = {}

    for sensor, score in rel.items():
        if score >= 95:
            band = "LOW"
        elif score >= 85:
            band = "MEDIUM"
        else:
            band = "HIGH"
        risks[sensor] = {"reliability": score, "outage_risk": band}

    # Fallback shape if no logs yet
    if not risks:
        risks = {
            "optical": {"reliability": 90.0, "outage_risk": "MEDIUM"},
            "seismic": {"reliability": 90.0, "outage_risk": "MEDIUM"},
            "ems": {"reliability": 90.0, "outage_risk": "MEDIUM"},
            "radiation": {"reliability": 90.0, "outage_risk": "MEDIUM"},
        }

    high_count = sum(1 for r in risks.values() if r["outage_risk"] == "HIGH")
    if high_count >= 2:
        posture = "AT_RISK"
    elif high_count == 1:
        posture = "WATCH"
    else:
        posture = "STABLE"

    return {
        "product_type": "Sensor Outage Predictor",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "posture": posture,
        "sensors": risks,
    }


def write_outage_prediction() -> Dict[str, str]:
    """
    Writes JSON + TXT snapshot for outage risk.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = compute_outage_risk()

    json_path = DOCS_DIR / "sensor_outage_prediction.json"
    txt_path = DOCS_DIR / "sensor_outage_prediction.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines = []
    lines.append("=== SENSOR OUTAGE PREDICTION ===")
    lines.append(f"Generated at: {data['generated_at']}")
    lines.append(f"Posture: {data['posture']}")
    lines.append("")
    lines.append("Per-sensor risk:")
    for name, info in data["sensors"].items():
        lines.append(
            f"  - {name}: reliability={info['reliability']:.2f}% "
            f"risk={info['outage_risk']}"
        )
    lines.append("")
    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_outage_prediction()
    print("Sensor Outage Prediction written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

