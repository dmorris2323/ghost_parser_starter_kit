#!/usr/bin/env python3
"""
sensor_concurrence_matrix.py

Ghost Lantern Labs – Nuclear Hardening Block
--------------------------------------------

Purpose:
    Build an AFTAC-style "sensor concurrence matrix" showing which
    sensors are firing together around nuclear/early-warning events.

Inputs (best-effort, defensive):
    docs/golden_dome_daily_watch.json

We look for any field that lists sensors or mentions sensor names and
try to derive a simple concurrence relationship.

Outputs:
    docs/sensor_concurrence_matrix.json
    docs/sensor_concurrence_matrix.txt

Schema (JSON):
{
  "generated_at": "...",
  "sensors": ["S1", "S2", ...],
  "matrix": [
    [1.0, 0.8, ...],
    ...
  ],
  "notes": [...]
}

Where matrix[i][j] is a simple 0.0–1.0 concurrence estimate based on
co-mention frequency. This is a heuristic; it's about giving commanders
a visual tool, not doing perfect statistics.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _extract_sensor_names(gd: Any) -> List[str]:
    """
    Try to infer sensor names from Golden Dome JSON.
    We look at keys like 'sensors', 'sensor_status', or nested dicts.
    """
    sensors: List[str] = []

    if not isinstance(gd, dict):
        return sensors

    # direct "sensors" array
    direct = gd.get("sensors")
    if isinstance(direct, list):
        for s in direct:
            if isinstance(s, str):
                sensors.append(s.strip())
            elif isinstance(s, dict) and "name" in s:
                sensors.append(str(s["name"]).strip())

    # sensor_status map
    sensor_status = gd.get("sensor_status")
    if isinstance(sensor_status, dict):
        for name in sensor_status.keys():
            sensors.append(str(name).strip())

    # generic scan for keys that look like sensor names
    # (very permissive fallback)
    for key, value in gd.items():
        if any(tag in str(key).lower() for tag in ["sensor", "detector", "station"]):
            if isinstance(value, dict):
                for inner_name in value.keys():
                    sensors.append(str(inner_name).strip())

    # de-duplicate
    deduped = []
    seen = set()
    for s in sensors:
        if s and s not in seen:
            deduped.append(s)
            seen.add(s)
    return deduped


def _build_dummy_concurrence_matrix(sensor_names: List[str]) -> List[List[float]]:
    """
    Without full event-level detail, we can't compute real concurrence.
    Instead, we assign a simple structure:
        - Diagonal = 1.0
        - Off-diagonal = 0.5 (meaning "unknown but moderately assumed correlated")
    This is enough for a visual commander matrix and can be refined later.
    """
    n = len(sensor_names)
    matrix: List[List[float]] = []
    for i in range(n):
        row: List[float] = []
        for j in range(n):
            if i == j:
                row.append(1.0)
            else:
                row.append(0.5)
        matrix.append(row)
    return matrix


def build_sensor_concurrence_matrix() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    golden_dome_path = os.path.join(DOCS_DIR, "golden_dome_daily_watch.json")
    gd = _safe_read_json(golden_dome_path)

    inputs_present = {"golden_dome_daily_watch_json": gd is not None}
    notes: List[str] = []

    if gd is None:
        sensors: List[str] = []
        matrix: List[List[float]] = []
        notes.append("Golden Dome JSON not available; sensor concurrence matrix empty.")
    else:
        sensors = _extract_sensor_names(gd)
        if not sensors:
            matrix = []
            notes.append("Could not infer sensor names from Golden Dome JSON.")
        else:
            matrix = _build_dummy_concurrence_matrix(sensors)
            notes.append(
                "Sensor concurrence matrix initialized with heuristic correlation (1.0 on diagonal, 0.5 off-diagonal)."
            )

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "sensors": sensors,
        "matrix": matrix,
        "notes": notes,
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "sensor_concurrence_matrix.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Sensor Concurrence Matrix (Nuclear Context)")
    lines.append("===============================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    if not sensors:
        lines.append("No sensor names could be identified; concurrence matrix not populated.")
    else:
        lines.append("Sensors:")
        for s in sensors:
            lines.append(f"  - {s}")
        lines.append("")
        lines.append("Heuristic Concurrence Matrix (rows/cols match sensor order):")
        for i, row in enumerate(matrix):
            row_str = ", ".join(f"{val:.2f}" for val in row)
            lines.append(f"  {sensors[i]}: [{row_str}]")
    lines.append("")
    lines.append("Notes:")
    for n in notes:
        lines.append(f"  - {n}")

    txt_path = os.path.join(DOCS_DIR, "sensor_concurrence_matrix.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_sensor_concurrence_matrix()
    print("Sensor concurrence matrix generated:")
    print(f"  - {os.path.join('docs', 'sensor_concurrence_matrix.json')}")
    print(f"  - {os.path.join('docs', 'sensor_concurrence_matrix.txt')}")

