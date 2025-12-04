"""
spectral_fallback_tree.py — Phase 3 Degraded-Mode Logic for Spectral Owl

Goal:
    Provide a deterministic fallback logic tree when:
      • LLM provider fails
      • AI chain times out
      • Data is incomplete
      • Owl needs to return guaranteed output

Exports:
    build_fallback_response(input_summary: dict) -> dict
"""

from datetime import datetime


def build_fallback_response(input_summary: dict) -> dict:
    """
    Deterministic fallback logic.
    Works without cloud, LLM, or full sensor data.
    """

    # Extract what we *can* trust.
    critical = input_summary.get("critical_alerts", 0)
    warnings = input_summary.get("warning_alerts", 0)
    reliability = input_summary.get("avg_reliability", 0)

    # Basic threat logic table.
    if critical > 0:
        level = "SEVERE"
        msg = "Critical anomalies detected. Recommend immediate review."
    elif warnings > 2:
        level = "ELEVATED"
        msg = "Multiple warnings detected. Investigate subsystem changes."
    else:
        level = "STABLE"
        msg = "No major anomalies detected. System appears nominal."

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": "fallback",
        "level": level,
        "message": msg,
        "inputs_used": input_summary,
    }


if __name__ == "__main__":
    test = {
        "critical_alerts": 1,
        "warning_alerts": 3,
        "avg_reliability": 92.5,
    }
    print(build_fallback_response(test))

