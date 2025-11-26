"""
anti_dos.py — Day 52
Basic Anti-DoS classifier + flood detector for Ghost Lantern Labs.

Provides:
- classify_traffic(events_per_minute, avg_payload_kb)
- detect_flood(df, source="fusion_scoring")
- quick_demo()
"""

from datetime import datetime
from typing import Literal

from fusion_logger import log_event

RiskLabel = Literal["no_traffic", "normal", "suspicious", "dos_suspected"]


def classify_traffic(events_per_minute: int, avg_payload_kb: float) -> RiskLabel:
    """
    Very simple heuristic classifier.

    - no_traffic:   zero events
    - normal:       low volume + small payloads
    - suspicious:   medium/high volume OR big payloads
    - dos_suspected: very high volume and/or very large payloads
    """
    if events_per_minute <= 0:
        label: RiskLabel = "no_traffic"
    elif events_per_minute < 200 and avg_payload_kb < 10:
        label = "normal"
    elif events_per_minute < 1000 and avg_payload_kb < 50:
        label = "suspicious"
    else:
        label = "dos_suspected"

    msg = (
        f"volume={events_per_minute}/min, "
        f"payload={avg_payload_kb:.1f}KB -> {label}"
    )
    print(f"[Anti-DoS] {msg}")
    log_event("anti_dos", "classify", msg)
    return label


def detect_flood(df, source: str = "fusion_scoring") -> RiskLabel:
    """
    Lightweight detector that looks at the current fused/scored DataFrame
    and infers whether traffic looks normal or flood-like.

    For now it just uses row count:
      - 0 rows      -> no_traffic
      - < 100       -> normal
      - < 1000      -> suspicious
      - >= 1000     -> dos_suspected

    This is intentionally simple. Later we can upgrade to:
      - ingest rate over time windows
      - quarantine volume
      - AOI_Hit ratios
      - sensor diversity, etc.
    """
    try:
        row_count = len(df)
    except Exception as e:
        msg = f"detect_flood(): invalid df ({e})"
        print(f"[Anti-DoS] {msg}")
        log_event("anti_dos", "detect_flood_error", msg)
        return "no_traffic"  # type: ignore[return-value]

    if row_count == 0:
        label: RiskLabel = "no_traffic"
    elif row_count < 100:
        label = "normal"
    elif row_count < 1000:
        label = "suspicious"
    else:
        label = "dos_suspected"

    msg = f"rows={row_count} -> {label} (source={source})"
    print(f"[Anti-DoS] {msg}")
    log_event("anti_dos", "detect_flood", msg)
    return label


def quick_demo() -> None:
    """Tiny demo you can run from CLI to sanity-check the classifier."""
    scenarios = [
        (50, 5.0),
        (350, 8.0),
        (1500, 2.0),
        (900, 80.0),
    ]
    for v, p in scenarios:
        label = classify_traffic(v, p)
        print(f"[Anti-DoS Demo] {v}/min @ {p:.1f}KB -> {label}")


if __name__ == "__main__":
    quick_demo()

