# src/week3_demo_freeze_packager.py
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from demo_freeze_loader import load_demo_freeze_manifest, is_demo_safe


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


_THIS = Path(__file__).resolve()
SRC_DIR = _THIS.parent
REPO_ROOT = SRC_DIR.parent

DEMO_DIR = REPO_ROOT / "docs" / "demo"
PKG_DIR = REPO_ROOT / "docs" / "packages"


def _write_json(p: Path, obj: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def run_week3_demo_freeze_packager() -> Dict[str, Any]:
    manifest = load_demo_freeze_manifest()
    demo_safe = is_demo_safe(manifest)

    required_files = list(manifest.get("required_files", [])) if isinstance(manifest.get("required_files"), list) else []
    optional_files = list(manifest.get("optional_files", [])) if isinstance(manifest.get("optional_files"), list) else []

    missing = [rel for rel in required_files if not (REPO_ROOT / rel).exists()]

    stamp = _utc_stamp()

    # Outputs
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    PKG_DIR.mkdir(parents=True, exist_ok=True)

    manifest_latest = DEMO_DIR / "demo_freeze_manifest_latest.json"
    manifest_stamped = DEMO_DIR / f"demo_freeze_manifest_{stamp}.json"

    pack_latest = PKG_DIR / "week3_demo_freeze_pack_latest.zip"
    pack_stamped = PKG_DIR / f"week3_demo_freeze_pack_{stamp}.zip"

    # Write normalized manifest copies
    normalized = dict(manifest)
    normalized["packaged_at_utc"] = datetime.now(timezone.utc).isoformat()
    normalized["demo_safe_resolved"] = demo_safe
    normalized["required_missing_resolved"] = missing

    _write_json(manifest_latest, normalized)
    _write_json(manifest_stamped, normalized)

    # Build ZIP (manifest + required + optional if present)
    files_to_zip: List[str] = []
    files_to_zip.append(str(manifest_latest.relative_to(REPO_ROOT)))

    for rel in required_files:
        p = REPO_ROOT / rel
        if p.exists():
            files_to_zip.append(rel)

    for rel in optional_files:
        p = REPO_ROOT / rel
        if p.exists():
            files_to_zip.append(rel)

    def _zip(zip_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for rel in files_to_zip:
                p = REPO_ROOT / rel
                if p.exists():
                    z.write(p, arcname=rel)

    _zip(pack_latest)
    _zip(pack_stamped)

    verdict = "PASS" if demo_safe and not missing else "FAIL"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "context": "week3_demo_freeze_packager",
        "verdict": verdict,
        "demo_safe": demo_safe,
        "required_missing": missing,
        "manifest_latest": str(manifest_latest),
        "manifest_stamped": str(manifest_stamped),
        "zip_latest": str(pack_latest),
        "zip_stamped": str(pack_stamped),
        "zipped_files": files_to_zip,
    }
    return out


def main() -> int:
    out = run_week3_demo_freeze_packager()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

