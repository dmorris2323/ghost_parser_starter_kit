"""
fusion_heat_index.py

Computes an overall "Fusion Heat Index" (FHI) representing
how turbulent / hot the battlespace is based on:
 - Critical alerts
 - Warning alerts
 - Sensor reliability
 - Drift status
 - Latency quality

Output:
{
    "FHI": 0–100,
    "level": "LOW | MODERATE | HIGH | CRITICAL",
    "inputs": {...}
}
"""

import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent


def _safe_read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def compute_fhi():
    # Load telemetry components
    drift = _safe_read_json(BASE / "docs" / "golden_dome_drift_latest.json") or {}
    reliability = _safe_read_json(BASE / "docs" / "sensor_reliability_latest.json") or {}
    latency = _safe_read_json(BASE / "docs" / "sensor_latency_latest.json") or {}
    owl = _safe_read_json(BASE / "docs" / "spectral_owl_latest.json") or {}

    # Base values
    critical_alerts = owl.get("critical_alerts", 0)
    warning_alerts = owl.get("warning_alerts", 0)
    avg_rel = reliability.get("avg_reliability", 90)
    drift_score = drift.get("drift_score", 0)
    latency_ok = latency.get("latency_score", 90)

    # Formula (simple but ISR-logical)
    heat = (
        (critical_alerts * 15)
        + (warning_alerts * 5)
        + (100 - avg_rel) * 0.3
        + (drift_score * 0.5)
        + (100 - latency_ok) * 0.2
    )

    heat = min(max(int(heat), 0), 100)

    if heat < 20:
        lvl = "LOW"
    elif heat < 40:
        lvl = "MODERATE"
    elif heat < 70:
        lvl = "HIGH"
    else:
        lvl = "CRITICAL"

    out = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "FHI": heat,
        "level": lvl,
        "inputs": {
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "avg_reliability": avg_rel,
            "drift_score": drift_score,
            "latency_score": latency_ok,
        },
    }

    # Save snapshot
    (BASE / "docs" / "fusion_heat_index_latest.json").write_text(json.dumps(out, indent=2))

    return out

