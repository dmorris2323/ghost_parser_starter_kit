"""
normalize_all_sensors.py — Ghost Lantern Labs
---------------------------------------------

Runs every sensor mock → normalizes it → prints the uniform record.
"""

from __future__ import annotations

from optical_sensor_mock import OpticalSensorMock
from seismic_sensor_mock import SeismicSensorMock
from ems_sensor_mock import EMSSensorMock
from radiation_sensor_mock import RadiationSensorMock
from generic_metrics_sensor_mock import GenericMetricsSensorMock

from sensor_interface import pretty_print_sample
from sensor_normalizer import normalize_sensor_sample


def main():
    sensors = [
        OpticalSensorMock(),
        SeismicSensorMock(),
        EMSSensorMock(),
        RadiationSensorMock(),
        GenericMetricsSensorMock(),
    ]

    for s in sensors:
        print("\n===== RAW SAMPLE =====")
        sample = s.sample()
        pretty_print_sample(sample)

        print("\n===== NORMALIZED RECORD =====")
        normalized = normalize_sensor_sample(sample)
        print(normalized.as_dict())


if __name__ == "__main__":
    main()

