"""
nuclear_decision_card.py

Commander Decision Card (Confidence-Aware)
"""

from typing import Dict, Any
from escalation_ladder import assess_escalation


def build_decision_card(
    *,
    trust_score: float,
    risk_score: float,
    alerts: Dict[str, int],
    degraded: bool = False,
) -> Dict[str, Any]:

    escalation = assess_escalation(
        trust_score=trust_score,
        risk_score=risk_score,
        alert_counts=alerts,
        degraded=degraded,
    )

    return {
        "decision_card": {
            "summary": "Nuclear ISR Escalation Assessment",
            "escalation_level": escalation["escalation_level"],
            "confidence": escalation["confidence_score"],
            "confidence_band": escalation["confidence_band"],
            "degraded_environment": degraded,
            "commander_note": escalation["explanation"],
        }
    }

