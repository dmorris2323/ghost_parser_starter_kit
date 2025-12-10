#!/usr/bin/env python3
"""
prelaunch_signals_analyzer.py

Day 66 – Ghost Lantern Labs
Pre-Launch Early Warning Hardening – Option C

This module inspects multiple upstream artifacts and produces a
normalized "pre-launch signal picture" that other modules can consume.

It is purely analytic and read-only. It NEVER mutates upstream data.

Inputs (all optional, defensive if missing):
    docs/golden_dome_daily_watch.json
    docs/sensor_latency_report.json or docs/sensor_latency.json
    docs/run_history_intel.json
    docs/adversary_patterns.json
    docs/adversary_pattern_memory.json

Output (structured in-memory object):
    analyze_prelaunch_signals() -> dict with keys:
        generated_at (UTC ISO)
        inputs_present: {name: bool}
        sensor_concurrence_score (0–100)
        ems_spike_score (0–100)
        latency_risk_score (0–100)
        pattern_anomaly_score (0–100)
        overall_signal_score (0–100)
        signals: list of {name, severity, rationale}
        notes: list of strings

The scoring is deliberately SIMPLE and EXPLAINABLE.
This is doctrine-aligned, not ML magic.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _detect_golden_dome_signals(gd: Any, signals: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Pulls very lightweight signals from golden_dome_daily_watch.json.
    We don't depend on any specific schema, just look for a few generic cues.
    """
    result = {
        "sensor_concurrence_score": 0.0,
        "ems_spike_score": 0.0,
    }

    if gd is None:
        return result

    # Heuristics: look for fields that smell like concurrence or EMS stress
    # We keep this extremely generic to avoid tight coupling to schema.
    text_blob = json.dumps(gd).lower()

    # crude concurrence: more mentions of "multi-sensor" / "concurrent"
    if "multi-sensor" in text_blob or "concurrent" in text_blob:
        signals.append({
            "name": "multi_sensor_concurrence",
            "severity": "MEDIUM",
            "rationale": "Golden Dome watch references multi-sensor or concurrent detections."
        })
        result["sensor_concurrence_score"] = 60.0

    # crude EMS spike: look for 'ems', 'rf', or 'spectrum' combined with 'spike', 'surge', or 'anomaly'
    if ("ems" in text_blob or "electromagnetic" in text_blob or "rf" in text_blob) and (
        "spike" in text_blob or "surge" in text_blob or "anomaly" in text_blob
    ):
        signals.append({
            "name": "ems_spike_indicator",
            "severity": "HIGH",
            "rationale": "Golden Dome watch references EMS/RF anomalies or spikes."
        })
        result["ems_spike_score"] = 75.0

    return result


def _detect_latency_signals(latency_data: Any, signals: List[Dict[str, Any]]) -> float:
    """
    Looks at a generic sensor latency report JSON and estimates a latency risk score (0–100).
    """
    if latency_data is None:
        return 0.0

    text_blob = json.dumps(latency_data).lower()

    # Try to infer worst-case latency if values exist
    worst_ms = None
    if isinstance(latency_data, dict):
        # Look for typical shapes like {"sensors": [{"name": ..., "latency_ms": ...}, ...]}
        sensors = latency_data.get("sensors")
        if isinstance(sensors, list):
            for s in sensors:
                if not isinstance(s, dict):
                    continue
                val = s.get("latency_ms")
                try:
                    if val is not None:
                        val = float(val)
                        if worst_ms is None or val > worst_ms:
                            worst_ms = val
                except Exception:
                    continue

    latency_risk = 0.0
    if worst_ms is not None:
        # Simple thresholding: 0–500ms = low, 500–2000 = medium, >2000 = high
        if worst_ms <= 500:
            latency_risk = 10.0
        elif worst_ms <= 2000:
            latency_risk = 40.0
        else:
            latency_risk = 75.0

    # Fallback: if we see words like "delay", "timeout", "stale", bump
    if any(word in text_blob for word in ["timeout", "stale", "delayed"]):
        latency_risk = max(latency_risk, 50.0)

    if latency_risk >= 60.0:
        sev = "HIGH"
    elif latency_risk >= 30.0:
        sev = "MEDIUM"
    else:
        sev = "LOW"

    if latency_risk > 0.0:
        signals.append({
            "name": "sensor_latency_risk",
            "severity": sev,
            "rationale": f"Worst-case latency suggests latency risk at ~{latency_risk:.1f}/100."
        })

    return latency_risk


