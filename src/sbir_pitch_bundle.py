"""
sbir_pitch_bundle.py

Ghost Lantern Labs – SBIR / Demo Pitch Bundle Exporter

Purpose:
    Collect the key GLL artifacts (briefs, health reports, resilience scores, etc.)
    into a single bundle folder under:

        src/docs/sbir_pitch_bundle/

    This folder can be zipped and sent as:
        - SBIR attachment
        - internal demo packet
        - "show me what you’ve built" evidence

Behavior:
    - Only copies files that actually exist (degrades safely).
    - Writes:
        - docs/sbir_pitch_bundle/manifest.json
        - docs/sbir_pitch_bundle/README_SPECTRAL_BUNDLE.txt
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
BUNDLE_DIR = DOCS_DIR / "sbir_pitch_bundle"


def _candidate_paths() -> List[Dict[str, Any]]:
    """
    Define candidate artifacts and where they currently live.
    We don't assume they all exist; we check each one.
    """

    return [
        # Core mission briefs
        {
            "label": "Daily Mission Brief (text)",
            "src": DOCS_DIR / "daily_mission_brief.txt",
            "dst_name": "daily_mission_brief.txt",
        },
        {
            "label": "Daily Mission Brief (HTML)",
            "src": DOCS_DIR / "daily_mission_brief.html",
            "dst_name": "daily_mission_brief.html",
        },

        # QA / health
        {
            "label": "QA Summary",
            "src": BASE / "qa_summary.txt",
            "dst_name": "qa_summary.txt",
        },
        {
            "label": "Sensor Health Report",
            "src": BASE / "sensor_health_report.txt",
            "dst_name": "sensor_health_report.txt",
        },

        # Reliability + resilience
        {
            "label": "Sensor Reliability Report",
            "src": DOCS_DIR / "reliability_report.txt",
            "dst_name": "reliability_report.txt",
        },
        {
            "label": "Spectral Resilience Score",
            "src": DOCS_DIR / "spectral_resilience_score.txt",
            "dst_name": "spectral_resilience_score.txt",
        },
        {
            "label": "Spectral Resilience Badge (text)",
            "src": DOCS_DIR / "spectral_resilience_badge.txt",
            "dst_name": "spectral_resilience_badge.txt",
        },
        {
            "label": "Spectral Resilience Badge (JSON)",
            "src": DOCS_DIR / "spectral_resilience_badge.json",
            "dst_name": "spectral_resilience_badge.json",
        },

        # Threat / doctrine
        {
            "label": "Threat Memory Doctrine Report",
            "src": DOCS_DIR / "threat_memory_doctrine_report.txt",
            "dst_name": "threat_memory_doctrine_report.txt",
        },

        # Cross-sensor + profiles
        {
            "label": "Cross-Sensor Report",
            "src": DOCS_DIR / "cross_sensor_report.txt",
            "dst_name": "cross_sensor_report.txt",
        },

        # System status / dashboard
        {
            "label": "System Status Dashboard (text)",
            "src": DOCS_DIR / "system_status_dashboard.txt",
            "dst_name": "system_status_dashboard.txt",
        },

        # Demo / roadmap
        {
            "label": "Day 100 Demo Roadmap",
            "src": DOCS_DIR / "demo_roadmap_day100.md",
            "dst_name": "demo_roadmap_day100.md",
        },
        {
            "label": "Golden Dome Status",
            "src": DOCS_DIR / "golden_dome_status.txt",
            "dst_name": "golden_dome_status.txt",
        },

        # Optional: demo deck manifest (if present)
        {
            "label": "Demo Deck Manifest (Day 58)",
            "src": DOCS_DIR / "demo_deck_manifest_day58.json",
            "dst_name": "demo_deck_manifest_day58.json",
        },
    ]


def build_sbir_bundle() -> Dict[str, Any]:
    """
    Build the SBIR/demo bundle folder and copy in everything that exists.
    Returns a dict summary.
    """
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = _candidate_paths()
    included = []
    missing = []

    for art in artifacts:
        src: Path = art["src"]
        dst_name: str = art["dst_name"]
        label: str = art["label"]

        if not src.exists():
            missing.append(
                {
                    "label": label,
                    "src": str(src),
                    "reason": "missing",
                }
            )
            continue

        dst = BUNDLE_DIR / dst_name
        shutil.copy2(src, dst)

        stat = dst.stat()
        included.append(
            {
                "label": label,
                "src": str(src),
                "dst": str(dst),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        )

    manifest = {
        "bundle_name": "GLL_Spectral_SBIR_Pitch_Bundle",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "base_dir": str(BUNDLE_DIR),
        "included": included,
        "missing": missing,
    }

    manifest_path = BUNDLE_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # Human-readable README
    readme_lines = []
    readme_lines.append("GHOST LANTERN LABS – SPECTRAL SBIR / DEMO BUNDLE")
    readme_lines.append("================================================")
    readme_lines.append("")
    readme_lines.append("This folder contains the core artifacts for demonstrating:")
    readme_lines.append("  • Fusion pipeline health and QA")
    readme_lines.append("  • Sensor health and reliability")
    readme_lines.append("  • Spectral Resilience score (overall system resilience)")
    readme_lines.append("  • Threat memory and doctrine awareness")
    readme_lines.append("  • Cross-sensor validation")
    readme_lines.append("  • Mission brief (text + HTML)")
    readme_lines.append("")
    readme_lines.append(f"Generated at: {manifest['generated_at']}")
    readme_lines.append("")
    readme_lines.append("Included files:")
    for item in included:
        readme_lines.append(f"  - {item['dst']}  ({item['label']})")
    readme_lines.append("")
    if missing:
        readme_lines.append("Artifacts not present at generation time (safe to ignore):")
        for miss in missing:
            readme_lines.append(f"  - {miss['label']}  (expected at {miss['src']})")
    readme_lines.append("")
    readme_lines.append("This bundle is suitable for:")
    readme_lines.append("  • Internal leadership demos")
    readme_lines.append("  • Early SBIR whiteboard conversations")
    readme_lines.append("  • Tech-school / master's program portfolio evidence")
    readme_lines.append("")

    readme_path = BUNDLE_DIR / "README_SPECTRAL_BUNDLE.txt"
    readme_path.write_text("\n".join(readme_lines))

    return {
        "status": "ok",
        "bundle_dir": str(BUNDLE_DIR),
        "manifest": str(manifest_path),
        "included_count": len(included),
        "missing_count": len(missing),
    }


def main() -> Dict[str, Any]:
    summary = build_sbir_bundle()
    print("[OK] SBIR / Demo bundle built.")
    print(f"Bundle directory: {summary['bundle_dir']}")
    print(f"Manifest:         {summary['manifest']}")
    print(f"Included files:   {summary['included_count']}")
    print(f"Missing (safe):   {summary['missing_count']}")
    return summary


if __name__ == "__main__":
    main()

