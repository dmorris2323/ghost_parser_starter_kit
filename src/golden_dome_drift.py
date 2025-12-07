"""
golden_dome_drift.py — Track Golden Dome drift based on status log.

Reads:
    docs/golden_dome_status.txt

Outputs:
    docs/golden_dome_drift_report.txt

Simple logic:
- Count lines containing "FAIL" (case-insensitive).
- Expose a drift score + status.
"""

from pathlib import Path
import json

STATUS_FILE = Path("docs/golden_dome_status.txt")
REPORT_FILE = Path("docs/golden_dome_drift_report.txt")


def compute_drift() -> dict:
    """
    Compute a basic drift score from the Golden Dome status file.
    """
    if not STATUS_FILE.exists():
        return {
            "status": "no_data",
            "message": f"{STATUS_FILE} not found",
            "drift_score": 0,
        }

    lines = STATUS_FILE.read_text().splitlines()
    fail_count = sum(1 for line in lines if "FAIL" in line.upper())

    return {
        "status": "ok",
        "drift_score": fail_count,
        "total_lines": len(lines),
    }


def write_drift() -> str:
    """
    Write drift report to REPORT_FILE and return its path as a string.
    """
    result = compute_drift()
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(result, indent=2))
    return str(REPORT_FILE)


if __name__ == "__main__":
    path = write_drift()
    print(f"Golden Dome drift report written to: {path}")

