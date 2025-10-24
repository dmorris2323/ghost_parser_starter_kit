import pandas as pd
from core_fusion import fuse_sources

log = pd.DataFrame({
    "DateTime": ["2025-10-08T14:10:00Z", "2025-10-08T14:30:00Z"],
    "Station":  ["PS931", "PS932"],
    "Lat":      [40.500, 39.600],
    "Lon":      [129.400, 129.100],
})

em = pd.DataFrame({
    "DateTime": [
        "2025-10-08T14:10:30Z",
        "2025-10-08T14:31:00Z",
    ],
    "RadarID": ["RDR02", "RDR03"],
    "Lat": [40.51, 39.59],   # very close to log lat values
    "Lon": [129.41, 129.11], # very close to log lon values
})

fused = fuse_sources(
    seismic_df=log,
    rf_df=em,
    time_tolerance="10min",
    max_delta_deg=0.5
)

print(fused)

# --- Persist today's fusion result ---
out_path = "outputs/fused_day16.csv"
fused.to_csv(out_path, index=False)
print(f"\nSaved fused output -> {out_path}")

