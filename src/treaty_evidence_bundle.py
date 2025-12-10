from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


EVIDENCE_FILES = [
    "golden_dome_daily_watch.json",
    "nuclear_decision_card.json",
    "installation_threat_map.json",
    "sensor_outage_prediction.json",
    "distributed_readiness_snapshot.json",
    "perimeter_incident_report.json",
    "base_defense_storyboard.json",
]


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def build_treaty_evidence_bundle() -> Dict[str, Any]:
    """
    Build a treaty / audit evidence bundle.

    This is designed as a "here is everything we had at time T" object:
      - What products were present
      - Their file paths
      - A light digest for each (status fields if present)

    Output:
      {
        "product_type": "Treaty Evidence Bundle",
        "generated_at": "...Z",
        "evidence_items": [
          {
            "name": "...",
            "path": "...",
            "exists": true/false,
            "status": "...",
            "summary": {...}
          },
          ...
        ]
      }
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)

    items: List[Dict[str, Any]] = []

    for fname in EVIDENCE_FILES:
        fpath = DOCS_DIR / fname
        data = _safe_read_json(fpath)
        exists = fpath.exists()

        status = data.get("status") or data.get("nuclear_threat_level") or data.get(
            "readiness"
        )

        # Light summary: pull any obvious keys if present
        summary_keys = [
            "nuclear_threat_level",
            "installation_threat_status",
            "outage_posture",
            "readiness",
            "avg_reliability",
            "total_perimeter_incidents",
            "product_type",
        ]
        summary = {}
        for k in summary_keys:
            if k in data:
                summary[k] = data[k]
            elif "summary" in data and isinstance(data["summary"], dict) and k in data["summary"]:
                summary[k] = data["summary"][k]

        items.append(
            {
                "name": fname.replace(".json", ""),
                "path": str(fpath),
                "exists": exists,
                "status": status or "UNKNOWN",
                "summary": summary,
            }
        )

    bundle = {
        "product_type": "Treaty Evidence Bundle",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "evidence_items": items,
        "notes": [
            "This bundle is intended for treaty, audit, or oversight workflows.",
            "Each item records existence, path, and a light summary at generation time.",
        ],
    }

    return bundle


def write_treaty_evidence_bundle() -> Dict[str, str]:
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_treaty_evidence_bundle()

    json_path = DOCS_DIR / "treaty_evidence_bundle.json"
    txt_path = DOCS_DIR / "treaty_evidence_bundle.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines = []
    lines.append("=== TREATY EVIDENCE BUNDLE ===")
    lines.append(f"Generated: {data['generated_at']}")
    lines.append("")
    for item in data["evidence_items"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  Path   : {item['path']}")
        lines.append(f"  Exists : {item['exists']}")
        lines.append(f"  Status : {item['status']}")
        if item["summary"]:
            lines.append("  Summary:")
            for k, v in item["summary"].items():
                lines.append(f"    {k}: {v}")
        lines.append("")

    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_treaty_evidence_bundle()
    print("Treaty Evidence Bundle written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

