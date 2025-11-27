"""
bad_data_heatmap_prep.py — Day 53
Prepares aggregate stats from bad_data_quarantine.csv
so we can later visualize attack / corruption patterns.
"""

import os
from pathlib import Path

import pandas as pd
from fusion_logger import log_event

QUARANTINE_FILE = Path("bad_data_quarantine.csv")
HEATMAP_READY = Path("bad_data_heatmap.csv")


def build_bad_data_heatmap() -> None:
    if not QUARANTINE_FILE.exists():
        msg = f"{QUARANTINE_FILE} not found — no bad data recorded yet."
        print(msg)
        log_event("bad_data_heatmap", "no_data", msg)
        return

    try:
        df = pd.read_csv(QUARANTINE_FILE)
    except Exception as e:
        msg = f"Failed to read {QUARANTINE_FILE}: {e}"
        print(msg)
        log_event("bad_data_heatmap", "read_error", msg)
        return

    if df.empty:
        msg = "Quarantine file is empty — nothing to aggregate."
        print(msg)
        log_event("bad_data_heatmap", "empty", msg)
        return

    # Assume there is a column 'reason' describing why row was quarantined
    if "reason" not in df.columns:
        msg = "Missing 'reason' column in bad_data_quarantine.csv"
        print(msg)
        log_event("bad_data_heatmap", "missing_reason", msg)
        return

    agg = df.groupby("reason").size().reset_index(name="count")
    agg.sort_values("count", ascending=False, inplace=True)

    agg.to_csv(HEATMAP_READY, index=False)

    msg = f"Bad-data heatmap data written to {HEATMAP_READY}"
    print(msg)
    log_event("bad_data_heatmap", "completed", msg)


if __name__ == "__main__":
    build_bad_data_heatmap()

