# apps/cli/parse_cli.py
import argparse, json, io, sys
from pathlib import Path
import pandas as pd

# local package
try:
    from ghost_parser import parse_lines, load_aois
except Exception as e:
    print(f"[FATAL] Cannot import ghost_parser: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    p = argparse.ArgumentParser(
        description="Ghost Lantern Labs — CLI parser (CSV/JSONL out)"
    )
    p.add_argument("--raw", required=True, help="Path to raw log file (.log/.txt)")
    p.add_argument("--aoi", default=None, help="Path to aoi.json (optional)")
    p.add_argument("--max-depth-km", type=float, default=2.5, help="Max depth (km)")
    p.add_argument("--min-mag", type=float, default=3.5, help="Min magnitude")
    p.add_argument("--max-mag", type=float, default=6.5, help="Max magnitude")
    p.add_argument("--out-csv", default="outputs/cli_parsed.csv", help="CSV output path")
    p.add_argument("--out-jsonl", default="outputs/cli_parsed.jsonl", help="JSONL output path")
    args = p.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.exists():
        print(f"[ERROR] Raw file not found: {raw_path}", file=sys.stderr)
        sys.exit(2)

    # Read raw lines
    lines = raw_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Load AOIs
    aois = {}
    if args.aoi:
        aoi_path = Path(args.aoi)
        if not aoi_path.exists():
            print(f"[WARN] AOI file not found: {aoi_path} (continuing without AOIs)", file=sys.stderr)
        else:
            try:
                aois = json.loads(aoi_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[WARN] AOI load error: {e} (continuing without AOIs)", file=sys.stderr)
                aois = {}

    # Parse
    rows = parse_lines(
        lines=lines,
        aois=aois,
        max_depth_km=args.max_depth_km,
        min_mag=args.min_mag,
        max_mag=args.max_mag,
    )
    df = pd.DataFrame(rows)

    # Ensure outputs folder
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_jsonl).parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    df.to_csv(args.out_csv, index=False)

    # Write JSONL
    with open(args.out_jsonl, "w", encoding="utf-8") as f:
        for _, r in df.iterrows():
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    print(f"[OK] Parsed rows: {len(df)}")
    print(f"[OK] CSV:   {args.out_csv}")
    print(f"[OK] JSONL: {args.out_jsonl}")

if __name__ == "__main__":
    main()

