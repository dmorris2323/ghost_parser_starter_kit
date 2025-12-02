"""
optical_sensor_mock.py — Ghost Lantern Labs
-------------------------------------------

Mock optical sensor:
- Simulates first flash / plume detection.
- Intended for testing sensor abstraction and fusion ingest.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import random

from sensor_interface import SensorBase, SensorSample, pretty_print_sample


class OpticalSensorMock(SensorBase):
    name = "optical_sensor_mock"
    sensor_type = "optical"

    def read(self) -> Dict[str, Any]:
        """
        Simulate a basic optical detection snapshot.
        """
        flash = random.choice([True, False])
        intensity = round(random.uniform(0.0, 1.0), 3)  # 0.0–1.0 normalized
        cloud_cover = random.choice(["low", "medium", "high"])

        return {
            "flash_detected": flash,
            "intensity": intensity,
            "cloud_cover": cloud_cover,
        }

    def validate(self, sample: Dict[str, Any]) -> Tuple[bool, str | None]:
        if "intensity" not in sample:
            return False, "Missing intensity field."
        try:
            val = float(sample["intensity"])
        except (TypeError, ValueError):
            return False, "Intensity not numeric."

        if not (0.0 <= val <= 1.0):
            return False, "Intensity out of expected range [0.0, 1.0]."

        return True, None

    def normalize(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize into a minimal, fusion-friendly dict.
        """
        intensity = float(sample["intensity"])
        cloud = sample.get("cloud_cover", "unknown")

        # Encode cloud cover into simple numeric scale.
        cloud_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
        cloud_score = cloud_map.get(str(cloud).lower(), 0.5)

        return {
            "sensor": self.name,
            "type": self.sensor_type,
            "flash": bool(sample.get("flash_detected", False)),
            "intensity_norm": intensity,
            "cloud_score": cloud_score,
        }


if __name__ == "__main__":
    sensor = OpticalSensorMock()
    s: SensorSample = sensor.sample()
    pretty_print_sample(s)

