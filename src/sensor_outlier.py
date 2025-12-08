# sensor_outlier.py
"""
Sensor Outlier Detector for Ghost Lantern Labs
Detects values outside expected windows for each sensor.
"""

from pathlib import Path
import json

LOG = Path("docs/outlier_report.json")

# Expected ranges (you can tune later)
EXPECTED = {
    "optical": (0, 1.2),
    "seismic": (0, 9.0),
    "ems": (0, 100),
    "radiation": (0, 500)
}

def detect_outliers():
    outliers = []

    # Load fused output if available
    data_file = Path("src/data/fused_output.csv")
    if not data_file.exists():
        return {"status": "no_data"}

    rows = data_file.read_text().splitlines()
    header = rows[0].split(",")
    for r in rows[1:]:
        cols = r.split(",")
        row = dict(zip(header, cols))

        for sensor, (low, high) in EXPECTED.items():
            val = row.get(sensor)
            if val is None:
                continue
            try:
                f = float(val)
            except:
                continue
            if f < low or f > high:
                outliers.append({
                    "sensor": sensor,
                    "value": f,
                    "expected_low": low,
                    "expected_high": high
                })

    result = {"status": "ok", "outliers": outliers}
    LOG.write_text(json.dumps(result, indent=2))
    return result

def export_outliers():
    result = detect_outliers()
    return f"Outlier report written → {LOG}"

