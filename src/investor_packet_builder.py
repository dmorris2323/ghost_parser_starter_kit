"""
investor_packet_builder.py

Ghost Lantern Labs – Investor / Commander Demo Packet Builder

Creates a timestamped demo packet under:
  src/docs/demo_packets/packet_YYYYMMDD_HHMMSS/

Copies in whatever key artifacts exist:
- daily mission briefs (txt + html)
- reliability report
- cross-sensor report
- exercise readiness brief
- demo deck manifest
- spectral snapshot / dashboard bundles (if any)

Also writes:
- manifest.json
- README_demo_packet.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
PACK_ROOT = DOCS_DIR / "demo_packets"


@dataclass
class PacketFile:
    label: str
    source: str
    copied_to: Optional[str]
    exists: bool


@dataclass
class PacketManifest:
    packet_id: str
    created_at: str
    base_dir: str
    files: List[PacketFile]


def _now_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _candidate_files() -> List[PacketFile]:
    """
    Define which artifacts we try to include.
    Paths are relative to src/.
    """
    mapping = [
        ("Daily Mission Brief (txt)", DOCS_DIR / "daily_mission_brief.txt"),
        ("Daily Mission Brief (html)", DOCS_DIR / "daily_mission_brief.html"),
        ("Profile Mission Brief", DOCS_DIR / "profile_mission_brief.txt"),
        ("Reliability Report", DOCS_DIR / "reliability_report.txt"),
        ("Cross-Sensor Report", DOCS_DIR / "cross_sensor_report.txt"),
        ("Exercise Readiness Brief (Pacific)", DOCS_DIR / "exercise_brief_pacific.txt"),
        ("SBIR Readiness Assessment", DOCS_DIR / "sbir_readiness_assessment.txt"),
        ("SBIR Score JSON", DOCS_DIR / "sbir_readiness_score.json"),
        ("Demo Deck Manifest", DOCS_DIR / "demo_deck_manifest_day58.json"),
        ("Spectral Snapshot Bundle", DOCS_DIR / "spectral_snapshot_bundle.json"),
        ("Spectral Dashboard Bundle", DOCS_DIR / "spectral_dashboard.json"),
    ]

    files: List[PacketFile] = []
    for label, path in mapping:
        exists = path.exists()
        files.append(
            PacketFile(
                label=label,
                source=str(path),
                copied_to=None,
                exists=exists,
            )
        )
    return files


def build_packet() -> PacketManifest:
    PACK_ROOT.mkdir(parents=True, exist_ok=True)

    slug = _now_slug()
    packet_dir = PACK_ROOT / f"packet_{slug}"
    packet_dir.mkdir(parents=True, exist_ok=True)

    candidates = _candidate_files()
    updated_files: List[PacketFile] = []

    for pf in candidates:
        src_path = Path(pf.source)
        if src_path.exists():
            dest_path = packet_dir / src_path.name
            try:
                # Copy file contents
                dest_path.write_text(src_path.read_text())
                updated_files.append(
                    PacketFile(
                        label=pf.label,
                        source=pf.source,
                        copied_to=str(dest_path),
                        exists=True,
                    )
                )
            except Exception:
                # If copy fails, mark as not copied but existing
                updated_files.append(
                    PacketFile(
                        label=pf.label,
                        source=pf.source,
                        copied_to=None,
                        exists=True,
                    )
                )
        else:
            updated_files.append(pf)

    manifest = PacketManifest(
        packet_id=slug,
        created_at=datetime.now().isoformat(timespec="seconds"),
        base_dir=str(packet_dir),
        files=updated_files,
    )

    # Write manifest.json
    manifest_path = packet_dir / "manifest.json"
    serializable = asdict(manifest)
    manifest_path.write_text(json.dumps(serializable, indent=2))

    # Write README
    readme_path = packet_dir / "README_demo_packet.txt"
    lines = []
    lines.append("Ghost Lantern Labs — Demo Packet")
    lines.append("--------------------------------")
    lines.append(f"Packet ID: {slug}")
    lines.append(f"Created At: {manifest.created_at}")
    lines.append("")
    lines.append("This folder is a snapshot of key demo artifacts from GLL.")
    lines.append("Files may include mission briefs, reliability reports,")
    lines.append("cross-sensor validation, SBIR readiness, and demo manifests.")
    lines.append("")
    lines.append("Suggested uses:")
    lines.append("- Attach to emails for advisors/investors/mentors.")
    lines.append("- Use as a briefing packet for internal commander demos.")
    lines.append("- Archive milestone states of GLL as you progress.")
    lines.append("")
    lines.append("Files in this packet:")
    for pf in updated_files:
        status = "COPIED" if (pf.exists and pf.copied_to) else ("MISSING" if not pf.exists else "EXISTS (not copied)")
        lines.append(f"- {pf.label}: {status}")
    lines.append("")

    readme_path.write_text("\n".join(lines))

    return manifest


def write_packet() -> Dict[str, str]:
    manifest = build_packet()
    packet_dir = Path(manifest.base_dir)
    return {
        "packet_dir": str(packet_dir),
        "manifest": str(packet_dir / "manifest.json"),
        "readme": str(packet_dir / "README_demo_packet.txt"),
    }


if __name__ == "__main__":
    out = write_packet()
    print("Demo packet created:")
    for k, v in out.items():
        print(f"  {k}: {v}")

