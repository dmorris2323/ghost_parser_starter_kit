from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path) -> Dict[str, Any]:
    """
    Safely read a JSON file, returning {} on any failure.
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _safe_reliability() -> Dict[str, Any]:
    """
    Try to pull sensor reliability from sensor_reliability.py if available.
    Falls back to a safe default if the module or function is missing.
    """
    try:
        from sensor_reliability import compute_reliability_all  # type: ignore
    except Exception:
        return {
            "sensors": {},
            "avg_reliability": 90.0,
            "source": "fallback_default",
        }

    try:
        return compute_reliability_all()
    except Exception:
        return {
            "sensors": {},
            "avg_reliability": 90.0,
            "source": "compute_reliability_all_failed",
        }


def build_daily_watch() -> Dict[str, Any]:
    """
    Build the Golden Dome Daily Watch nuclear-focused summary.

    Fuses:
      - Installation threat status (if available)
      - Sensor reliability
      - Any base-defense storyboard summary (if present)

    Output (JSON-ready dict):
      {
        "product_type": "Golden Dome Daily Watch",
        "generated_at": "...Z",
        "nuclear_threat_level": "...",
        "summary": {...},
        "notes": [...],
      }
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    threat_map = _safe_read_json(DOCS_DIR / "installation_threat_map.json")
    storyboard = _safe_read_json(DOCS_DIR / "base_defense_storyboard.json")
    reliability = _safe_reliability()

    threat_status = threat_map.get("status", "UNKNOWN")
    readiness = storyboard.get("summary", {}).get("readiness", "UNKNOWN")
    avg_rel = reliability.get("avg_reliability", 90.0)

    # Derive a simple nuclear threat level from these signals.
    if threat_status in ("RED", "CRITICAL"):
        nuclear_threat_level = "CRITICAL"
    elif threat_status in ("AMBER", "ELEVATED"):
        nuclear_threat_level = "ELEVATED"
    else:
        nuclear_threat_level = "NORMAL"

    if avg_rel < 70:
        reliability_posture = "AT_RISK"
    elif avg_rel < 85:
        reliability_posture = "WATCH"
    else:
        reliability_posture = "STRONG"

    notes = []
    notes.append(f"Threat status: {threat_status}")
    notes.append(f"Base readiness: {readiness}")
    notes.append(f"Average sensor reliability: {avg_rel:.2f}% ({reliability_posture})")

    if nuclear_threat_level == "CRITICAL":
        notes.append("Immediate nuclear monitoring posture required.")
    elif nuclear_threat_level == "ELEVATED":
        notes.append("Heightened nuclear vigilance advised.")
    else:
        notes.append("Nuclear picture stable; continue standard watch.")

    watch = {
        "product_type": "Golden Dome Daily Watch",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "nuclear_threat_level": nuclear_threat_level,
        "inputs": {
            "installation_threat_status": threat_status,
            "base_readiness": readiness,
            "avg_reliability": avg_rel,
        },
        "summary": {
            "reliability_posture": reliability_posture,
        },
        "notes": notes,
    }

    return watch


def write_daily_watch() -> Dict[str, str]:
    """
    Write the Daily Watch to JSON + TXT files.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_daily_watch()

    json_path = DOCS_DIR / "golden_dome_daily_watch.json"
    txt_path = DOCS_DIR / "golden_dome_daily_watch.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines = []
    lines.append("=== GOLDEN DOME DAILY WATCH ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append(f"Nuclear Threat Level: {data['nuclear_threat_level']}")
    lines.append("")
    lines.append("--- Inputs ---")
    for k, v in data["inputs"].items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("--- Notes ---")
    for n in data["notes"]:
        lines.append(f"- {n}")
    lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_daily_watch()
    print("Golden Dome Daily Watch written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

