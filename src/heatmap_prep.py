import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import SCORED_FILE, HEATMAP_FILE


def build_heatmap_data(
    scored_file: Path | str = SCORED_FILE,
    out_file: Path | str = HEATMAP_FILE
):
    """
    Prepare a minimal heatmap-ready CSV from the scored output.
    Uses paths defined in settings.py by default.
    """
    path = Path(scored_file)
    out_path = Path(out_file)

    if not path.exists():
        msg = f"No scored file found at: {path.resolve()}"
        print(f"❌ {msg}")
        log_event("heatmap_prep", "missing_file", msg)
        return None

    try:
        df = pd.read_csv(path)

        if "Score" not in df.columns:
            raise ValueError("Missing 'Score' column in scored input.")

        def threat_level(score):
            if score >= 90:
                return "Critical"
            elif score >= 50:
                return "High"
            else:
                return "Moderate"

        df["Threat_Level"] = df["Score"].apply(threat_level)

        df_out = df[["id", "Score", "Threat_Level"]].copy()

        df_out.to_csv(out_path, index=False)

        print(f"🔥 Heatmap-ready data written to {out_path.name}")
        log_event("heatmap_prep", "completed", f"Output -> {out_path.name}")

        return df_out

    except Exception as e:
        msg = f"Error in heatmap_prep: {e}"
        print(f"❌ {msg}")
        log_event("heatmap_prep", "error", msg)
        return None


if __name__ == "__main__":
    build_heatmap_data()

