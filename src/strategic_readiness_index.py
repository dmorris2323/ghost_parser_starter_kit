from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _score_nuclear_level(level: str) -> int:
    lvl = (level or "").upper()
    if lvl == "CRITICAL":
        return 40
    if lvl == "ELEVATED":
        return 75
    if lvl == "NORMAL":
        return 90
    return 60  # unknown → conservative mid score


def build_strategic_readiness_index() -> Dict[str, Any]:
    """
    Compute a 0–100 Strategic Readiness Index, fusing:

      - Nuclear posture (from Nuclear Decision Card / Golden Dome Watch)
      - Sensor reliability (from reliability report)
      - Base-defense posture (hotspots)
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    watch = _safe_read_json(DOCS_DIR / "golden_dome_daily_watch.json")
    card = _safe_read_json(DOCS_DIR / "nuclear_decision_card.json")
    reliability = _safe_read_json(DOCS_DIR / "sensor_reliability_report.json")
    hotspots = _safe_read_json(DOCS_DIR / "base_defense_hotspots.json")

    # Nuclear score
    nuclear_level = card.get("nuclear_threat_level") or watch.get("nuclear_threat_level", "UNKNOWN")
    nuclear_score = _score_nuclear_level(nuclear_level)

    # Reliability score (0–100)
    avg_rel = reliability.get("avg_reliability") or reliability.get("Average Reliability") or 90.0
    try:
        rel_score = float(avg_rel)
    except Exception:
        rel_score = 90.0

    # Base-defense score: penalize for hotspots
    hotspots_list = hotspots.get("hotspots", [])
    if isinstance(hotspots_list, list) and hotspots_list:
        worst_risk = max(h.get("risk_score", 0) for h in hotspots_list if isinstance(h, dict))
        if worst_risk >= 3:
            base_defense_score = 70
        elif worst_risk == 2:
            base_defense_score = 80
        else:
            base_defense_score = 90
    else:
        base_defense_score = 90

    # Fuse into single index (weighted average)
    # Nuclear posture weighs most heavily.
    sri = (
        0.5 * nuclear_score +
        0.3 * rel_score +
        0.2 * base_defense_score
    )

    sri = max(0.0, min(100.0, sri))

    if sri >= 85:
        posture = "STRONG"
    elif sri >= 70:
        posture = "WATCH"
    elif sri >= 55:
        posture = "AT_RISK"
    else:
        posture = "CRITICAL"

    return {
        "product_type": "Strategic Readiness Index",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "index": round(sri, 2),
        "posture": posture,
        "inputs": {
            "nuclear_threat_level": nuclear_level,
            "nuclear_score": nuclear_score,
            "avg_reliability": rel_score,
            "base_defense_score": base_defense_score,
        },
        "interpretation": {
            "STRONG": "Nuclear posture, sensors, and base defense are aligned and healthy.",
            "WATCH": "Overall posture acceptable, but watch trends and hotspots closely.",
            "AT_RISK": "Risk building — nuclear, sensors, or base defense need intervention.",
            "CRITICAL": "Severe degradation in one or more pillars — immediate action required.",
        },
    }


def write_strategic_readiness_index() -> Dict[str, str]:
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_strategic_readiness_index()

    json_path = DOCS_DIR / "strategic_readiness_index.json"
    txt_path = DOCS_DIR / "strategic_readiness_index.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines = []
    lines.append("=== STRATEGIC READINESS INDEX ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append(f"Index  : {data['index']}")
    lines.append(f"Posture: {data['posture']}")
    lines.append("")
    lines.append("--- Inputs ---")
    for k, v in data["inputs"].items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("--- Posture Interpretation ---")
    for k, v in data["interpretation"].items():
        lines.append(f"{k}: {v}")
    lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_strategic_readiness_index()
    print("Strategic Readiness Index written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

