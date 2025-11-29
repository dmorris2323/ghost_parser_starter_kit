"""
log_intel.py — Ghost Lantern Labs Log Intelligence (v1)

Reads the fusion_events.log and produces a simple, operator-friendly
summary of system health:

- How many recent events
- How many errors vs passes
- Which modules are the noisiest
- A simple GREEN / YELLOW / RED status

Safe to run any time:
    poetry run python src/log_intel.py
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

from fusion_logger import LOG_FILE, tail_log, log_event


@dataclass
class LogRecord:
    timestamp: datetime
    module: str
    event: str
    details: str


def _parse_line(line: str) -> LogRecord | None:
    """
    Parse a single log line of the form:
      2025-11-27T10:00:00.000000 | module | event | details
    Returns LogRecord or None if the line is malformed.
    """
    parts = [p.strip() for p in line.split("|", 3)]
    if len(parts) != 4:
        return None

    raw_ts, module, event, details = parts
    try:
        ts = datetime.fromisoformat(raw_ts)
    except Exception:
        # If timestamp somehow corrupt, just skip
        return None

    return LogRecord(timestamp=ts, module=module, event=event, details=details)


def analyze_logs(limit: int = 200) -> Dict[str, Any]:
    """
    Core analytics over the last <limit> log lines.

    Returns a dict with:
      - total
      - errors
      - passes
      - by_module
      - latest_event
      - status (GREEN/YELLOW/RED)
    """
    raw_lines = tail_log(limit)
    records: List[LogRecord] = []

    for line in raw_lines:
        rec = _parse_line(line)
        if rec is not None:
            records.append(rec)

    total = len(records)
    if total == 0:
        return {
            "total": 0,
            "errors": 0,
            "passes": 0,
            "by_module": {},
            "latest_event": "<no valid log records>",
            "status": "GREEN",
        }

    error_events = {"error", "fail", "failed", "schema_load_error"}
    pass_events = {"pass", "completed"}

    errors = 0
    passes = 0
    by_module = Counter()

    for r in records:
        by_module[r.module] += 1

        # crude classification by event keyword
        lower = r.event.lower()
        if any(key in lower for key in error_events):
            errors += 1
        if any(key in lower for key in pass_events):
            passes += 1

    latest = max(records, key=lambda r: r.timestamp)

    # Simple traffic light status
    if errors == 0:
        status = "GREEN"
    elif errors < 5:
        status = "YELLOW"
    else:
        status = "RED"

    return {
        "total": total,
        "errors": errors,
        "passes": passes,
        "by_module": dict(by_module.most_common(5)),
        "latest_event": f"{latest.timestamp.isoformat()} | {latest.module} | {latest.event}",
        "status": status,
    }


def summarize_logs(limit: int = 200) -> str:
    """
    Human-readable summary string for CLI or reports.
    """
    info = analyze_logs(limit)

    if info["total"] == 0:
        msg = "No valid log records found in fusion_events.log."
        log_event("log_intel", "summary", "no_records")
        return msg

    status = info["status"]
    total = info["total"]
    errors = info["errors"]
    passes = info["passes"]
    latest = info["latest_event"]
    by_module = info["by_module"]

    lines: List[str] = []
    lines.append("📊 GLL LOG INTELLIGENCE (Last ~{} events)".format(total))
    lines.append(f"Status: {status}")
    lines.append(f"- Errors: {errors}")
    lines.append(f"- Passes: {passes}")
    lines.append("")
    lines.append("Top noisy modules:")
    if by_module:
        for mod, count in by_module.items():
            lines.append(f"  • {mod}: {count} events")
    else:
        lines.append("  • <no module data>")

    lines.append("")
    lines.append(f"Most recent event:")
    lines.append(f"  {latest}")

    summary = "\n".join(lines)
    log_event("log_intel", "summary", f"status={status}, total={total}, errors={errors}")
    return summary


if __name__ == "__main__":
    if not LOG_FILE.exists():
        print("fusion_events.log not found. Run ghost_cli or pipeline first.")
    else:
        print(summarize_logs())

