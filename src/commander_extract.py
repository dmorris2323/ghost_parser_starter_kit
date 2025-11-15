import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import SCORED_FILE, COMMANDER_FILE


def commander_extract(
    scored_file: Path | str = SCORED_FILE,
    top_n: int = 5,
    out_file: Path | str = COMMANDER_FILE
):
    """
    Build commander-facing summary table from a scored CSV.
    Uses central paths from settings.py by default.
    """
    path = Path(scored_file)
    out_path = Path(out_file)

    if not path.exists():
        msg = f"File not found: {path.resolve()}"
        print(f"❌ {msg}")
        log_event("commander_extract", "error", msg)
        return None

    try:
        df = pd.read_csv(path)

        if "Score" not in df.columns:
            raise ValueError("Missing 'Score' column in scored input.")

        # sort & take top N (explicit even if pre-sorted)
        df_sorted = df.sort_values(by="Score", ascending=False)
        df_top = df_sorted.head(top_n).copy()

        # Build Description if not already present
        if "Description" not in df_top.columns:
            def build_desc(r):
                seismic = r["Seismic_Mag"] if "Seismic_Mag" in r else "NA"
                rad     = r["Radiation_uSv"] if "Radiation_uSv" in r else "NA"
                comms   = r["Comms_State"] if "Comms_State" in r else "NA"
                return f"Seismic {seismic}, Rad {rad} µSv, Comms: {comms}"
            df_top["Description"] = df_top.apply(build_desc, axis=1)

        # Ensure an id exists
        if "id" not in df_top.columns:
            df_top["id"] = range(1, len(df_top) + 1)

        summary = df_top.loc[:, ["id", "Description", "Score"]].copy()

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

        summary.to_csv(out_path, index=False)
        print(f"✅ Commander Extract complete — {len(summary)} events summarized to {out_path.name}")

        log_event("commander_extract", "completed", f"{len(summary)} events -> {out_path.name}")
        return summary

    except Exception as e:
        msg = f"Error in commander_extract: {e}"
        print(f"⚠️ {msg}")
        log_event("commander_extract", "error", msg)
        return None


if __name__ == "__main__":
    commander_extract()

