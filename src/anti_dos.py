"""
anti_dos.py — Day 53
Simple traffic classifier + flood detector for Ghost Lantern Labs.

- TrafficStats: small struct for volume + payload size
- classify_traffic: rules for NORMAL / SUSPICIOUS / DOS_SUSPECTED
- detect_flood: helper that works off a DataFrame
"""

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd

from fusion_logger import log_event


@dataclass
class TrafficStats:
    events_per_minute: int
    avg_payload_kb: float


# Backwards compatibility alias for older modules
TrafficMetrics = TrafficStats


def _normalize_input(
    stats_or_events: Union[TrafficStats, int],
    avg_payload_kb: Optional[float] = None,
) -> TrafficStats:
    """
    Accept either:
      - TrafficStats / TrafficMetrics object
      - or (events_per_minute: int, avg_payload_kb: float)

    and always return a TrafficStats instance.
    """
    if isinstance(stats_or_events, TrafficStats):
        return stats_or_events

    events = int(stats_or_events)
    payload = float(avg_payload_kb) if avg_payload_kb is not None else 0.0
    return TrafficStats(events_per_minute=events, avg_payload_kb=payload)


def classify_traffic(
    stats_or_events: Union[TrafficStats, int],
    avg_payload_kb: Optional[float] = None,
) -> str:
    """
    Very simple heuristic classifier.

    Input can be:
      - TrafficStats / TrafficMetrics
      - or (events_per_minute, avg_payload_kb)

    Returns one of:
      - "no_traffic"
      - "normal"
      - "suspicious"
      - "dos_suspected"
    """
    stats = _normalize_input(stats_or_events, avg_payload_kb)
    events_per_minute = stats.events_per_minute
    payload = stats.avg_payload_kb

    if events_per_minute <= 0:
        label = "no_traffic"
    elif events_per_minute < 200 and payload < 10:
        label = "normal"
    elif events_per_minute < 1000 and payload < 50:
        label = "suspicious"
    else:
        label = "dos_suspected"

    log_event(
        "anti_dos",
        "classify",
        f"volume={events_per_minute}/min, payload={payload:.1f}KB -> {label}",
    )
    return label


def estimate_metrics_from_df(df: pd.DataFrame) -> TrafficStats:
    """
    Rough stub: derive TrafficStats from a fusion DataFrame.

    For now:
      - events_per_minute = number of rows (pretend it's a 1-minute window)
      - avg_payload_kb    = constant 1.0 (placeholder)

    Later we can wire this to real ingest timing + payload sizes.
    """
    events = len(df)
    payload = 1.0  # placeholder
    stats = TrafficStats(events_per_minute=events, avg_payload_kb=payload)
    log_event("anti_dos", "metrics_from_df", f"rows={events} -> {stats}")
    return stats


def detect_flood(df: pd.DataFrame) -> str:
    """
    Convenience helper: derive metrics from a DataFrame and classify.
    """
    stats = estimate_metrics_from_df(df)
    label = classify_traffic(stats)
    log_event("anti_dos", "detect_flood", f"label={label}")
    return label


def quick_demo() -> None:
    """Tiny demo you can run standalone."""
    scenarios = [
        (50, 5.0),
        (350, 8.0),
        (1500, 2.0),
        (900, 80.0),
    ]
    for v, p in scenarios:
        label = classify_traffic(v, p)
        print(f"[Anti-DoS] {v}/min @ {p:.1f}KB -> {label}")


if __name__ == "__main__":
    quick_demo()

