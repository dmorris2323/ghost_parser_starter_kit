"""
fusion_minimap_overlay.py
-------------------------
Extracts the current fusion minimap and exports it into a GUI-friendly JSON file.

This allows the GUI to always show a minimap even if
- CLI minimap logic changes
- mission briefs fail
- sensors return partial data

Output:
    gui_minimap.json
"""

import json
from pathlib import Path
from datetime import datetime
from fusion_minimap import build_minimap  # your existing minimap module

OUTFILE = Path(__file__).parent / "gui_minimap.json"


def export_gui_minimap():
    """
    Build and export a clean JSON minimap dictionary for GUI consumption.
    """
    result = build_minimap()

    bundle = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "map": {},
    }

    # Convert defaultdict to normal dict
    for sector, stats in result["map"].items():
        bundle["map"][sector] = {
            "critical": stats.get("critical", 0),
            "warning": stats.get("warning", 0),
            "stable": stats.get("stable", 0),
        }

    OUTFILE.write_text(json.dumps(bundle, indent=2))
    return {
        "status": "ok",
        "file": str(OUTFILE),
        "sector_count": len(bundle["map"])
    }


if __name__ == "__main__":
    print(export_gui_minimap())

