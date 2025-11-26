"""
corruptor.py — Day 51
Simulates adversarial or broken telemetry.
"""

import pandas as pd
from pathlib import Path
import random

SRC = Path("data/fused_output.csv")
OUT = Path("data/fused_output_corrupted.csv")

def corrupt():
    df = pd.read_csv(SRC)

    # Randomly blank out fields
    for col in ["Seismic_Mag", "Radiation_uSv", "Comms_State"]:
        if random.random() < 0.5:
            idx = random.randint(0, len(df) - 1)
            df.loc[idx, col] = None

    # Add impossible values
    idx = random.randint(0, len(df) - 1)
    df.loc[idx, "Seismic_Mag"] = -9

    df.to_csv(OUT, index=False)
    print(f"[OK] Corrupted telemetry written → {OUT}")

if __name__ == "__main__":
    corrupt()

