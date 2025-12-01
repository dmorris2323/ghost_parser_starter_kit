"""
threat_memory.py — Spectral Owl / GLL
-------------------------------------
Persistent threat memory store.

CSV fields:
  timestamp, severity, source, note, profile
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from gll_profile import get_active_profile_name

MEMORY_PATH = Path("data/threat_memory.csv")


def ensure_header():
    if not MEMORY_PATH.exists():
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with MEMORY_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "severity", "source", "note", "profile"])


def append_event(severity: str, source: str, note: str) -> None:
    """
    Append a threat memory event with the active profile tagged.
    """
    ensure_header()
    ts = datetime.utcnow().isoformat()
    profile = get_active_profile_name()
    with MEMORY_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ts, severity, source, note, profile])


def load_events() -> List[Dict[str, str]]:
    """
    Load all threat memory events as dicts.
    """
    if not MEMORY_PATH.exists():
        return []

    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    events = load_events()
    print(f"Loaded {len(events)} threat memory event(s).")
    for row in events[-10:]:
        print(row)


if __name__ == "__main__":
    main()

