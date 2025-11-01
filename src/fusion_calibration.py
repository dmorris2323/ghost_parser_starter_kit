import pandas as pd

def calibrate_fusion(sensor_a, sensor_b):
    df_a = pd.read_csv(sensor_a)
    df_b = pd.read_csv(sensor_b)
    merged = pd.merge(df_a, df_b, on=["Lat", "Lon"], how="inner", suffixes=("_A", "_B"))
    merged["Delta_Mag"] = (merged["Mag_A"] - merged["Mag_B"]).abs()
    merged["Delta_Time"] = pd.to_datetime(merged["Time_A"]) - pd.to_datetime(merged["Time_B"])
    merged["Delta_Time"] = merged["Delta_Time"].dt.total_seconds().abs()
    merged["Cross_Confidence"] = 100 - (merged["Delta_Mag"]*10 + merged["Delta_Time"]/10)
    merged["Cross_Confidence"] = merged["Cross_Confidence"].clip(lower=0, upper=100)
    return merged

