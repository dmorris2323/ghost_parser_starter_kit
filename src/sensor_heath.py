"""
sensor_health.py — Ghost Lantern Labs
-------------------------------------

Runs a simple health check across all configured sensors and
produces a human-readable report.

This does NOT affect the pipeline. It is diagnostics-only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from sensor_interface import SensorSample
from optical_sensor_mock import OpticalSensorMock
from seismic_sensor_mock import SeismicSensorMock
from ems_sensor_mock import EMSSensorMock
from radiation_sensor_mock import RadiationSensorMock
from generic_metrics_sensor_mock import GenericMetricsSensorMock


BASE_DIR = Path(__file__).parent
REPORT_PATH = BASE_DIR / "sensor_health_report.txt"


def evaluate_sensor(sensor, iterations: int = 10) -> Dict[str, Any]:
    """
    Sample a sensor multiple times and compute:
    - availability (no exceptions)
    - validity_rate (% samples valid)
    """
    successes = 0
    failures = 0
    valid_count = 0
    samples: List[SensorSample] = []

    for _ in range(iterations):
        try:
            s: SensorSample = sensor.sample()
            samples.append(s)
            successes += 1
            if s.valid:
                valid_count += 1
        except Exception:  # noqa: BLE001
            failures += 1

    total = successes + failures
    availability = successes / total if total > 0 else 0.0
    validity_rate = valid_count / max(successes, 1)

    return {
        "name": getattr(sensor, "name", "unknown"),
        "sensor_type": getattr(sensor, "sensor_type", "unknown"),
        "iterations": iterations,
        "successes": successes,
        "failures": failures,
        "availability": round(availability, 3),
        "validity_rate": round(validity_rate, 3),
    }


def run_health_check() -> None:
    sensors = [
        OpticalSensorMock(),
        SeismicSensorMock(),
        EMSSensorMock(),
        RadiationSensorMock(),
        GenericMetricsSensorMock(),
    ]

    ts = datetime.utcnow().isoformat()
    lines: List[str] = []
    lines.append(f"Sensor Health Report — {ts} UTC")
    lines.append("=" * 60)
    lines.append("")

    for s in sensors:
        result = evaluate_sensor(s)
        lines.append(f"Sensor: {result['name']} ({result['sensor_type']})")
        lines.append(f"  Iterations:   {result['iterations']}")
        lines.append(f"  Successes:    {result['successes']}")
        lines.append(f"  Failures:     {result['failures']}")
        lines.append(f"  Availability: {result['availability']:.3f}")
        lines.append(f"  ValidityRate: {result['validity_rate']:.3f}")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("✅ Sensor health check complete.")
    print(f"   Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    run_health_check()

