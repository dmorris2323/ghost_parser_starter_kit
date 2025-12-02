"""
daily_sensor_brief.py — Ghost Lantern Labs
------------------------------------------

Reads data/run_history.csv and produces a simple
daily-style brief for the sensor layer:

- total runs
- average max_threat_hint
- average avg_threat_hint
- distribution of fallback_reason
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import csv
from statistics import mean


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RUN_HISTORY_PATH = DATA_DIR / "run_history.csv"


def load_run_history() -> List[Dict[str, Any]]:
    if not RUN_HISTORY_PATH.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with RUN_HISTORY_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_brief(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No run history available yet. Run sensor_run_history.py first."

    max_threats = []
    avg_threats = []
    fallback_counts: Dict[str, int] = {}

    for r in rows:
        try:
            max_t = float(r.get("max_threat_hint", 0.0))
            avg_t = float(r.get("avg_threat_hint", 0.0))
        except ValueError:
            max_t = 0.0
            avg_t = 0.0

        max_threats.append(max_t)
        avg_threats.append(avg_t)

        reason = r.get("fallback_reason", "unknown") or "unknown"
        fallback_counts[reason] = fallback_counts.get(reason, 0) + 1

    total_runs = len(rows)
    avg_max_threat = mean(max_threats)
    avg_avg_threat = mean(avg_threats)

    lines: List[str] = []
    lines.append("=== GLL Sensor Layer Daily Brief ===")
    lines.append(f"Total logged runs: {total_runs}")
    lines.append(f"Average MAX threat hint: {avg_max_threat:.3f}")
    lines.append(f"Average AVG threat hint: {avg_avg_threat:.3f}")
    lines.append("")
    lines.append("Fallback reasons (frequency):")

    for reason, count in sorted(fallback_counts.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"  {reason}: {count} run(s)")

    return "\n".join(lines)


def main() -> None:
    rows = load_run_history()
    brief = build_brief(rows)
    print(brief)


if __name__ == "__main__":
    main()

