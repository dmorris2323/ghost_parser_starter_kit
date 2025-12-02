"""
system_status_dashboard_txt.py
------------------------------

Builds a consolidated text dashboard for Ghost Lantern Labs:

 - Pipeline health summary
 - Sensor readiness brief
 - Fusion mini-map snapshot
 - Active profile status
 - Golden Dome alignment tier

Output:
  docs/system_status_dashboard.txt
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from pipeline_health import evaluate_pipeline_health
from sensor_readiness_brief import build_readiness_brief
from fusion_minimap import build_minimap
from profile_status import build_profile_status
from golden_dome_alignment_report import build_golden_dome_report, write_golden_dome_report


BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
DASHBOARD_PATH = DOCS_DIR / "system_status_dashboard.txt"
MINIMAP_TXT = BASE / "minimap.txt"


def _safe_read(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"{fallback}\n[ERROR reading {path.name}: {e}]"


def build_system_status_dashboard() -> str:
    """
    Assemble the full system status dashboard as a text string.
    """

    lines: List[str] = []
    lines.append("=== GHOST LANTERN LABS — SYSTEM STATUS DASHBOARD ===")
    lines.append("")

    # 1) Pipeline health
    lines.append(">>> PIPELINE HEALTH")
    try:
        health_report = evaluate_pipeline_health()
        lines.append(str(health_report))
    except Exception as e:
        lines.append(f"[ERROR] pipeline_health: {e}")
    lines.append("")

    # 2) Sensor readiness
    lines.append(">>> SENSOR READINESS BRIEF")
    try:
        sensor_brief = build_readiness_brief()
        lines.append(str(sensor_brief))
    except Exception as e:
        lines.append(f"[ERROR] sensor_readiness_brief: {e}")
    lines.append("")

    # 3) Fusion mini-map
    lines.append(">>> FUSION MINI-MAP (AOI SNAPSHOT)")
    try:
        mm_result = build_minimap()
        # Always try to show the text file if present
        minimap_text = _safe_read(
            MINIMAP_TXT,
            fallback="[Mini-map not available — minimap.txt missing.]",
        )
        lines.append(minimap_text)
        lines.append(f"[minimap_status] {mm_result}")
    except Exception as e:
        lines.append(f"[ERROR] fusion_minimap: {e}")
    lines.append("")

    # 4) Active profile status
    lines.append(">>> ACTIVE PROFILE STATUS")
    try:
        prof_status = build_profile_status()
        lines.append(str(prof_status))
    except Exception as e:
        lines.append(f"[ERROR] profile_status: {e}")
    lines.append("")

    # 5) Golden Dome alignment
    lines.append(">>> GOLDEN DOME ALIGNMENT")
    try:
        gd = build_golden_dome_report()
        lines.append(f"Tier: {gd.get('tier')}  |  Score: {gd.get('score')}%")
        lines.append("")
        for c in gd.get("checks", []):
            status = "OK " if getattr(c, "ok", False) else "MISS"
            lines.append(f" - [{status}] {c.name}: {c.detail}")
        # Also ensure the standalone report is written/updated
        write_golden_dome_report()
    except Exception as e:
        lines.append(f"[ERROR] golden_dome_alignment: {e}")
    lines.append("")

    lines.append("=== END OF SYSTEM STATUS DASHBOARD ===")

    return "\n".join(lines)


def write_system_status_dashboard() -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = build_system_status_dashboard()
    DASHBOARD_PATH.write_text(text, encoding="utf-8")
    return DASHBOARD_PATH


def main() -> None:
    path = write_system_status_dashboard()
    print(f"[OK] System status dashboard written -> {path}")


if __name__ == "__main__":
    main()

