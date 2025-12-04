"""
cross_sensor_report.py — Explains cross-sensor confidence trends
----------------------------------------------------------------
Creates a TXT report for commanders and GUI.
"""

from pathlib import Path
import csv

DATA = Path(__file__).parent / "data" / "cross_sensor_output.csv"
OUT = Path(__file__).parent / "docs" / "cross_sensor_report.txt"

def build_report():
    if not DATA.exists():
        return {"status": "error", "msg": "Run cross_sensor_validator.py first."}

    rows = list(csv.DictReader(DATA.open()))
    counts = {"VERY_HIGH": 0, "HIGH": 0, "LOW": 0, "NONE": 0}

    for r in rows:
        counts[r["confidence"]] = counts.get(r["confidence"], 0) + 1

    lines = []
    lines.append("=== CROSS-SENSOR CONFIDENCE REPORT ===")
    lines.append("")
    for k, v in counts.items():
        lines.append(f"{k}: {v}")

    OUT.write_text("\n".join(lines))
    return {"status": "ok", "path": str(OUT)}

if __name__ == "__main__":
    print(build_report())

