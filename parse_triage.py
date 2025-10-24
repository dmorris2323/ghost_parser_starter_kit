#!/usr/bin/env python3
import argparse, csv, json, sys
from pathlib import Path

def load_aois(path):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        print(f"[WARN] AOI file not found: {p}", file=sys.stderr)
        return {}
    with p.open() as f:
        return json.load(f)

def in_box(lat, lon, box):
    return (box["lat_min"] <= lat <= box["lat_max"]) and (box["lon_min"] <= lon <= box["lon_max"])

def triage(rec, aois):
    reasons = []
    try:
        depth_ok = rec["Depth_km"] <= 2.5
        mag_ok = 3.5 <= rec["Mag"] <= 6.5
    except Exception:
        return False, "bad_numeric_fields"

    if not (depth_ok and mag_ok):
        return False, ""

    if aois:
        for name, box in aois.items():
            if in_box(rec["Lat"], rec["Lon"], box):
                reasons.append(f"in_{name}")
                return True, "nk_zone+shallow+mag_range" if "NK" in name.upper() else "aoi+shallow+mag_range"
        return False, ""
    else:
        return True, "shallow+mag_range"

def parse_line(line):
    parts = [p.strip() for p in line.split("|")]
    if not parts or len(parts[0]) < 10:
        return None
    rec = {"DateTime": parts[0]}
    for part in parts[1:]:
        if ":" in part:
            k, v = part.split(":", 1)
            rec[k.strip()] = v.strip()

    def to_float(s, default=0.0):
        try:
            return float(s)
        except Exception:
            return default

    rec_out = {
        "DateTime": rec.get("DateTime", ""),
        "Station": rec.get("Station", ""),
        "Mag": to_float(rec.get("Mag", "0")),
        "Depth_km": to_float(rec.get("Depth", "0").lower().replace("km","").strip() if rec.get("Depth") else "0"),
        "Lat": to_float(rec.get("Lat", "0")),
        "Lon": to_float(rec.get("Lon", "0")),
        "Type": rec.get("Type", "")
    }
    return rec_out
    # v1.1.1 validation gate: skip lines missing required keys or numeric fields
    # Use original string fields from 'rec' to validate presence; if bad -> return None
    def is_float_str(s):
        try:
            float(s)
            return True
        except Exception:
            return False

    required_keys_present = all([
        rec_out["DateTime"] != "",
        rec_out["Type"] != "",
        rec_out["Station"] != ""
    ])

    numeric_ok = all([
        is_float_str(rec.get("Mag", "")),
        rec.get("Depth", "").lower().endswith("km"),
        is_float_str(rec.get("Lat", "")),
        is_float_str(rec.get("Lon", ""))
    ])

    if not (required_keys_present and numeric_ok):
        return None

def main():
    ap = argparse.ArgumentParser(description="Parse seismic-style logs to CSV/JSONL and apply a simple triage rule.")
    ap.add_argument("--in", dest="infile", required=True, help="Path to raw log (one event per line)")
    ap.add_argument("--out-csv", dest="out_csv", required=True, help="Output CSV path")
    ap.add_argument("--out-json", dest="out_json", required=True, help="Output JSONL path")
    ap.add_argument("--aoi", dest="aoi_file", default=None, help="Optional AOI JSON path")
    args = ap.parse_args()

    aois = load_aois(args.aoi_file)

    in_path = Path(args.infile)
    if not in_path.exists():
        print(f"[ERR] Input file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    flagged = 0
    total = 0

    with in_path.open() as f_in, open(args.out_json, "w") as f_json:
        for raw in f_in:
            raw = raw.strip()
            if not raw:
                continue
            rec = parse_line(raw)
            if not rec:
                continue
            total += 1
            is_flagged, reason = triage(rec, aois)
            rec["Flagged"] = bool(is_flagged)
            rec["Reasons"] = reason
            rows.append(rec)
            f_json.write(json.dumps(rec) + "\n")
            if is_flagged:
                flagged += 1

    fieldnames = ["DateTime","Station","Mag","Depth_km","Lat","Lon","Type","Flagged","Reasons"]
    with open(args.out_csv, "w", newline="") as f_csv:
        w = csv.DictWriter(f_csv, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"[OK] Parsed {total} events -> CSV: {args.out_csv}, JSONL: {args.out_json}")
    print(f"[OK] Flagged: {flagged}")

if __name__ == "__main__":
    main()
