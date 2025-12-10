"""
sensor_outage_predictor.py

Very lightweight "next outage" predictor.

Phase 1:
- Looks at run_history.csv if available.
- Counts how often each sensor shows up in errors.
- Produces a "risk bucket" (LOW / MEDIUM / HIGH) and simple notes.

Safe:
- Works even when run_history.csv is missing or incomplete.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)

RUN_HISTORY = DATA_DIR / "run_history.csv"


def _risk_bucket(error_count: int) -> str:
    if error_count == 0:
        return "LOW"
    if error_count <= 3:
        return "MEDIUM"
    return "HIGH"


def _load_error_counts() -> Counter:
    counts: Counter = Counter()
    if not RUN_HISTORY.exists():
        return counts

    try:
        with RUN_HISTORY.open("r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = (row.get("status") or "").lower()
                sensor = (row.get("sensor") or "global").lower()
                if status in {"fail", "error", "degraded"}:
                    counts[sensor] += 1
    except Exception:
        # Fail safely — just return empty
        return Counter()

    return counts


def predict_outages() -> Dict[str, Any]:
    """
    Build a simple prediction object per sensor based on error counts.
    """
    ts = datetime.utcnow().isoformat() + "Z"
    counts = _load_error_counts()

    sensors = ["optical", "seismic", "ems", "radiation", "global"]
    sensor_view = {}

    for s in sensors:
        c = counts.get(s, 0)
        sensor_view[s] = {
            "error_events": int(c),
            "outage_risk": _risk_bucket(c),
            "comment": (
                "No failures seen yet."
                if c == 0
                else "Some instability detected; monitor closely."
                if c <= 3
                else "High risk of outage; prioritize maintenance."
            ),
        }

    out = {
        "generated_at": ts,
        "source": str(RUN_HISTORY) if RUN_HISTORY.exists() else "no_history",
        "sensors": sensor_view,
    }

    # Write artifacts
    json_path = DOCS_DIR / "sensor_outage_forecast.json"
    txt_path = DOCS_DIR / "sensor_outage_forecast.txt"

    json_path.write_text(json.dumps(out, indent=2))
    lines = [
        "=== SENSOR OUTAGE PREDICTOR ===",
        f"Generated: {ts}",
        f"History Source: {out['source']}",
        "",
    ]
    for name, info in sensor_view.items():
        lines.append(f"[{name.upper()}] Risk={info['outage_risk']}, Errors={info['error_events']}")
        lines.append(f"  - {info['comment']}")
    txt_path.write_text("\n".join(lines))

    return {
        "status": "ok",
        "json_path": str(json_path),
        "text_path": str(txt_path),
    }


def main() -> None:
    print(json.dumps(predict_outages(), indent=2))


if __name__ == "__main__":
    main()

