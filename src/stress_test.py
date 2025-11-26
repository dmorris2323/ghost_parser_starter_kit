"""
stress_test.py — Day 51
Generates massive volumes of fake fused telemetry.
Used to stress-test GLL scoring, alerts, and heatmaps.
"""

import csv
import random
from pathlib import Path

OUT = Path("data/stress_fused_output.csv")

def generate_stress_data(n: int = 5000):
    header = [
        "id", "Seismic_Mag", "Radiation_uSv",
        "Comms_State", "AOI_Hit"
    ]

    states = ["Normal", "Burst", "Silence", "Down"]

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for i in range(1, n+1):
            row = [
                i,
                round(random.uniform(0.0, 6.0), 2),
                round(random.uniform(0.0, 10.0), 2),
                random.choice(states),
                random.choice([True, False]),
            ]
            writer.writerow(row)

    print(f"[OK] Stress test dataset written → {OUT}")

if __name__ == "__main__":
    generate_stress_data()

