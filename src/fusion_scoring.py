import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import FUSED_FILE, SCORED_FILE


def score_fusion(fused_file: Path | str = FUSED_FILE,
                 scored_file: Path | str = SCORED_FILE):
    """
    Read fused_output, assign scores, write scored_output.
    Uses central paths from settings.py by default.
    """
    fused_path = Path(fused_file)
    scored_path = Path(scored_file)

    # Handle missing file gracefully
    if not fused_path.exists():
        msg = f"File not found: {fused_path.resolve()}"
        print(f"❌ {msg}")
        log_event("fusion_scoring", "error", msg)
        return None

    try:
        df = pd.read_csv(fused_path)

        # Assign score based on AOI_Hit field
        df["Score"] = df.apply(
            lambda r: 100 if r.get("AOI_Hit", False) else 10,
            axis=1
        )

        # Sort by score descending
        df_sorted = df.sort_values(by="Score", ascending=False)

        # Save results
        df_sorted.to_csv(scored_path, index=False)
        print(f"✅ Scoring complete — {len(df_sorted)} rows saved to {scored_path.name}")

        # Log success
        log_event("fusion_scoring", "completed", f"{len(df_sorted)} rows -> {scored_path.name}")

        return df_sorted.head()

    except Exception as e:
        msg = f"Error during scoring: {e}"
        print(f"⚠️ {msg}")
        log_event("fusion_scoring", "error", msg)
        return None


if __name__ == "__main__":
    score_fusion()

