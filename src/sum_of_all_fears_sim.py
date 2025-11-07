import pandas as pd
import random

def simulate_event_series(events=10):
    data = []
    for i in range(events):
        seismic = round(random.uniform(2.0, 7.5), 1)  # magnitude
        radiation = round(random.uniform(0.01, 5.0), 2)  # µSv spike
        comms = random.choice(["Normal", "Burst", "Silence"])
        AOI_Hit = (seismic > 4.8 and radiation > 1.5 and comms == "Burst")
        data.append({
            "id": i + 1,
            "Seismic_Mag": seismic,
            "Radiation_uSv": radiation,
            "Comms_State": comms,
            "AOI_Hit": AOI_Hit
        })
    df = pd.DataFrame(data)
    df.to_csv("sum_fears_sim.csv", index=False)
    print(f"✅ Generated {events} simulated telemetry events (sum_fears_sim.csv)")
    return df

if __name__ == "__main__":
    simulate_event_series()

