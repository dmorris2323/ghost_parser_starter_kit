import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import FUSED_FILE, SCORED_FILE
from validators import (
    validate_required_columns,
    validate_numeric_fields,
    validate_row_integrity,
    validate_physics
)
from error_handler import safe_run


def score_fusion(
    fused_file: Path | str = FUSED_FILE,
    out_file: Path | str = SCORED_FILE
):
    """
    Scores fused_output.csv by AOI_Hit and produces scored_output.csv.
    Includes:
      - required column validation
      - numeric validation
      - physics validation
      - soft fallback (drop invalid rows)
    """
    fused_path = Path(fused_file)
    scored_path = Path(out_file)

    # 1) Check file exists
    if not fused_path.exists():
        msg = f"File not found: {fused_path.resolve()}"
        print(f"❌ {msg}")
        log_event("fusion_scoring", "error", msg)
        return None

    # 2) Load dataframe
    df = pd.read_csv(fused_path)

    # 3) Validate required columns
    required = ["id", "Seismic_Mag", "Radiation_uSv", "Comms_State", "AOI_Hit"]
    if not validate_required_columns(df, required, "fusion_scoring"):
        return None

    # 4) Validate row integrity (no nulls)
    if not validate_row_integrity(df, "fusion_scoring"):
        # Continue? No. Null violates telemetry.
        return None

    # 5) Validate numeric fields
    if not validate_numeric_fields(df, ["Seismic_Mag", "Radiation_uSv"], "fusion_scoring"):
        return None

    # 6) Physics validation — strict AND fallback
    # --------------------------------------------------------
    # First attempt strict validation
    strict_ok = validate_physics(df, "fusion_scoring")

    if not strict_ok:
        # Soft fallback — drop bad rows but continue scoring
        invalid_mask = df.apply(
            lambda r: not (
                4.0 <= float(r["Seismic_Mag"]) <= 9.5
                and 0 <= float(r["Radiation_uSv"]) <= 500
                and r["Comms_State"] in ["Normal", "Burst", "Silence"]
            ),
            axis=1
        )

        if invalid_mask.any():
            removed = df[invalid_mask]
            df = df[~invalid_mask]

            msg = f"Dropped {len(removed)} invalid rows (physics fallback)"
            print(f"⚠️ {msg}")
            log_event("fusion_scoring", "rows_dropped", msg)

        # If we dropped everything, abort
        if df.empty:
            msg = "All rows removed — no valid telemetry left."
            print(f"❌ {msg}")
            log_event("fusion_scoring", "error", msg)
            return None

    # 7) Apply scoring logic
    df["Score"] = df.apply(
        lambda r: 100 if bool(r.get("AOI_Hit")) else 10,
        axis=1
    )

    # 8) Sort and save
    df_sorted = df.sort_values(by="Score", ascending=False)
    df_sorted.to_csv(scored_path, index=False)

    print(f"✅ Scoring complete — {len(df_sorted)} rows saved to {scored_path.name}")
    log_event(
        "fusion_scoring",
        "completed",
        f"{len(df_sorted)} rows -> {scored_path.name}"
    )

    return df_sorted


if __name__ == "__main__":
    safe_run("fusion_scoring", score_fusion)

