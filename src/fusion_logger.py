"""
fusion_logger.py
Unified logging engine for Ghost Lantern Labs.

Now includes:
 - log_event()   → write structured logs
 - tail_log()    → read last N lines for ghost_cli display
"""

from datetime import datetime
from pathlib import Path

LOG_FILE = Path("fusion_events.log")


# ============= WRITE LOG EVENTS ============= #

def log_event(module: str, event: str, details: str) -> None:
    """
    Write a structured log entry:
       timestamp | module | event | details
    """
    timestamp = datetime.utcnow().isoformat()
    line = f"{timestamp} | {module} | {event} | {details}\n"

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line)


# ============= READ LAST N LOGS ============= #

def tail_log(limit: int = 20):
    """
    Returns the last <limit> log entries as a list of strings.
    Safe even with missing/empty log file.
    """
    if not LOG_FILE.exists():
        return ["<no logs recorded>"]

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    return lines[-limit:]

