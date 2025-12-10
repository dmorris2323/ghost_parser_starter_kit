from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from golden_dome_daily_watch import build_daily_watch


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_decision_card() -> Dict[str, Any]:
    """
    Build a commander-ready nuclear decision card.

    Fuses:
      - Golden Dome Daily Watch
      - Sensor outage prediction (if available)
      - Base-defense storyboard (if available)

    Output (JSON dict):
      {
        "product_type": "Nuclear Decision Card",
        "generated_at": "...Z",
        "decision_recommendation": "...",
        "nuclear_threat_level": "...",
        "key_factors": {...},
        "commander_actions": [...]
      }
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    watch = build_daily_watch()
    outage = _safe_read_json(DOCS_DIR / "sensor_outage_prediction.json")
    storyboard = _safe_read_json(DOCS_DIR / "base_defense_storyboard.json")

    nuclear_threat = watch.get("nuclear_threat_level", "NORMAL")
    avg_rel = watch.get("inputs", {}).get("avg_reliability", 90.0)
    outage_posture = outage.get("posture", "STABLE")
    readiness = storyboard.get("summary", {}).get("readiness", "READY")

    # Simple, clear recommendation logic
    if nuclear_threat == "CRITICAL":
        decision = "ELEVATE TO CRISIS ACTION"
    elif nuclear_threat == "ELEVATED" and (avg_rel >= 80 and outage_posture in ("STABLE", "WATCH")):
        decision = "MAINTAIN ELEVATED WATCH"
    elif nuclear_threat == "ELEVATED":
        decision = "VERIFY SENSORS, THEN MAINTAIN ELEVATED WATCH"
    else:
        decision = "MAINTAIN NORMAL NUCLEAR WATCH"

    actions = []

    # Threat-based actions
    if nuclear_threat == "CRITICAL":
        actions.append("1) Notify higher headquarters and nuclear warning centers immediately.")
        actions.append("2) Cross-check independent sensor streams (seismic, EMS, radiation).")
        actions.append("3) Prepare crisis-action briefing for commander within 15 minutes.")
    elif nuclear_threat == "ELEVATED":
        actions.append("1) Increase watch intensity and shorten reporting intervals.")
        actions.append("2) Validate that all critical sensors are online and calibrated.")
        actions.append("3) Flag any anomalous activity for rapid fusion review.")
    else:
        actions.append("1) Maintain standard watch; continue trend and anomaly monitoring.")
        actions.append("2) Log any unusual nuclear-related activity with timestamps.")
        actions.append("3) Ensure fallback and redundancy paths remain tested.")

    # Reliability / outage adjustments
    if outage_posture in ("WATCH", "AT_RISK"):
        actions.append("• Sensor outage posture elevated — coordinate with maintenance/C2 for mitigation.")
    if avg_rel < 80:
        actions.append("• Reliability degraded — treat all single-sensor anomalies as unconfirmed.")

    card = {
        "product_type": "Nuclear Decision Card",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "nuclear_threat_level": nuclear_threat,
        "decision_recommendation": decision,
        "key_factors": {
            "avg_reliability": avg_rel,
            "outage_posture": outage_posture,
            "base_readiness": readiness,
        },
        "commander_actions": actions,
        "source_products": {
            "golden_dome_daily_watch": "docs/golden_dome_daily_watch.json",
            "sensor_outage_prediction": "docs/sensor_outage_prediction.json",
            "base_defense_storyboard": "docs/base_defense_storyboard.json",
        },
    }

    return card


def write_decision_card() -> Dict[str, str]:
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_decision_card()

    json_path = DOCS_DIR / "nuclear_decision_card.json"
    txt_path = DOCS_DIR / "nuclear_decision_card.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines = []
    lines.append("=== NUCLEAR DECISION CARD ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append(f"Nuclear Threat Level: {data['nuclear_threat_level']}")
    lines.append(f"Recommendation: {data['decision_recommendation']}")
    lines.append("")
    lines.append("--- Key Factors ---")
    for k, v in data["key_factors"].items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("--- Commander Actions ---")
    for a in data["commander_actions"]:
        lines.append(f"- {a}")
    lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_decision_card()
    print("Nuclear Decision Card written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

