import pandas as pd
import json

def fuse_with_aoi(sensor_file: str, aoi_file: str):
    """
    Combines parsed sensor data with AOI boundaries to flag multi-sensor hits.
    """

    df = pd.read_csv(sensor_file)
    with open(aoi_file, "r") as f:
        aois = json.load(f)

    fused_rows = []
    for _, row in df.iterrows():
        lat, lon = row.get("Lat"), row.get("Lon")
        flags = []
        for name, box in aois.items():
            if (
                box["lat_min"] <= lat <= box["lat_max"]
                and box["lon_min"] <= lon <= box["lon_max"]
            ):
                flags.append(name)
        fused_rows.append({
            **row.to_dict(),
            "AOI_Hits": ", ".join(flags) if flags else "",
            "Fused": bool(flags)
        })

    fused_df = pd.DataFrame(fused_rows)
    return fused_df

