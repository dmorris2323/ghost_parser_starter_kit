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


def _extract_locations_from_threat_map(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    locs = data.get("locations") or data.get("sectors") or []
    if not isinstance(locs, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in locs:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("id") or "UNKNOWN"
        risk = item.get("risk_score") or item.get("score") or 0
        incidents = item.get("incidents", 0)
        out.append(
            {
                "name": name,
                "risk_score": risk,
                "incidents": incidents,
                "source": "installation_threat_map",
            }
        )
    return out


def _extract_locations_from_perimeter(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    locs = data.get("incidents") or []
    if not isinstance(locs, list):
        return []
    out: List[Dict[str, Any]] = []
    for inc in locs:
        if not isinstance(inc, dict):
            continue
        name = inc.get("location") or "UNKNOWN"
        severity = inc.get("severity") or "UNKNOWN"
        out.append(
            {
                "name": name,
                "risk_score": 1 if severity == "LOW" else 2 if severity == "MEDIUM" else 3,
                "incidents": 1,
                "source": "perimeter_incident_report",
                "severity": severity,
            }
        )
    return out


def build_base_defense_hotspots(top_n: int = 5) -> Dict[str, Any]:
    """
    Build a list of highest-risk base-defense hotspots.

    Combines:
      - installation_threat_map.json
      - perimeter_incident_report.json
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    threat_map = _safe_read_json(DOCS_DIR / "installation_threat_map.json")
    perimeter = _safe_read_json(DOCS_DIR / "perimeter_incident_report.json")

    records: List[Dict[str, Any]] = []
    records.extend(_extract_locations_from_threat_map(threat_map))
    records.extend(_extract_locations_from_perimeter(perimeter))

    # Aggregate by name
    agg: Dict[str, Dict[str, Any]] = {}
    for r in records:
        name = r["name"]
        if name not in agg:
            agg[name] = {
                "name": name,
                "risk_score": 0,
                "incidents": 0,
                "sources": set(),  # type: ignore
            }
        agg[name]["risk_score"] = max(agg[name]["risk_score"], r.get("risk_score", 0))
        agg[name]["incidents"] += r.get("incidents", 0)
        agg[name]["sources"].add(r["source"])  # type: ignore

    # Convert sources to list and sort
    hotspots: List[Dict[str, Any]] = []
    for name, info in agg.items():
        hotspots.append(
            {
                "name": name,
                "risk_score": info["risk_score"],
                "incidents": info["incidents"],
                "sources": sorted(list(info["sources"])),  # type: ignore
            }
        )

    hotspots.sort(key=lambda x: (x["risk_score"], x["incidents"]), reverse=True)
    hotspots = hotspots[:top_n]

    return {
        "product_type": "Base Defense Hotspots",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "top_n": top_n,
        "hotspots": hotspots,
        "notes": [
            "Hotspots aggregated from installation threat map and perimeter incidents.",
            "Risk score is a fused, simplified metric for quick commander awareness.",
        ],
    }


def write_base_defense_hotspots(top_n: int = 5) -> Dict[str, str]:
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_base_defense_hotspots(top_n=top_n)

    json_path = DOCS_DIR / "base_defense_hotspots.json"
    txt_path = DOCS_DIR / "base_defense_hotspots.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines: List[str] = []
    lines.append("=== BASE DEFENSE HOTSPOTS ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append(f"Top N: {data['top_n']}")
    lines.append("")
    if not data["hotspots"]:
        lines.append("No hotspots detected (no data or all clear).")
    else:
        for h in data["hotspots"]:
            lines.append(f"- {h['name']}")
            lines.append(f"  Risk score : {h['risk_score']}")
            lines.append(f"  Incidents  : {h['incidents']}")
            lines.append(f"  Sources    : {', '.join(h['sources'])}")
            lines.append("")
    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_base_defense_hotspots()
    print("Base Defense Hotspots written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

