"""
sensor_readiness_brief.py
"""

from sensor_reliability import build_reliability_table
from manifest_health import run_manifest_health

def build_readiness_brief() -> str:
    manifest = run_manifest_health()
    reliability = build_reliability_table()

    lines = []
    lines.append("=== SENSOR READINESS BRIEF ===")
    lines.append("")
    lines.append(f"Total sensors: {manifest['total']}")
    lines.append(f"Enabled: {manifest['enabled']}")
    lines.append(f"Disabled: {manifest['disabled']}")
    lines.append("")

    lines.append("=== RELIABILITY ===")
    for r in reliability:
        lines.append(f"{r['sensor'].upper():10} {r['score']}%  ({r['status']})")
    lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    print(build_readiness_brief())

