from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default


def _safe_read_text(path: Path, default: str = "N/A") -> str:
    try:
        if path.exists():
            return path.read_text().strip()
    except Exception:
        pass
    return default


def build_commander_tile() -> Dict[str, Any]:
    """
    Build a compact commander tile from the existing War Room Brief.

    If war_room_brief_latest.json does not exist, it will fall back to
    building a fresh bundle via gll_war_room_brief.build_war_room_bundle().
    """
    from gll_war_room_brief import build_war_room_bundle

    war_room_json_path = DOCS_DIR / "war_room_brief_latest.json"

    if war_room_json_path.exists():
        try:
            bundle = json.loads(war_room_json_path.read_text())
        except Exception:
            bundle = build_war_room_bundle()
    else:
        bundle = build_war_room_bundle()

    meta = bundle.get("meta", {})
    system_health = bundle.get("system_health", {})
    base_defense = bundle.get("base_defense", {})
    nuclear_picture = bundle.get("nuclear_picture", {})
    china_threat = bundle.get("china_threat", {})

    pipeline_health = system_health.get("pipeline_health", {})
    reliability = system_health.get("reliability", {})

    # Support both 'score' and 'health_score' naming
    health_score = pipeline_health.get(
        "score",
        pipeline_health.get("health_score", None),
    )

    avg_reliability = reliability.get("avg_reliability", None)

    # Base defense overall status heuristic
    bd_threat_map = base_defense.get("installation_threat_map", {})
    bd_outage = base_defense.get("sensor_outage_predictor", {})
    bd_readiness = base_defense.get("distributed_readiness_snapshot", {})
    bd_perimeter = base_defense.get("perimeter_incident_report", {})

    base_status = {
        "threat_map": bd_threat_map.get("status", "unknown"),
        "outage": bd_outage.get("status", "unknown"),
        "readiness": bd_readiness.get("status", "unknown"),
        "perimeter": bd_perimeter.get("status", "unknown"),
    }

    # Nuclear readiness summary
    nuke_snapshot = nuclear_picture.get("nuclear_readiness_snapshot", {})
    nuke_status = nuke_snapshot.get("overall_status", "unknown")

    # Quick China/SDA text tags
    china_notes = china_threat.get("china_threat_notes", "")
    sda_notes = china_threat.get("space_domain_awareness_notes", "")

    def _tag_from_text(text: str) -> str:
        t = text.lower()
        if not t or t.strip() == "":
            return "no_notes"
        if "high risk" in t or "critical" in t or "warfighting" in t:
            return "elevated"
        if "competition" in t or "watch" in t or "monitor" in t:
            return "watch"
        return "noted"

    china_tag = _tag_from_text(china_notes)
    sda_tag = _tag_from_text(sda_notes)

    # Top-level health state
    if health_score is None or avg_reliability is None:
        color = "AMBER"
    elif health_score >= 85 and avg_reliability >= 90:
        color = "GREEN"
    elif health_score >= 70:
        color = "AMBER"
    else:
        color = "RED"

    tile: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": "Ghost Lantern Labs — Commander Readiness Tile",
        "meta_version": meta.get("version", "1.0"),
        "overall_status": color,
        "pipeline": {
            "status": pipeline_health.get("status", "unknown"),
            "health_score": health_score,
            "notes": pipeline_health.get("notes", ""),
        },
        "reliability": {
            "avg_reliability": avg_reliability,
            "sensors": reliability.get("sensors", {}),
        },
        "base_defense": base_status,
        "nuclear": {
            "status": nuke_status,
            "golden_dome_status_text": nuclear_picture.get("golden_dome_status", ""),
        },
        "china_space": {
            "china_tag": china_tag,
            "sda_tag": sda_tag,
        },
    }

    return tile


def write_commander_tile() -> str:
    """
    Write commander_readiness_tile.json into docs and return its path.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    tile = build_commander_tile()
    out_path = DOCS_DIR / "commander_readiness_tile.json"
    out_path.write_text(json.dumps(tile, indent=2))
    return str(out_path)


if __name__ == "__main__":
    path = write_commander_tile()
    print(f"Commander Readiness Tile written to: {path}")

