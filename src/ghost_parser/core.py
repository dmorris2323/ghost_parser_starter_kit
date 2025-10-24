import json

def load_aois(aoi_json):
    if isinstance(aoi_json, dict):
        return aoi_json
    return json.loads(aoi_json)

def in_box(lat, lon, box):
    return (box["lat_min"] <= lat <= box["lat_max"]) and (box["lon_min"] <= lon <= box["lon_max"])

def _to_float(s, default=0.0):
    try:
        return float(str(s).lower().replace("km","").strip())
    except:
        return default

def parse_line(line: str):
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 2: return None
    rec = {"DateTime": parts[0]}
    for part in parts[1:]:
        if ":" in part:
            k, v = part.split(":", 1)
            rec[k.strip()] = v.strip()
    return {
        "DateTime": rec.get("DateTime",""),
        "Station":  rec.get("Station",""),
        "Mag":      _to_float(rec.get("Mag","0")),
        "Depth_km": _to_float(rec.get("Depth","0")),
        "Lat":      _to_float(rec.get("Lat","0")),
        "Lon":      _to_float(rec.get("Lon","0")),
        "Type":     rec.get("Type","")
    }

def triage(rec, aois=None, max_depth_km=2.5, min_mag=3.5, max_mag=6.5):
    aois = aois or {}
    depth_ok = rec["Depth_km"] <= max_depth_km
    mag_ok = (min_mag <= rec["Mag"] <= max_mag)
    if not (depth_ok and mag_ok):
        return False, ""
    if aois:
        for name, box in aois.items():
            if in_box(rec["Lat"], rec["Lon"], box):
                tag = "aoi+shallow+mag_range"
                if "NK" in name.upper(): tag = "nk_zone+shallow+mag_range"
                return True, tag
        return False, ""
    return True, "shallow+mag_range"

def parse_lines(lines, aois=None, **kw):
    rows, flagged = [], 0
    for ln in lines:
        ln = ln.strip()
        if not ln: continue
        rec = parse_line(ln)
        if not rec: continue
        is_flag, reason = triage(rec, aois, **kw)
        rec["Flagged"] = bool(is_flag)
        rec["Reasons"] = reason
        rows.append(rec)
        flagged += int(is_flag)
    return rows, flagged
