import re

def validate_line(line: str) -> bool:
    """
    Validate raw seismic/log line format.
    Expected: ISO timestamp + Station + Mag + Depth + Lat + Lon
    """
    pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\s+\|\s+Station:\s+PS\d{3}\s+\|"
    )
    return bool(pattern.match(line))

def validate_numeric_fields(rec: dict) -> bool:
    """Check if numeric fields are in reasonable ranges."""
    try:
        return (
            0.0 <= rec.get("Depth_km", 0) <= 700.0 and
            0.0 <= rec.get("Mag", 0) <= 10.0 and
            -90.0 <= rec.get("Lat", 0) <= 90.0 and
            -180.0 <= rec.get("Lon", 0) <= 180.0
        )
    except Exception:
        return False

