"""
owl_memory.py — Spectral Owl Memory Module
------------------------------------------

Centralized memory log for Spectral Owl.

- append_memory(event: str)      → append a line to owl_memory.txt
- load_memory_log(limit: int|None) → return last N lines (or all)
- read_memory_log(...)           → backwards-compatible alias
"""

from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path(__file__).parent.parent / "owl_memory.txt"


def _ensure_file():
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text("")


def append_memory(event: str) -> None:
    """
    Append a single memory event to owl_memory.txt with timestamp.
    """
    _ensure_file()
    ts = datetime.utcnow().isoformat() + "Z"
    line = f"{ts} | {event}\n"
    with MEMORY_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


def load_memory_log(limit: int | None = None) -> list[str]:
    """
    Load memory log lines.

    :param limit: if provided, return only the last N lines.
    :return: list of string lines (without trailing newline)
    """
    _ensure_file()
    lines = MEMORY_FILE.read_text(encoding="utf-8").splitlines()
    if limit is None or limit <= 0:
        return lines
    return lines[-limit:]


def read_memory_log(limit: int | None = None) -> list[str]:
    """
    Backwards-compatible alias for older code that imported read_memory_log().
    """
    return load_memory_log(limit=limit)


if __name__ == "__main__":
    # Simple self-test
    append_memory("Owl memory module initialized.")
    last = load_memory_log(limit=5)
    print("Last memory entries:")
    for line in last:
        print(line)

