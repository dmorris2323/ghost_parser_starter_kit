"""
fusion_sanitizer.py — Day 51
Makes sure fused_output is always clean, valid, and safe to score.
"""

import pandas as pd

SAFE_DEFAULTS = {
    "Seismic_Mag": 0.0,
    "Radiation_uSv": 0.0,
    "Comms_State": "UNKNOWN",
    "AOI_Hit": False,
}

def sanitize(df: pd.DataFrame) -> pd.DataFrame:
    """Replace NaN, None, blanks, or impossible values."""
    df = df.copy()

    for col, default in SAFE_DEFAULTS.items():
        # ensure column exists
        if col not in df.columns:
            df[col] = default

        # fill missing values
        df[col] = df[col].fillna(default)

        # impossible negatives → reset
        if col in ("Seismic_Mag", "Radiation_uSv"):
            df.loc[df[col] < 0, col] = default

    return df

