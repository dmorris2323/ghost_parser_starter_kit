"""
daily_mission_brief.py
"""

from pathlib import Path
from datetime import datetime
from profile_config import get_active_profile
from sensor_reliability import build_reliability_table
from sensor_readiness_brief import build_readiness_brief

def build_mission_brief() -> str:
    profile = get_active_profile()

    lines = []
    lines.append("=== DAILY MISSION BRIEF ===")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append(f"Active Profile: {profile.display_name}")
    lines.append("")

    lines.append("=== SENSOR RELIABILITY ===")
    for r in build_reliability_table():
        lines.append(f"{r['sensor'].upper():10} {r['score']}% ({r['status']})")
    lines.append("")

    lines.append(build_readiness_brief())
    return "\n".join(lines)

def write_daily_brief():
    text = build_mission_brief()
    out = Path(__file__).parent / "docs" / "daily_mission_brief.txt"
    out.write_text(text, encoding="utf-8")
    return out

if __name__ == "__main__":
    print(write_daily_brief())

