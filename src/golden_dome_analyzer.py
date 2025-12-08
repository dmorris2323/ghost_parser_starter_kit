"""
golden_dome_analyzer.py

Analyze Golden Dome history for anomalies and trend:

- Reads docs/golden_dome_history.csv
- Flags:
    * Low reliability
    * High drift magnitude
    * Crisis Mode ON snapshots
- Computes a simple trend summary.

Outputs:
- Prints analysis to stdout
- Writes detailed report to docs/golden_dome_analyzer_report.txt
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict, Any

HISTORY_CSV = Path("docs/golden_dome_history.csv")
REPORT_TXT = Path("docs/golden_dome_analyzer_report.txt")


def load_history() -> List[Dict[str, Any]]:
    if not HISTORY_CSV.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with HISTORY_CSV.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def _to_float(val, default=0.0) -> float:
    try:
        return float(val)
    except Exception:
        return float(default)


def analyze(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {
            "status": "empty",
            "message": "No Golden Dome history found.",
            "total_rows": 0,
        }

    anomalies = []
    reliabilities = []
    drifts = []
    crisis_on = 0

    for r in rows:
        rel = _to_float(r.get("avg_reliability", 0.0))
        drift = _to_float(r.get("drift_magnitude", 0.0))
        cmode = (r.get("crisis_mode", "OFF") or "").upper().strip()
        ts = r.get("timestamp", "")

        reliabilities.append(rel)
        drifts.append(drift)
        if cmode == "ON":
            crisis_on += 1

        # Simple anomaly rules
        if rel < 80.0:
            anomalies.append(
                f"[{ts}] LOW RELIABILITY: {rel} (drift={drift}, crisis={cmode})"
            )
        if drift > 10.0:
            anomalies.append(
                f"[{ts}] HIGH DRIFT: {drift} (reliability={rel}, crisis={cmode})"
            )
        if cmode == "ON":
            anomalies.append(
                f"[{ts}] CRISIS MODE ON (reliability={rel}, drift={drift})"
            )

    avg_rel = sum(reliabilities) / len(reliabilities) if reliabilities else 0.0
    avg_drift = sum(drifts) / len(drifts) if drifts else 0.0

    summary = {
        "status": "ok",
        "total_rows": len(rows),
        "avg_reliability": round(avg_rel, 2),
        "avg_drift": round(avg_drift, 2),
        "crisis_snapshots": crisis_on,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }
    return summary


def build_report() -> str:
    rows = load_history()
    summary = analyze(rows)

    REPORT_TXT.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []

    lines.append("=== GOLDEN DOME HISTORY ANALYZER ===")
    lines.append(f"Status: {summary.get('status')}")
    lines.append(f"Total snapshots: {summary.get('total_rows')}")
    lines.append(f"Average reliability: {summary.get('avg_reliability')}")
    lines.append(f"Average drift magnitude: {summary.get('avg_drift')}")
    lines.append(f"Crisis Mode snapshots: {summary.get('crisis_snapshots')}")
    lines.append(f"Anomaly count: {summary.get('anomaly_count')}")
    lines.append("")

    anomalies = summary.get("anomalies") or []
    if anomalies:
        lines.append("=== ANOMALIES ===")
        for a in anomalies:
            lines.append(a)
    else:
        lines.append("No anomalies detected based on current thresholds.")

    REPORT_TXT.write_text("\n".join(lines))
    return str(REPORT_TXT)


def main():
    path = build_report()
    print(f"Golden Dome Analyzer report written to: {path}")
    print()
    print(REPORT_TXT.read_text())


if __name__ == "__main__":
    main()

