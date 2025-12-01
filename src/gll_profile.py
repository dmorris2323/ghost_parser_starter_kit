"""
gll_profile.py — Ghost Lantern Labs
-----------------------------------
Holds the active configuration profile for GLL and simple helpers.

Profiles themselves are defined in config_profiles.py.
"""

from typing import Dict, Any
from config_profiles import get_profile, list_profiles

# Change this when you want a different default deployment mode.
# Options: "aftac_nuclear", "sports_team", "law_firm", "commercial_soc"
GLL_ACTIVE_PROFILE = "aftac_nuclear"


def get_active_profile_name() -> str:
    return GLL_ACTIVE_PROFILE


def get_active_profile() -> Dict[str, Any]:
    return get_profile(GLL_ACTIVE_PROFILE)


def get_available_profiles() -> Dict[str, str]:
    return list_profiles()


def main():
    name = get_active_profile_name()
    profile = get_active_profile()
    print(f"Active profile: {name}")
    if not profile:
        print("Profile not defined.")
        return
    print(f"Description: {profile.get('description', 'N/A')}")
    print(f"Domains: {', '.join(profile.get('domains', []))}")
    print(f"Threat types: {', '.join(profile.get('default_threat_types', []))}")
    print(f"Offline priority: {profile.get('offline_priority', False)}")
    sev = profile.get("severity_labels", {})
    if sev:
        print("Severity labels:")
        for k, v in sev.items():
            print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()

