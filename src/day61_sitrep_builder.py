"""
day61_sitrep_builder.py

Builds a Day 61 SITREP for Ghost Lantern Labs.

Pulls from:
- sensor_reliability (average + per-sensor)
- golden_dome_readiness_report
- any existing mission brief / dashboard artifacts (if present)

Output:
- docs/day61_sitrep.txt

You can treat this as the "what did I build today" commander note.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, Any

from sensor_reliability import compute_reliability_all, export_reliability_report
from golden_dome_readiness_report import build_readiness_report
from profile_config import get_active_profile


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_PATH = DOCS_DIR / "day61_sitrep.txt"


def build_day61_sitrep() -> Dict[str, Any]:
    """
    Build and write the Day 61 SITREP.

    Returns a small dict with the path + key stats.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    today = date(2025, 12, 5)  # Day 61 anchor
    profile = get_active_profile()
    profile_key = getattr(profile, "key", "unknown_profile")
    profile_name = getattr(profile, "display_name", "Unknown Profile")

    # Ensure core artifacts exist
    reliability_info = export_reliability_report()
    readiness_info = build_readiness_report()

    rel_stats = compute_reliability_all()

    lines: list[str] = []
    lines.append("=== GLL DAY 61 SITREP ===")
    lines.append("")
    lines.append(f"Date:        {today.isoformat()}  (Day 61 pre-BMT)")
    lines.append(f"Active Profile: {profile_name} ({profile_key})")
    lines.append("")
    lines.append("--- SENSOR GRID STATUS ---")
    lines.append(f"Average Reliability: {rel_stats['avg_reliability']:.2f}%")
    lines.append("Per-Sensor Snapshot:")
    for name, val in sorted(rel_stats["sensors"].items()):
        lines.append(f"  - {name}: {val:.2f}%")
    lines.append("")
    lines.append("--- GOLDEN DOME READINESS ---")
    lines.append(f"Assessment: {readiness_info['label']}")
    lines.append(f"Readiness Report: {readiness_info['path']}")
    lines.append("")
    lines.append("--- KEY ARTIFACTS (DAY 61) ---")
    lines.append(f"Sensor Reliability Report: {reliability_info['path']}")
    lines.append("Daily Mission Brief (HTML): docs/daily_mission_brief.html (if generated)")
    lines.append("Spectral Dashboard Bundle: src/spectral_dashboard_api.py (JSON export)")
    lines.append("")
    lines.append("Analyst Summary (for future Dex / commanders):")
    lines.append(
        "  * Day 61 focused on reliability and Golden Dome readiness. "
        "GLL now exposes explicit reliability stats and a readiness label, "
        "suitable for AFTAC / Golden Dome-style briefings."
    )
    lines.append(
        "  * These outputs prove GLL can reason ABOUT its own health and "
        "explain that health in human language — critical for ISR trust."
    )
    lines.append("")
    lines.append("Next Steps:")
    lines.append("  1) Wire these reports into your Day 100 demo deck.")
    lines.append("  2) Use Golden Dome readiness as a talking point at UTA / tech school.")
    lines.append("  3) Later: extend SITREP builder to auto-detect anomalies and trend shifts.")
    text = "\n".join(lines)

    OUT_PATH.write_text(text, encoding="utf-8")

    return {
        "path": str(OUT_PATH),
        "avg_reliability": rel_stats["avg_reliability"],
        "profile_name": profile_name,
        "readiness_label": readiness_info["label"],
    }


if __name__ == "__main__":
    out = build_day61_sitrep()
    print("Day 61 SITREP written:")
    print(f"  -> {out['path']}")
    print(f"Profile: {out['profile_name']}")
    print(f"Average reliability: {out['avg_reliability']:.2f}%")
    print(f"Golden Dome: {out['readiness_label']}")

