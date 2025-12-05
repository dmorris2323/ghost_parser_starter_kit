"""
golden_dome_readiness_report.py

Builds a commander-grade Golden Dome readiness report based on:
- Active profile (nuclear / sports / legal / SOC / etc.)
- Sensor reliability (from sensor_reliability.py)

Output:
- docs/golden_dome_readiness.txt

This does NOT try to be perfect; it guarantees a clean,
human-readable summary every time you run it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from sensor_reliability import compute_reliability_all
from profile_config import get_active_profile


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_PATH = DOCS_DIR / "golden_dome_readiness.txt"


def _readiness_label(avg_reliability: float) -> str:
    """
    Map average reliability to a simple readiness label.
    """
    if avg_reliability >= 97.0:
        return "GREEN – Mission ready, high confidence in sensor grid."
    if avg_reliability >= 93.0:
        return "AMBER – Ready, but watch for drift and single points of failure."
    if avg_reliability >= 85.0:
        return "YELLOW – Caution. Investigate weak sensors and recent failures."
    return "RED – Not acceptable for real-world Golden Dome operations."


def build_readiness_report() -> Dict[str, Any]:
    """
    Build the readiness report content and write it to disk.

    Returns:
        {
          "path": "...",
          "avg_reliability": float,
          "label": str,
          "profile_key": str,
          "profile_name": str,
        }
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    reliability = compute_reliability_all()
    avg = reliability["avg_reliability"]
    sensors = reliability["sensors"]

    profile = get_active_profile()
    profile_key = getattr(profile, "key", "unknown_profile")
    profile_name = getattr(profile, "display_name", "Unknown Profile")

    label = _readiness_label(avg)

    lines: list[str] = []
    lines.append("=== GOLDEN DOME READINESS REPORT ===")
    lines.append("")
    lines.append(f"Active Profile Key:   {profile_key}")
    lines.append(f"Active Profile Name:  {profile_name}")
    lines.append("")
    lines.append(f"Average Sensor Reliability: {avg:.2f}%")
    lines.append(f"Readiness Assessment: {label}")
    lines.append("")
    lines.append("Per-Sensor Reliability Snapshot:")
    for name in sorted(sensors.keys()):
        lines.append(f"  - {name}: {sensors[name]:.2f}%")
    lines.append("")
    lines.append("Analyst Notes:")
    lines.append("  * This is a pre-brief snapshot only.")
    lines.append("  * Use fusion_ingest + QA to confirm pipeline health.")
    lines.append("  * Golden Dome validation should combine:")
    lines.append("      - Sensor reliability")
    lines.append("      - Cross-sensor agreement")
    lines.append("      - AI independence status")
    lines.append("      - Known threat activity in AOI.")
    text = "\n".join(lines)

    OUT_PATH.write_text(text, encoding="utf-8")

    return {
        "path": str(OUT_PATH),
        "avg_reliability": avg,
        "label": label,
        "profile_key": profile_key,
        "profile_name": profile_name,
    }


if __name__ == "__main__":
    out = build_readiness_report()
    print("Golden Dome readiness report written:")
    print(f"  -> {out['path']}")
    print(f"Profile: {out['profile_name']} ({out['profile_key']})")
    print(f"Average reliability: {out['avg_reliability']:.2f}%")
    print(f"Assessment: {out['label']}")

