"""
seismic_sensor_mock.py — Ghost Lantern Labs
-------------------------------------------

Mock seismic sensor:
- Simulates a seismic magnitude and distance reading.
- Used to estimate "how big" and "how far" a disturbance is.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import random

from sensor_interface import SensorBase, SensorSample, pretty_print_sample


class SeismicSensorMock(SensorBase):
    name = "seismic_sensor_mock"
    sensor_type = "seismic"

    def read(self) -> Dict[str, Any]:
        """
        Simulate seismic magnitude and distance.
        """
        magnitude = round(random.uniform(0.0, 6.0), 2)
        distance_km = round(random.uniform(10.0, 1500.0), 1)
        snr = round(random.uniform(0.0, 40.0), 1)  # signal-to-noise ratio

        return {
            "magnitude": magnitude,
            "distance_km": distance_km,
            "snr_db": snr,
        }

    def validate(self, sample: Dict[str, Any]) -> Tuple[bool, str | None]:
        try:
            mag = float(sample.get("magnitude", 0.0))
            dist = float(sample.get("distance_km", 0.0))
            snr = float(sample.get("snr_db", 0.0))
        except (TypeError, ValueError):
            return False, "Non-numeric seismic fields."

        if mag < 0.0:
            return False, "Negative magnitude is invalid."
        if dist <= 0.0:
            return False, "Distance must be positive."
        if snr < 0.0:
            return False, "SNR must be non-negative."

        return True, None

    def normalize(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        mag = float(sample["magnitude"])
        dist = float(sample["distance_km"])
        snr = float(sample["snr_db"])

        # Very rough "yield-ish" proxy: larger mag, closer distance, higher snr = more concerning.
        threat_score = (mag * snr) / max(dist, 1.0)

        return {
            "sensor": self.name,
            "type": self.sensor_type,
            "mag": mag,
            "distance_km": dist,
            "snr_db": snr,
            "threat_score": round(threat_score, 3),
        }


if __name__ == "__main__":
    sensor = SeismicSensorMock()
    s: SensorSample = sensor.sample()
    pretty_print_sample(s)

