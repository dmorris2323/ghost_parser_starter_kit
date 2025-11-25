"""
owl_memory.py — Day 51
The Spectral Owl’s lightweight memory system.
"""

from datetime import datetime
from fusion_logger import log_event

MEMORY_FILE = "owl_memory.txt"

def remember(key: str, value: str):
    """Append a memory line to owl_memory.txt."""
    line = f"{datetime.utcnow().isoformat()} | {key} | {value}\n"
    with open(MEMORY_FILE, "a") as f:
        f.write(line)
    log_event("spectral_owl", "memory_write", f"{key} -> {value}")

def recall_all():
    """Return all memory lines, or an empty list if file is missing."""
    try:
        with open(MEMORY_FILE, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        return []

