"""
sensor_drift_predictor.py

Computes a simple per-sensor "drift score" and exports a drift report.
Drift here means: how close a sensor looks to going out-of-family
based on recent normalized load and error rate.

Input:
  - data/sensor_ingest.csv (sensor, load_norm, error_rate_norm, ...)

Output:
  - docs/drift_report.txt (human-readable)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)


@dataclass
class SensorDrift:
    sensor: str
    drift_score: float  # 0.0 (no drift) → 1.0 (high drift)
    status: str         # "stable" | "trending" | "rising"
    projected_hours_to_issue: str  # e.g. "24h+" or "0–8h"


def _load_sensor_rows(path: Path) -> List[dict]:
    if not path.exists():
        return []

    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _compute_drift_for_row(row: dict) -> float:
    """
    Cheap drift heuristic:
      - higher normalized load → more drift risk
      - higher normalized error_rate → more drift risk
    """
    try:
        load = float(row.get("load_norm", 0.0))
    except (TypeError, ValueError):
        load = 0.0

    try:
        err = float(row.get("error_rate_norm", 0.0))
    except (TypeError, ValueError):
        err = 0.0

    load = max(0.0, min(1.0, load))
    err = max(0.0, min(1.0, err))

    return (load + err) / 2.0


def _status_from_score(score: float) -> Tuple[str, str]:
    """
    Map drift score → (status, projected_hours_to_issue)
    """
    if score < 0.35:
        return "stable", "24h+"
    elif score < 0.65:
        return "trending", "8–24h"
    else:
        return "rising", "0–8h"


def get_drift_scores() -> Dict[str, SensorDrift]:
    """
    Returns a dict: sensor_name -> SensorDrift
    Based on the latest row for each sensor in data/sensor_ingest.csv.
    """
    ingest_path = DATA_DIR / "sensor_ingest.csv"
    rows = _load_sensor_rows(ingest_path)
    if not rows:
        return {}

    latest_by_sensor: Dict[str, dict] = {}
    for row in rows:
        sensor = row.get("sensor") or row.get("sensor_name") or "UNKNOWN"
        latest_by_sensor[sensor] = row  # last row wins

    results: Dict[str, SensorDrift] = {}
    for sensor, row in latest_by_sensor.items():
        drift_score = _compute_drift_for_row(row)
        status, horizon = _status_from_score(drift_score)
        results[sensor] = SensorDrift(
            sensor=sensor,
            drift_score=round(drift_score, 3),
            status=status,
            projected_hours_to_issue=horizon,
        )

    return results


def _format_ascii_bar(score: float, width: int = 20) -> str:
    score = max(0.0, min(1.0, score))
    filled = int(round(score * width))
    empty = width - filled
    return "[" + ("█" * filled) + ("░" * empty) + "]"


def build_drift_report_text() -> str:
    drifts = get_drift_scores()

    lines: List[str] = []
    lines.append("=== SENSOR DRIFT PREDICTION REPORT ===")
    if not drifts:
        lines.append("No sensor_ingest.csv data found. Run fusion_ingest first.")
        return "\n".join(lines)

    lines.append("")
    lines.append(f"Total sensors with drift data: {len(drifts)}")
    lines.append("")
    lines.append("Sensor           Status     Drift    Horizon      Visual")
    lines.append("--------------- ---------- ------- ----------- -------------------------")

    for sensor, d in sorted(drifts.items(), key=lambda kv: kv[0]):
        bar = _format_ascii_bar(d.drift_score)
        pct = f"{int(round(d.drift_score * 100)):3d}%"
        name = sensor[:15].ljust(15)
        status = d.status.ljust(10)
        horizon = d.projected_hours_to_issue.ljust(11)
        lines.append(f"{name} {status} {pct}  {horizon}  {bar}")

    return "\n".join(lines)


def export_drift_report() -> str:
    """
    Writes docs/drift_report.txt and returns the path as string.
    """
    text = build_drift_report_text()
    out_path = DOCS_DIR / "drift_report.txt"
    out_path.write_text(text)
    return str(out_path)


def main() -> None:
    path = export_drift_report()
    print(f"[OK] Drift report written → {path}")


if __name__ == "__main__":
    main()

