#!/usr/bin/env python3
"""
nuclear_brief_packet.py

Day 66 – Ghost Lantern Labs

Builds a single, commander-facing Nuclear Brief Packet that stitches together:
- Nuclear Status Summary
- Escalation Ladder
- Treaty Evidence Bundle overview

Outputs:
- docs/nuclear_brief_packet.txt

This is designed to be the "print this and hand it to the CO/CC" product,
or the first page in a SBIR/AFWERX or AFTAC-style demo.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def build_nuclear_brief_packet() -> str:
    os.makedirs(DOCS_DIR, exist_ok=True)

    status_json_path = os.path.join(DOCS_DIR, "nuclear_status_summary.json")
    status_txt_path = os.path.join(DOCS_DIR, "nuclear_status_summary.txt")
    ladder_json_path = os.path.join(DOCS_DIR, "escalation_ladder.json")
    ladder_txt_path = os.path.join(DOCS_DIR, "escalation_ladder.txt")
    treaty_bundle_path = os.path.join(DOCS_DIR, "treaty_evidence_bundle.json")

    status_json = _safe_read_json(status_json_path)
    status_txt = _safe_read_text(status_txt_path)
    ladder_json = _safe_read_json(ladder_json_path)
    ladder_txt = _safe_read_text(ladder_txt_path)
    treaty_bundle = _safe_read_json(treaty_bundle_path)

    # Pull out a few key lines for fast reading
    escalation_level = None
    ladder_rationale = None
    if ladder_json:
        escalation_level = ladder_json.get("escalation_level")
        ladder_rationale = ladder_json.get("rationale")

    crisis_line = None
    golden_dome_line = None
    if status_json:
        signals = status_json.get("nuclear_signals", {})
        crisis_line = signals.get("crisis_mode_line")
        golden_dome_line = signals.get("golden_dome_readiness_line")

    # Build plain-text packet
    lines = []
    lines.append("GLL Nuclear Brief Packet")
    lines.append("========================")
    lines.append(f"Generated at (UTC): {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append("1. High-Level Nuclear Posture Snapshot")
    lines.append("--------------------------------------")
    lines.append(f"  Escalation Level: {escalation_level or 'UNKNOWN'}")
    lines.append(f"  Crisis Mode Line: {crisis_line or 'UNKNOWN'}")
    lines.append(f"  Golden Dome Readiness Line: {golden_dome_line or 'UNKNOWN'}")
    lines.append("")
    if ladder_rationale:
        lines.append("  Escalation Rationale:")
        lines.append(f"    {ladder_rationale}")
        lines.append("")
    else:
        lines.append("  Escalation Rationale: [No escalation ladder rationale available]")
        lines.append("")

    lines.append("2. Nuclear Status Summary (Excerpt)")
    lines.append("----------------------------------")
    if status_txt:
        # Show the first ~60 lines or so
        excerpt_lines = status_txt.splitlines()[:60]
        lines.extend(f"  {ln}" for ln in excerpt_lines)
    else:
        lines.append("  [No nuclear_status_summary.txt available]")
    lines.append("")

    lines.append("3. Escalation Ladder (Full Text)")
    lines.append("--------------------------------")
    if ladder_txt:
        for ln in ladder_txt.splitlines():
            lines.append(f"  {ln}")
    else:
        lines.append("  [No escalation_ladder.txt available]")
    lines.append("")

    lines.append("4. Treaty Evidence Bundle Overview")
    lines.append("----------------------------------")
    if treaty_bundle and isinstance(treaty_bundle, dict):
        artifacts = treaty_bundle.get("artifacts", [])
        if artifacts:
            for art in artifacts:
                name = art.get("name")
                path = art.get("path")
                exists = art.get("exists")
                desc = art.get("description")
                lines.append(f"  - {name}:")
                lines.append(f"      Path: {path}")
                lines.append(f"      Exists: {exists}")
                if desc:
                    lines.append(f"      Description: {desc}")
                lines.append("")
        else:
            lines.append("  [Treaty evidence bundle has no artifacts listed]")
    else:
        lines.append("  [No treaty_evidence_bundle.json available]")
    lines.append("")

    lines.append("5. Commander Notes")
    lines.append("-------------------")
    lines.append("  - Use this packet as a starting point for deeper review.")
    lines.append("  - Pair with full mission brief, sensor reports, and higher HQ guidance.")
    lines.append("  - GLL is providing an integrated nuclear/treaty snapshot, not a final adjudication.")
    lines.append("")

    out_path = os.path.join(DOCS_DIR, "nuclear_brief_packet.txt")
    packet_text = "\n".join(lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(packet_text)

    return out_path


if __name__ == "__main__":
    path = build_nuclear_brief_packet()
    print("Nuclear Brief Packet generated:")
    print(f"  - {path}")

