from ghost_parser import parse_lines

def test_parses_valid_line_and_flags_in_aoi():
    lines = [
        "2025-10-25T10:00:00Z | Station: PS100 | Mag: 4.2 | Depth: 1.0km | Lat: 40.200 | Lon: 129.200 | Type: event"
    ]
    aois = {
        "NK_AOI": {"lat_min":39.0, "lat_max":41.0, "lon_min":128.0, "lon_max":130.0}
    }
    rows = parse_lines(lines, aois, max_depth_km=2.5, min_mag=3.5, max_mag=6.5)
    assert len(rows) == 1
    r = rows[0]
    assert r["Flagged"] is True
    assert "mag_range" in r["Reasons"]

def test_skips_garbage_line():
    lines = ["This is not a valid line at all"]
    aois = {}
    rows = parse_lines(lines, aois, 2.5, 3.5, 6.5)
    # parse_lines ignores lines it can't understand
    assert len(rows) == 0
