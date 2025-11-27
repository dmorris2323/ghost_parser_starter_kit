"""
owl_brain.py — Spectral Owl reasoning engine

Consolidated version — Day 53

Provides:
- analyze_fusion: inspect scored_output.csv for critical events
- think: use LLM adapter (dummy-local by default) for textual reasoning
- threat_snapshot: combine fusion status with Anti-DoS traffic classification
"""

import pandas as pd

from fusion_logger import log_event
from spectral_owl.llm_adapter import get_llm
from anti_dos import classify_traffic


def analyze_fusion(path: str = "scored_output.csv") -> str:
    """
    Core rule-based reasoning about the fusion output.

    Returns a short status string that other modules (CLI, mission brief,
    anti-DoS scan) can display.
    """
    try:
        df = pd.read_csv(path)
    except Exception as e:
        msg = f"Could not read {path}: {e}"
        log_event("spectral_owl", "error", msg)
        return msg

    if df.empty:
        result = "No events to analyze."
        log_event("spectral_owl", "analysis", result)
        return result

    # Basic rule: anything with Score > 70 is "critical"
    if "Score" not in df.columns:
        result = "Score column missing in fusion output."
        log_event("spectral_owl", "analysis", result)
        return result

    critical = df[df["Score"] > 70]

    if len(critical) == 0:
        result = "Situation stable — no high risk events."
    else:
        result = f"{len(critical)} critical event(s). Recommend operator review."

    log_event("spectral_owl", "analysis", result)
    return result


def think(task: str) -> str:
    """
    Simple entry point to show that Spectral Owl can 'think' about a task.

    Uses the DummyLocalEngine via llm_adapter, which is completely offline
    and vendor-independent.
    """
    engine = get_llm()
    prompt = f"Spectral Owl system task: {task}"
    response = engine.generate(prompt)
    log_event("spectral_owl", "think", task)
    return response


def threat_snapshot() -> str:
    """
    Combine fusion status + Anti-DoS traffic classification into one line.

    For now, traffic metrics are simple fixed values; later they can be
    wired to real telemetry rates.
    """
    fusion_status = analyze_fusion()

    # Example traffic metrics — can be replaced with real values later
    events_per_minute = 350
    avg_payload_kb = 8.0

    traffic_label = classify_traffic(events_per_minute, avg_payload_kb).upper()

    snapshot = (
        f"Fusion: {fusion_status} | "
        f"Traffic: {events_per_minute}/min @ {avg_payload_kb:.1f}KB -> {traffic_label}"
    )

    log_event("spectral_owl", "threat_snapshot", snapshot)
    return snapshot

