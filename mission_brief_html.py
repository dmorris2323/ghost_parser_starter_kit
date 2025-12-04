"""
mission_brief_html.py — builds the HTML mission brief
Includes Golden Dome Tile injection
"""

import json
from pathlib import Path

from mission_briefing import build_mission_briefing
from golden_dome_tile import build_golden_dome_tile


HTML_TEMPLATE = Path("docs/mission_brief_template.html")


def write_daily_brief():
    if not HTML_TEMPLATE.exists():
        raise FileNotFoundError("Missing docs/mission_brief_template.html")

    # Raw briefing data
    brief = build_mission_briefing()

    stats = {
        "avg_reliability": brief.get("sensor_reliability", 90.0),
        "agreement_score": brief.get("owl_agreement", 85.0),
    }

    # Profile
    current_profile = brief.get("profile", {"display_name": "Unknown"})

    # Build Golden Dome Tile
    tile = build_golden_dome_tile(
        reliability=stats["avg_reliability"],
        agreement=stats["agreement_score"],
        profile=current_profile["display_name"]
    )

    html = HTML_TEMPLATE.read_text()

    # Insert Golden Dome Tile
    html = html.replace("{{GOLDEN_DOME_TILE}}", json.dumps(tile, indent=2))

    # Insert main briefing text
    html = html.replace("{{BRIEF_TEXT}}", brief.get("text_brief", ""))

    out_path = Path("docs/daily_mission_brief.html")
    out_path.write_text(html)

    return out_path


if __name__ == "__main__":
    print(write_daily_brief())

