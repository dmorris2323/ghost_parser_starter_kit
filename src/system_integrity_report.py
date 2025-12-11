#!/usr/bin/env python3
"""
system_integrity_report.py

Ghost Lantern Labs – System Integrity Report
-------------------------------------------

Purpose:
    Generate a human-readable integrity report for GLL using
    SPS Mutation Watcher v2.

Output:
    - src/docs/system_integrity_report.txt
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from sps_mutation_watcher import run_sps_immunity_scan


SRC_DIR = Path(__file__).resolve().parent
DOCS_DIR = SRC_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = DOCS_DIR / "system_integrity_report.txt"


def generate_system_integrity_report() -> Dict[str, Any]:
    scan = run_sps_immunity_scan()
    summary = scan["summary"]
    files = scan["files"]

    lines = []
    lines.append("Ghost Lantern Labs – System Integrity Report")
    lines.append("------------------------------------------------")
    lines.append(f"Generated at (UTC): {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"  Total tracked:      {summary['total_tracked']}")
    lines.append(f"  Clean:              {summary['clean']}")
    lines.append(f"  Modified:           {summary['modified']}")
    lines.append(f"  Missing:            {summary['missing']}")
    lines.append(f"  Untracked baseline: {summary['untracked_baseline']}")
    lines.append("")
    lines.append("Per-file status:")
    for label, status in sorted(files.items()):
        lines.append(f"  - {label}: {status}")
    lines.append("")
    lines.append(f"Baseline file: {scan['baseline_path']}")
    lines.append("If files are MODIFIED or MISSING, investigate before using GLL for critical work.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    return {
        "report_path": str(REPORT_PATH),
        "summary": summary,
    }


if __name__ == "__main__":
    result = generate_system_integrity_report()
    print(f"System Integrity Report written to: {result['report_path']}")
    print("Summary:", result["summary"])

