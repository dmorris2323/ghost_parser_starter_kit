"""
demo_deck_manifest.py
---------------------
Builds a JSON manifest listing all demo-ready assets that should appear
in your Ghost Lantern Labs Day 58 / Day 100 Demo Deck.

This allows the GUI, CLI, and future web dashboard to know exactly
which files to pull into slides, marketing decks, mission brief
overviews, or investor-style previews.

Output:
    docs/demo_deck_manifest_day58.json
"""

import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"
OUT = DOCS / "demo_deck_manifest_day58.json"


def collect_demo_assets():
    """
    Collects structured metadata about your live system:
      • Fusion outputs
      • Sensor outputs
      • Spectral Owl memory
      • Threat memory
      • Minimap overlays
      • SOS overlays
      • Daily mission briefs
      • Stress-test artifacts
      • Operator snapshots
      • Profile-aware mission brief
    """

    assets = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "system": {
            "fusion_outputs": [
                str((BASE / "fused_output.csv").resolve()),
                str((BASE / "data" / "fused_output.csv").resolve())
            ],
            "scored_outputs": [
                str((BASE / "scored_output.csv").resolve()),
                str((BASE / "data" / "scored_output.csv").resolve())
            ],
            "sensor_ingest": [
                str((BASE / "data" / "sensor_ingest.csv").resolve())
            ],
            "operator_snapshot": [
                str((BASE / "operator_snapshot.txt").resolve()),
                str((BASE / "demos" / "day56" / "operator_snapshot_day56.txt").resolve())
            ],
            "minimap": [
                str((BASE / "gui_minimap.json").resolve())
            ],
            "sos_overlay": [
                str((BASE / "gui_sos_overlay.json").resolve())
            ],
            "threat_memory": [
                str((BASE / "spectral_owl" / "threat_memory.py").resolve()),
                str((BASE / "data" / "threat_memory.csv").resolve())
            ],
            "mission_briefs": [
                str((BASE / "docs" / "daily_mission_brief.html").resolve()),
                str((BASE / "docs" / "daily_mission_brief.txt").resolve()),
                str((BASE / "docs" / "profile_mission_brief.txt").resolve())
            ],
            "stress_test": [
                str((BASE / "stress_test.py").resolve()),
                str((BASE / "data" / "stress_test_last_run.txt").resolve())
            ],
            "fusion_health": [
                str((BASE / "pipeline_health.txt").resolve()),
                str((BASE / "sensor_health.py").resolve())
            ]
        },
        "demos": {
            "day54_demo": str((BASE / "demos" / "day54").resolve()),
            "day56_demo": str((BASE / "demos" / "day56").resolve()),
            "family_law_demo": str((BASE / "demos" / "family_law_demo").resolve())
        },
        "profiles": {
            "active_profile": str((BASE / "config" / "profile.txt").resolve()),
            "profiles_folder": str((BASE / "config_profiles.py").resolve())
        }
    }

    return assets


def build_demo_deck_manifest():
    """
    Wrapper used by ghost_cli Option 23.
    Builds the manifest JSON and returns a status string.
    """
    assets = collect_demo_assets()
    DOCS.mkdir(exist_ok=True, parents=True)
    OUT.write_text(json.dumps(assets, indent=4))
    return f"[OK] Demo Deck Manifest built → {OUT}"


def main():
    # Keep CLI/terminal usage working too.
    print(build_demo_deck_manifest())


if __name__ == "__main__":
    main()

