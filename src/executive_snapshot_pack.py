"""
executive_snapshot_pack.py
--------------------------

Builds a single "Executive Snapshot Pack" file that bundles together:
  - GLL readiness status
  - System integrity report
  - Latest mission brief (HTML)
  - Latest scenario pack (if any)
  - Golden Dome drift report (if any)

Outputs:
  docs/executive_snapshot_pack.json
  docs/executive_snapshot_readme.md

This is designed so you can hand ONE file to:
  - a commander
  - an SBIR reviewer
  - a tech lead
and they can see the state of Ghost Lantern Labs in one place.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"

READINESS_FILE = DOCS / "gll_readiness_status.json"
INTEGRITY_FILE = DOCS / "system_integrity_report.json"
MISSION_HTML = DOCS / "daily_mission_brief.html"
SCENARIO_PACK = DOCS / "scenario_pack_latest.json"
DRIFT_REPORT = DOCS / "golden_dome_drift_report.txt"

OUTPUT_JSON = DOCS / "executive_snapshot_pack.json"
OUTPUT_MD = DOCS / "executive_snapshot_readme.md"


def _safe_read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text()
    except Exception:
        return None


def _safe_read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return {"error": f"Failed to parse {path.name}"}


def build_executive_snapshot() -> Dict[str, Any]:
    DOCS.mkdir(exist_ok=True, parents=True)

    now = datetime.now(timezone.utc).isoformat()

    readiness = _safe_read_json(READINESS_FILE)
    integrity = _safe_read_json(INTEGRITY_FILE)
    mission_html = _safe_read_text(MISSION_HTML)
    scenario = _safe_read_json(SCENARIO_PACK)
    drift = _safe_read_text(DRIFT_REPORT)

    pack: Dict[str, Any] = {
        "generated_at": now,
        "base_dir": str(BASE),
        "artifacts": {
            "gll_readiness_status": {
                "path": str(READINESS_FILE),
                "present": readiness is not None,
                "content": readiness,
            },
            "system_integrity_report": {
                "path": str(INTEGRITY_FILE),
                "present": integrity is not None,
                "content": integrity,
            },
            "daily_mission_brief_html": {
                "path": str(MISSION_HTML),
                "present": mission_html is not None,
                "content": mission_html,
            },
            "scenario_pack_latest": {
                "path": str(SCENARIO_PACK),
                "present": scenario is not None,
                "content": scenario,
            },
            "golden_dome_drift_report": {
                "path": str(DRIFT_REPORT),
                "present": drift is not None,
                "content": drift,
            },
        },
        "notes": {
            "purpose": (
                "Single-file executive snapshot for commanders, reviewers, or investors. "
                "Shows GLL readiness, integrity, mission brief, and key nuclear/Golden-Dome context."
            ),
            "missing_files_safe": (
                "If some artifacts are missing, they are flagged as present=False but the pack still builds. "
                "This is intentional to support partial environments."
            ),
        },
    }

    OUTPUT_JSON.write_text(json.dumps(pack, indent=2))

    # Build a lightweight README
    lines = []
    lines.append("# Ghost Lantern Labs — Executive Snapshot Pack")
    lines.append("")
    lines.append(f"Generated at: `{now}`")
    lines.append(f"Base directory: `{BASE}`")
    lines.append("")
    lines.append("## Included Artifacts")
    for key, meta in pack["artifacts"].items():
        status = "OK" if meta["present"] else "MISSING"
        lines.append(f"- **{key}**")
        lines.append(f"  - Path: `{meta['path']}`")
        lines.append(f"  - Status: `{status}`")
    lines.append("")
    lines.append("## Purpose")
    lines.append(pack["notes"]["purpose"])
    lines.append("")
    lines.append("## Usage")
    lines.append("- Attach `executive_snapshot_pack.json` to emails or tickets as a single source of truth.")
    lines.append("- Use it for SBIR/AFWERX review packages, commander briefs, or investor diligence.")
    lines.append("- Combine with screenshots (CLI Option 22 / dashboard) for a complete story.")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines))

    return {
        "output_json": str(OUTPUT_JSON),
        "output_md": str(OUTPUT_MD),
    }


def main() -> Dict[str, Any]:
    return build_executive_snapshot()


if __name__ == "__main__":
    out = main()
    print("=== Executive Snapshot Pack Built ===")
    print(json.dumps(out, indent=2))

