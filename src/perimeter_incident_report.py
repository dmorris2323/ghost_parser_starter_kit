from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"


def _iter_threat_log(path: Path) -> Iterable[Dict[str, Any]]:
    """
    Safely iterate over threat_memory_log.jsonl.
    Each line should be a JSON object. Malformed lines are skipped.
    """
    if not path.exists():
        return []
    try:
        lines = path.read_text().splitlines()
    except Exception:
        return []

    events: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if isinstance(ev, dict):
                events.append(ev)
        except Exception:
            continue
    return events


def _classify_sector(ev: Dict[str, Any]) -> str:
    """
    Map generic 'sector'/'zone' hints into named perimeter sectors.
    Defaults to UNKNOWN.
    """
    raw = (ev.get("sector") or ev.get("zone") or "").upper()

    if "NORTH" in raw or raw == "N":
        return "PERIMETER_NORTH"
    if "SOUTH" in raw or raw == "S":
        return "PERIMETER_SOUTH"
    if "EAST" in raw or raw == "E":
        return "PERIMETER_EAST"
    if "WEST" in raw or raw == "W":
        return "PERIMETER_WEST"
    if "GATE" in raw:
        return "GATE_COMPLEX"
    if "AIRFIELD" in raw or "RUNWAY" in raw:
        return "AIRFIELD"
    return "UNKNOWN"


def _classify_pattern(ev: Dict[str, Any]) -> str:
    """
    Very simple tagger for 'drone', 'gate', 'fence', etc.
    Helps tie to real-world incident narratives.
    """
    text = " ".join(
        str(ev.get(k, "")).lower()
        for k in ("event_type", "details", "Description", "message")
    )

    if any(word in text for word in ("uav", "drone", "quad", "uas")):
        return "DRONE_ACTIVITY"
    if "gate" in text or "entry control" in text:
        return "GATE_PRESSURE"
    if "fence" in text or "perimeter" in text:
        return "FENCE_PROBE"
    if "jam" in text or "jamming" in text:
        return "EMS_JAMMING"
    if "rad" in text or "radiation" in text:
        return "RADIATION_ANOMALY"
    return "GENERAL_INCIDENT"


def build_perimeter_incident_report(max_events: int = 50) -> Dict[str, Any]:
    """
    Build an Installation / Perimeter Incident Report from threat_memory_log.jsonl.

    Output structure:
      {
        "product_type": "Perimeter Incident Report",
        "generated_at": "...Z",
        "total_events": int,
        "sector_counts": {...},
        "pattern_counts": {...},
        "recent_events": [ ... up to max_events ... ]
      }
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    threat_log = DATA_DIR / "threat_memory_log.jsonl"
    events = list(_iter_threat_log(threat_log))

    sector_counts: Dict[str, int] = {}
    pattern_counts: Dict[str, int] = {}

    recent: List[Dict[str, Any]] = []

    for ev in events:
        sector = _classify_sector(ev)
        pattern = _classify_pattern(ev)

        sector_counts[sector] = sector_counts.get(sector, 0) + 1
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    # Sort newest first by timestamp if present
    def _parse_ts(e: Dict[str, Any]) -> float:
        t = e.get("timestamp") or e.get("time") or ""
        try:
            # ISO-ish fallback
            return datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    events_sorted = sorted(events, key=_parse_ts, reverse=True)
    for ev in events_sorted[:max_events]:
        # Strip to a small, briefing-friendly subset
        recent.append(
            {
                "timestamp": ev.get("timestamp"),
                "sector": _classify_sector(ev),
                "pattern": _classify_pattern(ev),
                "severity": ev.get("severity"),
                "event_type": ev.get("event_type") or ev.get("Description"),
                "details": ev.get("details"),
            }
        )

    report = {
        "product_type": "Perimeter Incident Report",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_events": len(events),
        "sector_counts": sector_counts,
        "pattern_counts": pattern_counts,
        "recent_events": recent,
    }

    # If no data at all, return a shaped-safe default
    if len(events) == 0:
        report["note"] = "No perimeter incidents recorded yet; this is a shaped default."

    return report


def write_perimeter_incident_report() -> Dict[str, str]:
    """
    Write JSON and TXT versions under docs/.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    data = build_perimeter_incident_report()

    json_path = DOCS_DIR / "perimeter_incident_report.json"
    txt_path = DOCS_DIR / "perimeter_incident_report.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines: List[str] = []
    lines.append("=== PERIMETER INCIDENT REPORT ===")
    lines.append(f"Generated at: {data['generated_at']}")
    lines.append(f"Total events in log: {data['total_events']}")
    lines.append("")

    if "note" in data:
        lines.append(f"NOTE: {data['note']}")
        lines.append("")

    lines.append("Sector incident counts:")
    for sector, count in sorted(data["sector_counts"].items()):
        lines.append(f"  - {sector}: {count}")
    lines.append("")

    lines.append("Pattern counts:")
    for pattern, count in sorted(data["pattern_counts"].items()):
        lines.append(f"  - {pattern}: {count}")
    lines.append("")

    lines.append("Most recent events:")
    for ev in data["recent_events"]:
        lines.append(
            f"  [{ev.get('timestamp')}] {ev['sector']} | {ev['pattern']} | "
            f"severity={ev.get('severity')} | type={ev.get('event_type')}"
        )
        if ev.get("details"):
            lines.append(f"    details: {ev['details']}")
    lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_perimeter_incident_report()
    print("Perimeter Incident Report written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

