"""
spectral_snapshot_bundle.py

Builds a single "Spectral Snapshot Bundle" JSON file that collects:
  - Spectral dashboard bundle
  - GUI minimap overlay
  - SOS overlay
  - Run-history intel brief (text)
  - Mission brief text

Output:
  src/docs/spectral_snapshot_bundle.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


BASE = Path(__file__).parent

DASHBOARD_BUNDLE_JSON = BASE / "docs" / "spectral_dashboard_bundle.json"
MINIMAP_JSON = BASE / "gui_minimap.json"
SOS_JSON = BASE / "gui_sos_overlay.json"
RUN_HISTORY_BRIEF = BASE / "run_history_intel_brief.txt"
MISSION_BRIEF_TXT = BASE / "docs" / "daily_mission_brief.txt"
PROFILE_MISSION_BRIEF_TXT = BASE / "docs" / "profile_mission_brief.txt"

SNAPSHOT_OUT = BASE / "docs" / "spectral_snapshot_bundle.json"


def safe_load_json(path: Path) -> Any:
    """Load JSON safely; return None on any failure or missing file."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def safe_load_text(path: Path) -> str | None:
    """Load text safely; return None on any failure or missing file."""
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def build_snapshot_bundle() -> Dict[str, Any]:
    """
    Build a unified snapshot of the current GLL state for GUI/demo/export.
    This function never throws if files are missing; it simply returns what it can.
    """

    dashboard = safe_load_json(DASHBOARD_BUNDLE_JSON)
    minimap = safe_load_json(MINIMAP_JSON)
    sos = safe_load_json(SOS_JSON)
    run_history = safe_load_text(RUN_HISTORY_BRIEF)

    # Prefer profile-aware mission brief if present
    mission = safe_load_text(PROFILE_MISSION_BRIEF_TXT)
    if mission is None:
        mission = safe_load_text(MISSION_BRIEF_TXT)

    bundle: Dict[str, Any] = {
        "meta": {
            "description": "Ghost Lantern Labs — Spectral Snapshot Bundle",
            "version": "1.0",
        },
        "dashboard_bundle": dashboard,
        "minimap_overlay": minimap,
        "sos_overlay": sos,
        "run_history_brief": run_history,
        "mission_brief": mission,
    }

    SNAPSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_OUT.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    return bundle


def main() -> str:
    build_snapshot_bundle()
    return f"Spectral snapshot bundle written to: {SNAPSHOT_OUT}"


if __name__ == "__main__":
    print(main())

