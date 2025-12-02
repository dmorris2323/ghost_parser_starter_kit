"""
sensor_run_history.py — Ghost Lantern Labs
------------------------------------------

Runs multiple sensor ingest cycles and logs a compact history:

- For each run:
  - Collect sensor samples via fusion_ingest.collect_sensor_samples()
  - Build a fusion record (valid_sensor_count, fallback_reason)
  - Normalize each sensor to get threat_hint
  - Compute:
      * max_threat_hint
      * avg_threat_hint
  - Append a row to data/run_history.csv

This is a lightweight "ISR timeline" for your sensor layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import csv

from fusion_ingest import collect_sensor_samples, build_fusion_record
from sensor_interface import SensorSample
from sensor_normalizer import normalize_sensor_sample, NormalizedRecord


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

RUN_HISTORY_PATH = DATA_DIR / "run_history.csv"


def run_single_cycle(run_id: int) -> Dict[str, Any]:
    """
    Run one ingest + normalization cycle and return a summary dict.
    """
    samples: List[SensorSample] = collect_sensor_samples()
    fusion_record = build_fusion_record(samples)

    normalized: List[NormalizedRecord] = []
    for s in samples:
        if not s.valid:
            continue
        nr = normalize_sensor_sample(s)
        normalized.append(nr)

    threat_values = [nr.threat_hint for nr in normalized] or [0.0]
    max_threat = max(threat_values)
    avg_threat = sum(threat_values) / len(threat_values)

    ts = datetime.utcnow().isoformat()

    summary = {
        "timestamp_utc": ts,
        "run_id": run_id,
        "valid_sensor_count": fusion_record.get("valid_sensor_count", 0),
        "fallback_reason": fusion_record.get("fallback_reason", "unknown"),
        "max_threat_hint": round(max_threat, 3),
        "avg_threat_hint": round(avg_threat, 3),
    }
    return summary


def append_run_history(row: Dict[str, Any]) -> None:
    """
    Append a single summary row to run_history.csv
    """
    fieldnames = [
        "timestamp_utc",
        "run_id",
        "valid_sensor_count",
        "fallback_reason",
        "max_threat_hint",
        "avg_threat_hint",
    ]

    file_exists = RUN_HISTORY_PATH.exists()
    with RUN_HISTORY_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main(iterations: int = 10) -> None:
    """
    Run N cycles and log them.
    """
    print(f"🏃 Running {iterations} sensor cycles and logging to {RUN_HISTORY_PATH} ...")

    for i in range(1, iterations + 1):
        summary = run_single_cycle(i)
        append_run_history(summary)
        print(
            f"  Run {i}: "
            f"valid={summary['valid_sensor_count']} "
            f"fallback={summary['fallback_reason']} "
            f"max_threat={summary['max_threat_hint']} "
            f"avg_threat={summary['avg_threat_hint']}"
        )

    print("✅ Sensor run history updated.")


if __name__ == "__main__":
    main()

