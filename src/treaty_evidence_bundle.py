"""
treaty_evidence_bundle.py — Treaty Evidence Bundle
--------------------------------------------------
Packages key GLL outputs into a single JSON descriptor for treaty / audit use.

Output:
  - src/docs/treaty_evidence_bundle.json
"""

from pathlib import Path
from datetime import datetime, timezone
import json

BASE = Path(__file__).resolve().parent.parent  # /parser_starter_kit
SRC = BASE / "src"
DOCS = SRC / "docs"

OUT_JSON = DOCS / "treaty_evidence_bundle.json"


def build_treaty_bundle() -> str:
    """Build the treaty evidence bundle descriptor and return its JSON path."""
    DOCS.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()

    candidates = [
        ("daily_mission_brief.html", DOCS / "daily_mission_brief.html"),
        ("daily_mission_brief.txt", DOCS / "daily_mission_brief.txt"),
        ("golden_dome_drift_report.txt", DOCS / "golden_dome_drift_report.txt"),
        ("golden_dome_daily_watch.json", DOCS / "golden_dome_daily_watch.json"),
        ("nuclear_decision_card.txt", DOCS / "nuclear_decision_card.txt"),
        ("gll_readiness.txt", DOCS / "gll_readiness.txt"),
        ("system_integrity_report.txt", DOCS / "system_integrity_report.txt"),
        ("prelaunch_watchboard.json", DOCS / "prelaunch_watchboard.json"),
        ("scenario_pack_latest.json", DOCS / "scenario_pack_latest.json"),
    ]

    files = []
    for name, path in candidates:
        files.append(
            {
                "name": name,
                "path": str(path),
                "exists": path.exists(),
            }
        )

    payload = {
        "generated_at": ts,
        "bundle_name": "GLL Treaty Evidence Bundle",
        "description": (
            "Collection of mission briefs and nuclear readiness artifacts suitable "
            "for treaty / audit workflows."
        ),
        "files": files,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2))
    return str(OUT_JSON)


if __name__ == "__main__":
    print(build_treaty_bundle())

