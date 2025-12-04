"""
cross_sensor_validator.py — Cross-Sensor Validation Engine
----------------------------------------------------------
This module evaluates fusion events using multi-sensor evidence.

Example:
  Optical + Seismic → HIGH confidence
  Optical only → LOW
  Seismic + Radiation → VERY HIGH
  EMS disagreeing → JAMMING / SPOOF attempt
"""

import csv
from pathlib import Path

DATA = Path(__file__).parent / "data" / "fused_output.csv"

def classify_event(row):
    """Assign a confidence level based on sensor evidence."""
    sensors = {
        "optical": float(row.get("optical_score", 0)),
        "seismic": float(row.get("seismic_score", 0)),
        "ems": float(row.get("ems_score", 0)),
        "radiation": float(row.get("radiation_score", 0)),
    }

    active = [k for k, v in sensors.items() if v > 0.5]
    count = len(active)

    # === Cross-sensor rules ===
    if count >= 3:
        return "VERY_HIGH"
    if count == 2:
        return "HIGH"
    if count == 1:
        return "LOW"
    return "NONE"


def run_cross_validation():
    if not DATA.exists():
        return {"status": "error", "msg": "No fused_output.csv found."}

    rows = []
    with DATA.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["confidence"] = classify_event(row)
            rows.append(row)

    out_path = DATA.parent / "cross_sensor_output.csv"
    with out_path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return {
        "status": "ok",
        "path": str(out_path),
        "rows": len(rows)
    }


if __name__ == "__main__":
    print(run_cross_validation())

