import pandas as pd
from pathlib import Path

def commander_extract(scored_file="scored_output.csv", top_n=5):
    path = Path(scored_file)
    if not path.exists():
        print(f"❌ File not found: {path.resolve()}")
        return None

    df = pd.read_csv(path)

    # Take top N by Score (assumes already sorted, but we’ll be explicit)
    df_sorted = df.sort_values(by="Score", ascending=False)
    df_top = df_sorted.head(top_n).copy()

    # If there's no Description column, build one from the telemetry fields
    if "Description" not in df_top.columns:
        def build_desc(r):
            seismic = r.get("Seismic_Mag", "NA")
            rad = r.get("Radiation_uSv", "NA")
            comms = r.get("Comms_State", "NA")
            return f"Seismic {seismic}, Rad {rad} µSv, Comms: {comms}"

        df_top["Description"] = df_top.apply(build_desc, axis=1)

    # Now construct the commander-facing summary
    summary = df_top[["id", "Description", "Score"]].copy()

    # Add a simple confidence label based on Score
    def confidence_label(score):
        if score >= 90:
            return "Critical"
        elif score >= 50:
            return "High"
        else:
            return "Moderate"

    summary["Confidence_Level"] = summary["Score"].apply(confidence_label)

    summary.to_csv("commander_extract.csv", index=False)

    print(f"✅ Commander Extract complete — {len(summary)} events summarized to commander_extract.csv")
    return summary

