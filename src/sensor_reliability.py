"""
sensor_reliability.py

Ghost Lantern Labs – Sensor Reliability Predictor (Day 59)

This module:
- Reads run_history.csv (if present) and estimates reliability per sensor.
- Falls back to sensible defaults if data is missing.
- Writes a human-readable reliability report to src/docs/reliability_report.txt.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"


@dataclass
class SensorReliability:
    name: str
    reliability: float  # 0–100
    last_seen: Optional[str] = None
    last_status: Optional[str] = None
    projected_window: str = "unknown"  # "stable", "watch", "at_risk"


def _load_run_history() -> List[dict]:
    """
    Load run_history.csv if it exists.
    If missing or malformed, return an empty list.
    """
    path = DATA_DIR / "run_history.csv"
    if not path.exists():
        return []

    rows: List[dict] = []
    try:
        with path.open("r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception:
        # Don't let bad CSV kill the system.
        return []

    return rows


def _parse_timestamp(value: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    return None


def compute_reliability_scores() -> Dict[str, SensorReliability]:
    """
    Compute reliability scores per sensor from run_history rows.

    Heuristic:
    - If we have rows with 'sensor' + 'status':
        - reliability = (#pass / total) * 100
    - If no data → default reliability and 'watch' window.

    Sensors we care about by default:
    - optical, seismic, ems, radiation
    """
    rows = _load_run_history()

    sensors = ["optical", "seismic", "ems", "radiation"]
    results: Dict[str, SensorReliability] = {}

    # Initialize defaults
    default_baseline = {
        "optical": 0.92,
        "seismic": 0.88,
        "ems": 0.95,
        "radiation": 0.97,
    }

    # Aggregate stats
    stats: Dict[str, dict] = {s: {"total": 0, "pass": 0, "last_seen": None, "last_status": None} for s in sensors}

    for row in rows:
        sensor_name = (row.get("sensor") or "").strip().lower()
        if sensor_name not in sensors:
            continue

        status = (row.get("status") or "").strip().lower()  # expect "pass" or "fail"
        ts_raw = row.get("timestamp") or row.get("time") or ""

        stats[sensor_name]["total"] += 1
        if status == "pass":
            stats[sensor_name]["pass"] += 1

        ts = _parse_timestamp(ts_raw)
        if ts:
            # Keep the latest timestamp
            prev_ts = stats[sensor_name]["last_seen"]
            if prev_ts is None or ts > prev_ts:
                stats[sensor_name]["last_seen"] = ts
                stats[sensor_name]["last_status"] = status
        else:
            # No valid timestamp; just record status
            stats[sensor_name]["last_status"] = status or stats[sensor_name]["last_status"]

    # Build SensorReliability objects
    for s in sensors:
        s_stats = stats[s]
        total = s_stats["total"]
        passed = s_stats["pass"]

        if total > 0:
            reliability = (passed / total) * 100.0
        else:
            # No data: use default baseline * 100
            baseline = default_baseline.get(s, 0.85)
            reliability = baseline * 100.0

        # Projected window heuristic
        if reliability >= 90.0:
            proj = "stable"
        elif reliability >= 75.0:
            proj = "watch"
        else:
            proj = "at_risk"

        last_seen = s_stats["last_seen"]
        last_seen_str = last_seen.isoformat() if isinstance(last_seen, datetime) else None

        results[s] = SensorReliability(
            name=s,
            reliability=reliability,
            last_seen=last_seen_str,
            last_status=s_stats["last_status"],
            projected_window=proj,
        )

    return results


def ascii_bar(percentage: float, width: int = 16) -> str:
    """
    Build a simple ASCII bar like:
    [██████████░░░░]
    """
    if percentage < 0:
        percentage = 0.0
    if percentage > 100:
        percentage = 100.0

    filled = int(round((percentage / 100.0) * width))
    empty = width - filled
    return "[" + ("█" * filled) + ("░" * empty) + "]"


def build_reliability_report_text() -> str:
    """
    Build a human-readable reliability report.
    """
    scores = compute_reliability_scores()

    lines: List[str] = []
    lines.append("=== SENSOR RELIABILITY REPORT ===")
    lines.append("Ghost Lantern Labs – Day 59 module")
    lines.append("")
    lines.append(f"{'SENSOR':10} {'BAR':20} {'REL':>6}   WINDOW       LAST_SEEN")
    lines.append("-" * 70)

    for name in sorted(scores.keys()):
        s = scores[name]
        bar = ascii_bar(s.reliability)
        rel_str = f"{s.reliability:5.1f}%"
        last = s.last_seen or "n/a"
        window = s.projected_window
        lines.append(f"{name.upper():10} {bar:20} {rel_str:>6}   {window:<10} {last}")

    lines.append("")
    return "\n".join(lines)


def export_reliability_report() -> dict:
    """
    Write the report to docs/reliability_report.txt and return a status dict.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DOCS_DIR / "reliability_report.txt"
    text = build_reliability_report_text()
    report_path.write_text(text, encoding="utf-8")

    return {
        "status": "ok",
        "file": str(report_path),
        "lines": text.count("\n") + 1,
    }


def main() -> None:
    report = export_reliability_report()
    print(build_reliability_report_text())
    print("")
    print(f"[OK] Reliability report written → {report['file']}")


if __name__ == "__main__":
    main()

