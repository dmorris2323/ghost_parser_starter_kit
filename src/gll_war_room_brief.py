from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"


def _safe_read_json(path: Path, default: Any) -> Any:
    """Safely read JSON, return default on any error."""
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default


def _safe_read_text(path: Path, default: str = "N/A") -> str:
    """Safely read text, return default on any error."""
    try:
        if path.exists():
            return path.read_text().strip()
    except Exception:
        pass
    return default


def build_war_room_bundle() -> Dict[str, Any]:
    """
    Build a commander-grade war room bundle.

    Aggregates:
      • System / pipeline health
      • Base-defense picture
      • Nuclear / Golden Dome picture
      • China / PLA / space threat context
    """

    # ---------- SYSTEM / PIPELINE HEALTH ----------
    pipeline_health = _safe_read_json(
        DOCS_DIR / "pipeline_health.json",
        {
            "status": "unknown",
            "score": 0,
            "notes": "pipeline_health.json not found – run pipeline health check.",
        },
    )

    reliability = _safe_read_json(
        DOCS_DIR / "sensor_reliability_summary.json",
        {
            "avg_reliability": 92.0,
            "sensors": {},
            "notes": "sensor_reliability_summary.json not found – using defaults.",
        },
    )

    sos_overlay = _safe_read_json(
        BASE_DIR / "gui_sos_overlay.json",
        {
            "status": "no_data",
            "message": "Run SOS export / Option 20 to populate overlay.",
        },
    )

    minimap = _safe_read_json(
        BASE_DIR / "gui_minimap.json",
        {
            "status": "no_data",
            "message": "Run minimap export / Option 19 to populate minimap.",
        },
    )

    # ---------- BASE DEFENSE PICTURE ----------
    base_threat_map = _safe_read_json(
        DOCS_DIR / "installation_threat_map.json",
        {"status": "no_data", "message": "No installation_threat_map.json present."},
    )

    sensor_outage = _safe_read_json(
        DOCS_DIR / "sensor_outage_predictor.json",
        {"status": "no_data", "message": "No sensor_outage_predictor.json present."},
    )

    readiness_snapshot = _safe_read_json(
        DOCS_DIR / "distributed_readiness_snapshot.json",
        {
            "status": "no_data",
            "message": "No distributed_readiness_snapshot.json present.",
        },
    )

    perimeter_incidents = _safe_read_json(
        DOCS_DIR / "perimeter_incident_report.json",
        {"status": "no_data", "message": "No perimeter_incident_report.json present."},
    )

    base_storyboard = _safe_read_text(
        DOCS_DIR / "base_defense_storyboard.txt",
        "No base_defense_storyboard.txt present.",
    )

    # ---------- NUCLEAR / GOLDEN DOME PICTURE ----------
    golden_dome_status = _safe_read_text(
        DOCS_DIR / "golden_dome_status.txt",
        "Golden Dome status file missing – run Golden Dome validator.",
    )

    nuclear_snapshot = _safe_read_json(
        DOCS_DIR / "nuclear_readiness_snapshot.json",
        {
            "status": "no_data",
            "message": "No nuclear_readiness_snapshot.json present.",
        },
    )

    nuclear_decision_card = _safe_read_text(
        DOCS_DIR / "nuclear_decision_card.txt",
        "No nuclear_decision_card.txt present.",
    )

    treaty_bundle = _safe_read_text(
        DOCS_DIR / "treaty_evidence_bundle.txt",
        "No treaty_evidence_bundle.txt present.",
    )

    # ---------- CHINA / PLA / SPACE THREAT ----------
    china_notes = _safe_read_text(
        DOCS_DIR / "china_threat_notes.txt",
        "No china_threat_notes.txt – add PLA / SSF notes here as you study.",
    )

    sda_notes = _safe_read_text(
        DOCS_DIR / "space_domain_awareness_notes.txt",
        "No space_domain_awareness_notes.txt present.",
    )

    ts = datetime.utcnow().isoformat() + "Z"

    bundle: Dict[str, Any] = {
        "meta": {
            "generated_at": ts,
            "tool": "Ghost Lantern Labs — War Room Brief",
            "version": "1.0",
        },
        "system_health": {
            "pipeline_health": pipeline_health,
            "reliability": reliability,
            "sos_overlay": sos_overlay,
            "minimap": minimap,
        },
        "base_defense": {
            "installation_threat_map": base_threat_map,
            "sensor_outage_predictor": sensor_outage,
            "distributed_readiness_snapshot": readiness_snapshot,
            "perimeter_incident_report": perimeter_incidents,
            "storyboard_text": base_storyboard,
        },
        "nuclear_picture": {
            "golden_dome_status": golden_dome_status,
            "nuclear_readiness_snapshot": nuclear_snapshot,
            "nuclear_decision_card": nuclear_decision_card,
            "treaty_evidence_bundle": treaty_bundle,
        },
        "china_threat": {
            "china_threat_notes": china_notes,
            "space_domain_awareness_notes": sda_notes,
        },
    }
    return bundle


def _render_section(title: str, body: str) -> str:
    bar = "=" * len(title)
    return f"{title}\n{bar}\n{body}\n\n"


