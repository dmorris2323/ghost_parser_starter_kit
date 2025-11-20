import pandas as pd
from pathlib import Path
from fusion_logger import log_event
from settings import FUSED_FILE
from error_handler import safe_run

def edge_case_simulator(out_file: Path | str = FUSED_FILE):
    """
    Generates intentionally malformed or edge-case fusion data
    to test validator strength and module resilience.
    """
    df = pd.DataFrame([
        # Normal
        {"id": 1, "Seismic_Mag": 5.0, "Radiation_uSv": 3.1, "Comms_State": "Normal", "AOI_Hit": False},
        # Missing Comms
        {"id": 2, "Seismic_Mag": 5.3, "Radiation_uSv": 2.7, "Comms_State": None, "AOI_Hit": True},
        # Bad Seismic Range
        {"id": 3, "Seismic_Mag": 15.2, "Radiation_uSv": 1.0, "Comms_State": "Burst", "AOI_Hit": False},
        # Non-numeric Radiation
        {"id": 4, "Seismic_Mag": 4.7, "Radiation_uSv": "abc", "Comms_State": "Normal", "AOI_Hit": False},
        # Wrong Comms State
        {"id": 5, "Seismic_Mag": 5.2, "Radiation_uSv": 0.8, "Comms_State": "Broken", "AOI_Hit": True},
    ])

    df.to_csv(out_file, index=False)
    print(f"⚠️ Edge case fused_output.csv written to {out_file}")
    log_event("edge_case_simulator", "completed", "Generated malformed dataset")

if __name__ == "__main__":
    safe_run("edge_case_simulator", edge_case_simulator)

