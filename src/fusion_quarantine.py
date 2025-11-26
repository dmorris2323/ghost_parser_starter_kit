"""
fusion_quarantine.py — Day 52
Saves suspicious rows for forensics instead of deleting them.
"""

import pandas as pd
from fusion_logger import log_event

QUAR_FILE = "quarantine.csv"

def quarantine(df: pd.DataFrame, mask) -> None:
    bad = df[mask]
    if len(bad) == 0:
        return

    bad.to_csv(QUAR_FILE, mode="a", header=False, index=False)
    log_event("quarantine", "rows_isolated", f"{len(bad)} rows quarantined")

