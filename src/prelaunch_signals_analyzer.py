#!/usr/bin/env python3
"""
prelaunch_signals_analyzer.py

Ghost Lantern Labs – Nuclear / Pre-Launch Early Warning Stack
-------------------------------------------------------------

Purpose:
    Fuse multiple upstream nuclear/ISR indicators into a single
    "pre-launch signal pressure" view that can feed the
    prelaunch_watchboard and commander products.

Inputs (all optional, defensive):
    docs/golden_dome_daily_watch.json     -> nuclear readiness & drift hints
    docs/sensor_latency_report.json       -> sensor latency & potential blindness
    docs/run_history_intel.json           -> recent events / runs / anomalies
    docs/adversary_pattern_memory.json    -> persistent adversary patterns (if present)

Outputs:
    docs/prelaunch_signals_analysis.json
    docs/prelaunch_signals_analysis.txt

Key metrics:
    - sensor_concurrence_score  (0–100)
    - ems_spike_score           (0–100)
    - latency_risk_score        (0–100)
    - pattern_anomaly_score     (0–100)
    - composite_signal_pressure (0–100)

Everything is deterministic, no external LLM calls. This is a
"safety shell" around more complex AI reasoning and can stand on its own
for degraded / offline use.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


# ------------------------
# Safe I/O helpers
# ------------------------

def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


# ------------------------
# Feature extraction
# ------------------------

def _extract_sensor_concurrence_score(gd: Any) -> Dict[str, Any]:
    """
    Rough estimate of how many sensors appear "alive" and working together.
    """
    if not isinstance(gd, dict):
        return {"score": 0.0, "notes": ["Golden Dome JSON not available."]}

    sensors_ok = 0
    sensors_total = 0
    notes: List[str] = []

    sensor_status = gd.get("sensor_status")
    if isinstance(sensor_status, dict):
        for name, status in sensor_status.items():
            sensors_total += 1
            # consider any non-error state as "ok"
            status_str = str(status).lower()
            if any(k in status_str for k in ["ok", "green", "nominal", "online"]):
                sensors_ok += 1
    else:
        notes.append("No structured 'sensor_status' map; assuming low concurrence.")

    if sensors_total == 0:
        score = 20.0  # conservative default if we can't see sensors
        notes.append("No visible sensor inventory; defaulting concurrence to 20/100.")
    else:
        ratio = sensors_ok / max(1, sensors_total)
        # 0.0 => score 10, 1.0 => score 100
        score = 10.0 + (ratio * 90.0)
        notes.append(
            f"{sensors_ok}/{sensors_total} sensors appear nominal; concurrence score derived from ratio."
        )

    return {"score": max(0.0, min(100.0, score)), "notes": notes}


def _extract_latency_risk_score(latency_report: Any) -> Dict[str, Any]:
    """
    Derive a latency risk (0–100). Higher latency => higher risk.
    """
    if not isinstance(latency_report, dict):
        return {"score": 30.0, "notes": ["No latency report JSON; applying conservative baseline risk."]}

    notes: List[str] = []
    global_latency_ms = latency_report.get("global_latency_ms")
    if global_latency_ms is None:
        # fallback: scan for any "max_latency_ms" field
        for key in latency_report.keys():
            if "latency" in str(key).lower():
                try:
                    global_latency_ms = float(latency_report[key])
                    break
                except Exception:
                    continue

    if global_latency_ms is None:
        score = 30.0
        notes.append("Latency metrics missing; applying conservative latency risk 30/100.")
    else:
        try:
            global_latency_ms = float(global_latency_ms)
            # <250ms => low risk; >2000ms => high risk
            if global_latency_ms <= 250:
                score = 10.0
                notes.append("Global latency appears low (<250ms); minimal latency risk.")
            elif global_latency_ms <= 750:
                score = 30.0
                notes.append("Global latency moderate (250–750ms); mild latency risk.")
            elif global_latency_ms <= 2000:
                score = 60.0
                notes.append("Global latency elevated (750–2000ms); notable latency risk.")
            else:
                score = 85.0
                notes.append("Global latency very high (>2000ms); serious latency risk for early warning.")
        except Exception:
            score = 40.0
            notes.append("Could not parse global latency; applying medium latency risk.")
    return {"score": max(0.0, min(100.0, score)), "notes": notes}


def _extract_ems_spike_score(run_history: Any) -> Dict[str, Any]:
    """
    Heuristic: look in run_history_intel for EMS or RF-related events and cluster them.
    """
    notes: List[str] = []
    if run_history is None:
        return {"score": 20.0, "notes": ["No run_history_intel.json; EMS spike set to low default."]}

    events: List[Dict[str, Any]] = []
    if isinstance(run_history, list):
        events = [e for e in run_history if isinstance(e, dict)]
    elif isinstance(run_history, dict):
        for key in ("events", "runs", "history"):
            v = run_history.get(key)
            if isinstance(v, list):
                events = [e for e in v if isinstance(e, dict)]
                break

    if not events:
        notes.append("No events found in run history; EMS spike considered low.")
        return {"score": 10.0, "notes": notes}

    ems_hits = 0
    for e in events:
        blob = json.dumps(e).lower()
        if any(tag in blob for tag in ["ems", "rf", "jam", "jamming", "spectrum", "comms_anomaly"]):
            ems_hits += 1

    if ems_hits == 0:
        score = 15.0
        notes.append("No EMS/RF-related events detected; EMS spike minimal.")
    elif ems_hits < 5:
        score = 40.0
        notes.append(f"{ems_hits} EMS-related events detected; modest EMS spike.")
    else:
        score = 75.0
        notes.append(f"{ems_hits} EMS-related events detected; significant EMS spike pattern.")

    return {"score": max(0.0, min(100.0, score)), "notes": notes}


def _extract_pattern_anomaly_score(pattern_memory: Any) -> Dict[str, Any]:
    """
    Look into adversary_pattern_memory.json for anomaly flags.
    """
    if pattern_memory is None:
        return {"score": 20.0, "notes": ["No adversary_pattern_memory.json; pattern anomaly minimal by default."]}

    notes: List[str] = []
    anomalies = 0
    total_patterns = 0

    if isinstance(pattern_memory, list):
        items = [p for p in pattern_memory if isinstance(p, dict)]
    elif isinstance(pattern_memory, dict):
        items = pattern_memory.get("patterns") or pattern_memory.get("entries") or []
        if isinstance(items, list):
            items = [p for p in items if isinstance(p, dict)]
        else:
            items = []
    else:
        items = []

    for p in items:
        total_patterns += 1
        blob = json.dumps(p).lower()
        if any(tag in blob for tag in ["anomaly", "new tactic", "unseen pattern", "novel", "zero-day"]):
            anomalies += 1

    if total_patterns == 0:
        return {"score": 25.0, "notes": ["No structured adversary patterns; assigning conservative anomaly level."]}

    ratio = anomalies / max(1, total_patterns)
    if anomalies == 0:
        score = 15.0
        notes.append("No anomalous adversary patterns flagged; pattern anomaly low.")
    elif ratio < 0.25:
        score = 45.0
        notes.append(f"{anomalies}/{total_patterns} patterns flagged anomalous; mild anomaly pressure.")
    elif ratio < 0.6:
        score = 70.0
        notes.append(f"{anomalies}/{total_patterns} patterns flagged anomalous; significant anomaly pressure.")
    else:
        score = 90.0
        notes.append(f"{anomalies}/{total_patterns} patterns flagged anomalous; extreme anomaly pressure.")

    return {"score": max(0.0, min(100.0, score)), "notes": notes}


# ------------------------
# Composite signal pressure
# ------------------------

def _compute_composite_pressure(
    sensor_conc: float,
    ems_spike: float,
    latency_risk: float,
    pattern_anomaly: float,
) -> float:
    """
    Combine the four metrics into a single composite 0–100 pressure.
    We treat them as:
        - sensor_conc:   stability / integrity booster (low conc can cap pressure)
        - ems_spike:     direct contributor
        - latency_risk:  moderates how actionable the spike is
        - pattern_anom:  strategic red flag

    Rough rule:
        base = (ems_spike * 0.4) + (pattern_anomaly * 0.4) + (latency_risk * 0.2)
        then adjusted by sensor_conc as a ceiling.
    """
    base = (ems_spike * 0.4) + (pattern_anomaly * 0.4) + (latency_risk * 0.2)
    # sensor concurrence acts as a soft ceiling (if conc=50, pressure <= ~60)
    ceiling = max(40.0, sensor_conc + 20.0)
    return max(0.0, min(100.0, min(base, ceiling)))


# ------------------------
# Main builder
# ------------------------

def analyze_prelaunch_signals() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    golden_dome_path = os.path.join(DOCS_DIR, "golden_dome_daily_watch.json")
    latency_path = os.path.join(DOCS_DIR, "sensor_latency_report.json")
    run_history_path = os.path.join(DOCS_DIR, "run_history_intel.json")
    pattern_mem_path = os.path.join(DOCS_DIR, "adversary_pattern_memory.json")

    golden_dome = _safe_read_json(golden_dome_path)
    latency_report = _safe_read_json(latency_path)
    run_history = _safe_read_json(run_history_path)
    pattern_memory = _safe_read_json(pattern_mem_path)

    inputs_present = {
        "golden_dome_daily_watch_json": golden_dome is not None,
        "sensor_latency_report_json": latency_report is not None,
        "run_history_intel_json": run_history is not None,
        "adversary_pattern_memory_json": pattern_memory is not None,
    }

    sensor_info = _extract_sensor_concurrence_score(golden_dome)
    latency_info = _extract_latency_risk_score(latency_report)
    ems_info = _extract_ems_spike_score(run_history)
    pattern_info = _extract_pattern_anomaly_score(pattern_memory)

    sensor_conc_score = sensor_info["score"]
    latency_risk_score = latency_info["score"]
    ems_spike_score = ems_info["score"]
    pattern_anomaly_score = pattern_info["score"]

    composite_pressure = _compute_composite_pressure(
        sensor_conc=sensor_conc_score,
        ems_spike=ems_spike_score,
        latency_risk=latency_risk_score,
        pattern_anomaly=pattern_anomaly_score,
    )

    rationale: List[str] = []
    rationale.extend(sensor_info["notes"])
    rationale.extend(latency_info["notes"])
    rationale.extend(ems_info["notes"])
    rationale.extend(pattern_info["notes"])
    rationale.append(
        f"Composite pre-launch signal pressure computed as a blend of EMS spikes, adversary anomalies, "
        f"latency risk, and sensor concurrence; final pressure: {composite_pressure:.1f}/100."
    )

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "sensor_concurrence_score": sensor_conc_score,
        "ems_spike_score": ems_spike_score,
        "latency_risk_score": latency_risk_score,
        "pattern_anomaly_score": pattern_anomaly_score,
        "composite_signal_pressure": composite_pressure,
        "rationale": rationale,
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "prelaunch_signals_analysis.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT (commander-facing)
    lines: List[str] = []
    lines.append("GLL Pre-Launch Signals Analysis")
    lines.append("================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Sensor Concurrence Score: {sensor_conc_score:.1f}/100")
    lines.append(f"EMS Spike Score: {ems_spike_score:.1f}/100")
    lines.append(f"Latency Risk Score: {latency_risk_score:.1f}/100")
    lines.append(f"Pattern Anomaly Score: {pattern_anomaly_score:.1f}/100")
    lines.append("")
    lines.append(f"Composite Pre-Launch Signal Pressure: {composite_pressure:.1f}/100")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append("Rationale:")
    for r in rationale:
        lines.append(f"  - {r}")

    txt_path = os.path.join(DOCS_DIR, "prelaunch_signals_analysis.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = analyze_prelaunch_signals()
    print("Pre-launch signals analysis generated:")
    print(f"  - {os.path.join('docs', 'prelaunch_signals_analysis.json')}")
    print(f"  - {os.path.join('docs', 'prelaunch_signals_analysis.txt')}")

