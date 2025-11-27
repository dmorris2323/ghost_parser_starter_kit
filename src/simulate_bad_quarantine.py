"""
simulate_bad_quarantine.py — Day 53
Generate a fake bad_data_quarantine.csv so we can test
the bad-data heatmap and anti-DoS defenses without
touching the live fusion pipeline.
"""

from datetime import datetime, timedelta
from pathlib import Path
import csv

from fusion_logger import log_event

QUARANTINE_PATH = Path("bad_data_quarantine.csv")


def generate_fake_quarantine() -> None:
    now = datetime.utcnow()

    rows = []

    # Low-level noise over time
    for i in range(10):
        rows.append(
            {
                "timestamp": (now - timedelta(minutes=60 - i)).isoformat(),
                "source": "sensor_cluster_north",
                "reason": "missing_fields",
                "count": 1,
                "severity": "low",
                "sensor_type": "seismic",
                "aoi": "NK_COAST",
            }
        )

    # Medium anomaly burst
    for i in range(5):
        rows.append(
            {
                "timestamp": (now - timedelta(minutes=10 - i)).isoformat(),
                "source": "gateway_alpha",
                "reason": "invalid_values",
                "count": 5,
                "severity": "medium",
                "sensor_type": "radiation",
                "aoi": "NK_INLAND",
            }
        )

    # Heavy suspected flood
    for i in range(3):
        rows.append(
            {
                "timestamp": (now - timedelta(minutes=3 - i)).isoformat(),
                "source": "unknown_edge_node",
                "reason": "suspicious_volume",
                "count": 50,
                "severity": "high",
                "sensor_type": "network",
                "aoi": "GLOBAL",
            }
        )

    header = [
        "timestamp",
        "source",
        "reason",
        "count",
        "severity",
        "sensor_type",
        "aoi",
    ]

    with QUARANTINE_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] bad_data_quarantine.csv written with {len(rows)} rows")
    log_event("simulate_bad_quarantine", "completed", f"{len(rows)} rows")


if __name__ == "__main__":
    generate_fake_quarantine()

