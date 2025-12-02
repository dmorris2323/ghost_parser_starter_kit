"""
ems_sensor_mock.py — Ghost Lantern Labs
---------------------------------------

Mock EMS (electromagnetic spectrum) sensor:
- Simulates detection of jamming or spoofing behavior.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import random

from sensor_interface import SensorBase, SensorSample, pretty_print_sample


class EMSSensorMock(SensorBase):
    name = "ems_sensor_mock"
    sensor_type = "ems"

    def read(self) -> Dict[str, Any]:
        """
        Simulate EMS snapshot.
        """
        jamming_detected = random.choice([True, False, False])  # biased toward normal
        band_mhz = random.choice([225, 300, 900, 1500])
        snr_db = round(random.uniform(-5.0, 30.0), 1)
        anomaly_score = round(random.uniform(0.0, 1.0), 3)

        return {
            "jamming_detected": jamming_detected,
            "band_mhz": band_mhz,
            "snr_db": snr_db,
            "anomaly_score": anomaly_score,
        }

    def validate(self, sample: Dict[str, Any]) -> Tuple[bool, str | None]:
        try:
            band = float(sample.get("band_mhz", 0.0))
            snr = float(sample.get("snr_db", 0.0))
            anomaly = float(sample.get("anomaly_score", 0.0))
        except (TypeError, ValueError):
            return False, "Non-numeric EMS fields."

        if anomaly < 0.0 or anomaly > 1.0:
            return False, "Anomaly score must be in [0.0, 1.0]."

        if band <= 0.0:
            return False, "Band must be positive frequency."

        return True, None

    def normalize(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        jamming = bool(sample.get("jamming_detected", False))
        band = float(sample["band_mhz"])
        snr = float(sample["snr_db"])
        anomaly = float(sample["anomaly_score"])

        # Very rough fusion weight: EMS-concerning if jamming + high anomaly + poor SNR.
        ems_threat = 0.0
        if jamming:
            ems_threat += 0.4
        ems_threat += anomaly * 0.5
        if snr < 0.0:
            ems_threat += 0.1

        return {
            "sensor": self.name,
            "type": self.sensor_type,
            "jamming": jamming,
            "band_mhz": band,
            "snr_db": snr,
            "anomaly_score": anomaly,
            "ems_threat": round(min(1.0, ems_threat), 3),
        }


if __name__ == "__main__":
    sensor = EMSSensorMock()
    s: SensorSample = sensor.sample()
    pretty_print_sample(s)