def render_war_room_text(bundle: Dict[str, Any]) -> str:
    """Human-readable TXT war room brief for commanders."""

    lines: list[str] = []

    # ----- HEADER -----
    lines.append("GHOST LANTERN LABS — WAR ROOM BRIEF")
    lines.append(f"Generated: {bundle.get('meta', {}).get('generated_at', 'N/A')}")
    lines.append("")

    # ----- SYSTEM HEALTH -----
    ph = bundle.get("system_health", {}).get("pipeline_health", {})
    rel = bundle.get("system_health", {}).get("reliability", {})

    ph_status = ph.get("status", "unknown")
    # some versions use "score", some "health_score" – support both
    ph_score = ph.get("score", ph.get("health_score", "N/A"))
    avg_rel = rel.get("avg_reliability", "N/A")

    sys_body = []
    sys_body.append(f"Pipeline status : {ph_status}")
    sys_body.append(f"Pipeline score  : {ph_score}")
    sys_body.append(f"Avg reliability : {avg_rel}%")
    sys_body.append("")
    sys_body.append("Notes:")
    sys_body.append(f"  {ph.get('notes', 'No notes available.')}")
    lines.append(_render_section("SYSTEM HEALTH SUMMARY", "\n".join(sys_body)))

    # ----- BASE DEFENSE PICTURE -----
    bd = bundle.get("base_defense", {})
    bd_lines = []
    bd_lines.append(
        f"Threat map status        : "
        f"{bd.get('installation_threat_map', {}).get('status', 'unknown')}"
    )
    bd_lines.append(
        f"Sensor outage predictor  : "
        f"{bd.get('sensor_outage_predictor', {}).get('status', 'unknown')}"
    )
    bd_lines.append(
        f"Readiness snapshot       : "
        f"{bd.get('distributed_readiness_snapshot', {}).get('status', 'unknown')}"
    )
    bd_lines.append(
        f"Perimeter incident state : "
        f"{bd.get('perimeter_incident_report', {}).get('status', 'unknown')}"
    )
    bd_lines.append("")
    bd_lines.append("Base Defense Storyboard (short excerpt):")
    storyboard = bd.get("storyboard_text", "")
    if len(storyboard) > 600:
        storyboard = storyboard[:600] + "\n[...]"
    bd_lines.append(storyboard or "No storyboard text available.")
    lines.append(_render_section("BASE DEFENSE PICTURE", "\n".join(bd_lines)))

    # ----- NUCLEAR / GOLDEN DOME PICTURE -----
    npic = bundle.get("nuclear_picture", {})
    n_lines = []

    n_lines.append("Golden Dome Status:")
    n_lines.append(npic.get("golden_dome_status", "No Golden Dome status text."))
    n_lines.append("")

    n_lines.append("Nuclear Readiness Snapshot (JSON excerpt):")
    n_snap = json.dumps(npic.get("nuclear_readiness_snapshot", {}), indent=2)
    if len(n_snap) > 800:
        n_snap = n_snap[:800] + "\n[...]"
    n_lines.append(n_snap)
    n_lines.append("")

    n_lines.append("Nuclear Decision Card:")
    ndc = npic.get("nuclear_decision_card", "")
    if len(ndc) > 800:
        ndc = ndc[:800] + "\n[...]"
    n_lines.append(ndc or "No nuclear decision card text.")
    n_lines.append("")

    n_lines.append("Treaty Evidence Bundle (excerpt):")
    teb = npic.get("treaty_evidence_bundle", "")
    if len(teb) > 800:
        teb = teb[:800] + "\n[...]"
    n_lines.append(teb or "No treaty evidence bundle text.")
    lines.append(
        _render_section("NUCLEAR / GOLDEN DOME PICTURE", "\n".join(n_lines))
    )

    # ----- CHINA / PLA / SPACE THREAT -----
    ch = bundle.get("china_threat", {})
    c_lines = []
    c_lines.append("China / PLA / SSF Threat Notes:")
    c_lines.append(ch.get("china_threat_notes", "No China threat notes yet."))
    c_lines.append("")
    c_lines.append("Space Domain Awareness Notes:")
    c_lines.append(ch.get("space_domain_awareness_notes", "No SDA notes yet."))
    lines.append(
        _render_section("CHINA / SPACE THREAT CONTEXT", "\n".join(c_lines))
    )

    return "\n".join(lines).rstrip() + "\n"


def write_war_room_brief() -> Dict[str, str]:
    """
    Main entry – used by ghost_cli Option 42.

    Writes both JSON and TXT war room brief files and returns their paths:
      • docs/war_room_brief_latest.json
      • docs/war_room_brief_latest.txt
    """
    bundle = build_war_room_bundle()

    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    json_path = DOCS_DIR / "war_room_brief_latest.json"
    txt_path = DOCS_DIR / "war_room_brief_latest.txt"

    json_path.write_text(json.dumps(bundle, indent=2))
    txt_path.write_text(render_war_room_text(bundle))

    return {
        "json_path": str(json_path),
        "txt_path": str(txt_path),
    }


if __name__ == "__main__":
    out = write_war_room_brief()
    print("=== WAR ROOM BRIEF BUILT ===")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

