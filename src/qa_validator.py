import pandas as pd

def validate_parsed(df: pd.DataFrame):
    """
    Simple QA checks for parsed output.
    Flags missing coordinates, impossible magnitudes, or duplicate timestamps.
    Returns summary dictionary.
    """
    issues = {
        "missing_coords": df[df["Lat"].isna() | df["Lon"].isna()].shape[0],
        "bad_mag": df[(df["Mag"] < 0) | (df["Mag"] > 10)].shape[0],
        "duplicates": df["Time"].duplicated().sum(),
    }
    issues["total_flags"] = sum(issues.values())
    return issues

