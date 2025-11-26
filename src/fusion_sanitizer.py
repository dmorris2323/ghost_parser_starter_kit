"""
fusion_sanitizer.py — Day 52
Makes sure fused_output is always clean, valid, and safe to score.
Also quarantines bad rows into bad_data_quarantine.csv for forensics.
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

from fusion_logger import log_event

# Where we store quarantined bad data (when you run from src/)
QUARANTINE_FILE = Path("bad_data_quarantine.csv")

SAFE_DEFAULTS = {
    "Seismic_Mag": 0.0,
    "Radiation_uSv": 0.0,
    "Comms_State": "UNKNOWN",
    "AOI_Hit": False,
}


def _append_quarantine(rows: pd.DataFrame, reason: str, source_module: str = "fusion_sanitizer") -> None:
    """
    Append bad rows to the quarantine CSV with a timestamp + reason.
    """
    if rows is None or rows.empty:
        return

    # Make sure we don't mutate the original slice
    qdf = rows.copy()

    # Add metadata columns
    qdf.insert(0, "Quarantine_Reason", reason)
    qdf.insert(0, "Source_Module", source_module)
    qdf.insert(0, "Quarantine_Time_UTC", datetime.utcnow().isoformat())

    # Write / append to CSV
    write_header = not QUARANTINE_FILE.exists()
    mode = "w" if write_header else "a"

    qdf.to_csv(
        QUARANTINE_FILE,
        mode=mode,
        index=False,
        header=write_header,
    )

    log_event(
        "bad_data_quarantine",
        "quarantine",
        f"{len(qdf)} row(s) quarantined for reason='{reason}'",
    )


def sanitize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace NaN, None, blanks, or impossible values.
    Also quarantine rows that had impossible physics.
    """
    df = df.copy()
    original_len = len(df)

    # Ensure all SAFE_DEFAULTS columns exist and fill NaN
    for col, default in SAFE_DEFAULTS.items():
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default)

    # Physics rules: negative seismic / radiation are impossible
    for col in ("Seismic_Mag", "Radiation_uSv"):
        if col in df.columns:
            bad_mask = df[col] < 0
            if bad_mask.any():
                bad_rows = df[bad_mask]
                _append_quarantine(bad_rows, reason=f"negative_{col}", source_module="fusion_sanitizer")
                # Clamp those values to safe default for live pipeline
                df.loc[bad_mask, col] = SAFE_DEFAULTS[col]

    log_event(
        "fusion_sanitizer",
        "sanitize",
        f"{original_len} rows in, {len(df)} rows remain after cleaning",
    )
    return df

