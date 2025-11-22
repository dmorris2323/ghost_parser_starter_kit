from pathlib import Path
import csv

DATA_DIR = Path("data")
SEISMIC_FILE = DATA_DIR / "seismic_events.csv"
FUSED_FILE = DATA_DIR / "fused_output.csv"


def build_fused_output_from_seismic(
    in_file: Path | str = SEISMIC_FILE,
    out_file: Path | str = FUSED_FILE,
) -> None:
    """
    Convert seismic_events.csv -> fused_output.csv
    Schema:
      id, Seismic_Mag, Radiation_uSv, Comms_State, AOI_Hit
    """

    in_path = Path(in_file)
    out_path = Path(out_file)

    rows = []
    with in_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for idx, r in enumerate(reader, start=1):
            # Map CSV fields -> fusion schema
            seismic_mag = float(r["Mag"])

            # Placeholder for now – you’ll replace later with real radiation data
            radiation_usv = 0.0

            # Simple comms assumption – always Normal for now
            comms_state = "Normal"

            aoi_hit = r["Flagged"].strip().upper() == "TRUE"

            rows.append(
                {
                    "id": idx,
                    "Seismic_Mag": seismic_mag,
                    "Radiation_uSv": radiation_usv,
                    "Comms_State": comms_state,
                    "AOI_Hit": aoi_hit,
                }
            )

    # Always write strict header + rows
    header = ["id", "Seismic_Mag", "Radiation_uSv", "Comms_State", "AOI_Hit"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] fused_output.csv written to {out_path}")


if __name__ == "__main__":
    build_fused_output_from_seismic()
