from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BRIEFS_DIR = Path("docs") / "briefs"
VALID_DIR = Path("docs") / "validation"

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

def _read_txt_best_effort(p: Path, max_chars: int = 1200) -> str:
    try:
        if not _exists(p):
            return ""
        s = p.read_text(encoding="utf-8", errors="replace")
        return s[:max_chars]
    except Exception:
        return ""

def _open_folder_best_effort(folder: Path) -> str:
    """
    Best-effort open on macOS; safe no-op elsewhere.
    Returns a short status string.
    """
    try:
        if not _exists(folder):
            return "SKIP:folder_missing"
        # macOS Finder open
        subprocess.run(["open", str(folder)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "OK:open_called"
    except Exception:
        return "SKIP:open_failed"

def run_mobile_enjoy_mode(context: str = "week3_mobile_enjoy_mode") -> Dict[str, Any]:
    """
    Prints the 'demo pack' paths for quick viewing on desktop or mobile.
    Must never crash.
    """

    # Core demo artifacts (latest)
    paths = {
        "commander_brief_txt": BRIEFS_DIR / "commander_brief_latest.txt",
        "commander_brief_json": BRIEFS_DIR / "commander_brief_latest.json",
        "week3_operator_summary_txt": BRIEFS_DIR / "week3_operator_summary_latest.txt",
        "legal_case_snapshot_txt": BRIEFS_DIR / "legal_case_snapshot_latest.txt",
        "legal_case_snapshot_json": BRIEFS_DIR / "legal_case_snapshot_latest.json",
        "legal_case_snapshot_stress": BRIEFS_DIR / "legal_case_snapshot_stress_latest.json",
        "week3_demo_pack_gate": VALID_DIR / "week3_demo_pack_gate_latest.json",
        "fusion_core_regression_txt": Path("docs") / "validation" / "fusion_core_regression_latest.txt",
        "fusion_core_regression_json": Path("docs") / "validation" / "fusion_core_regression_latest.json",
    }

    manifest: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "context": context,
        "briefs_dir": str(BRIEFS_DIR),
        "validation_dir": str(VALID_DIR),
        "artifacts": {},
        "open_folder": None,
        "notes": [
            "Assessment is probabilistic and bounded; operator judgment applies.",
            "This mode is read-only and demo-safe. No baselines updated.",
        ],
    }

    # Collect existence + short previews
    for k, p in paths.items():
        manifest["artifacts"][k] = {
            "path": str(p),
            "present": _exists(p),
        }

    # Optional previews (txt only)
    manifest["previews"] = {
        "week3_operator_summary": _read_txt_best_effort(paths["week3_operator_summary_txt"]),
        "legal_case_snapshot": _read_txt_best_effort(paths["legal_case_snapshot_txt"]),
        "commander_brief_head": _read_txt_best_effort(paths["commander_brief_txt"]),
    }

    # Best-effort open briefs folder (macOS)
    manifest["open_folder"] = _open_folder_best_effort(BRIEFS_DIR)

    # Write a manifest so you can pull it from anywhere
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    latest_manifest = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
    stamped_manifest = BRIEFS_DIR / f"mobile_enjoy_manifest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    latest_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    stamped_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    manifest["manifest_latest"] = str(latest_manifest)
    manifest["manifest_stamped"] = str(stamped_manifest)

    return manifest

def main() -> int:
    res = run_mobile_enjoy_mode()
    print(json.dumps(res, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

