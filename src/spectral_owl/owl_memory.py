"""
owl_memory.py — Spectral Owl memory log + diagnostics

This module handles:
  - Appending memory events to owl_memory.txt
  - Loading recent memory events
  - Producing a human-readable diagnostics summary
    used by the CLI "Owl Memory Diagnostics" option.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict, List

# Base = repo_root/src
BASE = Path(__file__).resolve().parent.parent
LOG_PATH = BASE / "owl_memory.txt"


def _ensure_log_file() -> None:
    """Make sure the owl memory log file exists."""
    if not LOG_PATH.exists():
        LOG_PATH.touch()


def append_memory_event(event_type: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Append a single event to owl_memory.txt as a JSON line.

    event_type: short label, e.g. "analysis_run", "dos_scan", "family_law_demo"
    details: optional dict with extra context
    """
    _ensure_log_file()

    record: Dict[str, Any] = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
    }
    if details:
        record["details"] = details

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return record


def load_memory_log(limit: int | None = None) -> List[Dict[str, Any]]:
    """
    Load events from owl_memory.txt.

    Returns a list of dicts sorted in file order.
    If limit is provided, only the last N events are returned.
    """
    if not LOG_PATH.exists():
        return []

    text = LOG_PATH.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]

    records: List[Dict[str, Any]] = []
    for ln in lines:
        try:
            rec = json.loads(ln)
            if isinstance(rec, dict):
                records.append(rec)
        except json.JSONDecodeError:
            # Skip bad lines, but don't crash
            continue

    if limit is not None and limit > 0:
        return records[-limit:]

    return records


def owl_memory_diagnostics(limit: int = 200) -> str:
    """
    Produce a human-readable diagnostics summary of recent Owl memory events.

    This is what ghost_cli Option 16 will print.
    """
    records = load_memory_log(limit=limit)
    total = len(records)

    if total == 0:
        return "=== OWL MEMORY DIAGNOSTICS ===\nNo events logged yet."

    # Count by type
    by_type: Dict[str, int] = {}
    last_ts: str | None = None

    for rec in records:
        t = rec.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        if rec.get("ts"):
            last_ts = rec["ts"]

    lines: List[str] = []
    lines.append("=== OWL MEMORY DIAGNOSTICS ===")
    lines.append(f"Total events (last {limit} max): {total}")
    if last_ts:
        lines.append(f"Last event timestamp: {last_ts}")
    lines.append("")
    lines.append("Events by type:")
    for t, count in sorted(by_type.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"  - {t}: {count}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Quick self-test
    print(owl_memory_diagnostics())

