"""
operator_training_summary.py

Summarize operator training history from docs/operator_training_log.csv

Outputs:
- Total minutes by domain
- Total minutes overall
- Entry count
- Simple "intensity" metric

Writes:
- docs/operator_training_summary.txt
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

LOG_PATH = Path("docs/operator_training_log.csv")
SUMMARY_PATH = Path("docs/operator_training_summary.txt")


def load_entries():
    if not LOG_PATH.exists():
        return []

    rows = []
    with LOG_PATH.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def _to_int(val, default=0) -> int:
    try:
        return int(val)
    except Exception:
        return int(default)


def build_summary() -> Dict[str, Any]:
    entries = load_entries()
    if not entries:
        return {
            "status": "empty",
            "message": "No operator_training_log.csv entries found.",
            "total_entries": 0,
            "total_minutes": 0,
            "by_domain": {},
            "intensity_score": 0,
        }

    by_domain: Dict[str, int] = defaultdict(int)
    total_minutes = 0

    for r in entries:
        dom = (r.get("domain") or "unspecified").strip()
        mins = _to_int(r.get("duration_min", 0))
        by_domain[dom] += mins
        total_minutes += mins

    # crude intensity score: minutes / 60, capped at 10
    intensity = min(10, round(total_minutes / 60, 2))

    return {
        "status": "ok",
        "total_entries": len(entries),
        "total_minutes": total_minutes,
        "by_domain": dict(sorted(by_domain.items(), key=lambda kv: kv[0])),
        "intensity_score": intensity,
    }


def write_summary() -> str:
    summary = build_summary()
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("=== OPERATOR TRAINING SUMMARY ===")
    lines.append(f"Status: {summary.get('status')}")
    lines.append(f"Total entries: {summary.get('total_entries')}")
    lines.append(f"Total minutes: {summary.get('total_minutes')}")
    lines.append(f"Intensity score (0–10): {summary.get('intensity_score')}")
    lines.append("")

    by_domain = summary.get("by_domain", {})
    if by_domain:
        lines.append("Minutes by domain:")
        for dom, mins in by_domain.items():
            lines.append(f"  - {dom}: {mins} min")
    else:
        lines.append("No domain data available.")

    SUMMARY_PATH.write_text("\n".join(lines))
    return str(SUMMARY_PATH)


def main():
    path = write_summary()
    print(f"Operator training summary written to: {path}")
    print()
    print(SUMMARY_PATH.read_text())


if __name__ == "__main__":
    main()
