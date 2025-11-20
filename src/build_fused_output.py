import pandas as pd
from pathlib import Path

from settings import FUSED_FILE
from fusion_logger import log_event
from error_handler import safe_run


def build_fused_output(out_file: Path | str = FUSED_FILE):
    """
    Build a strict, telemetry-style fused_output.csv
    that matches the expectations of fusion_scoring.

    Columns:
      - id
      - Seismic_Mag
      - Radiation_uSv
      - Comms_State (Normal/Burst/Silence)
      - AOI_Hit (True/False)
    """
    path = Path(out_file)

    # Sample fused telemetry – you can adjust later as needed
    data = [
        {"id": 1, "Seismic_Mag": 5.1, "Radiation_uSv": 3.66, "Comms_State": "Normal",  "AOI_Hit": False},
        {"id": 2, "Seismic_Mag": 5.2, "Radiation_uSv": 1.62, "Comms_State": "Burst",   "AOI_Hit": True},
        {"id": 3, "Seismic_Mag": 5.0, "Radiation_uSv": 3.17, "Comms_State": "Normal",  "AOI_Hit": False},
        {"id": 4, "Seismic_Mag": 4.4, "Radiation_uSv": 0.19, "Comms_State": "Silence", "AOI_Hit": False},
        {"id": 5, "Seismic_Mag": 4.1, "Radiation_uSv": 3.39, "Comms_State": "Normal",  "AOI_Hit": True},
    ]

    df = pd.DataFrame(data)
    df.to_csv(path, index=False)

    print(f"✅ Fused telemetry written to {path}")
    log_event("build_fused_output", "completed", f"{len(df)} rows -> {path.name}")

    return df


if __name__ == "__main__":
    safe_run("build_fused_output", build_fused_output)

