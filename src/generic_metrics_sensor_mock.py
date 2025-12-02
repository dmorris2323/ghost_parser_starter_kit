"""
generic_metrics_sensor_mock.py — Ghost Lantern Labs
---------------------------------------------------

Generic "metrics" sensor for non-military / industry-neutral use.

Simulates:
- system_load (0.0–1.0)
- requests_per_min
- error_rate (0.0–1.0)

This lets GLL handle non-ICADS environments with the same sensor abstraction.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import random

from sensor_interface import SensorBase, SensorSample, pretty_print_sample


class GenericMetricsSensorMock(SensorBase):
    name = "generic_metrics_sensor_mock"
    sensor_type = "generic"

    def read(self) -> Dict[str, Any]:
        """
        Simulate system metric snapshot.
        """
        load = round(random.uniform(0.0, 1.0), 3)
        requests_per_min = random.randint(10, 2000)
        error_rate = round(random.uniform(0.0, 0.2), 3)

        return {
            "load": load,
            "requests_per_min": requests_per_min,
            "error_rate": error_rate,
        }

    def validate(self, sample: Dict[str, Any]) -> Tuple[bool, str | None]:
        try:
            load = float(sample.get("load", 0.0))
            rpm = int(sample.get("requests_per_min", 0))
            err = float(sample.get("error_rate", 0.0))
        except (TypeError, ValueError):
            return False, "Non-numeric generic metric fields."

        if not (0.0 <= load <= 1.0):
            return False, "Load must be in [0.0, 1.0]."
        if rpm < 0:
            return False, "Requests per minute cannot be negative."
        if not (0.0 <= err <= 1.0):
            return False, "Error rate must be in [0.0, 1.0]."

        return True, None

    def normalize(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        load = float(sample["load"])
        rpm = int(sample["requests_per_min"])
        err = float(sample["error_rate"])

        return {
            "sensor": self.name,
            "type": self.sensor_type,
            "load_norm": load,
            "requests_per_min": rpm,
            "error_rate_norm": err,
        }


if __name__ == "__main__":
    sensor = GenericMetricsSensorMock()
    s: SensorSample = sensor.sample()
    pretty_print_sample(s)

