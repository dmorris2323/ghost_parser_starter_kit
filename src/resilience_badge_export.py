"""
resilience_badge_export.py

Helper to regenerate the Spectral Resilience report + badge.

You can call this from:
    - CLI (python resilience_badge_export.py)
    - Future ghost_cli option
    - Future GUI/automation hooks
"""

from pathlib import Path
from spectral_resilience_score import (
    write_resilience_report,
    export_resilience_badge,
)


def main():
    report_path: Path = write_resilience_report()
    badge_info = export_resilience_badge()

    print(f"[OK] Resilience report written → {report_path}")
    print(f"[OK] Resilience badge written → {badge_info['txt']}")
    print(f"Overall resilience: {badge_info['overall']}/100")

    return {
        "report": str(report_path),
        **badge_info,
    }


if __name__ == "__main__":
    main()

