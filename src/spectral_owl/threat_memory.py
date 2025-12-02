"""
spectral_owl.threat_memory
--------------------------

Central store for Spectral Owl's threat memory.

Responsibilities:
 - Append new threat events to a CSV log
 - Load all threat events into Python dicts
 - Provide basic stats such as counts per type
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import csv
from typing import List, Dict, Optional

# Where we store threat memory events
DATA_PATH = Path("data/threat_memory.csv")


def _ensure_parent():
    """Make sure the data directory exists."""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def append_event(
    event_type: str,
    severity: str = "info",
    doctrine_tag: Optional[str] = None,
    note: str = "",
    source: str = "owl_brain",
) -> None:
    """
    Append a single threat event to the CSV log.

    Fields:
      - timestamp (UTC ISO8601)
      - source        (e.g., 'owl_brain', 'anti_dos', 'family_law_demo')
      - type          (e.g., 'DoS', 'anomaly', 'legal_case')
      - severity      (e.g., 'low', 'medium', 'high', 'critical')
      - doctrine_tag  (optional: 'AFDP2-0', 'PLA_SSF', 'Nuclear_EMS', etc.)
      - note          (free-text description)
    """
    _ensure_parent()

    fieldnames = [
        "timestamp",
        "source",
        "type",
        "severity",
        "doctrine_tag",
        "note",
    ]

    write_header = not DATA_PATH.exists()

    with DATA_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "source": source,
                "type": event_type,
                "severity": severity,
                "doctrine_tag": doctrine_tag or "",
                "note": note,
            }
        )


def load_events() -> List[Dict[str, str]]:
    """
    Load all threat events from CSV.

    Returns:
      A list of dicts. If file doesn't exist, returns [].
    """
    if not DATA_PATH.exists():
        return []

    events: List[Dict[str, str]] = []
    with DATA_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(dict(row))
    return events


def count_by_type(events: Optional[List[Dict[str, str]]] = None) -> Dict[str, int]:
    """
    Count events grouped by 'type' field.

    If events is None, this function will call load_events().
    """
    if events is None:
        events = load_events()

    counts: Dict[str, int] = {}

    for ev in events:
        # Be defensive: support different possible keys
        t = (
            ev.get("type")
            or ev.get("threat_type")
            or ev.get("category")
            or "UNKNOWN"
        )
        counts[t] = counts.get(t, 0) + 1

    return counts


# Optional helper: count by severity (could be useful for stats)
def count_by_severity(events: Optional[List[Dict[str, str]]] = None) -> Dict[str, int]:
    """
    Count events grouped by severity ('low', 'medium', 'high', 'critical').
    """
    if events is None:
        events = load_events()

    counts: Dict[str, int] = {}

    for ev in events:
        sev = ev.get("severity") or "unknown"
        counts[sev] = counts.get(sev, 0) + 1

    return counts


if __name__ == "__main__":
    # Simple self-test
    print("=== THREAT MEMORY SELF-TEST ===")
    print(f"Data path: {DATA_PATH}")

    events = load_events()
    print(f"Loaded {len(events)} event(s).")

    print("\nCounts by type:")
    print(count_by_type(events))

    print("\nCounts by severity:")
    print(count_by_severity(events))

