"""
daily_mission_brief.py
----------------------

Builds a daily mission brief that includes:

 - Core system / fusion status (mission_briefing)
 - Sensor readiness overview (sensor_readiness_brief)
 - Active profile overview (profile_status)

Output:
 - Prints to stdout
 - Writes to: docs/daily_mission_brief.txt
"""

from datetime import datetime
from pathlib import Path

from mission_briefing import build_mission_briefing
from sensor_readiness_brief import build_readiness_brief
from profile_status import build_profile_status


OUTPUT_PATH = Path("docs/daily_mission_brief.txt")


def build_daily_brief() -> str:
    lines = []

    # Header
    lines.append("=== GHOST LANTERN LABS — DAILY MISSION BRIEF ===")
    lines.append(f"Generated (UTC): {datetime.utcnow().isoformat()}")
    lines.append("")

    # Core mission brief (system + fusion status)
    lines.append("=== CORE MISSION STATUS ===")
    lines.append(build_mission_briefing())
    lines.append("")

    # Sensor readiness overview
    lines.append("=== SENSOR READINESS OVERVIEW ===")
    lines.append(build_readiness_brief())
    lines.append("")

    # Active profile status
    lines.append("=== ACTIVE PROFILE STATUS ===")
    lines.append(build_profile_status())
    lines.append("")

    return "\n".join(lines)


def write_daily_brief():
    brief = build_daily_brief()

    # Ensure docs/ exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(brief, encoding="utf-8")
    print(f"[OK] Daily mission brief written → {OUTPUT_PATH}")
    print()
    print(brief)


if __name__ == "__main__":
    write_daily_brief()