def _detect_pattern_anomalies(pattern_data: Any, signals: List[Dict[str, Any]]) -> float:
    """
    Looks at adversary pattern memory and tries to infer whether patterns
    show clustering, rapid tempo, or escalation near 'now'.
    This remains very generic and safe.
    """
    if pattern_data is None:
        return 0.0

    score = 0.0
    events_count = 0

    # Try to treat structures like list of events or dict with 'events'/'patterns'
    if isinstance(pattern_data, list):
        events = [e for e in pattern_data if isinstance(e, dict)]
    elif isinstance(pattern_data, dict):
        if isinstance(pattern_data.get("events"), list):
            events = [e for e in pattern_data["events"] if isinstance(e, dict)]
        elif isinstance(pattern_data.get("patterns"), list):
            events = [e for e in pattern_data["patterns"] if isinstance(e, dict)]
        else:
            events = []
    else:
        events = []

    events_count = len(events)

    if events_count >= 20:
        score += 40.0  # lots of activity
    elif events_count >= 5:
        score += 20.0

    # Look for crude escalation hints: words like "escalation", "pivot", "new phase"
    text_blob = json.dumps(events).lower()
    if any(w in text_blob for w in ["escalat", "new phase", "intensif", "surge"]):
        score += 30.0

    # Bound to [0, 100]
    score = max(0.0, min(100.0, score))

    if score > 0.0:
        sev = "MEDIUM" if score < 70.0 else "HIGH"
        signals.append({
            "name": "pattern_anomaly_pressure",
            "severity": sev,
            "rationale": f"Adversary pattern memory shows activity level and language consistent with score ~{score:.1f}/100."
        })

    return score


def analyze_prelaunch_signals() -> Dict[str, Any]:
    """
    Main entry point.

    Returns a dict suitable for downstream use by prelaunch_watchboard
    and early_warning_scorecard.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    golden_dome_path = os.path.join(DOCS_DIR, "golden_dome_daily_watch.json")
    latency_report_path = os.path.join(DOCS_DIR, "sensor_latency_report.json")
    latency_alt_path = os.path.join(DOCS_DIR, "sensor_latency.json")
    run_history_intel_path = os.path.join(DOCS_DIR, "run_history_intel.json")
    adversary_patterns_path = os.path.join(DOCS_DIR, "adversary_patterns.json")
    adversary_pattern_memory_path = os.path.join(DOCS_DIR, "adversary_pattern_memory.json")

    golden_dome = _safe_read_json(golden_dome_path)
    latency_data = _safe_read_json(latency_report_path) or _safe_read_json(latency_alt_path)
    run_history_intel = _safe_read_json(run_history_intel_path)
    adversary_patterns = _safe_read_json(adversary_patterns_path)
    adversary_pattern_memory = _safe_read_json(adversary_pattern_memory_path)

    inputs_present = {
        "golden_dome_daily_watch_json": golden_dome is not None,
        "sensor_latency_report": latency_data is not None,
        "run_history_intel": run_history_intel is not None,
        "adversary_patterns": adversary_patterns is not None,
        "adversary_pattern_memory": adversary_pattern_memory is not None,
    }

    signals: List[Dict[str, Any]] = []
    notes: List[str] = []

    # Golden Dome cues
    gd_scores = _detect_golden_dome_signals(golden_dome, signals)

    # Latency cues
    latency_risk = _detect_latency_signals(latency_data, signals)

    # Pattern cues (merge patterns + pattern memory if both exist)
    combined_patterns = adversary_patterns or adversary_pattern_memory
    pattern_anomaly_score = _detect_pattern_anomalies(combined_patterns, signals)

    # Run-history intel presence – just a confidence booster for coverage
    coverage_bonus = 0.0
    if run_history_intel is not None:
        coverage_bonus = 10.0
        notes.append("run_history_intel.json present: pre-launch analysis has better temporal context.")

    # Aggregate scoring (lightweight, explainable)
    sensor_conc = gd_scores["sensor_concurrence_score"]
    ems_spike = gd_scores["ems_spike_score"]

    # Treat each signal band as partial contributions to overall signal pressure
    components = [sensor_conc, ems_spike, latency_risk, pattern_anomaly_score]
    non_zero = [c for c in components if c > 0.0]
    if non_zero:
        overall = sum(non_zero) / len(non_zero) + coverage_bonus
    else:
        overall = 0.0

    overall = max(0.0, min(100.0, overall))

    if overall == 0.0:
        notes.append("No strong pre-launch signals detected from available artifacts.")
    else:
        notes.append(f"Composite pre-launch signal score computed at ~{overall:.1f}/100.")

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "sensor_concurrence_score": sensor_conc,
        "ems_spike_score": ems_spike,
        "latency_risk_score": latency_risk,
        "pattern_anomaly_score": pattern_anomaly_score,
        "overall_signal_score": overall,
        "signals": signals,
        "notes": notes,
    }

    return result


if __name__ == "__main__":
    out = analyze_prelaunch_signals()
    print(json.dumps(out, indent=2, sort_keys=True))

