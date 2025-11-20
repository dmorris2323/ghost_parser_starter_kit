import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import SCORED_FILE, HEATMAP_FILE
from validators import (
    validate_required_columns,
    validate_numeric_fields,
    validate_row_integrity,
)
from error_handler import safe_run


def build_heatmap_data(
    scored_file: Path | str = SCORED_FILE,
    out_file: Path | str = HEATMAP_FILE,
):
    """
    Prepare a minimal heatmap-ready CSV from scored_output.csv.

    Output schema:
      - id
      - Score
      - Threat_Level (Critical / High / Moderate)
    """

    path = Path(scored_file)
    out_path = Path(out_file)

    # 1) Check file exists
    if not path.exists():
        msg = f"File not found: {path.resolve()}"
        print(f"❌ {msg}")
        log_event("heatmap_prep", "error", msg)
        return None

    # 2) Load data
    df = pd.read_csv(path)

    # 3) Validate basic structure (no null rows)
    if not validate_row_integrity(df, "heatmap_prep"):
        return None

    # 4) Ensure id and Score are present
    if not validate_required_columns(df, ["id", "Score"], "heatmap_prep"):
        return None

    # 5) Validate Score is numeric
    if not validate_numeric_fields(df, ["Score"], "heatmap_prep"):
        return None

    # 6) Derive Threat_Level from Score
    def threat_level(score):
        try:
            s = float(score)
        except Exception:
            return "Moderate"

        if s >= 90:
            return "Critical"
        elif s >= 50:
            return "High"
        else:
            return "Moderate"

    df["Threat_Level"] = df["Score"].apply(threat_level)

    df_out = df.loc[:, ["id", "Score", "Threat_Level"]].copy()
    df_out.to_csv(out_path, index=False)

    print(f"🔥 Heatmap-ready data written to {out_path.name}")
    log_event(
        "heatmap_prep",
        "completed",
        f"{len(df_out)} records -> {out_path.name}",
    )

    return df_out


if __name__ == "__main__":
    safe_run("heatmap_prep", build_heatmap_data)

