"""
nuclear_mission_brief.py

Builds a narrative nuclear-focused mission brief for Ghost Lantern Labs,
combining:

- Golden Dome nuclear readiness snapshot
- Pre-launch ISR watchboard
- Fusion Heat Index
- (Optionally) GLL readiness headline

Outputs:
- docs/nuclear_mission_brief.txt
- docs/nuclear_mission_brief.md
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"
DOCS.mkdir(exist_ok=True)


def _safe_build_snapshot() -> Dict[str, Any]:
    try:
        from golden_dome_snapshot import build_snapshot  # type: ignore
        return build_snapshot()
    except Exception:
        return {"status": "no_data", "note": "golden_dome_snapshot not available"}


def _safe_build_watchboard() -> Dict[str, Any]:
    try:
        from prelaunch_watchboard import build_watchboard  # type: ignore
        path = Path(build_watchboard())
        if path.exists():
            return json.loads(path.read_text())
        return {"status": "no_file", "path": str(path)}
    except Exception as e:
        return {"status": "error", "note": f"prelaunch_watchboard failed: {e!r}"}


def _safe_compute_fhi() -> Dict[str, Any]:
    try:
        from fusion_heat_index import compute_fhi  # type: ignore
        return compute_fhi()
    except Exception:
        return {"status": "no_data", "note": "fusion_heat_index not available"}


def _safe_readiness_headline() -> str:
    try:
        from gll_readiness import compute_gll_readiness  # type: ignore
        r = compute_gll_readiness()
        status = r.get("status", "unknown")
        score = r.get("score", "n/a")
        return f"GLL readiness status: {status} (score={score})"
    except Exception:
        return "GLL readiness status: unknown (no readiness module response)"


def build_nuclear_mission_brief() -> Dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()

    snapshot = _safe_build_snapshot()
    watchboard = _safe_build_watchboard()
    fhi = _safe_compute_fhi()
    readiness_headline = _safe_readiness_headline()

    txt_path = DOCS / "nuclear_mission_brief.txt"
    md_path = DOCS / "nuclear_mission_brief.md"

    txt_lines = [
        "=== GHOST LANTERN LABS — NUCLEAR MISSION BRIEF ===",
        f"Generated at (UTC): {ts}",
        "",
        readiness_headline,
        "",
        "=== GOLDEN DOME NUCLEAR SNAPSHOT ===",
        json.dumps(snapshot, indent=2),
        "",
        "=== PRE-LAUNCH ISR WATCHBOARD ===",
        json.dumps(watchboard, indent=2),
        "",
        "=== FUSION HEAT INDEX (BATTLESPACE TEMPERATURE) ===",
        json.dumps(fhi, indent=2),
        "",
        "=== NOTES ===",
        "- This brief is NOT real-world tasking; it is an engineering demo.",
        "- Calibrate with real sensor schemas and doctrine before any operational use.",
        "",
    ]
    txt_path.write_text("\n".join(txt_lines))

    md_lines = [
        "# Ghost Lantern Labs — Nuclear Mission Brief",
        "",
        f"**Generated at (UTC):** {ts}",
        "",
        f"**Readiness Headline:** {readiness_headline}",
        "",
        "## Golden Dome Nuclear Snapshot",
        "```json",
        json.dumps(snapshot, indent=2),
        "```",
        "",
        "## Pre-Launch ISR Watchboard",
        "```json",
        json.dumps(watchboard, indent=2),
        "```",
        "",
        "## Fusion Heat Index (Battlespace Temperature)",
        "```json",
        json.dumps(fhi, indent=2),
        "```",
        "",
        "## Notes",
        "- Engineering / demo only — not an operational nuclear C2 system.",
        "- Replace sample data with validated sources before real-world integration.",
        "",
    ]
    md_path.write_text("\n".join(md_lines))

    return {
        "txt_path": str(txt_path),
        "md_path": str(md_path),
        "generated_at": ts,
    }


if __name__ == "__main__":
    out = build_nuclear_mission_brief()
    print("=== NUCLEAR MISSION BRIEF BUILT ===")
    print(json.dumps(out, indent=2))

