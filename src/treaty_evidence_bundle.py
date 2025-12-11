#!/usr/bin/env python3
"""
treaty_evidence_bundle.py

Ghost Lantern Labs – Treaty Evidence Bundle (v2)
------------------------------------------------

Purpose:
    Build a structured JSON "evidence bundle" that points to the key artifacts
    GLL can provide in a nuclear / treaty / audit / investigation context.

    It looks for artifacts in both:
        • src/docs
        • docs
    so the bundle is robust to minor layout differences.

Outputs:
    • src/docs/treaty_evidence_bundle.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent
SRC_DOCS = BASE_DIR / "docs"
ROOT_DOCS = BASE_DIR.parent / "docs"
OUTPUT_PATH = SRC_DOCS / "treaty_evidence_bundle.json"


ARTIFACTS = [
    # Daily mission briefs
    {
        "key": "daily_mission_brief_html",
        "label": "Daily Mission Brief (HTML)",
        "filenames": ["daily_mission_brief.html"],
    },
    {
        "key": "daily_mission_brief_txt",
        "label": "Daily Mission Brief (TXT)",
        "filenames": ["daily_mission_brief.txt"],
    },

    # Golden Dome / nuclear
    {
        "key": "golden_dome_drift_report",
        "label": "Golden Dome Drift Report",
        "filenames": ["golden_dome_drift_report.txt"],
    },
    {
        "key": "golden_dome_daily_watch",
        "label": "Golden Dome Daily Watch (JSON)",
        "filenames": ["golden_dome_daily_watch.json"],
    },
    {
        "key": "golden_dome_snapshot",
        "label": "Golden Dome Snapshot",
        "filenames": ["golden_dome_snapshot.json", "golden_dome_snapshot.txt"],
    },
    {
        "key": "nuclear_decision_card",
        "label": "Nuclear Decision Card",
        "filenames": ["nuclear_decision_card.txt"],
    },

    # Early-warning / signal fusion
    {
        "key": "prelaunch_watchboard",
        "label": "Prelaunch ISR Watchboard",
        "filenames": ["prelaunch_watchboard.json"],
    },
    {
        "key": "nuclear_signal_fusion",
        "label": "Nuclear Signal Fusion Summary",
        "filenames": ["nuclear_signal_fusion.json", "nuclear_signal_fusion.txt"],
    },

    # System readiness / integrity
    {
        "key": "gll_readiness",
        "label": "GLL Readiness Report",
        "filenames": ["gll_readiness.txt"],
    },
    {
        "key": "system_integrity_report",
        "label": "System Integrity Report",
        "filenames": ["system_integrity_report.txt"],
    },

    # Scenario / evidence packs
    {
        "key": "scenario_pack_latest",
        "label": "Scenario Pack (Latest)",
        "filenames": ["scenario_pack_latest.json"],
    },
]


def _resolve_file(filename: str) -> Optional[Path]:
    """
    Look for filename in src/docs and docs.
    Return the first existing path, or None if not found.
    """
    candidates = [
        SRC_DOCS / filename,
        ROOT_DOCS / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def build_treaty_evidence_bundle() -> Dict[str, Any]:
    """
    Build the treaty evidence bundle JSON and write it to disk.
    """
    SRC_DOCS.mkdir(parents=True, exist_ok=True)

    entries: List[Dict[str, Any]] = []
    missing: List[Dict[str, str]] = []

    for art in ARTIFACTS:
        key = art["key"]
        label = art["label"]
        filenames = art["filenames"]

        found_path: Optional[Path] = None
        tried: List[str] = []

        for fname in filenames:
            path = _resolve_file(fname)
            tried.append(fname)
            if path is not None:
                found_path = path
                break

        if found_path is not None:
            entries.append(
                {
                    "key": key,
                    "label": label,
                    "path": str(found_path),
                    "exists": True,
                    "filenames_considered": tried,
                }
            )
        else:
            entries.append(
                {
                    "key": key,
                    "label": label,
                    "path": None,
                    "exists": False,
                    "filenames_considered": tried,
                }
            )
            missing.append({"key": key, "label": label})

    bundle: Dict[str, Any] = {
        "description": "GLL Treaty Evidence Bundle – key artifacts for nuclear/treaty/audit work.",
        "doc_roots": {
            "src_docs": str(SRC_DOCS),
            "root_docs": str(ROOT_DOCS),
        },
        "artifacts": entries,
        "missing_artifacts": missing,
    }

    OUTPUT_PATH.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    return {
        "bundle_path": str(OUTPUT_PATH),
        "bundle": bundle,
    }


if __name__ == "__main__":
    result = build_treaty_evidence_bundle()
    print("Treaty Evidence Bundle written:")
    print(f"  JSON: {result['bundle_path']}")
    if result["bundle"].get("missing_artifacts"):
        print("Missing artifacts:")
        for m in result["bundle"]["missing_artifacts"]:
            print(f"  - {m['label']} ({m['key']})")

