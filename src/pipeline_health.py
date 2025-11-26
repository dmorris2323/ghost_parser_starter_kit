"""
pipeline_health.py — Day 51
Checks status of all major GLL modules.
"""

from pathlib import Path
import pandas as pd

def check_file(path: str):
    p = Path(path)
    if not p.exists():
        return f"❌ Missing: {path}"
    if p.stat().st_size == 0:
        return f"⚠️ Empty: {path}"
    return f"✅ OK: {path}"

def pipeline_health():
    checks = [
        check_file("scored_output.csv"),
        check_file("commander_extract.csv"),
        check_file("heatmap_data.csv"),
        check_file("daily_report.txt"),
        check_file("critical_alerts.csv"),
        check_file("operator_snapshot.txt"),
    ]
    return "\n".join(checks)

if __name__ == "__main__":
    print(pipeline_health())

