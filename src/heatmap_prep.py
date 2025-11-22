import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from error_handler import safe_run

try:
    from settings import SCORED_FILE
except ImportError:
    SCORED_FILE = "scored_output.csv"

HEATMAP_FILE = "heatmap_data.csv"

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


def generate_heatmap_data(
    scored_file: str | Path = SCORED_FILE,
    out_file: str | Path = HEATMAP_FILE,
):
    """
    Prepare scored data for use in a spatial/heatmap visualization.
    """

    module_name = "heatmap_prep"

    path = Path(scored_file)
    out_path = Path(out_file)

    if not path.exists():
        msg = f"No scored file found at: {path.resolve()}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return None

    # 1) Load
    df = pd.read_csv(path)

    # 2) Basic validation
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

    # 3) Select key columns (keep flexible if extra columns exist)
    keep_cols = []
    for col in [
        "id",
        "Seismic_Mag",
        "Radiation_uSv",
        "Comms_State",
        "Score",
    ]:
        if col in df.columns:
            keep_cols.append(col)

    heatmap_df = df.loc[:, keep_cols].copy()

    # 4) Write output
    heatmap_df.to_csv(out_path, index=False)
    print(f"🔥 Heatmap-ready data written to {out_path.name}")
    log_event(
        module_name,
        "completed",
        f"{len(heatmap_df)} records -> {out_path.name}",
    )

    return heatmap_df


if __name__ == "__main__":
    safe_run("heatmap_prep", generate_heatmap_data)

