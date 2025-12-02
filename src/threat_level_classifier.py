"""
threat_level_classifier.py — Ghost Lantern Labs
-----------------------------------------------

Reads data/run_history.csv and classifies each run into:
- LOW
- MEDIUM
- HIGH

based on max_threat_hint.

Outputs:
- data/threat_levels.csv

This is the bridge between numeric scores and commander-friendly language.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import csv


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RUN_HISTORY_PATH = DATA_DIR / "run_history.csv"
THREAT_LEVELS_PATH = DATA_DIR / "threat_levels.csv"


def load_run_history() -> List[Dict[str, Any]]:
    if not RUN_HISTORY_PATH.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with RUN_HISTORY_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def classify_threat(max_threat: float) -> str:
    """
    Convert numeric max_threat_hint into a discrete level.
    Tunable thresholds:

    - HIGH:   >= 0.7
    - MEDIUM: 0.3–0.7
    - LOW:    < 0.3
    """
    if max_threat >= 0.7:
        return "HIGH"
    if max_threat >= 0.3:
        return "MEDIUM"
    return "LOW"


def build_threat_rows(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for r in history:
        try:
            max_t = float(r.get("max_threat_hint", 0.0))
            avg_t = float(r.get("avg_threat_hint", 0.0))
        except ValueError:
            max_t = 0.0
            avg_t = 0.0

        level = classify_threat(max_t)

        rows.append(
            {
                "timestamp_utc": r.get("timestamp_utc", ""),
                "run_id": r.get("run_id", ""),
                "valid_sensor_count": r.get("valid_sensor_count", ""),
                "fallback_reason": r.get("fallback_reason", ""),
                "max_threat_hint": f"{max_t:.3f}",
                "avg_threat_hint": f"{avg_t:.3f}",
                "threat_level": level,
            }
        )

    return rows


def write_threat_levels(rows: List[Dict[str, Any]]) -> None:
    fieldnames = [
        "timestamp_utc",
        "run_id",
        "valid_sensor_count",
        "fallback_reason",
        "max_threat_hint",
        "avg_threat_hint",
        "threat_level",
    ]

    THREAT_LEVELS_PATH.parent.mkdir(exist_ok=True, parents=True)

    with THREAT_LEVELS_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    history = load_run_history()
    if not history:
        print("No run history found. Run sensor_run_history.py first.")
        return

    rows = build_threat_rows(history)
    write_threat_levels(rows)

    total = len(rows)
    high = sum(1 for r in rows if r["threat_level"] == "HIGH")
    med = sum(1 for r in rows if r["threat_level"] == "MEDIUM")
    low = sum(1 for r in rows if r["threat_level"] == "LOW")

    print(f"✅ Threat levels written to: {THREAT_LEVELS_PATH}")
    print(f"   Total runs: {total}  HIGH={high}  MEDIUM={med}  LOW={low}")


if __name__ == "__main__":
    main()

