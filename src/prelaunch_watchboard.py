"""
prelaunch_watchboard.py

Creates an ISR Pre-Launch Watchboard synthesizing:
 - Fusion Heat Index
 - Drift
 - Latency
 - Reliability
 - Owl threat memory
 - Nuclear readiness

This becomes a consolidated intelligence snapshot for
Golden Dome / missile early-warning operations.
"""

import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent


def _safe(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def build_watchboard():
    drift = _safe(BASE / "docs" / "golden_dome_drift_latest.json") or {}
    rel = _safe(BASE / "docs" / "sensor_reliability_latest.json") or {}
    lat = _safe(BASE / "docs" / "sensor_latency_latest.json") or {}
    owl = _safe(BASE / "docs" / "spectral_owl_latest.json") or {}
    trust = _safe(BASE / "docs" / "fusion_trust_latest.json") or {}
    nuke = _safe(BASE / "docs" / "golden_dome_snapshot_latest.json") or {}
    fhi = _safe(BASE / "docs" / "fusion_heat_index_latest.json") or {}

    board = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fusion_heat_index": fhi.get("FHI", None),
        "heat_level": fhi.get("level", "UNKNOWN"),
        "trust_score": trust.get("fusion_trust", None),
        "drift_status": drift.get("status", "unknown"),
        "avg_reliability": rel.get("avg_reliability", None),
        "latency": lat.get("latency_score", None),
        "critical_alerts": owl.get("critical_alerts", None),
        "warning_alerts": owl.get("warning_alerts", None),
        "nuclear_readiness": nuke,
    }

    out = BASE / "docs" / "prelaunch_watchboard_latest.json"
    out.write_text(json.dumps(board, indent=2))
    return out

