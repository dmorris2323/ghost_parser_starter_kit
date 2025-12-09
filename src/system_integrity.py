"""
system_integrity.py — GLL System Integrity & Sanity Check

This module verifies:
- Critical files exist (data, docs, configs)
- Sensor profiles & manifests are present
- Recent run-history and fusion outputs exist

It is defensive and WILL NOT crash if something is missing.
Instead, it records "missing" status and continues.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List


ROOT = Path(__file__).resolve().parent.parent  # repo root (../.. from src/)
SRC = Path(__file__).resolve().parent
DOCS = SRC / "docs"
DATA = SRC / "data"
CONFIG = SRC / "config"


def _check_file(path: Path) -> Dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def _check_dir(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "items": 0}
    return {
        "path": str(path),
        "exists": True,
        "items": len(list(path.iterdir())),
    }


def compute_system_integrity() -> Dict[str, Any]:
    checks: Dict[str, Any] = {}

    # Core directories
    checks["dirs"] = {
        "src": _check_dir(SRC),
        "data": _check_dir(DATA),
        "docs": _check_dir(DOCS),
        "config": _check_dir(CONFIG),
    }

    # Key data artifacts
    checks["data_files"] = {
        "fused_output.csv": _check_file(DATA / "fused_output.csv"),
        "scored_output.csv": _check_file(DATA / "scored_output.csv"),
        "run_history.csv": _check_file(DATA / "run_history.csv"),
        "sensor_ingest.csv": _check_file(DATA / "sensor_ingest.csv"),
    }

    # Mission brief artifacts
    checks["docs_files"] = {
        "daily_mission_brief.txt": _check_file(DOCS / "daily_mission_brief.txt"),
        "daily_mission_brief.html": _check_file(DOCS / "daily_mission_brief.html"),
        "gll_readiness.json": _check_file(DOCS / "gll_readiness.json"),
    }

    # Sensor manifest / profiles
    manifest = SRC / "sensor_manifest.json"
    profiles_dir = SRC / "sensor_profiles"
    checks["sensor_manifest"] = _check_file(manifest)
    checks["sensor_profiles_dir"] = _check_dir(profiles_dir)

    # Simple health summary
    missing: List[str] = []
    for section, vals in checks.items():
        if isinstance(vals, dict):
            for name, info in vals.items():
                if isinstance(info, dict) and not info.get("exists", True):
                    missing.append(f"{section}.{name}")

    status = "GREEN"
    if missing:
        if len(missing) > 5:
            status = "RED"
        else:
            status = "YELLOW"

    return {
        "status": status,
        "missing_items": missing,
        "checks": checks,
    }


def write_system_integrity(path: str | Path = "docs/system_integrity_report.txt") -> str:
    """
    Writes a human-readable integrity report and returns path.
    """
    res = compute_system_integrity()
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("=== GLL SYSTEM INTEGRITY REPORT ===")
    lines.append(f"Status: {res['status']}")
    lines.append("")

    if res["missing_items"]:
        lines.append("Missing or non-existent items:")
        for item in res["missing_items"]:
            lines.append(f"  - {item}")
        lines.append("")
    else:
        lines.append("All critical checked items present.")
        lines.append("")

    lines.append("Raw JSON:")
    lines.append(json.dumps(res, indent=2))

    p.write_text("\n".join(lines))
    return str(p)


if __name__ == "__main__":
    print(write_system_integrity())

