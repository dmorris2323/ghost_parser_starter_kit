"""
pipeline_health.py

Computes an overall health score for the GLL fusion pipeline.

Inputs:
  - qa_summary.txt   (PASS/FAIL counts)
  - critical_alerts.csv (for anomaly density)
  - operator_snapshot.txt (optional context)

Outputs:
  - pipeline_health.txt
  - dict with score + components
"""

from pathlib import Path
import csv
from typing import Dict, Any


HEALTH_FILE = Path("pipeline_health.txt")


def _parse_qa_summary(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0

    text = path.read_text(encoding="utf-8").splitlines()
    passed = 0
    failed = 0
    for line in text:
        if line.strip().startswith("[PASS]"):
            passed += 1
        elif line.strip().startswith("[FAIL]"):
            failed += 1
    return passed, failed


def _count_critical_alerts() -> int:
    path = Path("critical_alerts.csv")
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def evaluate_pipeline_health() -> Dict[str, Any]:
    """
    Compute a simple health score:

      - Base score from QA:
          100 if all tests pass and at least 1 test
          70 if some pass and some fail
          40 if all fail or no tests detected

      - Penalty from critical alerts:
          -5 points per critical alert, capped at -40

    Returns dict with:
      - score (0–100)
      - qa_passed
      - qa_failed
      - critical_alerts
      - status
      - notes
    """
    qa_passed, qa_failed = _parse_qa_summary(Path("qa_summary.txt"))
    critical_alerts = _count_critical_alerts()

    # Base from QA
    if qa_passed > 0 and qa_failed == 0:
        base = 100
        qa_status = "All tests passed."
    elif qa_passed > 0 and qa_failed > 0:
        base = 70
        qa_status = "Mixed results — some tests failing."
    else:
        base = 40
        qa_status = "No passing tests detected or QA summary missing."

    # Penalty from alerts
    penalty = min(critical_alerts * 5, 40)
    score = max(0, base - penalty)

    if score >= 90:
        status = "GREEN"
    elif score >= 70:
        status = "AMBER"
    else:
        status = "RED"

    notes = []
    notes.append(qa_status)
    if critical_alerts > 0:
        notes.append(f"{critical_alerts} critical alert(s) present — reduced health score.")
    else:
        notes.append("No critical alerts detected in current run.")

    summary = {
        "score": score,
        "qa_passed": qa_passed,
        "qa_failed": qa_failed,
        "critical_alerts": critical_alerts,
        "status": status,
        "notes": " ".join(notes),
    }

    _write_health_file(summary)
    return summary


def _write_health_file(summary: Dict[str, Any]) -> None:
    lines = []
    lines.append("======================================")
    lines.append(" GLL PIPELINE HEALTH SUMMARY")
    lines.append("======================================")
    lines.append(f"Overall Health Score: {summary['score']}/100")
    lines.append(f"Status: {summary['status']}")
    lines.append("")
    lines.append(f"QA Passed: {summary['qa_passed']}")
    lines.append(f"QA Failed: {summary['qa_failed']}")
    lines.append(f"Critical Alerts: {summary['critical_alerts']}")
    lines.append("")
    lines.append("Notes:")
    lines.append(summary["notes"])
    lines.append("")

    HEALTH_FILE.write_text("\n".join(lines), encoding="utf-8")

