import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from error_handler import safe_run

# settings may define default fused/scored paths
try:
    from settings import FUSED_FILE, SCORED_FILE
except ImportError:
    FUSED_FILE = "fused_output.csv"
    SCORED_FILE = "scored_output.csv"

# validators (with safe fallback for validate_schema)
try:
    from validators import (
        validate_row_integrity,
        validate_required_columns,
        validate_numeric_fields,
        validate_physics,
        validate_schema,
    )
except ImportError:
    from validators import (
        validate_row_integrity,
        validate_required_columns,
        validate_numeric_fields,
        validate_physics,
    )

    def validate_schema(df, module_name: str) -> bool:
        # no-op if not implemented
        return True


def score_fusion(
    fused_file: str | Path = FUSED_FILE,
    out_file: str | Path = SCORED_FILE,
):
    """
    Read fused_output, validate it, apply scoring, write scored_output.
    """

    module_name = "fusion_scoring"

    fused_path = Path(fused_file)
    out_path = Path(out_file)

    if not fused_path.exists():
        msg = f"File not found: {fused_path.resolve()}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return None

    # 1) Load
    df = pd.read_csv(fused_path)

    # 2) Validate
    if not validate_row_integrity(df, module_name):
        return None

    if not validate_required_columns(
        df,
        ["id", "Seismic_Mag", "Radiation_uSv", "Comms_State", "AOI_Hit"],
        module_name,
    ):
        return None

    if not validate_numeric_fields(
        df,
        ["Seismic_Mag", "Radiation_uSv"],
        module_name,
    ):
        return None

    if not validate_physics(df, module_name):
        return None

    # Strict schema check (will be a no-op if not implemented)
    if not validate_schema(df, module_name):
        return None

    # 3) Score
    def _score_row(r):
        try:
            return 100 if bool(r.get("AOI_Hit", False)) else 10
        except Exception:
            return 10

    df["Score"] = df.apply(_score_row, axis=1)

    # 4) Sort + write
    df_sorted = df.sort_values(by="Score", ascending=False)
    df_sorted.to_csv(out_path, index=False)

    print(f"✅ Scoring complete — {len(df_sorted)} rows saved to {out_path.name}")
    log_event(
        module_name,
        "completed",
        f"{len(df_sorted)} rows -> {out_path.name}",
    )

    return df_sorted


if __name__ == "__main__":
    safe_run("fusion_scoring", score_fusion)

