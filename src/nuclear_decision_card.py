"""
nuclear_decision_card.py — Nuclear Decision Card
------------------------------------------------
Produces a one-page, commander-grade decision card for nuclear readiness.

Output:
  - src/docs/nuclear_decision_card.txt
"""

from pathlib import Path
from datetime import datetime, timezone
import json

from golden_dome_snapshot import build_snapshot
from fusion_trust import compute_trust
from crisis_mode_flag import status as crisis_status

BASE = Path(__file__).resolve().parent.parent  # /parser_starter_kit
SRC = BASE / "src"
DOCS = SRC / "docs"

OUT_TXT = DOCS / "nuclear_decision_card.txt"


def write_decision_card() -> str:
    """Write the nuclear decision card and return its path."""
    DOCS.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()
    snapshot = build_snapshot()
    trust = compute_trust()
    crisis = crisis_status()

    readiness = snapshot.get("readiness_level", snapshot.get("status", "UNKNOWN"))
    heat_index = snapshot.get("fusion_heat_index", "n/a")

    lines = []
    lines.append("===== NUCLEAR DECISION CARD — GHOST LANTERN LABS =====")
    lines.append(f"Generated at (UTC): {ts}")
    lines.append("")
    lines.append(f"Crisis Mode: {crisis}")
    lines.append(f"Golden Dome Readiness: {readiness}")
    lines.append(f"Fusion Heat Index: {heat_index}")
    lines.append("")
    lines.append("Fusion Trust Score:")
    lines.append(json.dumps(trust, indent=2))
    lines.append("")
    lines.append("Raw Nuclear Snapshot Payload:")
    lines.append(json.dumps(snapshot, indent=2))
    lines.append("")
    lines.append("Notes:")
    lines.append(" - This card is for rapid commander situational awareness.")
    lines.append(" - It summarizes GLL's nuclear readiness view, not final authority.")
    lines.append("")

    OUT_TXT.write_text("\n".join(lines))
    return str(OUT_TXT)


if __name__ == "__main__":
    print(write_decision_card())

