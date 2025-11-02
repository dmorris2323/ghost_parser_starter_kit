# src/ghost_parser_cli.py
import argparse, os, sys, io, json
from datetime import datetime
import pandas as pd

# make local imports work when run as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ghost_parser import parse_lines, load_aois  # you already have these

def _read_lines(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f.readlines()]

def _write_bytes(path: str, data: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

def _mk_report(df: pd.DataFrame, preset: str, max_depth_km: float, min_mag: float, max_mag: float, aois: dict) -> bytes:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")
    aoi_keys = ", ".join(list(aois.keys())) if aois else "None"
    preset_line = f"Preset: {preset} | Depth≤{max_depth_km}km | Mag {min_mag}–{max_mag}"

    reason_counts = (
        df.get("Reasons", pd.Series([], dtype=str))
          .fillna("")
          .replace("", "(none)")
          .value_counts()
          .to_dict()
    )

    md = []
    md.append("Ghost Lantern Labs — Operational Parse Report")
    md.append("")
    md.append(f"# Ghost Parser Report — {now}")
    md.append("")
    md.append("**Run Summary**")
    md.append(f"- Parsed events: **{len(df)}**")
    flagged = int(df.get("Flagged", False).astype(bool).sum()) if "Flagged" in df.columns else 0
    md.append(f"- Flagged: **{flagged}**")
    md.append(f"- {preset_line}")
    md.append(f"- AOIs: {aoi_keys}")
    md.append("")
    md.append("**Reason counts:**")
    if reason_counts:
        for k, v in reason_counts.items():
            md.append(f"- {k}: {v}")
    else:
        md.append("- (none)")
    md.append("")
    md.append("**Sample flagged rows (first 5):**")
    sample = df[df.get("Flagged", False) == True].head(5) if "Flagged" in df.columns else pd.DataFrame()
    try:
        if sample.empty:
            md.append("_No flagged rows in sample._")
        else:
            md.append(sample.to_markdown(index=False))
    except Exception:
        # fallback if tabulate missing
        md.append("_Markdown table unavailable (install `tabulate`). Showing CSV rows:_")
        md.append(sample.to_csv(index=False))

    return ("\n".join(md)).encode("utf-8")

def main():
    ap = argparse.ArgumentParser(description="Ghost Parser — CLI")
    ap.add_argument("--log", required=True, help="Path to UTF-8 log file")
    ap.add_argument("--aoi", default=None, help="Path to AOI JSON (optional)")
    ap.add_argument("--preset", default="Default", help="Preset label for the run")
    ap.add_argument("--max-depth-km", type=float, default=2.5)
    ap.add_argument("--min-mag", type=float, default=3.5)
    ap.add_argument("--max-mag", type=float, default=6.5)
    ap.add_argument("--out-csv", default="outputs/cli_day28.csv")
    ap.add_argument("--out-md", default="outputs/cli_day28.md")
    args = ap.parse_args()

    lines = _read_lines(args.log)
    aois = load_aois(args.aoi) if args.aoi else {}

    rows = parse_lines(lines, aois, args.max_depth_km, args.min_mag, args.max_mag)
    df = pd.DataFrame(rows)

    # Save CSV
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    _write_bytes(args.out_csv, csv_bytes)

    # Save MD report
    md_bytes = _mk_report(df, args.preset, args.max_depth_km, args.min_mag, args.max_mag, aois)
    _write_bytes(args.out_md, md_bytes)

    # Console summary
    flagged = int(df.get("Flagged", False).astype(bool).sum()) if "Flagged" in df.columns else 0
    print(f"[OK] Parsed: {len(df)} | Flagged: {flagged}")
    print(f"[OUT] CSV: {args.out_csv}")
    print(f"[OUT] MD : {args.out_md}")

if __name__ == "__main__":
    main()

