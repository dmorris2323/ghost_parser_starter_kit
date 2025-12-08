"""
golden_dome_history.py — Log Golden Dome state over time.

Captures:
  - timestamp
  - operator
  - crisis_mode
  - avg_reliability
  - agreement_score
  - drift_magnitude (if provided)

Appends rows to: docs/golden_dome_history.csv
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from golden_dome_drift import compute_drift
from sensor_reliability import compute_reliability_all
from crisis_mode_flag import status as crisis_status
from operator_identity import get_identity

HISTORY_CSV = Path("docs/golden_dome_history.csv")


def _ensure_header(path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "timestamp",
                    "operator",
                    "crisis_mode",
                    "avg_reliability",
                    "agreement_score",
                    "drift_magnitude",
                ]
            )


def snapshot_state() -> Dict[str, Any]:
    """
    Build a single snapshot of Golden Dome state.
    """
    # Defaults
    avg_rel = 90.0
    agreement = 90.0
    drift_mag = 0.0

    try:
        rel = compute_reliability_all()
        if isinstance(rel, dict):
            avg_rel = rel.get("avg_reliability", avg_rel) or avg_rel
    except Exception:
        pass

    try:
        drift = compute_drift()
        if isinstance(drift, dict):
            agreement = drift.get("agreement_score", agreement) or agreement
            drift_mag = drift.get("drift_magnitude", drift_mag) or drift_mag
    except Exception:
        pass

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "operator": get_identity(),
        "crisis_mode": crisis_status(),
        "avg_reliability": round(float(avg_rel), 2),
        "agreement_score": round(float(agreement), 2),
        "drift_magnitude": round(float(drift_mag), 2),
    }


def append_snapshot() -> str:
    """
    Append a snapshot row and return CSV path.
    """
    _ensure_header(HISTORY_CSV)
    snap = snapshot_state()

    with HISTORY_CSV.open("a", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                snap["timestamp"],
                snap["operator"],
                snap["crisis_mode"],
                snap["avg_reliability"],
                snap["agreement_score"],
                snap["drift_magnitude"],
            ]
        )

    return str(HISTORY_CSV)


def print_tail(n: int = 5):
    if not HISTORY_CSV.exists():
        print("No Golden Dome history yet.")
        return

    rows = HISTORY_CSV.read_text().splitlines()
    tail = rows[-n:] if len(rows) > n else rows
    print("\n=== Golden Dome History (tail) ===")
    for line in tail:
        print(line)
    print("==================================\n")


def main():
    path = append_snapshot()
    print(f"Golden Dome snapshot appended to: {path}")
    print_tail()


if __name__ == "__main__":
    main()

