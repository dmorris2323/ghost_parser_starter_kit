import pandas as pd
from pathlib import Path
from fusion_logger import log_event

def build_heatmap_data(scored_file="scored_output.csv", out_file="heatmap_data.csv"):
    path = Path(scored_file)
    if not path.exists():
        print(f"❌ No scored file found at: {path.resolve()}")
        log_event("heatmap_prep", "missing_file", str(path.resolve()))
        return None

    try:
        df = pd.read_csv(path)

        # Create simplified heatmap fields
        df["Threat_Level"] = df["Score"].apply(
            lambda s: "Critical" if s >= 90 else ("High" if s >= 50 else "Moderate")
        )

        # Optional: if you later add lat/long or AOI tags, they will auto-integrate here
        df_out = df[["id", "Score", "Threat_Level"]].copy()

        df_out.to_csv(out_file, index=False)
        print(f"🔥 Heatmap-ready data written to {out_file}")

        log_event("heatmap_prep", "completed", f"Output -> {out_file}")
        return df_out

    except Exception as e:
        print(f"Error: {e}")
        log_event("heatmap_prep", "error", str(e))
        return None

if __name__ == "__main__":
    build_heatmap_data()

