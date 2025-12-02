"""
sensor_readiness_brief.py
-------------------------

Creates a readiness summary of:
 - Enabled sensors
 - Their descriptions
 - Their thresholds
"""

from manifest_health import run_manifest_health
from sensor_profile_loader import load_profile


def build_readiness_brief():
    mh = run_manifest_health()

    lines = []
    lines.append("=== SENSOR READINESS BRIEF ===")
    lines.append(f"Total sensors: {mh['total']}")
    lines.append(f"Enabled: {mh['enabled']}")
    lines.append(f"Disabled: {mh['disabled']}")
    lines.append("")

    for sensor in mh["enabled"]:
        p = load_profile(sensor)
        if not p:
            lines.append(f"[{sensor.upper()}]")
            lines.append("  No profile found.\n")
            continue

        lines.append(f"[{sensor.upper()}]")
        lines.append(f"  Description: {p['description']}")
        lines.append(f"  Warning threshold: {p['warning_threshold']}")
        lines.append(f"  Critical threshold: {p['critical_threshold']}")
        lines.append(f"  Notes: {p.get('notes', '')}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_readiness_brief())

