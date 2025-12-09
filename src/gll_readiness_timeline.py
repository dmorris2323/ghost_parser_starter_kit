"""
gll_readiness_timeline.py
-------------------------

Builds and updates a long-term timeline of GLL readiness snapshots.

Inputs (if present):
  docs/gll_readiness_status.json  - latest readiness snapshot
  docs/system_integrity_report.json (optional, logged as context only)

Outputs:
  docs/gll_readiness_timeline.json  - structured JSON timeline
  docs/gll_readiness_timeline.md    - human-readable markdown summary

This module is intentionally LO-FRAGILE:
- It does NOT assume any specific JSON schema.
- It records whatever keys exist under a timestamp wrapper.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"

READINESS_FILE = DOCS / "gll_readiness_status.json"
INTEGRITY_FILE = DOCS / "system_integrity_report.json"

TIMELINE_JSON = DOCS / "gll_readiness_timeline.json"
TIMELINE_MD = DOCS / "gll_readiness_timeline.md"


def _load_json_if_exists(path: Path) -> Any:
    """Safely load JSON if file exists, else return None."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        # If it's corrupted, we still don't want to crash the timeline.
        return {"error": f"Failed to parse {path.name}"}


def _load_timeline() -> List[Dict[str, Any]]:
    if not TIMELINE_JSON.exists():
        return []
    try:
        return json.loads(TIMELINE_JSON.read_text())
    except Exception:
        # If the file is corrupted, start a new timeline but keep a note.
        return [{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Previous timeline could not be parsed; new timeline started."
        }]


def _write_timeline_json(entries: List[Dict[str, Any]]) -> None:
    DOCS.mkdir(exist_ok=True, parents=True)
    TIMELINE_JSON.write_text(json.dumps(entries, indent=2))


def _write_timeline_md(entries: List[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# GLL Readiness Timeline")
    lines.append("")
    lines.append(f"Total snapshots: {len(entries)}")
    lines.append("")

    for idx, entry in enumerate(entries, start=1):
        ts = entry.get("timestamp", "unknown")
        meta = entry.get("meta", {})
        status = entry.get("status_snapshot")
        integrity = entry.get("integrity_snapshot")

        lines.append(f"## Snapshot {idx}")
        lines.append(f"- Timestamp: `{ts}`")
        lines.append(f"- Source files: {meta.get('sources', [])}")
        lines.append(f"- Notes: {meta.get('notes', '')}")
        lines.append("")
        lines.append("### Readiness Snapshot (raw)")
        lines.append("```json")
        lines.append(json.dumps(status, indent=2, default=str))
        lines.append("```")
        lines.append("")
        if integrity is not None:
            lines.append("### System Integrity Snapshot (raw)")
            lines.append("```json")
            lines.append(json.dumps(integrity, indent=2, default=str))
            lines.append("```")
            lines.append("")
        lines.append("---")
        lines.append("")

    TIMELINE_MD.write_text("\n".join(lines))


def build_readiness_timeline() -> Dict[str, str]:
    """
    Append the latest readiness snapshot to the long-term timeline.

    Returns:
      dict with paths to JSON and markdown outputs.
    """
    DOCS.mkdir(exist_ok=True, parents=True)

    # Load current snapshots (may be None if not yet generated)
    readiness = _load_json_if_exists(READINESS_FILE)
    integrity = _load_json_if_exists(INTEGRITY_FILE)

    ts = datetime.now(timezone.utc).isoformat()

    entry: Dict[str, Any] = {
        "timestamp": ts,
        "meta": {
            "sources": [],
            "notes": ""
        },
        "status_snapshot": readiness,
        "integrity_snapshot": integrity,
    }

    srcs = []
    if readiness is not None:
        srcs.append(READINESS_FILE.name)
    if integrity is not None:
        srcs.append(INTEGRITY_FILE.name)
    if not srcs:
        entry["meta"]["notes"] = "No readiness or integrity files present at time of capture."
    else:
        entry["meta"]["notes"] = "Snapshot captured successfully."
    entry["meta"]["sources"] = srcs

    timeline = _load_timeline()
    timeline.append(entry)

    _write_timeline_json(timeline)
    _write_timeline_md(timeline)

    return {
        "timeline_json": str(TIMELINE_JSON),
        "timeline_md": str(TIMELINE_MD),
        "snapshots_recorded": str(len(timeline)),
    }


def main() -> Dict[str, str]:
    return build_readiness_timeline()


if __name__ == "__main__":
    out = main()
    print("=== GLL Readiness Timeline Updated ===")
    print(json.dumps(out, indent=2))

