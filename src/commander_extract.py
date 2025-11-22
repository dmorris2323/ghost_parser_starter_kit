import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from error_handler import safe_run

try:
    from settings import SCORED_FILE, COMMANDER_FILE
except ImportError:
    SCORED_FILE = "scored_output.csv"
    COMMANDER_FILE = "commander_extract.csv"

# validators (with safe fallback for validate_schema)
try:
    from validators import (
        validate_row_integrity,
        validate_required_columns,
        validate_numeric_fields,
        validate_schema,
    )
except ImportError:
    from validators import (
        validate_row_integrity,
        validate_required_columns,
        validate_numeric_fields,
    )

    def validate_schema(df, module_name: str) -> bool:
        return True


def commander_extract(
    scored_file: str | Path = SCORED_FILE,
    top_n: int = 5,
    out_file: str | Path = COMMANDER_FILE,
):
    """
    Build commander-facing summary table from scored_output.
    """

    module_name = "commander_extract"

    path = Path(scored_file)
    out_path = Path(out_file)

    if not path.exists():
        msg = f"File not found: {path.resolve()}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return None

    # 1) Load
    df = pd.read_csv(path)

    # 2) Validate
    if not validate_row_integrity(df, module_name):
        return None

    if not validate_required_columns(
        df,
        ["id", "Score"],
        module_name,
    ):
        return None

    if not validate_numeric_fields(
        df,
        ["Score"],
        module_name,
    ):
        return None

    if not validate_schema(df, module_name):
        return None

    # 3) Sort & take top N
    df_sorted = df.sort_values(by="Score", ascending=False)
    df_top = df_sorted.head(top_n).copy()

    # 4) Description synthesis if missing
    if "Description" not in df_top.columns:

        def build_desc(r):
            seismic = r["Seismic_Mag"] if "Seismic_Mag" in r else "NA"
            rad = r["Radiation_uSv"] if "Radiation_uSv" in r else "NA"
            comms = r["Comms_State"] if "Comms_State" in r else "NA"
            return f"Seismic {seismic}, Rad {rad} µSv, Comms: {comms}"

        df_top["Description"] = df_top.apply(build_desc, axis=1)

    # 5) Ensure id exists
    if "id" not in df_top.columns:
        df_top["id"] = range(1, len(df_top) + 1)

    # 6) Commander-facing summary
    summary = df_top.loc[:, ["id", "Description", "Score"]].copy()

    # 7) Confidence labels
    def confidence_label(x):
        try:
            s = float(x)
        except Exception:
            return "Moderate"
        if s >= 90:
            return "Critical"
        elif s >= 50:
            return "High"
        else:
            return "Moderate"

    summary["Confidence_Level"] = summary["Score"].apply(confidence_label)

    # 8) Write out
    summary.to_csv(out_path, index=False)
    print(
        f"✅ Commander Extract complete — {len(summary)} events summarized to {out_path.name}"
    )
    log_event(
        module_name,
        "completed",
        f"{len(summary)} events -> {out_path.name}",
    )

    return summary


if __name__ == "__main__":
    safe_run("commander_extract", commander_extract)

