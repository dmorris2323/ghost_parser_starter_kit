"""
radiation_sensor_mock.py — Ghost Lantern Labs
---------------------------------------------

Mock radiation sensor:
- Simulates background vs spike conditions.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import random

from sensor_interface import SensorBase, SensorSample, pretty_print_sample


class RadiationSensorMock(SensorBase):
    name = "radiation_sensor_mock"
    sensor_type = "radiation"

    def read(self) -> Dict[str, Any]:
        """
        Simulate a radiation reading in microsieverts (uSv).
        """
        background = round(random.uniform(0.05, 0.20), 3)
        # Occasionally generate a spike
        if random.random() < 0.1:
            current = round(background + random.uniform(0.5, 3.0), 3)
        else:
            current = round(background + random.uniform(-0.02, 0.05), 3)

        return {
            "background_uSv": background,
            "current_uSv": current,
        }

    def validate(self, sample: Dict[str, Any]) -> Tuple[bool, str | None]:
        try:
            bg = float(sample.get("background_uSv", 0.0))
            cur = float(sample.get("current_uSv", 0.0))
        except (TypeError, ValueError):
            return False, "Non-numeric radiation fields."

        if bg < 0.0 or cur < 0.0:
            return False, "Radiation cannot be negative."

        return True, None

    def normalize(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        bg = float(sample["background_uSv"])
        cur = float(sample["current_uSv"])
        delta = cur - bg

        spike = delta > 0.3  # very crude, just a placeholder condition

        return {
            "sensor": self.name,
            "type": self.sensor_type,
            "background_uSv": bg,
            "current_uSv": cur,
            "delta_uSv": round(delta, 3),
            "spike": spike,
        }


if __name__ == "__main__":
    sensor = RadiationSensorMock()
    s: SensorSample = sensor.sample()
    pretty_print_sample(s)

