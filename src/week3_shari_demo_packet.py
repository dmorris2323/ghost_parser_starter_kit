from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_copy(src: Path, dst: Path, manifest: Dict[str, Any]) -> None:
    """
    Copy file if present. Record status in manifest.
    """
    if src.exists():
        shutil.copy2(src, dst)
        manifest["files"].append(
            {"name": src.name, "copied": True, "source": str(src)}
        )
    else:
        manifest["files"].append(
            {"name": src.name, "copied": False, "source": str(src)}
        )


def run_week3_shari_demo_packet(
    context: str = "week3_shari_demo_packet",
) -> Dict[str, Any]:
    """
    Build a single demo folder suitable for:
      - Mobile viewing
      - AirDrop / zip
      - Non-technical walkthrough (Shari)

    This is READ-ONLY and demo-safe.
    """

    generated_at = _utc_now_iso()
    stamp = _stamp()

    packet_dir = BRIEFS_DIR / "shari_demo_packet_latest"
    stamped_dir = BRIEFS_DIR / f"shari_demo_packet_{stamp}"

    packet_dir.mkdir(parents=True, exist_ok=True)
    stamped_dir.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "context": context,
        "packet_latest": str(packet_dir),
        "packet_stamped": str(stamped_dir),
        "files": [],
        "notes": [
            "This packet is demo-only and read-only.",
            "Assessment is probabilistic and bounded; operator judgment applies.",
        ],
    }

    # -----------------------------
    # Core demo artifacts
    # -----------------------------
    artifacts = [
        BRIEFS_DIR / "commander_brief_latest.txt",
        BRIEFS_DIR / "commander_brief_latest.json",
        BRIEFS_DIR / "week3_operator_summary_latest.txt",
        BRIEFS_DIR / "legal_case_snapshot_latest.txt",
        BRIEFS_DIR / "legal_case_snapshot_latest.json",
        BRIEFS_DIR / "week3_shari_demo_checklist_latest.txt",
        BRIEFS_DIR / "mobile_enjoy_manifest_latest.json",
        VALIDATION_DIR / "week3_demo_pack_gate_latest.json",
        VALIDATION_DIR / "fusion_core_regression_latest.json",
    ]

    for src in artifacts:
        _safe_copy(src, packet_dir / src.name, manifest)
        _safe_copy(src, stamped_dir / src.name, manifest)

    # -----------------------------
    # README for non-technical user
    # -----------------------------
    readme_text = (
        "GHOST LANTERN LABS — SHARI DEMO PACK\n"
        "==================================\n\n"
        "START HERE (recommended order):\n"
        "1) week3_shari_demo_checklist_latest.txt\n"
        "2) legal_case_snapshot_latest.txt\n"
        "3) week3_operator_summary_latest.txt\n"
        "4) commander_brief_latest.txt\n\n"
        "WHAT THIS IS:\n"
        "- A demo-safe intelligence-style decision system\n"
        "- Legal case snapshot mirrors collections/legal reasoning\n"
        "- Outputs are bounded, explainable, and auditable\n\n"
        "WHAT THIS IS NOT:\n"
        "- Not legal advice\n"
        "- Not automated decision-making\n"
        "- Operator judgment always applies\n\n"
        "NOTE:\n"
        "Assessment is probabilistic and bounded; operator judgment applies.\n"
    )

    readme_latest = packet_dir / "README_START_HERE.txt"
    readme_stamped = stamped_dir / "README_START_HERE.txt"

    readme_latest.write_text(readme_text, encoding="utf-8")
    readme_stamped.write_text(readme_text, encoding="utf-8")

    manifest["files"].append(
        {"name": "README_START_HERE.txt", "copied": True, "source": "generated"}
    )

    # -----------------------------
    # Write manifest
    # -----------------------------
    manifest_latest = packet_dir / "shari_demo_packet_manifest.json"
    manifest_stamped = stamped_dir / "shari_demo_packet_manifest.json"

    manifest_latest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest_stamped.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "generated_at_utc": generated_at,
        "context": context,
        "packet_latest": str(packet_dir),
        "packet_stamped": str(stamped_dir),
        "manifest_latest": str(manifest_latest),
        "manifest_stamped": str(manifest_stamped),
        "verdict": "PASS",
        "notes": manifest["notes"],
    }


def main() -> int:
    out = run_week3_shari_demo_packet()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

