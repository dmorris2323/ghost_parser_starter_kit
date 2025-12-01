"""
system_status_dashboard_txt.py — Ghost Lantern Labs
---------------------------------------------------
Builds a single text dashboard with:

  - Active profile status
  - Pipeline health (if available)
  - Operator snapshot (if available)
  - Threat memory stats (if available)
  - Doctrine threat summary (if available)

Output:
  docs/system_status_dashboard.txt
"""

from pathlib import Path
from datetime import datetime

from profile_status import build_profile_status

PIPELINE_HEALTH = Path("pipeline_health.txt")
OPERATOR_SNAPSHOT = Path("operator_snapshot.txt")
THREAT_STATS = Path("threat_memory_stats.txt")
DOCTRINE_REPORT = Path("docs/threat_memory_doctrine_report.txt")
OUTPUT = Path("docs/system_status_dashboard.txt")


def read_if_exists(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")


def main():
    lines = []
    lines.append("Ghost Lantern Labs — System Status Dashboard")
    lines.append("============================================")
    lines.append(f"Generated: {datetime.utcnow().isoformat()} UTC")
    lines.append("")

    # Profile
    lines.append("=== ACTIVE PROFILE ===")
    lines.append(build_profile_status())
    lines.append("")

    # Pipeline health
    lines.append("=== PIPELINE HEALTH ===")
    lines.append(read_if_exists(PIPELINE_HEALTH, "No pipeline_health.txt found."))
    lines.append("")

    # Operator snapshot
    lines.append("=== OPERATOR SNAPSHOT ===")
    lines.append(read_if_exists(OPERATOR_SNAPSHOT, "No operator_snapshot.txt found."))
    lines.append("")

    # Threat stats
    lines.append("=== THREAT STATS ===")
    lines.append(read_if_exists(THREAT_STATS, "No threat_memory_stats.txt found yet."))
    lines.append("")

    # Doctrine report
    lines.append("=== DOCTRINE SUMMARY ===")
    lines.append(
        read_if_exists(
            DOCTRINE_REPORT,
            "No threat_memory_doctrine_report.txt found yet.",
        )
    )

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote dashboard → {OUTPUT}")


if __name__ == "__main__":
    main()

