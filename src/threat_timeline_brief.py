"""
threat_timeline_brief.py — Ghost Lantern Labs
---------------------------------------------

Reads data/threat_levels.csv and produces a simple
timeline-aware threat brief:

- total runs
- counts of LOW / MEDIUM / HIGH
- latest run snapshot
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import csv


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
THREAT_LEVELS_PATH = DATA_DIR / "threat_levels.csv"


def load_threat_levels() -> List[Dict[str, Any]]:
    if not THREAT_LEVELS_PATH.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with THREAT_LEVELS_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_brief(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No threat level file found. Run threat_level_classifier.py first."

    total = len(rows)
    high = sum(1 for r in rows if r.get("threat_level") == "HIGH")
    med = sum(1 for r in rows if r.get("threat_level") == "MEDIUM")
    low = sum(1 for r in rows if r.get("threat_level") == "LOW")

    latest = rows[-1]

    lines: List[str] = []
    lines.append("=== GLL Threat Timeline Brief ===")
    lines.append(f"Total logged runs: {total}")
    lines.append(f"Threat breakdown: HIGH={high}, MEDIUM={med}, LOW={low}")
    lines.append("")
    lines.append("Most recent run:")
    lines.append(f"  Timestamp (UTC): {latest.get('timestamp_utc', '')}")
    lines.append(f"  Run ID:          {latest.get('run_id', '')}")
    lines.append(f"  Threat level:    {latest.get('threat_level', '')}")
    lines.append(f"  Max threat hint: {latest.get('max_threat_hint', '')}")
    lines.append(f"  Avg threat hint: {latest.get('avg_threat_hint', '')}")
    lines.append(f"  Valid sensors:   {latest.get('valid_sensor_count', '')}")
    lines.append(f"  Fallback reason: {latest.get('fallback_reason', '')}")

    return "\n".join(lines)


def main() -> None:
    rows = load_threat_levels()
    brief = build_brief(rows)
    print(brief)


if __name__ == "__main__":
    main()

