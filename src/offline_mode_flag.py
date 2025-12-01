"""
offline_mode_flag.py — Ghost Lantern Labs
-----------------------------------------

Central helper for marking GLL as:

- NORMAL_OPERATION
- OFFLINE_OR_DEGRADED

Writes a simple text file 'offline_status.txt' in the src directory
so an operator (or future UI) can quickly see the current state.

This does NOT attempt to detect offline mode by itself.
It is meant to be called by higher-level logic, e.g.,
the LLM adapter when it falls back to local_rules.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

STATUS_PATH = Path(__file__).parent / "offline_status.txt"


def _write_status(status: str, reason: Optional[str] = None) -> None:
    """
    Internal helper to write the status file.
    """
    ts = datetime.utcnow().isoformat()
    lines = [
        f"TIMESTAMP_UTC: {ts}",
        f"STATUS: {status}",
    ]
    if reason:
        lines.append(f"REASON: {reason}")

    text = "\n".join(lines) + "\n"
    STATUS_PATH.write_text(text, encoding="utf-8")


def set_offline_mode(reason: str) -> None:
    """
    Mark system as offline/degraded. Call this when we know
    we're running on local_rules or when primary providers fail.
    """
    _write_status("OFFLINE_OR_DEGRADED", reason)


def set_online_mode() -> None:
    """
    Mark system as in normal operation.
    Call this when primary provider is being used successfully.
    """
    _write_status("NORMAL_OPERATION", None)


def get_status() -> str:
    """
    Quick helper to read current status as a string.
    If file does not exist yet, assume NORMAL_OPERATION.
    """
    if not STATUS_PATH.exists():
        return "UNKNOWN (no offline_status.txt found; assuming NORMAL_OPERATION)"

    return STATUS_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    # Quick manual test: flip modes
    set_online_mode()
    print("Online status:\n", get_status())
    set_offline_mode("manual_test: forced degraded for demo")
    print("Offline status:\n", get_status())

