from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from demo_lock import enforce_demo_lock


BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _present(path: Path) -> Dict[str, Any]:
    return {"path": str(path), "present": path.exists()}


def _preview_txt(path: Path, max_chars: int = 800) -> str:
    try:
        if not path.exists():
            return "MISSING"
        s = path.read_text(encoding="utf-8")
        return s[:max_chars]
    except Exception:
        return "UNREADABLE"


def _open_folder_best_effort(folder: Path) -> str:
    try:
        # macOS: open
        subprocess.run(["open", str(folder)], check=False)
        return "OK:open_called"
    except Exception:
        return "SKIP:open_failed"


def run_mobile_enjoy_mode(context: str = "week3_mobile_enjoy_mode") -> Dict[str, Any]:
    """
    Read-only demo utility: emits a manifest of the demo-safe artifacts and opens the folder.
    Must never crash.
    """
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "commander_brief_txt": _present(BRIEFS_DIR / "commander_brief_latest.txt"),
        "commander_brief_json": _present(BRIEFS_DIR / "commander_brief_latest.json"),
        "week3_operator_summary_txt": _present(BRIEFS_DIR / "week3_operator_summary_latest.txt"),
        "legal_case_snapshot_txt": _present(BRIEFS_DIR / "legal_case_snapshot_latest.txt"),
        "legal_case_snapshot_json": _present(BRIEFS_DIR / "legal_case_snapshot_latest.json"),
        "legal_case_snapshot_stress": _present(BRIEFS_DIR / "legal_case_snapshot_stress_latest.json"),
        "week3_demo_pack_gate": _present(VALIDATION_DIR / "week3_demo_pack_gate_latest.json"),
        "fusion_core_regression_txt": _present(VALIDATION_DIR / "fusion_core_regression_latest.txt"),
        "fusion_core_regression_json": _present(VALIDATION_DIR / "fusion_core_regression_latest.json"),
    }

    result: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "context": context,
        "briefs_dir": str(BRIEFS_DIR),
        "validation_dir": str(VALIDATION_DIR),
        "artifacts": artifacts,
        "open_folder": _open_folder_best_effort(BRIEFS_DIR),
        "notes": [
            "Assessment is probabilistic and bounded; operator judgment applies.",
            "This mode is read-only and demo-safe. No baselines updated.",
        ],
        "previews": {
            "week3_operator_summary": _preview_txt(BRIEFS_DIR / "week3_operator_summary_latest.txt"),
            "legal_case_snapshot": _preview_txt(BRIEFS_DIR / "legal_case_snapshot_latest.txt"),
            "commander_brief_head": _preview_txt(BRIEFS_DIR / "commander_brief_latest.txt"),
        },
    }

    # DEMO LOCK ENFORCEMENT (requested)
    result.update(enforce_demo_lock("week3_mobile_enjoy_mode"))

    latest_manifest = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
    stamped_manifest = BRIEFS_DIR / f"mobile_enjoy_manifest_{_stamp()}.json"
    _write_json(latest_manifest, result)
    _write_json(stamped_manifest, result)

    result["manifest_latest"] = str(latest_manifest)
    result["manifest_stamped"] = str(stamped_manifest)

    return result


def main() -> int:
    res = run_mobile_enjoy_mode()
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

