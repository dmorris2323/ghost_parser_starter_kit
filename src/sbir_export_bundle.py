"""
sbir_export_bundle.py

Builds a self-contained "SBIR / Demo Export Bundle" directory that
collects the latest:

- Scenario Pack JSON
- Capability Snapshot Markdown
- A small JSON manifest
- A human-readable README

Intended for:
- SBIR / AFWERX style concept packages
- Demo handoffs
- Portfolio artifacts

Output directory (created if missing):
  src/docs/sbir_export_bundle/

Files inside:
  - scenario_pack.json
  - capability_snapshot.md
  - manifest.json
  - README_SBIR_BUNDLE.md
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)

BUNDLE_DIR = DOCS_DIR / "sbir_export_bundle"

SCENARIO_SRC = DOCS_DIR / "scenario_pack_latest.json"
SNAPSHOT_SRC = DOCS_DIR / "capability_snapshot.md"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_bundle_dir() -> None:
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)


def _copy_if_exists(src: Path, dst: Path) -> Dict[str, Any]:
    """
    Copy file if it exists; otherwise return a status noting it's missing.
    """
    if not src.exists():
        return {
            "status": "missing",
            "source": str(src),
            "dest": str(dst),
        }

    shutil.copyfile(src, dst)
    return {
        "status": "copied",
        "source": str(src),
        "dest": str(dst),
        "size_bytes": dst.stat().st_size,
    }


def _build_manifest(copy_results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generated_at": _utc_now_iso(),
        "bundle_dir": str(BUNDLE_DIR),
        "files": copy_results,
        "notes": [
            "This bundle is designed as a lightweight export package for demos,",
            "SBIR concept handoffs, or portfolio artifacts.",
            "It intentionally avoids any classified, proprietary, or environment-specific data.",
        ],
    }


def _write_manifest(manifest: Dict[str, Any]) -> Path:
    path = BUNDLE_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2))
    return path


def _write_readme(manifest: Dict[str, Any]) -> Path:
    """
    Write a human-readable README explaining what's in the bundle.
    """
    path = BUNDLE_DIR / "README_SBIR_BUNDLE.md"
    lines = []

    lines.append("# Ghost Lantern Labs — SBIR / Demo Export Bundle")
    lines.append("")
    lines.append(f"**Generated:** {manifest.get('generated_at', _utc_now_iso())}")
    lines.append("")
    lines.append("This folder contains a small, self-contained snapshot of the current")
    lines.append("Ghost Lantern Labs (GLL) prototype state, suitable for:")
    lines.append("")
    lines.append("- Early technical demos")
    lines.append("- Concept briefs for mentors or partners")
    lines.append("- SBIR / AFWERX style exploration (concept-level only)")
    lines.append("- Portfolio evidence of engineering work")
    lines.append("")
    lines.append("## Included Files")
    lines.append("")

    files = manifest.get("files", {})
    scenario_info = files.get("scenario_pack", {})
    snapshot_info = files.get("capability_snapshot", {})

    # Scenario pack description
    lines.append("### `scenario_pack.json`")
    if scenario_info.get("status") == "copied":
        lines.append("- Status: copied successfully")
    else:
        lines.append("- Status: MISSING (scenario pack was not available at export time)")
    lines.append(
        "- Contains: Fusion Trust, Operator Safety Layer, mini-map, and SOS overlay "
        "stitched into one JSON document."
    )
    lines.append("")

    # Capability snapshot description
    lines.append("### `capability_snapshot.md`")
    if snapshot_info.get("status") == "copied":
        lines.append("- Status: copied successfully")
    else:
        lines.append("- Status: MISSING (capability snapshot was not available at export time)")
    lines.append(
        "- Contains: Human-readable summary of GLL capabilities, including current "
        "fusion trust and safety posture where available."
    )
    lines.append("")

    lines.append("### `manifest.json`")
    lines.append(
        "- Machine-readable summary describing where this bundle was generated, "
        "which files exist, and any missing pieces."
    )
    lines.append("")

    lines.append("### `README_SBIR_BUNDLE.md`")
    lines.append("- This file. Explains the bundle in plain language.")
    lines.append("")

    lines.append("## Regeneration")
    lines.append("")
    lines.append("To regenerate this bundle from the project root:")
    lines.append("")
    lines.append("```bash")
    lines.append("cd src")
    lines.append("python scenario_pack_builder.py")
    lines.append("python capability_snapshot.py")
    lines.append("python sbir_export_bundle.py")
    lines.append("```")
    lines.append("")
    lines.append("This will refresh the scenario pack, capability snapshot, and rebuild this bundle.")
    lines.append("")

    path.write_text("\n".join(lines))
    return path


def build_sbir_bundle() -> Dict[str, Any]:
    """
    Main orchestration function to build the SBIR/demo bundle.
    """
    _ensure_bundle_dir()

    # Targets inside the bundle
    scenario_dst = BUNDLE_DIR / "scenario_pack.json"
    snapshot_dst = BUNDLE_DIR / "capability_snapshot.md"

    copy_results = {
        "scenario_pack": _copy_if_exists(SCENARIO_SRC, scenario_dst),
        "capability_snapshot": _copy_if_exists(SNAPSHOT_SRC, snapshot_dst),
    }

    manifest = _build_manifest(copy_results)
    manifest_path = _write_manifest(manifest)
    readme_path = _write_readme(manifest)

    return {
        "status": "ok",
        "bundle_dir": str(BUNDLE_DIR),
        "manifest": str(manifest_path),
        "readme": str(readme_path),
        "files": copy_results,
    }


if __name__ == "__main__":
    out = build_sbir_bundle()
    print("=== SBIR / Demo Export Bundle ===")
    print(f"Bundle dir : {out['bundle_dir']}")
    print(f"Manifest   : {out['manifest']}")
    print(f"README     : {out['readme']}")
    print("Files:")
    for key, info in out["files"].items():
        print(f"  - {key}: {info['status']}")

