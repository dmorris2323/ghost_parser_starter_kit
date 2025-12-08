# sensor_latency.py
# Tracks latency across all GLL sensors and produces latency intelligence.

from pathlib import Path
import time
import random
import json

LAT_FILE = Path("data/sensor_latency_log.json")


def _fake_latency():
    """Simulates realistic latency for each sensor in milliseconds."""
    return {
        "optical": random.randint(40, 140),
        "seismic": random.randint(50, 180),
        "ems": random.randint(60, 200),
        "radiation": random.randint(30, 120),
    }


def log_latency():
    LAT_FILE.parent.mkdir(exist_ok=True)

    data = _fake_latency()
    entry = {"timestamp": time.time(), "latency_ms": data}

    if LAT_FILE.exists():
        current = json.loads(LAT_FILE.read_text())
    else:
        current = []

    current.append(entry)
    LAT_FILE.write_text(json.dumps(current, indent=2))

    return entry


def compute_latency_report():
    if not LAT_FILE.exists():
        return {"status": "no_data"}

    entries = json.loads(LAT_FILE.read_text())
    latest = entries[-1]["latency_ms"]

    avg = {k: sum(e["latency_ms"][k] for e in entries) / len(entries)
           for k in latest.keys()}

    alerts = {k: ("VIOLATION" if v > 150 else "OK") for k, v in latest.items()}

    return {
        "latest": latest,
        "average": avg,
        "alerts": alerts,
        "entries_logged": len(entries),
    }


def write_latency_report():
    report = compute_latency_report()
    out = Path("docs/sensor_latency_report.json")
    out.write_text(json.dumps(report, indent=2))
    return str(out)

