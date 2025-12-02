"""
daily_mission_brief.py — Ghost Lantern Labs
-------------------------------------------

Synthesizes multiple GLL outputs into a single daily "mission brief"
for the operator / commander.

Inputs (if present):
- data/run_history.csv           (from sensor_run_history.py)
- data/threat_levels.csv         (from threat_level_classifier.py)
- sensor_health_report.txt       (from sensor_health.py)

Reuses:
- daily_sensor_brief.build_brief()
- threat_timeline_brief.build_brief()
- analyst_notes.build_notes()

Output:
- docs/daily_mission_brief.txt   (human-readable text brief)

This is an ISR-style brief artifact suitable for demos.
"""

from __future__ import annotations

from pathlib import Path

from daily_sensor_brief import load_run_history, build_brief as build_sensor_brief
from threat_timeline_brief import load_threat_levels, build_brief as build_threat_brief
from analyst_notes import build_notes as build_analyst_notes


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(exist_ok=True, parents=True)

SENSOR_HEALTH_PATH = BASE_DIR / "sensor_health_report.txt"
MISSION_BRIEF_PATH = DOCS_DIR / "daily_mission_brief.txt"


def read_sensor_health() -> str:
    """
    Return the contents of sensor_health_report.txt if it exists,
    otherwise a simple note.
    """
    if not SENSOR_HEALTH_PATH.exists():
        return "No sensor health report available. Run sensor_health.py to generate one."
    return SENSOR_HEALTH_PATH.read_text(encoding="utf-8")


def build_mission_brief() -> str:
    """
    Construct the full daily mission brief as a string.
    """
    lines: list[str] = []
    lines.append("===== GLL DAILY MISSION BRIEF =====")
    lines.append("")

    # 1. Sensor Layer Summary (from run_history)
    run_rows = load_run_history()
    sensor_summary = build_sensor_brief(run_rows)
    lines.append(">> SENSOR LAYER SUMMARY")
    lines.append(sensor_summary)
    lines.append("")

    # 2. Threat Timeline Overview (from threat_levels)
    threat_rows = load_threat_levels()
    threat_summary = build_threat_brief(threat_rows)
    lines.append(">> THREAT TIMELINE OVERVIEW")
    lines.append(threat_summary)
    lines.append("")

    # 3. Sensor Health Snapshot (from sensor_health_report.txt)
    health_text = read_sensor_health()
    lines.append(">> SENSOR HEALTH SNAPSHOT")
    lines.append(health_text)
    lines.append("")

    # 4. Analyst Notes (rule-based)
    lines.append(">> ANALYST NOTES")
    notes = build_analyst_notes()
    lines.append(notes)
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    brief = build_mission_brief()
    MISSION_BRIEF_PATH.write_text(brief, encoding="utf-8")
    print("✅ Daily mission brief generated.")
    print(f"   Path: {MISSION_BRIEF_PATH}")
    print("\n----- BRIEF PREVIEW -----\n")
    print(brief)


if __name__ == "__main__":
    main()

