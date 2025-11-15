import pandas as pd
import random
import time

def telemetry_check(fused_file: str = "fused_output.csv"):
    """
    Build a fake telemetry stream for every AOI hit and compute signal-to-noise.
    """
    df = pd.read_csv(fused_file)

    # Safety: only keep rows that actually hit an AOI if that column exists
    if "AOI_Hit" in df.columns:
        df = df[df["AOI_Hit"] == True]

    telemetry_rows = []

    # For every AOI hit, create 5 fake telemetry readings
    for _, row in df.iterrows():
        for _ in range(5):
            signal = round(random.uniform(0.5, 1.0), 2)
            noise  = round(random.uniform(0.0, 0.4), 2)
            telemetry_rows.append(
                {
                    "Station": row.get("Station", "UNK"),
                    "AOI_Hit": row.get("AOI_Hit", False),
                    "Lat": row.get("Lat", 0.0),
                    "Lon": row.get("Lon", 0.0),
                    "Signal": signal,
                    "Noise": noise,
                    "Time": time.time(),
                }
            )

    if not telemetry_rows:
        print("⚠️ No AOI hits found in fused_output.csv; nothing to simulate.")
        return pd.DataFrame()

    out = pd.DataFrame(telemetry_rows)
    out["Signal_to_Noise"] = (out["Signal"] / (out["Noise"] + 0.01)).round(2)

    out.to_csv("telemetry_qacheck.csv", index=False)
    print(f"✅ Telemetry QA generated — {len(out)} rows saved to telemetry_qacheck.csv")
    return out.head()

