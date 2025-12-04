"""
golden_dome_tile.py — Golden Dome Fitness Tile
Summarizes whether the system meets Air Force 'Golden Dome' readiness baseline.

Inputs: reliability, cross-sensor agreement, profile state, owl status.
Outputs: a 1-tile summary for GUI + HTML.
"""

from datetime import datetime

def build_golden_dome_tile(reliability: float, agreement: float, profile: str) -> dict:
    badge = "GREEN"
    msg = "Mission-ready."

    if reliability < 70 or agreement < 60:
        badge = "YELLOW"
        msg = "System degraded. Review anomalies."

    if reliability < 50 or agreement < 40:
        badge = "RED"
        msg = "System NOT ready for mission tasks."

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "profile": profile,
        "reliability": reliability,
        "agreement": agreement,
        "badge": badge,
        "message": msg,
    }

