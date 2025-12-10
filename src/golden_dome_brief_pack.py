from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from golden_dome_daily_watch import build_daily_watch
from nuclear_decision_card import build_decision_card
from treaty_evidence_bundle import build_treaty_evidence_bundle


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def build_golden_dome_brief_pack() -> Dict[str, Any]:
    """
    Build an all-in-one Golden Dome nuclear brief pack.

    Fuses:
      - Daily Watch
      - Nuclear Decision Card
      - Treaty Evidence Bundle
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    watch = build_daily_watch()
    card = build_decision_card()
    bundle = build_treaty_evidence_bundle()

    pack = {
        "product_type": "Golden Dome Nuclear Brief Pack",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "watch": watch,
        "decision_card": card,
        "treaty_evidence_bundle": bundle,
    }

    return pack


def write_golden_dome_brief_pack() -> Dict[str, str]:
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_golden_dome_brief_pack()

    json_path = DOCS_DIR / "golden_dome_brief_pack.json"
    txt_path = DOCS_DIR / "golden_dome_brief_pack.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines = []
    lines.append("=== GOLDEN DOME NUCLEAR BRIEF PACK ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append("")
    lines.append("Includes:")
    lines.append("  • Golden Dome Daily Watch")
    lines.append("  • Nuclear Decision Card")
    lines.append("  • Treaty Evidence Bundle")
    lines.append("")
    lines.append("See JSON for full detail:")
    lines.append(f"  {json_path}")
    lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_golden_dome_brief_pack()
    print("Golden Dome Nuclear Brief Pack written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

