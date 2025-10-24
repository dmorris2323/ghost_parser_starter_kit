# src/ghost_parser/__init__.py
from __future__ import annotations
import json
from typing import List, Dict

def load_aois(path: str | None) -> dict:
    """Load AOI boxes from a JSON file (or return empty dict)."""
    if not path:
        return {}
    import os
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_lines(
    lines: List[str],
    aois: dict | None = None,
    max_depth_km: float = 2.5,
    min_mag: float = 3.5,
    max_mag: float = 6.5
) -> List[Dict]:
    """
    Parse raw log lines and triage (flag) based on AOI + depth + magnitude.

    Args:
        lines: list of raw 'YYYY... | Station: ... | Mag: ... | Depth: ...km | Lat: ... | Lon: ... | Type: ...'
        aois: dict of AOI boxes, e.g. {"NK": {"lat_min":39,"lat_max":41,"lon_min":128,"lon_max":130}}
        max_depth_km: depth threshold (<= flags as shallow)
        min_mag: minimum magnitude to consider for flag
        max_mag: maximum magnitude to consider for flag

    Returns:
        List of dict rows with fields:
        DateTime, Station, Mag, Depth_km, Lat, Lon, Type, Flagged (bool), Reasons (str)
    """
    if aois is None:
        aois = {}

    def in_box(lat: float, lon: float, box: dict) -> bool:
        return (box["lat_min"] <= lat <= box["lat_max"]) and (box["lon_min"] <= lon <= box["lon_max"])

    def to_float(s, default=0.0) -> float:
        try:
            return float(str(s).lower().replace("km", "").strip())
        except Exception:
            return default

    rows: List[Dict] = []
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        rec = {"DateTime": parts[0]}
        for part in parts[1:]:
            if ":" in part:
                k, v = part.split(":", 1)
                rec[k.strip()] = v.strip()

        row = {
            "DateTime": rec.get("DateTime", ""),
            "Station":  rec.get("Station", ""),
            "Mag":      to_float(rec.get("Mag", "0")),
            "Depth_km": to_float(rec.get("Depth", "0")),
            "Lat":      to_float(rec.get("Lat", "0")),
            "Lon":      to_float(rec.get("Lon", "0")),
            "Type":     rec.get("Type", ""),
        }

        # Apply thresholds
        depth_ok = row["Depth_km"] <= max_depth_km
        mag_ok   = (min_mag <= row["Mag"] <= max_mag)

        flagged = False
        reason  = ""
        if depth_ok and mag_ok:
            if aois:
                # Flag only if inside any AOI
                for name, box in aois.items():
                    if in_box(row["Lat"], row["Lon"], box):
                        reason  = "nk_zone+shallow+mag_range" if "NK" in name.upper() else "aoi+shallow+mag_range"
                        flagged = True
                        break
            else:
                # No AOIs provided — global shallow+mag window
                flagged = True
                reason  = "shallow+mag_range"

        row["Flagged"] = flagged
        row["Reasons"] = reason
        rows.append(row)

    return rows

