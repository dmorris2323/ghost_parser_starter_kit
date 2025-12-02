"""
ingest_tuning.py
----------------

This module pulls sensor thresholds from the JSON profiles
so ingest and scoring can adapt to customer configurations.

Used by:
 - fusion_ingest.py
 - sensor readiness brief
 - future GUI tuning panel
"""

from sensor_profile_loader import load_profile


def get_thresholds(sensor_name: str):
    """
    Returns threshold dict for a given sensor.
    Example:
        get_thresholds("optical")
        -> {"critical": 0.85, "warning": 0.55}
    """

    profile = load_profile(sensor_name)

    if not profile:
        return None

    return {
        "critical": profile.get("critical_threshold"),
        "warning": profile.get("warning_threshold"),
        "notes": profile.get("notes", "")
    }


def get_sensor_description(sensor_name: str):
    """
    Returns the human-readable description for GUI and briefings.
    """

    profile = load_profile(sensor_name)
    if not profile:
        return "No profile found."

    return profile.get("description", "No description available.")


# Self-test when run directly
if __name__ == "__main__":
    print("=== INGEST TUNING SELF-TEST ===")
    sensors = ["optical", "seismic", "ems", "radiation"]

    for s in sensors:
        print(f"\n--- {s.upper()} ---")
        print(get_thresholds(s))
        print(get_sensor_description(s))

