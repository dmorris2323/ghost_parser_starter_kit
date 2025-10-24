# src/ghost_parser/fusion/core_fusion.py
from __future__ import annotations
import math
import pandas as pd

# --- small utilities ---

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two lat/lon points in kilometers.
    """
    R = 6371.0  # km
    try:
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlmb = math.radians(float(lon2) - float(lon1))
    except Exception:
        return float("nan")
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _coerce_time_lat_lon(df: pd.DataFrame, tcol: str, lat: str, lon: str) -> pd.DataFrame:
    """
    Return a copy with parsed datetime and numeric lat/lon; drops rows missing any of the three.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    out = df.copy()
    out[tcol] = pd.to_datetime(out[tcol], errors="coerce", utc=True)
    out[lat]  = pd.to_numeric(out[lat], errors="coerce")
    out[lon]  = pd.to_numeric(out[lon], errors="coerce")
    out = out.dropna(subset=[tcol, lat, lon]).sort_values(tcol)
    return out


def fuse_sources(
    seismic_df: pd.DataFrame,
    rf_df: pd.DataFrame,
    time_tolerance: str = "10min",
    max_delta_deg: float = 0.5,
    # column names in the inputs
    time_col_log: str = "DateTime",
    lat_log: str = "Lat",
    lon_log: str = "Lon",
    time_col_rf: str = "DateTime",
    lat_rf: str = "Lat",
    lon_rf: str = "Lon",
) -> pd.DataFrame:
    """
    Time-nearest fuse of seismic (log) and RF (em) observations with simple spatial screen.
    Produces Distance_km, Match_confidence, Confidence_label, Correlates.

    Returns a DataFrame with:
      Station (if present), RadarID (if present), t_log, t_rf,
      lat_log, lon_log, lat_rf, lon_rf,
      Delta_time_s, Delta_lat, Delta_lon,
      Distance_km, Match_confidence, Confidence_label, Correlates
    """
    # 1) Coerce + sort
    log = _coerce_time_lat_lon(seismic_df, time_col_log, lat_log, lon_log)
    em  = _coerce_time_lat_lon(rf_df,       time_col_rf,  lat_rf,  lon_rf)
    if log.empty or em.empty:
        return pd.DataFrame()

    # Preserve IDs if present
    station_col = "Station" if "Station" in log.columns else None
    radar_col   = "RadarID" if "RadarID" in em.columns else None

    # 2) Rename so we have clear left/right coordinates + times
    log_ren = log.rename(columns={
        time_col_log: "t_log",
        lat_log: "lat_log",
        lon_log: "lon_log"
    })
    em_ren = em.rename(columns={
        time_col_rf: "t_rf",
        lat_rf: "lat_rf",
        lon_rf: "lon_rf"
    })

    # 3) As-of merge by time (nearest within tolerance)
    tol = pd.Timedelta(time_tolerance)
    merged = pd.merge_asof(
        log_ren.sort_values("t_log"),
        em_ren.sort_values("t_rf"),
        left_on="t_log",
        right_on="t_rf",
        direction="nearest",
        tolerance=tol
    )

    # Drop rows that failed to find a time-near partner
    merged = merged.dropna(subset=["t_rf"]).copy()
    if merged.empty:
        return merged

    # 4) Compute deltas
    merged["Delta_time_s"] = (merged["t_rf"] - merged["t_log"]).dt.total_seconds().abs()
    merged["Delta_lat"]    = (merged["lat_log"] - merged["lat_rf"]).abs()
    merged["Delta_lon"]    = (merged["lon_log"] - merged["lon_rf"]).abs()

    # 5) Distance + confidence
    merged["Distance_km"] = merged.apply(
        lambda r: haversine(r["lat_log"], r["lon_log"], r["lat_rf"], r["lon_rf"]),
        axis=1
    )
    # Simple score: farther = lower confidence (5 km -> -25 points)
    merged["Match_confidence"] = (100 - (merged["Distance_km"] * 5)).clip(lower=0, upper=100)

    def _bucket(v: float) -> str:
        try:
            v = float(v)
        except Exception:
            return "Low"
        if v >= 80: return "High"
        if v >= 50: return "Medium"
        return "Low"

    merged["Confidence_label"] = merged["Match_confidence"].apply(_bucket)

    # 6) Simple correlate decision (time + spatial windows)
    merged["Correlates"] = (
        (merged["Delta_time_s"] <= tol.total_seconds()) &
        (merged["Delta_lat"]    <= max_delta_deg) &
        (merged["Delta_lon"]    <= max_delta_deg)
    )

    # 7) Order useful columns
    cols = [
        c for c in [
            station_col, "t_log", "lat_log", "lon_log",
            radar_col,   "t_rf",  "lat_rf",  "lon_rf",
            "Delta_time_s", "Delta_lat", "Delta_lon",
            "Distance_km", "Match_confidence", "Confidence_label", "Correlates"
        ] if c is not None
    ]
    return merged[cols].reset_index(drop=True)

