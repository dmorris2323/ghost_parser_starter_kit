"""
fusion_minimap.py
-----------------

Creates a tiny ASCII "map" of sensor events grouped by AOI box.
Useful for demos, operator briefings, and future GUI overlays.

Input:
  - fused_output.csv   (normal pipeline output)

Output:
  - minimap.txt
  - dict returned to caller

Example ASCII output:

   [AOI_NK_COAST]   ⚠️ 2 anomalies
   [AOI_GLOBAL]     ✔️ stable
   [AOI_INLAND]     ❗ 1 critical
"""

import csv
from pathlib import Path
from collections import defaultdict


DATA = Path("data/fused_output.csv")
OUT = Path("minimap.txt")


def load_fused():
    if not DATA.exists():
        return []

    rows = []
    with DATA.open() as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def classify(score: float):
    """Basic thresholds (these will later tie to profile thresholds)."""
    try:
        s = float(score)
    except:
        return "unknown"

    if s >= 0.85:
        return "critical"
    elif s >= 0.55:
        return "warning"
    return "stable"


def build_minimap():
    data = load_fused()
    if not data:
        OUT.write_text("No fused data available.\n")
        return {"status": "empty"}

    map_counts = defaultdict(lambda: {"critical": 0, "warning": 0, "stable": 0})

    for row in data:
        aoi = row.get("AOI", "UNKNOWN")
        z = classify(row.get("score", 0))
        map_counts[aoi][z] += 1

    lines = []
    lines.append("=== SENSOR FUSION MINI-MAP ===")
    lines.append("")

    for aoi, counts in map_counts.items():
        if counts["critical"] > 0:
            icon = "❗"
        elif counts["warning"] > 0:
            icon = "⚠️"
        else:
            icon = "✔️"

        lines.append(f"[{aoi}]   {icon}  C:{counts['critical']}  W:{counts['warning']}  S:{counts['stable']}")

    text = "\n".join(lines)
    OUT.write_text(text)

    return {"status": "ok", "map": map_counts, "file": str(OUT)}


if __name__ == "__main__":
    out = build_minimap()
    print(out)
    print(f"[OK] Minimap written → {OUT}")

