#!/usr/bin/env python3
"""
sps_mutation_watcher.py

Ghost Lantern Labs – SPS Module 2 (Mutation Watcher v2)
-------------------------------------------------------

Purpose:
    Provide a lightweight integrity check for mission-critical GLL modules.

    - Computes SHA-256 hashes for key files.
    - Stores a baseline in src/docs/sps_integrity_baseline.json.
    - Compares current hashes to baseline.
    - Reports per-file status: CLEAN / MODIFIED / MISSING.
    - Exposes a high-level "immunity scan" summary.

This is NOT anti-malware magic – it is a practical guardrail:
    "Did someone (or you) change core modules without updating the baseline?"
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
from typing import Dict, Any


SRC_DIR = Path(__file__).resolve().parent          # .../src
DOCS_DIR = SRC_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_PATH = DOCS_DIR / "sps_integrity_baseline.json"

# Mission-critical modules / apps we want to watch.
# Paths are relative to src/.
CRITICAL_PATHS = {
    # Core fusion / ISR brain
    "fusion_ingest.py": Path("fusion_ingest.py"),
    "fusion_sanitizer.py": Path("fusion_sanitizer.py"),
    "fusion_scoring.py": Path("fusion_scoring.py"),
    "fusion_alerts.py": Path("fusion_alerts.py"),

    # Mission briefs / dashboard plumbing
    "daily_mission_brief.py": Path("daily_mission_brief.py"),
    "mission_brief_html.py": Path("mission_brief_html.py"),
    "spectral_dashboard_api.py": Path("spectral_dashboard_api.py"),

    # Training + scenario engines
    "training_curve_engine.py": Path("training_curve_engine.py"),
    "scenario_engine.py": Path("scenario_engine.py"),
    "shari_legal_pack.py": Path("shari_legal_pack.py"),

    # CLI & GUI entrypoints
    "ghost_cli.py": Path("ghost_cli.py"),
    "apps/gui/app.py": Path("apps/gui/app.py"),
    "apps/gui/joint_readiness_app.py": Path("apps/gui/joint_readiness_app.py"),
    "apps/gui/training_dashboard_app.py": Path("apps/gui/training_dashboard_app.py"),
    "apps/gui/mission_scenario_app.py": Path("apps/gui/mission_scenario_app.py"),
}


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def _hash_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_baseline() -> Dict[str, str]:
    if not BASELINE_PATH.exists():
        return {}
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def generate_integrity_baseline() -> Dict[str, str]:
    """
    Generate a fresh baseline of hashes for all CRITICAL_PATHS
    that currently exist. Overwrites any existing baseline.
    """
    baseline: Dict[str, str] = {}
    for label, rel_path in CRITICAL_PATHS.items():
        fpath = SRC_DIR / rel_path
        if fpath.exists():
            baseline[label] = _hash_file(fpath)
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    return baseline


def check_integrity() -> Dict[str, str]:
    """
    Compare current file hashes to the baseline.

    Returns:
        dict: {label: "CLEAN" | "MODIFIED" | "MISSING" | "UNTRACKED_BASELINE"}
    """
    baseline = _load_baseline()
    if not baseline:
        baseline = generate_integrity_baseline()

    report: Dict[str, str] = {}

    # Check files in baseline (what we care about).
    for label, base_hash in baseline.items():
        rel_path = CRITICAL_PATHS.get(label)
        if rel_path is None:
            # Baseline knows a file we no longer track – flag it.
            report[label] = "UNTRACKED_BASELINE"
            continue

        fpath = SRC_DIR / rel_path
        if not fpath.exists():
            report[label] = "MISSING"
            continue

        current_hash = _hash_file(fpath)
        if current_hash == base_hash:
            report[label] = "CLEAN"
        else:
            report[label] = "MODIFIED"

    # Any CRITICAL_PATHS not yet in baseline get no status – that is okay.
    return report


def run_sps_immunity_scan() -> Dict[str, Any]:
    """
    High-level wrapper that computes a summary:
        - clean / modified / missing counts
        - per-file statuses
    """
    report = check_integrity()

    clean = sum(1 for s in report.values() if s == "CLEAN")
    modified = sum(1 for s in report.values() if s == "MODIFIED")
    missing = sum(1 for s in report.values() if s == "MISSING")
    untracked = sum(1 for s in report.values() if s == "UNTRACKED_BASELINE")

    return {
        "summary": {
            "clean": clean,
            "modified": modified,
            "missing": missing,
            "untracked_baseline": untracked,
            "total_tracked": len(report),
        },
        "files": report,
        "baseline_path": str(BASELINE_PATH),
    }


if __name__ == "__main__":
    print(json.dumps(run_sps_immunity_scan(), indent=2))

