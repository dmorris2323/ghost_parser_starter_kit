"""
gui_screenshot_export.py
------------------------
Exports GUI + CLI artifacts into a single /screenshots/ folder
for demo decks (Day 100, Shari demo, conferences, etc.)
"""

import os
from pathlib import Path
import shutil
from datetime import datetime

BASE = Path(__file__).resolve().parent
OUT = BASE / "screenshots"

FILES = {
    "mission_brief_html": BASE / "docs" / "daily_mission_brief.html",
    "minimap": BASE / "gui_minimap.json",
    "sos_overlay": BASE / "gui_sos_overlay.json",
    "operator_snapshot": BASE / "operator_snapshot.txt",
    "threat_memory_summary": BASE / "threat_memory_summary.txt",
}

def export_screenshots():
    OUT.mkdir(exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    exported = []

    for label, fp in FILES.items():
        if fp.exists():
            target = OUT / f"{label}_{timestamp}.txt"
            shutil.copy(fp, target)
            exported.append(str(target))
        else:
            exported.append(f"{label}: [MISSING]")

    bundle = OUT / f"bundle_{timestamp}.txt"
    bundle.write_text("\n".join(exported))

    return {
        "status": "ok",
        "exported": exported,
        "bundle": str(bundle)
    }

if __name__ == "__main__":
    print(export_screenshots())

