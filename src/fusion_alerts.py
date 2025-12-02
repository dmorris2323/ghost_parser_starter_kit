"""
fusion_alerts.py — Ghost Lantern Labs
-------------------------------------
Alert builder, critical alert loader, and scoring helpers.
"""

import csv
from pathlib import Path

ALERT_FILE = Path(__file__).parent / "critical_alerts.csv"


def build_alerts(fused_csv="fused_output.csv"):
    """
    Create alert records from fused_output.csv.
    Critical = any sensor > 0.85
    Warning = any sensor > 0.55
    """
    fused_path = Path(__file__).parent / fused_csv
    if not fused_path.exists():
        return {"status": "fail", "reason": "missing fused_output"}

    rows = fused_path.read_text().splitlines()
    if len(rows) <= 1:
        return {"status": "fail", "reason": "no usable rows"}

    reader = csv.DictReader(rows)

    alerts = []
    for row in reader:
        crit = []
        warn = []

        for k, v in row.items():
            if k.lower() in ["timestamp", "sensor", "id"]:
                continue
            try:
                value = float(v)
            except:
                continue

            if value >= 0.85:
                crit.append(k)
            elif value >= 0.55:
                warn.append(k)

        alerts.append({
            "timestamp": row.get("timestamp", "N/A"),
            "critical_sensors": ";".join(crit),
            "warning_sensors": ";".join(warn),
        })

    # write critical alerts
    with ALERT_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "critical_sensors", "warning_sensors"])
        writer.writeheader()
        for a in alerts:
            writer.writerow(a)

    return {"status": "ok", "alerts_written": len(alerts), "file": str(ALERT_FILE)}


def load_critical_alerts():
    """
    REQUIRED BY spectral_dashboard_api.py

    Returns list of dicts:
    [
        {"timestamp": "...", "critical_sensors": "...", "warning_sensors": "..."},
        ...
    ]
    """
    if not ALERT_FILE.exists():
        return []

    with ALERT_FILE.open() as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def score_alerts():
    """
    Optional scoring helper.
    """
    alerts = load_critical_alerts()
    if not alerts:
        return {"status": "ok", "score": 0}

    score = sum(1 for a in alerts if a.get("critical_sensors"))
    return {"status": "ok", "score": score}

