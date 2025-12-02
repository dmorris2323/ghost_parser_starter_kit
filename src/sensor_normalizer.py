"""
sensor_normalizer.py — Ghost Lantern Labs
-----------------------------------------

This module unifies ALL sensor mocks into a single
standardized fusion-ready data structure.

This is what real ISR fusion platforms use:
a "normalization layer" that hides differences between sensors.

Every sensor must output:
    - sensor (name)
    - type (optical, seismic, ems, radiation, generic)
    - feature_1 ... feature_N (numeric only)
    - threat_hint (0.0–1.0)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List

from sensor_interface import SensorSample
from sensor_mapping import SENSOR_FIELD_MAP


@dataclass
class NormalizedRecord:
    """
    A structure representing the final uniform sensor record.
    """
    timestamp: str
    sensor: str
    sensor_type: str
    features: Dict[str, float]
    threat_hint: float

    def as_dict(self) -> Dict[str, Any]:
        out = {
            "timestamp": self.timestamp,
            "sensor": self.sensor,
            "sensor_type": self.sensor_type,
            "threat_hint": self.threat_hint,
        }
        out.update(self.features)
        return out


def normalize_sensor_sample(sample: SensorSample) -> NormalizedRecord:
    """
    Take a raw SensorSample (any sensor) and convert it into a
    clean, numeric-only feature dictionary based on lookup table.
    """
    if not sample.valid:
        return NormalizedRecord(
            timestamp=datetime.utcnow().isoformat(),
            sensor=sample.sensor_name,
            sensor_type=sample.sensor_type,
            features={},
            threat_hint=0.0,
        )

    mappings = SENSOR_FIELD_MAP.get(sample.sensor_type, {})
    features: Dict[str, float] = {}

    # Extract normalized numeric fields
    for out_field, src_field in mappings.items():
        val = sample.clean.get(src_field, None)
        try:
            features[out_field] = float(val)
        except Exception:
            features[out_field] = 0.0

    # Estimate threat hint using simple heuristics
    threat_hint = estimate_threat(sample)

    return NormalizedRecord(
        timestamp=datetime.utcnow().isoformat(),
        sensor=sample.sensor_name,
        sensor_type=sample.sensor_type,
        features=features,
        threat_hint=round(threat_hint, 3),
    )


def estimate_threat(sample: SensorSample) -> float:
    """
    Very simple threat heuristic used for early fusion.
    """
    clean = sample.clean

    if sample.sensor_type == "optical":
        return 0.4 if clean.get("flash") else 0.1

    if sample.sensor_type == "seismic":
        return min(1.0, clean.get("threat_score", 0.0) / 10.0)

    if sample.sensor_type == "ems":
        return clean.get("ems_threat", 0.0)

    if sample.sensor_type == "radiation":
        return 0.6 if clean.get("spike") else 0.1

    if sample.sensor_type == "generic":
        load = clean.get("load_norm", 0.0)
        err = clean.get("error_rate_norm", 0.0)
        return min(1.0, (load * 0.3) + (err * 0.7))

    return 0.0

