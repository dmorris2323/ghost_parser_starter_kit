"""
demo_gui_pack.py
----------------

Builds a full GUI-ready demo pack in one shot:

 - Ensures daily mission brief TXT exists
 - Builds HTML mission brief (with profile badge + minimap panel)
 - Builds/refreshes Fusion Mini-Map TXT
 - Builds/refreshes Fusion Mini-Map PNG
 - Builds profile-aware mission brief TXT

Outputs (all relative to src/):
 - docs/daily_mission_brief.txt
 - docs/daily_mission_brief.html
 - docs/profile_mission_brief.txt
 - minimap.txt
 - minimap.png
"""

from __future__ import annotations

from pathlib import Path

from daily_mission_brief import write_daily_brief
from mission_brief_html import write_html_brief
from fusion_minimap import build_minimap
from fusion_minimap_png import main as build_minimap_png
from profile_mission_brief import write_profile_brief


def build_gui_demo_pack() -> dict:
    """
    Build the full GUI demo pack and return a summary dict.
    """

    # Ensure base text brief
    write_daily_brief()

    # Build HTML brief (includes profile badge + minimap panel)
    write_html_brief()

    # Build minimap.txt and minimap.png
    mm_result = build_minimap()
    png_result = build_minimap_png()

    # Build profile-aware brief
    write_profile_brief()

    base = Path(__file__).parent

    summary = {
        "status": "ok",
        "artifacts": {
            "daily_brief_txt": str(base / "docs" / "daily_mission_brief.txt"),
            "daily_brief_html": str(base / "docs" / "daily_mission_brief.html"),
            "profile_brief_txt": str(base / "docs" / "profile_mission_brief.txt"),
            "minimap_txt": str(base / "minimap.txt"),
            "minimap_png": str(base / "minimap.png"),
        },
        "minimap_status": mm_result,
        "minimap_png_status": png_result,
    }

    return summary


def main():
    result = build_gui_demo_pack()
    print("[OK] GUI demo pack built.")
    print("Artifacts:")
    for k, v in result["artifacts"].items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()

