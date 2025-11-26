"""
bad_data_heatmap.py — Day 52
Summarizes bad_data_quarantine.csv into a simple "heatmap" table:
- time bucket (hourly)
- quarantine reason
- count of bad rows

Output: bad_data_heatmap.csv (in src/ when run from src/)
"""

from pathlib import Path

import pandas as pd

QUARANTINE_FILE = Path("bad_data_quarantine.csv")
HEATMAP_FILE = Path("bad_data_heatmap.csv")


def build_bad_data_heatmap(
    quarantine_path: Path = QUARANTINE_FILE,
    out_path: Path = HEATMAP_FILE,
) -> None:
    if not quarantine_path.exists():
        print(f"[HEATMAP] No quarantine file found at {quarantine_path}. Nothing to summarize.")
        return

    df = pd.read_csv(quarantine_path)

    required_cols = {"Quarantine_Time_UTC", "Quarantine_Reason"}
    if not required_cols.issubset(set(df.columns)):
        print(f"[HEATMAP] Quarantine file missing required columns: {required_cols}")
        return

    # Parse time to datetime and floor to hour bucket
    df["Quarantine_Time_UTC"] = pd.to_datetime(df["Quarantine_Time_UTC"], errors="coerce")
    df["Time_Bucket"] = df["Quarantine_Time_UTC"].dt.floor("H").dt.strftime("%Y-%m-%dT%H:00Z")

    # Group by hour + reason
    grouped = (
        df.groupby(["Time_Bucket", "Quarantine_Reason"])
        .size()
        .reset_index(name="Count")
        .sort_values(["Time_Bucket", "Quarantine_Reason"])
    )

    if grouped.empty:
        print("[HEATMAP] No rows to summarize after grouping.")
        return

    grouped.to_csv(out_path, index=False)
    print(f"[HEATMAP] bad_data_heatmap.csv written to {out_path}")
    print(grouped.head(10))


if __name__ == "__main__":
    build_bad_data_heatmap()

