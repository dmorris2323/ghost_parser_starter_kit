"""
escalation_ladder.py

Nuclear / AFTAC Escalation Ladder (HARDENED)

Purpose:
- Map ambiguous indicators to bounded escalation levels
- Explicitly quantify confidence and uncertainty
- Prevent over-escalation from partial or noisy data
"""

from typing import Dict, Any


ESCALATION_LEVELS = [
    "NO_CONCERN",
    "ANOMALY_OBSERVED",
    "ELEVATED_WATCH",
    "HEIGHTENED_CONCERN",
    "POTENTIAL_ESCALATION",
    "CRISIS_INDICATOR",
]


def assess_escalation(
    *,
    trust_score: float,
    risk_score: float,
    alert_counts: Dict[str, int],
    degraded: bool = False,
) -> Dict[str, Any]:
    """
    Returns a bounded escalation assessment with confidence annotation.
    """

    crit = alert_counts.get("crit", 0)
    high = alert_counts.get("high", 0)
    anomaly = alert_counts.get("anomaly", 0)

    # Base ladder logic (conservative by design)
    if crit == 0 and high == 0 and risk_score < 30:
        level = "NO_CONCERN"
    elif anomaly > 10 and risk_score < 40:
        level = "ANOMALY_OBSERVED"
    elif high >= 3 or risk_score >= 45:
        level = "ELEVATED_WATCH"
    elif high >= 6 or risk_score >= 60:
        level = "HEIGHTENED_CONCERN"
    elif crit >= 1 and risk_score >= 70:
        level = "POTENTIAL_ESCALATION"
    else:
        level = "ANOMALY_OBSERVED"

    # Confidence handling
    confidence = max(0.0, min(100.0, trust_score))

    if degraded:
        confidence = confidence * 0.75  # explicit penalty under degraded ops

    confidence_band = (
        "HIGH" if confidence >= 80 else
        "MEDIUM" if confidence >= 55 else
        "LOW"
    )

    return {
        "escalation_level": level,
        "confidence_score": round(confidence, 1),
        "confidence_band": confidence_band,
        "degraded_environment": degraded,
        "explanation": _explain(level, confidence_band, degraded),
    }


def _explain(level: str, band: str, degraded: bool) -> str:
    msg = f"Escalation assessed as {level} with {band} confidence."
    if degraded:
        msg += " Environment is degraded; uncertainty explicitly increased."
    return msg

