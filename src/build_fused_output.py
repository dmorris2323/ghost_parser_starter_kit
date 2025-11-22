import pandas as pd
from pathlib import Path

# 🔒 STRICT SCHEMA — update this if you expand fusion_schema.md
SCHEMA_COLUMNS = [
    "id",
    "Seismic_Mag",
    "Radiation_uSv",
    "Comms_State",
    "AOI_Hit",
    "Score",
    "Confidence_Level",
    "Description",
]


def build_fused_output(out_file: Path | str = "fused_output.csv"):
    """
    Build a strict, telemetry-style fused_output.csv
    that matches the expectations of fusion_scoring.
    """

    path = Path(out_file)

    # Sample fused telemetry – can be replaced with real data later
    data = [
        {"id": 1, "Seismic_Mag": 5.1, "Radiation_uSv": 3.66,
            "Comms_State": "Normal",  "AOI_Hit": False},
        {"id": 2, "Seismic_Mag": 5.2, "Radiation_uSv": 1.62,
            "Comms_State": "Burst",   "AOI_Hit": True},
        {"id": 3, "Seismic_Mag": 5.0, "Radiation_uSv": 3.17,
            "Comms_State": "Normal",  "AOI_Hit": False},
        {"id": 4, "Seismic_Mag": 4.4, "Radiation_uSv": 0.19,
            "Comms_State": "Silence", "AOI_Hit": False},
        {"id": 5, "Seismic_Mag": 4.1, "Radiation_uSv": 3.39,
            "Comms_State": "Normal",  "AOI_Hit": True},
    ]

    df = pd.DataFrame(data)

    # 🔒 Enforce strict schema order and required columns
    df = df.reindex(columns=SCHEMA_COLUMNS)

    # 🔧 Fill defaults for missing columns (safe placeholders)
    df = df.fillna({
        "Score": 0,
        "Confidence_Level": "Unknown",
        "Description": "",
    })

    # 📝 Write final fused_output.csv
    df.to_csv(path, index=False)

    print(f"✅ fused_output.csv written with strict schema → {path}")
