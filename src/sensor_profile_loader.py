"""
sensor_profile_loader.py
------------------------

Loads sensor profiles from /sensor_profiles/*.json

Used by:
 - ingest tuning
 - readiness brief
 - mission briefing enhancements
 - GUI (future)
"""

import json
from pathlib import Path

BASE = Path(__file__).parent / "sensor_profiles"


def load_profile(sensor_name: str):
    """
    Load a sensor profile JSON by name.
    Example:
        load_profile("optical")
    """

    path = BASE / f"{sensor_name}_profile.json"

    if not path.exists():
        return None

    try:
        return json.loads(path.read_text())
    except Exception as e:
        return {"error": str(e), "sensor_name": sensor_name}


def list_all_profiles():
    """
    Returns a list of all available sensor names.
    Example:
        ["optical", "seismic", "ems", "radiation"]
    """
    profiles = []

    for f in BASE.glob("*_profile.json"):
        stem = f.stem  # e.g., optical_profile
        name = stem.replace("_profile", "")
        profiles.append(name)

    return sorted(profiles)


# Run test when executed directly
if __name__ == "__main__":
    print("=== SENSOR PROFILE LOADER TEST ===")
    print("Available profiles:", list_all_profiles())
    print()

    for p in list_all_profiles():
        print(f"--- {p.upper()} PROFILE ---")
        print(load_profile(p))
        print()

