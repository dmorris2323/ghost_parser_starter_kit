"""
golden_dome_tile.py

Builds a compact "Golden Dome Readiness" tile for:
- HTML mission brief
- GUI dashboard
- CLI / future exports

Inputs:
    reliability: float 0–100 (average sensor reliability)
    agreement:   float 0–100 (how often sensors + Owl agree)
    profile:     str, active profile display name

Output:
    dict with:
        profile, reliability, agreement, status, summary
"""

from __future__ import annotations
from typing import Tuple, Dict, Any


def _clamp(value: float | None, lo: float = 0.0, hi: float = 100.0) -> float | None:
    """Clamp a numeric value into [lo, hi], allow None."""
    if value is None:
        return None
    try:
        v = float(value)
    except (ValueError, TypeError):
        return None
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def _classify_status(reliability: float | None,
                     agreement: float | None) -> Tuple[str, str]:
    """
    Turn raw reliability + agreement into a simple traffic-light status and summary.

    Rules (tunable later):
        GREEN  = reliability >= 92 and agreement >= 88
        YELLOW = reliability >= 80 and agreement >= 70
        RED    = everything else / degraded / unknown
    """
    if reliability is None or agreement is None:
        return (
            "UNKNOWN",
            "Insufficient data to assess Golden Dome readiness. "
            "Collect more runs and ensure all sensors are reporting."
        )

    r = _clamp(reliability)
    a = _clamp(agreement)

    if r is None or a is None:
        return (
            "UNKNOWN",
            "Telemetry malformed. Check sensor feeds and run history."
        )

    if r >= 92.0 and a >= 88.0:
        return (
            "GREEN",
            "System is ready: high sensor reliability and strong cross-sensor/Owl agreement."
        )
    elif r >= 80.0 and a >= 70.0:
        return (
            "YELLOW",
            "System is usable but not ideal: watch reliability trends and cross-sensor disputes."
        )
    else:
        return (
            "RED",
            "System is in a degraded state: low reliability or poor agreement. "
            "Commanders should treat fused outputs with caution and investigate immediately."
        )


def build_golden_dome_tile(reliability: float | None,
                           agreement: float | None,
                           profile: str) -> Dict[str, Any]:
    """
    Public builder used by:
        - mission_brief_html.py
        - GUI (apps/gui/app.py)
        - any future exporters

    Returns a JSON-safe dict.
    """
    rel = _clamp(reliability)
    agr = _clamp(agreement)
    status, summary = _classify_status(rel, agr)

    return {
        "profile": profile or "UNKNOWN_PROFILE",
        "reliability": round(rel, 1) if rel is not None else None,
        "agreement": round(agr, 1) if agr is not None else None,
        "status": status,
        "summary": summary,
    }


if __name__ == "__main__":
    # Simple self-test so you can run:
    #   python golden_dome_tile.py
    sample = build_golden_dome_tile(93.4, 89.1, "aftac_nuclear")
    import json
    print(json.dumps(sample, indent=2))

