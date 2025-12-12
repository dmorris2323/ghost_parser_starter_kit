# instructor_pack_export.py
# Module 6 — Instructor Pack Export (zip-like manifest + links) (SAFE)
#
# Produces a single manifest JSON that "packages" a run:
#  - scenario packet
#  - telemetry bundle
#  - rubric grade report (Module 4)
#  - AAR report (Module 5)
#  - training sessions log
#  - optional curve/summary artifacts if present
#
# No zipping to keep it simple/portable. Manifest includes file paths + SHA256 hashes.

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


def _sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_stat(path: Path) -> Dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"exists": False, "path": str(path)}
    return {
        "exists": True,
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "modified_utc": datetime.utcfromtimestamp(path.stat().st_mtime).isoformat(),
    }


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return str(path)


def export_instructor_packet(
    scenario_json_path: str,
    grade_json_path: Optional[str] = None,
    aar_json_path: Optional[str] = None,
    trainee: str = "Ghost",
    include_optional_artifacts: bool = True,
) -> Dict[str, Any]:
    """
    scenario_json_path: required path to scenario packet json
    grade_json_path: optional rubric grade report json path
    aar_json_path: optional AAR json path
    """
    scenario_path = Path(scenario_json_path)
    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario not found: {scenario_json_path}")

    scenario = _load_json(scenario_path)
    scenario_id = scenario.get("scenario_id", "unknown")
    telemetry_path = Path(scenario.get("telemetry_json_path", "")) if scenario.get("telemetry_json_path") else None

    # standard logs
    sessions_log = Path("src/docs/training/training_sessions.json")

    # optional artifacts
    optional: Dict[str, Any] = {}
    if include_optional_artifacts:
        # "latest" files (best-effort)
        optional["latest_grade"] = _safe_stat(Path("src/docs/training/grades/rubric_latest.json"))
        optional["latest_aar"] = _safe_stat(Path("src/docs/training/aars/aar_latest.json"))
        optional["latest_scenario"] = _safe_stat(Path("src/docs/scenarios/scenario_latest.json"))
        # GUI bundle (if you export it)
        optional["spectral_dashboard_bundle"] = _safe_stat(Path("outputs/spectral_dashboard.json"))
        # Training curve engine might not exist yet (best-effort)
        optional["training_curve_latest"] = _safe_stat(Path("src/docs/training/training_curve_latest.json"))

    pack = {
        "instructor_packet_version": 1,
        "generated_at": datetime.utcnow().isoformat(),
        "trainee": trainee,
        "scenario": {
            "scenario_id": scenario_id,
            "difficulty": scenario.get("difficulty_used"),
            "patterns_truth": scenario.get("patterns_used", []),
            "scenario_json": _safe_stat(scenario_path),
            "telemetry_json": _safe_stat(telemetry_path) if telemetry_path else {"exists": False, "path": None},
        },
        "grading": {
            "grade_report_json": _safe_stat(Path(grade_json_path)) if grade_json_path else {"exists": False, "path": None},
        },
        "aar": {
            "aar_json": _safe_stat(Path(aar_json_path)) if aar_json_path else {"exists": False, "path": None},
        },
        "training_log": _safe_stat(sessions_log),
        "optional_artifacts": optional,
        "safe_notice": "Synthetic-only training packet. No real-world sensitive telemetry.",
    }

    out_dir = Path("src/docs/training/instructor_packs")
    ts = int(datetime.utcnow().timestamp())
    out_path = out_dir / f"instructor_packet_{scenario_id}_{ts}.json"
    latest_path = out_dir / "instructor_packet_latest.json"

    _write_json(out_path, pack)
    _write_json(latest_path, pack)

    return {
        "packet_path": str(out_path),
        "latest_path": str(latest_path),
        "scenario_id": scenario_id,
    }

