"""
anti_dos_metrics.py — Day 53
Stub to produce fake traffic metrics for Anti-DoS.

Later this will read real ingest rates / payloads.
"""

from anti_dos import TrafficMetrics


def get_current_metrics() -> TrafficMetrics:
    """
    For now, returns fixed numbers so we can wire the flow.
    Later: compute from logs or telemetry.
    """
    # Pretend we're seeing moderate traffic
    return TrafficMetrics(events_per_minute=350, avg_payload_kb=8.0)

