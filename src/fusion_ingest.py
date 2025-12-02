"""
fusion_ingest.py — Ghost Lantern Labs
-------------------------------------

Purpose:
- Collect samples from multiple sensors (optical, seismic, EMS, radiation, generic).
- Apply simple fallback logic (e.g., if optical fails, still rely on seismic/EMS).
- Produce a fusion-ready CSV for downstream pipeline use.
- Route invalid sensor samples into bad_data_quarantine.csv for later forensics.

This is a V1 ingest layer. It does NOT modify your existing fusion pipeline.
It simply creates a sensor_ingest.csv file and appends bad sensor samples to
bad_data_quarantine.csv.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import csv

from sensor_interface import SensorSample
from optical_sensor_mock import OpticalSensorMock
from seismic_sensor_mock import SeismicSensorMock
from ems_sensor_mock import EMSSensorMock
from radiation_sensor_mock import RadiationSensorMock
from generic_metrics_sensor_mock import GenericMetricsSensorMock


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SENSOR_INGEST_PATH = DATA_DIR / "sensor_ingest.csv"
BAD_DATA_QUARANTINE_PATH = BASE_DIR / "bad_data_quarantine.csv"


def collect_sensor_samples() -> List[SensorSample]:
    """
    Instantiate all current sensors and collect one sample each.
    """
    sensors = [
        OpticalSensorMock(),
        SeismicSensorMock(),
        EMSSensorMock(),
        RadiationSensorMock(),
        GenericMetricsSensorMock(),
    ]

    samples: List[SensorSample] = []
    for s in sensors:
        samples.append(s.sample())

    return samples


def route_invalid_to_quarantine(samples: List[SensorSample]) -> None:
    """
    Any invalid sensor sample is appended to bad_data_quarantine.csv
    with basic context and raw data.
    """
    fieldnames = [
        "timestamp_utc",
        "sensor_name",
        "sensor_type",
        "reason",
        "raw",
    ]

    file_exists = BAD_DATA_QUARANTINE_PATH.exists()
    with BAD_DATA_QUARANTINE_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        ts = datetime.utcnow().isoformat()
        for sample in samples:
            if not sample.valid:
                writer.writerow(
                    {
                        "timestamp_utc": ts,
                        "sensor_name": sample.sensor_name,
                        "sensor_type": sample.sensor_type,
                        "reason": sample.reason or "invalid_sample",
                        "raw": repr(sample.raw),
                    }
                )


def build_fusion_record(samples: List[SensorSample]) -> Dict[str, Any]:
    """
    Build a single fusion-ready record using available sensors.

    Fallback logic:
    - If optical invalid, we still rely on seismic and EMS to characterize threat.
    - If seismic and EMS are also invalid, we mark the record as "weak".
    """
    ts = datetime.utcnow().isoformat()

    # Helper lookups
    by_type = {s.sensor_type: s for s in samples}
    optical = by_type.get("optical")
    seismic = by_type.get("seismic")
    ems = by_type.get("ems")
    radiation = by_type.get("radiation")
    generic = by_type.get("generic")

    fallback_reason = "ok"

    # Optical
    optical_flash = None
    optical_intensity = None
    if optical and optical.valid:
        optical_flash = bool(optical.clean.get("flash"))
        optical_intensity = optical.clean.get("intensity_norm")
    else:
        fallback_reason = "optical_invalid"
        optical_flash = False
        optical_intensity = None

    # Seismic
    seismic_threat = None
    if seismic and seismic.valid:
        seismic_threat = seismic.clean.get("threat_score")

    # EMS
    ems_threat = None
    if ems and ems.valid:
        ems_threat = ems.clean.get("ems_threat")

    # Radiation
    radiation_spike = None
    if radiation and radiation.valid:
        radiation_spike = bool(radiation.clean.get("spike"))

    # Generic metrics (industry-neutral sensor)
    generic_load = None
    generic_error_rate = None
    if generic and generic.valid:
        generic_load = generic.clean.get("load_norm")
        generic_error_rate = generic.clean.get("error_rate_norm")

    # Refine fallback_reason based on overall availability
    valid_count = sum(1 for s in samples if s.valid)
    if valid_count == 0:
        fallback_reason = "all_sensors_invalid"
    elif fallback_reason == "optical_invalid":
        # If we still have seismic or EMS valid, explicitly call that out.
        if (seismic and seismic.valid) or (ems and ems.valid):
            fallback_reason = "optical_invalid_fallback_to_seismic_ems"

    return {
        "timestamp_utc": ts,
        "fusion_id": ts.replace(":", "").replace("-", ""),
        "optical_flash": optical_flash,
        "optical_intensity": optical_intensity,
        "seismic_threat": seismic_threat,
        "ems_threat": ems_threat,
        "radiation_spike": radiation_spike,
        "generic_load": generic_load,
        "generic_error_rate": generic_error_rate,
        "fallback_reason": fallback_reason,
        "valid_sensor_count": valid_count,
    }


def append_fusion_record(record: Dict[str, Any]) -> None:
    """
    Append a single fusion record into sensor_ingest.csv
    """
    fieldnames = [
        "timestamp_utc",
        "fusion_id",
        "optical_flash",
        "optical_intensity",
        "seismic_threat",
        "ems_threat",
        "radiation_spike",
        "generic_load",
        "generic_error_rate",
        "fallback_reason",
        "valid_sensor_count",
    ]

    file_exists = SENSOR_INGEST_PATH.exists()
    with SENSOR_INGEST_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def main() -> None:
    """
    End-to-end ingest:
    - Collect sensor samples
    - Route invalid ones to quarantine
    - Build fusion record
    - Append to sensor_ingest.csv
    """
    samples = collect_sensor_samples()
    route_invalid_to_quarantine(samples)
    record = build_fusion_record(samples)
    append_fusion_record(record)

    print("✅ Sensor ingest complete.")
    print(f"   Wrote 1 fusion record to: {SENSOR_INGEST_PATH}")
    print(f"   Fallback reason: {record['fallback_reason']}")
    print(f"   Valid sensors: {record['valid_sensor_count']}")


if __name__ == "__main__":
    main()

