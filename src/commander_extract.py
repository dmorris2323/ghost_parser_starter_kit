import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import SCORED_FILE, COMMANDER_FILE
from validators import (
    validate_required_columns,
    validate_numeric_fields,
    validate_row_integrity,
    validate_physics,
)
from error_handler import safe_run


def commander_extract(
    scored_file: Path | str = SCORED_FILE,
    top_n: int = 5,
    out_file: Path | str = COMMANDER_FILE,
):
    """
    Build a commander-facing summary table from scored_output.csv.
    Uses:
      - structural validation
      - numeric validation on Score
      - physics sanity (if telemetry present)
    Produces commander_extract.csv with:
      id, Description, Score, Confidence_Level
    """

    path = Path(scored_file)
    out_path = Path(out_file)

    # 1) Ensure scored file exists
    if not path.exists():
        msg = f"File not found: {path.resolve()}"
        print(f"❌ {msg}")
        log_event("commander_extract", "error", msg)
        return None

    # 2) Load data
    df = pd.read_csv(path)

    # 3) Validate row integrity (no nulls)
    if not validate_row_integrity(df, "commander_extract"):
        return None

    # 4) Ensure Score is present
    if not validate_required_columns(df, ["Score"], "commander_extract"):
        return None

    # 5) Ensure Score is numeric
    if not validate_numeric_fields(df, ["Score"], "commander_extract"):
        return None

    # 6) Physics validation (only effective if telemetry fields exist)
    if not validate_physics(df, "commander_extract"):
        # At this stage, scoring should have already cleaned physics.
        # If this fails, better to abort than brief on bad data.
        return None

    # 7) Sort & take top N
    df_sorted = df.sort_values(by="Score", ascending=False)
    df_top = df_sorted.head(top_n).copy()

    # 8) Build Description if missing
    if "Description" not in df_top.columns:
        def build_desc(r):
            seismic = r.get("Seismic_Mag", "NA")
            rad = r.get("Radiation_uSv", "NA")
            comms = r.get("Comms_State", "NA")
            return f"Seismic {seismic}, Rad {rad} µSv, Comms: {comms}"

        df_top["Description"] = df_top.apply(build_desc, axis=1)

    # 9) Ensure id exists
    if "id" not in df_top.columns:
        df_top["id"] = range(1, len(df_top) + 1)

    # 10) Build summary view
    summary = df_top.loc[:, ["id", "Description", "Score"]].copy()

    # 11) Add confidence label
    def confidence_label(val):
        try:
            s = float(val)
        except Exception:
            return "Moderate"

        if s >= 90:
            return "Critical"
        elif s >= 50:
            return "High"
        else:
            return "Moderate"

    summary["Confidence_Level"] = summary["Score"].apply(confidence_label)

    # 12) Save
    summary.to_csv(out_path, index=False)

    print(f"✅ Commander Extract complete — {len(summary)} events summarized to {out_path.name}")
    log_event(
        "commander_extract",
        "completed",
        f"{len(summary)} events -> {out_path.name}",
    )

    return summary


if __name__ == "__main__":
    safe_run("commander_extract", commander_extract)

