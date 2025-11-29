"""
threat_memory.py

Spectral Owl persistent threat memory system.
Stores anomalies over time so the AI can learn repeating patterns,
track DoS frequency, and produce intelligence summaries.

Data is saved as CSV so even without AI, humans can analyze patterns.
"""

from pathlib import Path
import csv
from datetime import datetime

MEMORY_FILE = Path("data/threat_memory.csv")


def _ensure_file():
    if not MEMORY_FILE.exists():
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with MEMORY_FILE.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "severity", "event_type", "details"])


def append_event(severity: str, event_type: str, details: str = ""):
    """
    Add a threat record into persistent memory.
    """
    _ensure_file()
    with MEMORY_FILE.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), severity, event_type, details])


def load_events():
    """
    Return full threat event history as list[dict]
    """
    _ensure_file()
    rows = []
    with MEMORY_FILE.open("r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def count_by_type():
    """
    Return count of how many times each event type occurred.
    """
    events = load_events()
    freq = {}
    for e in events:
        t = e["event_type"]
        freq[t] = freq.get(t, 0) + 1
    return freq


def recent_events(n=20):
    """
    Return the last N events recorded.
    """
    events = load_events()
    return events[-n:]

