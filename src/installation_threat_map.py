from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"


def _safe_iter_threat_log(path: Path):
    """
    Iterate over threat_memory_log.jsonl if it exists.
    Each line is expected to be a JSON object.
    """
    if not path.exists():
        return
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                # Skip malformed lines
                continue
    except Exception:
        return


def build_installation_threat_map() -> Dict[str, Any]:
    """
    Build a perimeter-style Installation Threat Map from threat_memory_log.jsonl.
    Falls back to a shaped default if there is no data.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    threat_log = DATA_DIR / "threat_memory_log.jsonl"

    # sector -> {critical, high, other}
    sectors: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"critical": 0, "high": 0, "other": 0}
    )

    for ev in _safe_iter_threat_log(threat_log) or []:
        sector = ev.get("sector") or ev.get("zone") or "UNKNOWN"
        sev = (ev.get("severity") or "").lower()

        if "critical" in sev:
            key = "critical"
        elif "high" in sev:
            key = "high"
        else:
            key = "other"

        sectors[sector][key] += 1

    # If zero data, return a shaped but empty map
    if not sectors:
        sectors = {
            "PERIMETER_NORTH": {"critical": 0, "high": 0, "other": 0},
            "PERIMETER_SOUTH": {"critical": 0, "high": 0, "other": 0},
            "PERIMETER_EAST": {"critical": 0, "high": 0, "other": 0},
            "PERIMETER_WEST": {"critical": 0, "high": 0, "other": 0},
        }

    overall_critical = sum(v["critical"] for v in sectors.values())
    if overall_critical > 5:
        status = "RED"
    elif overall_critical > 0:
        status = "AMBER"
    else:
        status = "GREEN"

    out = {
        "product_type": "Installation Threat Map",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "sectors": sectors,
    }
    return out


def write_installation_threat_map() -> Dict[str, str]:
    """
    Writes both JSON and TXT products for the installation threat map.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    data = build_installation_threat_map()

    json_path = DOCS_DIR / "installation_threat_map.json"
    txt_path = DOCS_DIR / "installation_threat_map.txt"

    json_path.write_text(json.dumps(data, indent=2))

    lines: List[str] = []
    lines.append("=== INSTALLATION THREAT MAP ===")
    lines.append(f"Generated at: {data['generated_at']}")
    lines.append(f"Overall Status: {data['status']}")
    lines.append("")
    lines.append("Sector breakdown:")
    for sector, counts in data["sectors"].items():
        lines.append(
            f"  - {sector}: critical={counts['critical']} "
            f"high={counts['high']} other={counts['other']}"
        )
    lines.append("")
    txt_path.write_text("\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path)}


if __name__ == "__main__":
    out = write_installation_threat_map()
    print("Installation Threat Map written:")
    print(f"JSON → {out['json_path']}")
    print(f"TXT  → {out['txt_path']}")

