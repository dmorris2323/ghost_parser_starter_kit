from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _score_threat(level: str) -> int:
    """
    Map nuclear threat level to a numeric score.
    """
    lvl = (level or "").upper()
    if lvl == "CRITICAL":
        return 3
    if lvl == "ELEVATED":
        return 2
    if lvl == "NORMAL":
        return 1
    return 0


def build_nuclear_risk_timeline() -> Dict[str, Any]:
    """
    Build a simple nuclear risk timeline from available products.

    It looks for:
      - golden_dome_daily_watch.json
      - nuclear_decision_card.json

    and creates a small "timeline" object that can later be extended
    with historical data (e.g., archived copies with timestamps).
    For now, it builds a one-point "today" snapshot.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    watch_path = DOCS_DIR / "golden_dome_daily_watch.json"
    card_path = DOCS_DIR / "nuclear_decision_card.json"

    watch = _safe_read_json(watch_path)
    card = _safe_read_json(card_path)

    today_iso = datetime.utcnow().date().isoformat()

    watch_level = watch.get("nuclear_threat_level", "UNKNOWN")
    card_level = card.get("nuclear_threat_level", watch_level)

    watch_score = _score_threat(watch_level)
    card_score = _score_threat(card_level)

    # Simple fusion: max of the two scores
    fused_score = max(watch_score, card_score)

    entry = {
        "date": today_iso,
        "watch_level": watch_level,
        "decision_card_level": card_level,
        "fused_risk_score": fused_score,
        "source_files": {
            "watch": str(watch_path),
            "decision_card": str(card_path),
        },
    }

    timeline: List[Dict[str, Any]] = [entry]

    return {
        "product_type": "Nuclear Risk Timeline",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "entries": timeline,
        "risk_scale": {
            "0": "No data / unknown",
            "1": "Normal watch",
            "2": "Elevated nuclear vigilance",
            "3": "Critical nuclear posture",
        },
        "notes": [
            "Timeline currently contains a single 'today' entry.",
            "In future, this can be extended to append daily snapshots over time.",
        ],
    }


def write_nuclear_risk_timeline() -> Dict[str, str]:
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_nuclear_risk_timeline()

    json_path = DOCS_DIR / "nuclear_risk_timeline.json"
    txt_path = DOCS_DIR / "nuclear_risk_timeline.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines: List[str] = []
    lines.append("=== NUCLEAR RISK TIMELINE ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append("")
    for entry in data["entries"]:
        lines.append(f"Date: {entry['date']}")
        lines.append(f"  Watch level        : {entry['watch_level']}")
        lines.append(f"  Decision card level: {entry['decision_card_level']}")
        lines.append(f"  Fused risk score   : {entry['fused_risk_score']}")
        lines.append("")
    lines.append("Scale:")
    for k, v in data["risk_scale"].items():
        lines.append(f"  {k}: {v}")
    lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_nuclear_risk_timeline()
    print("Nuclear Risk Timeline written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

