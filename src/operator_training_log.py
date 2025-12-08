"""
operator_training_log.py — Track operator training sessions.

Each entry:
  - timestamp_utc
  - operator
  - domain        (e.g. 'GLL_tech', 'UTA', 'BMT_prep', 'doctrine', 'PT')
  - duration_min  (int)
  - notes
  - source        (e.g. 'Day62_20x', '50x_module1', 'UTA_Day1')
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict

from operator_identity import get_identity

LOG_PATH = Path("docs/operator_training_log.csv")


def _ensure_header(path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "timestamp_utc",
                    "operator",
                    "domain",
                    "duration_min",
                    "notes",
                    "source",
                ]
            )


def add_entry(
    domain: str,
    duration_min: int,
    notes: str,
    source: str,
) -> Dict[str, str]:
    _ensure_header(LOG_PATH)

    row = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "operator": get_identity(),
        "domain": domain.strip() or "unspecified",
        "duration_min": str(duration_min),
        "notes": notes.strip(),
        "source": source.strip() or "manual",
    }

    with LOG_PATH.open("a", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp_utc",
                "operator",
                "domain",
                "duration_min",
                "notes",
                "source",
            ],
        )
        w.writerow(row)

    return row


def interactive_add():
    print("=== Operator Training Log ===")
    domain = input("Domain (e.g. GLL_tech/UTA/BMT_prep/doctrine/PT): ").strip()
    dur = input("Duration in minutes (e.g. 30): ").strip()
    notes = input("Notes (short description): ").strip()
    source = input("Source tag (e.g. Day62_50x_module1): ").strip()

    try:
        duration_min = int(dur)
    except ValueError:
        duration_min = 0

    row = add_entry(domain, duration_min, notes, source)
    print("\nEntry added:\n", row)
    print(f"\nLog path: {LOG_PATH}")


def main():
    interactive_add()


if __name__ == "__main__":
    main()

