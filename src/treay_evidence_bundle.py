#!/usr/bin/env python3
"""
treaty_evidence_bundle.py

Day 65–66 – Ghost Lantern Labs

Builds a "GLL Treaty Evidence Bundle" describing key evidence artifacts
relevant to nuclear/treaty monitoring, audits, and investigations.

Original Day 65 artifacts:
- daily_mission_brief.html / .txt
- golden_dome_drift_report.txt
- golden_dome_daily_watch.json
- nuclear_decision_card.txt
- gll_readiness.txt
- system_integrity_report.txt
- prelaunch_watchboard.json
- scenario_pack_latest.json

Day 66 expansion:
- nuclear_status_summary.json / .txt
- escalation_ladder.json / .txt
- nuclear_brief_packet.txt

Output:
- docs/treaty_evidence_bundle.json
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _file_meta(rel_path: str) -> Dict[str, Any]:
    abs_path = os.path.join(DOCS_DIR, rel_path)
    exists = os.path.exists(abs_path)
    meta: Dict[str, Any] = {
        "path": os.path.join("docs", rel_path),
        "exists": exists,
        "last_modified": None,
    }
    if exists:
        try:
            ts = os.path.getmtime(abs_path)
            meta["last_modified"] = datetime.fromtimestamp(ts).isoformat()
        except Exception:
            meta["last_modified"] = None
    return meta


def build_treaty_evidence_bundle() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    artifacts: List[Dict[str, Any]] = []

    def add_artifact(
        name: str,
        rel_path: str,
        description: str,
    ) -> None:
        meta = _file_meta(rel_path)
        meta["name"] = name
        meta["description"] = description
        artifacts.append(meta)

    # Core daily brief artifacts
    add_artifact(
        "Daily Mission Brief (HTML)",
        "daily_mission_brief.html",
        "Full HTML daily mission brief for the active GLL profile.",
    )
    add_artifact(
        "Daily Mission Brief (Text)",
        "daily_mission_brief.txt",
        "Plain-text daily mission brief for quick reading or printing.",
    )

    # Golden Dome & nuclear readiness artifacts
    add_artifact(
        "Golden Dome Drift Report",
        "golden_dome_drift_report.txt",
        "Assessment of how current system behavior is drifting from Golden Dome readiness standards.",
    )
    add_artifact(
        "Golden Dome Daily Watch (JSON)",
        "golden_dome_daily_watch.json",
        "Structured Golden Dome daily watch product summarizing nuclear readiness, drift, trust, and forecast.",
    )
    add_artifact(
        "Golden Dome Daily Watch (Text)",
        "golden_dome_daily_watch.txt",
        "Human-readable Golden Dome daily watch narrative for commanders.",
    )
    add_artifact(
        "Nuclear Decision Card",
        "nuclear_decision_card.txt",
        "One-page decision card summarizing crisis mode, Golden Dome readiness, fusion trust, and nuclear snapshot.",
    )

    # System-level readiness & integrity
    add_artifact(
        "GLL Readiness Report",
        "gll_readiness.txt",
        "System-level readiness assessment for GLL, summarizing overall posture.",
    )
    add_artifact(
        "System Integrity Report",
        "system_integrity_report.txt",
        "Report on core system integrity checks and health.",
    )

    # Pre-launch / scenario artifacts
    add_artifact(
        "Pre-launch ISR Watchboard",
        "prelaunch_watchboard.json",
        "Structured pre-launch ISR watchboard for missile-related or nuclear-related activity.",
    )
    add_artifact(
        "Scenario Pack (Latest)",
        "scenario_pack_latest.json",
        "Latest GLL scenario pack describing simulated or real-world ISR scenarios.",
    )

    # Day 66 – Nuclear consolidation & escalation artifacts
    add_artifact(
        "Nuclear Status Summary (JSON)",
        "nuclear_status_summary.json",
        "Structured summary of nuclear/treaty-related artifacts and key signals.",
    )
    add_artifact(
        "Nuclear Status Summary (Text)",
        "nuclear_status_summary.txt",
        "Human-readable summary of nuclear/treaty-related artifacts and signals.",
    )
    add_artifact(
        "Escalation Ladder (JSON)",
        "escalation_ladder.json",
        "Structured Nuclear Escalation Ladder assessment (STEADY/TENSE/BRINK/FLASHPOINT).",
    )
    add_artifact(
        "Escalation Ladder (Text)",
        "escalation_ladder.txt",
        "Human-readable escalation ladder assessment with rationale.",
    )
    add_artifact(
        "Nuclear Brief Packet",
        "nuclear_brief_packet.txt",
        "Commander-facing packet combining status summary, escalation ladder, and treaty evidence overview.",
    )

    bundle: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "description": (
            "GLL Treaty Evidence Bundle: consolidated list of nuclear/treaty-relevant "
            "artifacts suitable for audits, investigations, and higher-level review."
        ),
        "artifacts": artifacts,
    }

    out_path = os.path.join(DOCS_DIR, "treaty_evidence_bundle.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, sort_keys=True)

    return bundle


if __name__ == "__main__":
    bundle = build_treaty_evidence_bundle()
    print("Treaty Evidence Bundle generated:")
    print(f"  - {os.path.join('docs', 'treaty_evidence_bundle.json')}")
    print(f"Artifacts listed: {len(bundle.get('artifacts', []))}")

