#!/usr/bin/env python3
"""
anti_dos_guard.py

Ghost Lantern Labs – Ingest / DoS Stress Analyzer
-------------------------------------------------

Purpose:
    Provide a read-only, non-invasive analysis of recent pipeline activity
    to estimate DoS-style stress and basic ingest anomalies.

    - Reads docs/run_history.json if present.
    - Computes:
        • total_events
        • unique_sensors (if sensor_id/device_id present)
        • time span (minutes)
        • avg events per minute
        • burst_level (LOW / MEDIUM / HIGH / NO_DATA)
        • findings (human-readable)
        • recommendations (mitigation ideas)

    This module DOES NOT modify the fusion pipeline, configs, or ingest logic.
    It is a diagnostic tool only and is safe to run at any time.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")
RUN_HISTORY_PATH = os.path.join(DOCS_DIR, "run_history.json")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _parse_timestamp(entry: Dict[str, Any]) -> Optional[datetime]:
    """
    Try to parse a timestamp from a run_history entry.

    Looks for common keys: timestamp_utc, timestamp, time.
    Returns None if parsing fails.
    """
    ts_keys = ["timestamp_utc", "timestamp", "time"]
    for key in ts_keys:
        raw = entry.get(key)
        if not raw:
            continue
        if isinstance(raw, (int, float)):
            # Treat as Unix epoch
            try:
                return datetime.utcfromtimestamp(float(raw))
            except Exception:
                continue
        if isinstance(raw, str):
            # Try ISO-style formats
            for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ",
                        "%Y-%m-%dT%H:%M:%SZ",
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(raw, fmt)
                except Exception:
                    continue
            # Last resort: fromisoformat (Python 3.7+)
            try:
                return datetime.fromisoformat(raw)
            except Exception:
                continue
    return None


def _extract_sensor_id(entry: Dict[str, Any]) -> Optional[str]:
    """
    Try to pull out some notion of 'sensor id' from a history entry.
    Keys tried: sensor_id, sensor, source, device_id.
    """
    for key in ("sensor_id", "sensor", "source", "device_id"):
        val = entry.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _compute_time_span_minutes(timestamps: List[datetime]) -> Optional[float]:
    if not timestamps:
        return None
    if len(timestamps) == 1:
        return 0.0
    t_min = min(timestamps)
    t_max = max(timestamps)
    delta = (t_max - t_min).total_seconds() / 60.0
    return max(delta, 0.0)


def _classify_burst(avg_events_per_minute: Optional[float],
                    total_events: int) -> str:
    """
    Very simple heuristic burst classifier.
    You can tune thresholds later as you see real data.

    - NO_DATA: no timing info or no events
    - LOW:     low activity
    - MEDIUM:  moderate bursts
    - HIGH:    sustained high rate (DoS risk)
    """
    if total_events == 0:
        return "NO_DATA"
    if avg_events_per_minute is None:
        # Events exist, but we can't compute a rate
        return "LOW"

    if avg_events_per_minute < 50.0:
        return "LOW"
    if avg_events_per_minute < 200.0:
        return "MEDIUM"
    return "HIGH"


def analyze_dos_surface() -> Dict[str, Any]:
    """
    Analyze run_history (if present) and return a DoS / ingest stress summary.

    The output is a dict with keys:
        - total_events
        - unique_sensors
        - time_span_minutes
        - avg_events_per_minute
        - burst_level
        - findings
        - recommendations
    """
    history = _safe_read_json(RUN_HISTORY_PATH)

    if not isinstance(history, list) or not history:
        return {
            "status": "NO_DATA",
            "message": "run_history.json not found or empty – cannot assess DoS surface yet.",
            "total_events": 0,
            "unique_sensors": 0,
            "time_span_minutes": None,
            "avg_events_per_minute": None,
            "burst_level": "NO_DATA",
            "findings": [
                "No run history available; DoS/ingest stress cannot yet be assessed.",
                "Once GLL has more runs, this module will compute basic burst and sensor-load metrics.",
            ],
            "recommendations": [
                "Continue running fusion_ingest and mission flows to build up run_history.",
                "Ensure run_history.json is being written as part of normal GLL executions.",
            ],
        }

    # Collect timestamps and sensor ids
    timestamps: List[datetime] = []
    sensors: List[str] = []

    for entry in history:
        if not isinstance(entry, dict):
            continue
        ts = _parse_timestamp(entry)
        if ts:
            timestamps.append(ts)
        sid = _extract_sensor_id(entry)
        if sid:
            sensors.append(sid)

    total_events = len(history)
    unique_sensors = len(set(sensors)) if sensors else 0
    span_minutes = _compute_time_span_minutes(timestamps)

    if span_minutes is None or span_minutes <= 0.0:
        avg_per_minute: Optional[float] = None
    else:
        avg_per_minute = total_events / span_minutes

    burst_level = _classify_burst(avg_per_minute, total_events)

    findings: List[str] = []
    recommendations: List[str] = []

    findings.append(f"Total recorded events: {total_events}.")
    if unique_sensors > 0:
        findings.append(f"Unique sensors / sources seen: {unique_sensors}.")
    else:
        findings.append("Sensor identifiers not present in run_history entries.")

    if span_minutes is not None:
        findings.append(f"Observed time span: ~{span_minutes:.1f} minute(s).")
    else:
        findings.append("Could not compute time span – timestamps missing or invalid.")

    if avg_per_minute is not None:
        findings.append(f"Average event rate: {avg_per_minute:.1f} events/minute.")
    else:
        findings.append("Average event rate could not be computed – insufficient timing data.")

    if burst_level == "LOW":
        findings.append("Current ingest activity appears low and controlled.")
    elif burst_level == "MEDIUM":
        findings.append("Moderate burst activity detected – worth watching, but not clearly DoS-level.")
    elif burst_level == "HIGH":
        findings.append("Sustained high event rate detected – potential DoS or runaway ingest condition.")
    else:
        findings.append("DoS classification not possible yet – no meaningful timing data.")

    # Recommendations based on burst level
    if burst_level in ("LOW", "NO_DATA"):
        recommendations.extend([
            "Maintain current ingest patterns while you mature GLL’s telemetry footprint.",
            "Consider adding basic per-sensor rate limits once real-world traffic is observed.",
        ])
    elif burst_level == "MEDIUM":
        recommendations.extend([
            "Review the sources driving the higher event rate; verify it is expected and legitimate.",
            "Plan to implement basic throttle / rate-limit controls per sensor and per source IP.",
            "Add monitoring around ingest queues to catch any further growth in burst intensity.",
        ])
    elif burst_level == "HIGH":
        recommendations.extend([
            "Treat current ingest behavior as potential DoS or runaway telemetry.",
            "Immediately consider implementing rate limits on per-sensor and per-source basis.",
            "Add alerting when sustained high rates are detected over multiple windows.",
            "Prepare a playbook for temporarily dropping non-critical telemetry during extreme load.",
        ])

    return {
        "status": "OK",
        "message": "DoS surface analysis completed.",
        "total_events": total_events,
        "unique_sensors": unique_sensors,
        "time_span_minutes": span_minutes,
        "avg_events_per_minute": avg_per_minute,
        "burst_level": burst_level,
        "findings": findings,
        "recommendations": recommendations,
        "source_file": RUN_HISTORY_PATH,
    }


if __name__ == "__main__":
    summary = analyze_dos_surface()
    print(json.dumps(summary, indent=2))

