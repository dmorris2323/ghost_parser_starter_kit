"""
fusion_ingest.py
----------------

Unified ingest pipeline for GLL.
Now includes:
 - sensor profile thresholds
 - ingest tuning hooks
 - modular sensor loading
"""

from datetime import datetime
from pathlib import Path
import csv
import random

from sensor_interface import SensorSample
from ingest_tuning import get_thresholds
from sensor_manifest_loader import load_manifest


OUTPUT_PATH = Path("data/sensor_ingest.csv")


def collect_sensor_samples():
    """
    Load enabled sensors from manifest and collect readings.
    """

    manifest = load_manifest()
    enabled = manifest.get("enabled", [])

    samples = []

    for sensor_name in enabled:
        # Dynamically import sensor modules
        mod_name = f"{sensor_name}_sensor_mock"
        try:
            mod = __import__(mod_name)
        except ModuleNotFoundError:
            print(f"[WARN] Sensor module {mod_name} not found. Skipping.")
            continue

        if hasattr(mod, "sample"):
            s = mod.sample()
            samples.append((sensor_name, s))
        else:
            print(f"[WARN] Sensor module {mod_name} missing 'sample()' function.")

    return samples


def build_fusion_record(sensor_name, sample: SensorSample):
    """
    Produce a single fused record entry for later scoring and alerts.
    """

    thresholds = get_thresholds(sensor_name)

    fusion_dict = {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor": sensor_name,
        "load_norm": sample.load_norm,
        "requests_per_min": sample.requests_per_min,
        "error_rate_norm": sample.error_rate_norm,
    }

    if thresholds:
        fusion_dict["warn_threshold"] = thresholds["warning"]
        fusion_dict["crit_threshold"] = thresholds["critical"]
    else:
        fusion_dict["warn_threshold"] = None
        fusion_dict["crit_threshold"] = None

    return fusion_dict


def write_fusion_records(records):
    """
    Write records to CSV.
    """

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    header = [
        "timestamp",
        "sensor",
        "load_norm",
        "requests_per_min",
        "error_rate_norm",
        "warn_threshold",
        "crit_threshold",
    ]

    write_header = not OUTPUT_PATH.exists()

    with open(OUTPUT_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if write_header:
            writer.writeheader()
        for r in records:
            writer.writerow(r)


def main():
    print("[INFO] Collecting sensor samples...")
    samples = collect_sensor_samples()

    if not samples:
        print("[WARN] No samples collected.")
        return

    records = []
    for sensor_name, sample in samples:
        rec = build_fusion_record(sensor_name, sample)
        records.append(rec)

    print("[INFO] Writing fusion ingest output...")
    write_fusion_records(records)

    print(f"[DONE] Wrote {len(records)} ingest records → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

