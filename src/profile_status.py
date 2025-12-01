"""
profile_status.py — Ghost Lantern Labs
--------------------------------------
Shows the active profile and its key settings in a human-readable way.
"""

from gll_profile import get_active_profile_name, get_active_profile


def build_profile_status() -> str:
    name = get_active_profile_name()
    profile = get_active_profile()

    if not profile:
        return f"Active profile: {name} (UNKNOWN / not defined)"

    lines = []
    lines.append(f"Active profile: {name}")
    lines.append(f"Description: {profile.get('description', 'N/A')}")
    domains = profile.get("domains", [])
    if domains:
        lines.append(f"Domains: {', '.join(domains)}")
    threats = profile.get("default_threat_types", [])
    if threats:
        lines.append(f"Default threat types: {', '.join(threats)}")
    lines.append(f"Offline priority: {profile.get('offline_priority', False)}")
    sev = profile.get("severity_labels", {})
    if sev:
        lines.append("Severity labels:")
        for k, v in sev.items():
            lines.append(f"  - {k}: {v}")

    return "\n".join(lines)


def main():
    print(build_profile_status())


if __name__ == "__main__":
    main()

