"""
sensor_interface.py — Ghost Lantern Labs
----------------------------------------

Common interface and helpers for all sensor-like inputs.

GLL should be able to treat:
- optical sensors
- seismic sensors
- EMS/jammer sensors
- radiation sensors
- OR non-military "sensors" (logs, metrics, biometrics, etc.)

in a uniform way.

This module defines:
- A base SensorBase class with expected methods.
- A helper to run a single sample and pretty-print it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class SensorSample:
    """
    Generic container for a single sensor reading.

    'raw'   = original sensor dict
    'clean' = normalized dict ready for fusion pipeline
    'valid' = True/False after validation
    'reason' = validation note (None if valid)
    """
    sensor_name: str
    sensor_type: str
    raw: Dict[str, Any]
    clean: Dict[str, Any]
    valid: bool
    reason: str | None = None


class SensorBase:
    """
    Base class / interface for all GLL sensors.

    Subclasses should implement:
    - name (str)
    - sensor_type (str) — e.g. "optical", "seismic", "ems", "radiation", "generic"
    - read() -> Dict[str, Any]
    - validate(sample) -> (bool, reason)
    - normalize(sample) -> Dict[str, Any]
    - metadata() -> Dict[str, Any]
    """

    name: str = "abstract_sensor"
    sensor_type: str = "generic"

    def read(self) -> Dict[str, Any]:
        raise NotImplementedError

    def validate(self, sample: Dict[str, Any]) -> Tuple[bool, str | None]:
        raise NotImplementedError

    def normalize(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "sensor_type": self.sensor_type,
        }

    def sample(self) -> SensorSample:
        """
        Convenience method:
        - read raw data
        - validate
        - normalize
        - return SensorSample object
        """
        raw = self.read()
        valid, reason = self.validate(raw)
        clean = self.normalize(raw) if valid else {}

        return SensorSample(
            sensor_name=self.name,
            sensor_type=self.sensor_type,
            raw=raw,
            clean=clean,
            valid=valid,
            reason=reason,
        )


def pretty_print_sample(sample: SensorSample) -> None:
    """
    Human-friendly printout for quick diagnostics and demos.
    """
    print(f"Sensor: {sample.sensor_name} ({sample.sensor_type})")
    print(f"Valid: {sample.valid}  Reason: {sample.reason}")
    print("Raw:", sample.raw)
    print("Clean:", sample.clean)

