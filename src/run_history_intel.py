"""
run_history_intel.py — Run-History Intelligence Timeline

Reads data/run_history.csv and produces:
  • A simple pass/fail timeline
  • Streaks and success rates
  • A human-readable brief saved to run_history_intel_brief.txt

This version is DEFENSIVE:
  • Does NOT assume a 'status' column exists
  • Tries to infer status from common fields (status/result/outcome/exit_code)
  • Never crashes on missing keys — unknown rows are treated as 'unknown'
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

BASE = Path(__file__).parent
RUN_HISTORY_CSV = BASE / "data" / "run_history.csv"
BRIEF_FILE = BASE / "run_history_intel_brief.txt"


@dataclass
class RunRecord:
    raw: Dict[str, Any]
    status: str  # "pass", "fail", or "unknown"
    label: str   # short label (e.g., tests, qa_validator, fusion_run)
    timestamp: str  # best-effort timestamp string


def infer_status(row: Dict[str, str]) -> str:
    """
    Try to infer pass/fail from whatever fields exist.
    Priority:
      - status
      - result
      - outcome
      - exit_code (0 = pass, else fail)
    Anything else → 'unknown'
    """
    candidates = [
        row.get("status"),
        row.get("result"),
        row.get("outcome"),
    ]

    for val in candidates:
        if not val:
            continue
        v = str(val).strip().lower()
        if v in ("pass", "ok", "success", "passed"):
            return "pass"
        if v in ("fail", "error", "failed", "failure"):
            return "fail"

    # Try exit_code if present
    exit_code = row.get("exit_code")
    if exit_code is not None:
        try:
            code = int(exit_code)
            return "pass" if code == 0 else "fail"
        except ValueError:
            pass

    return "unknown"


def infer_label(row: Dict[str, str]) -> str:
    """
    Choose a human-readable label for the run.
    Try:
      - label
      - job
      - task
      - command
      - script
    Fallback: 'run'
    """
    for key in ("label", "job", "task", "command", "script"):
        val = row.get(key)
        if val:
            return str(val).strip()
    return "run"


def infer_timestamp(row: Dict[str, str]) -> str:
    """
    Best-effort timestamp:
      - timestamp
      - time
      - started_at
      - finished_at
    Fallback: 'unknown'
    """
    for key in ("timestamp", "time", "started_at", "finished_at"):
        val = row.get(key)
        if val:
            return str(val).strip()
    return "unknown"


def load_run_history() -> List[RunRecord]:
    if not RUN_HISTORY_CSV.exists():
        return []

    records: List[RunRecord] = []
    with RUN_HISTORY_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip totally empty rows
            if not any(row.values()):
                continue
            status = infer_status(row)
            label = infer_label(row)
            ts = infer_timestamp(row)
            records.append(RunRecord(raw=row, status=status, label=label, timestamp=ts))
    return records


def analyze_trends(records: List[RunRecord]) -> Dict[str, Any]:
    total = len(records)
    total_pass = sum(1 for r in records if r.status == "pass")
    total_fail = sum(1 for r in records if r.status == "fail")
    total_unknown = sum(1 for r in records if r.status == "unknown")

    # Success rate based on known pass/fail only
    known = total_pass + total_fail
    success_rate = (total_pass / known * 100) if known > 0 else 0.0

    # Streak: look from the end backwards until status changes
    current_streak = 0
    current_type = None  # "pass", "fail", "mixed", "unknown", or None

    if records:
        last_status = records[-1].status
        if last_status in ("pass", "fail"):
            current_type = last_status
            for r in reversed(records):
                if r.status == last_status:
                    current_streak += 1
                else:
                    break
        else:
            current_type = "unknown"
            current_streak = 1

    return {
        "total": total,
        "pass": total_pass,
        "fail": total_fail,
        "unknown": total_unknown,
        "success_rate": round(success_rate, 1),
        "current_streak": current_streak,
        "current_type": current_type,
        "last_run": records[-1] if records else None,
    }


def build_brief(records: List[RunRecord], trends: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("=== RUN HISTORY INTELLIGENCE BRIEF ===")
    lines.append("")
    if not records:
        lines.append("No run history found (data/run_history.csv missing or empty).")
        return "\n".join(lines)

    lines.append(f"Total runs logged: {trends['total']}")
    lines.append(f"  Pass:    {trends['pass']}")
    lines.append(f"  Fail:    {trends['fail']}")
    lines.append(f"  Unknown: {trends['unknown']}")
    lines.append(f"Success rate (known only): {trends['success_rate']}%")
    lines.append("")

    if trends["current_type"] is None:
        lines.append("Current streak: N/A (no runs yet)")
    else:
        lines.append(
            f"Current streak: {trends['current_streak']} × {trends['current_type'].upper()}"
        )

    last = trends["last_run"]
    if last:
        lines.append("")
        lines.append("Last run:")
        lines.append(f"  Label:     {last.label}")
        lines.append(f"  Status:    {last.status}")
        lines.append(f"  Timestamp: {last.timestamp}")

    # Small timeline of last 10 runs
    lines.append("")
    lines.append("Recent timeline (last 10):")
    for r in records[-10:]:
        lines.append(f"- {r.timestamp} | {r.label} | {r.status}")

    return "\n".join(lines)


def main() -> str:
    records = load_run_history()
    trends = analyze_trends(records)
    brief = build_brief(records, trends)
    BRIEF_FILE.write_text(brief, encoding="utf-8")
    return f"Run-history intelligence brief written to {BRIEF_FILE}"


if __name__ == "__main__":
    print(main())

