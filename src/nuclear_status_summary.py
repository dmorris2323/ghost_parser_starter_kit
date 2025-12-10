#!/usr/bin/env python3
"""
nuclear_status_summary.py

Day 66 – Ghost Lantern Labs

Builds a consolidated Nuclear Status Summary by inspecting existing
nuclear/treaty-related outputs, including:

- docs/golden_dome_daily_watch.json
- docs/golden_dome_daily_watch.txt
- docs/nuclear_decision_card.txt
- docs/treaty_evidence_bundle.json
- docs/gll_readiness.txt
- docs/system_integrity_report.txt
- docs/prelaunch_watchboard.json

Outputs:
- docs/nuclear_status_summary.json
- docs/nuclear_status_summary.txt

This module is deliberately defensive: if any inputs are missing,
it degrades gracefully and notes the missing artifacts instead of failing.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as exc:
        return f"[ERROR reading {os.path.basename(path)}: {exc}]"


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def _file_meta(path: str) -> Dict[str, Any]:
    exists = os.path.exists(path)
    meta: Dict[str, Any] = {
        "path": path,
        "exists": exists,
        "last_modified": None,
    }
    if exists:
        try:
            ts = os.path.getmtime(path)
            meta["last_modified"] = datetime.fromtimestamp(ts).isoformat()
        except Exception:
            meta["last_modified"] = None
    return meta


def build_nuclear_status_summary() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    # Define key artifact paths (relative to src/docs)
    golden_dome_daily_watch_json = os.path.join(DOCS_DIR, "golden_dome_daily_watch.json")
    golden_dome_daily_watch_txt = os.path.join(DOCS_DIR, "golden_dome_daily_watch.txt")
    nuclear_decision_card_txt = os.path.join(DOCS_DIR, "nuclear_decision_card.txt")
    treaty_evidence_bundle_json = os.path.join(DOCS_DIR, "treaty_evidence_bundle.json")
    gll_readiness_txt = os.path.join(DOCS_DIR, "gll_readiness.txt")
    system_integrity_report_txt = os.path.join(DOCS_DIR, "system_integrity_report.txt")
    prelaunch_watchboard_json = os.path.join(DOCS_DIR, "prelaunch_watchboard.json")

    # Load artifact content
    golden_dome_json = _safe_read_json(golden_dome_daily_watch_json)
    golden_dome_text = _safe_read_text(golden_dome_daily_watch_txt)
    nuclear_decision_card_text = _safe_read_text(nuclear_decision_card_txt)
    treaty_bundle = _safe_read_json(treaty_evidence_bundle_json)
    gll_readiness_text = _safe_read_text(gll_readiness_txt)
    system_integrity_text = _safe_read_text(system_integrity_report_txt)
    prelaunch_watchboard = _safe_read_json(prelaunch_watchboard_json)

    # High-level presence map
    artifacts_present: Dict[str, bool] = {
        "golden_dome_daily_watch_json": golden_dome_json is not None,
        "golden_dome_daily_watch_txt": golden_dome_text is not None,
        "nuclear_decision_card_txt": nuclear_decision_card_text is not None,
        "treaty_evidence_bundle_json": treaty_bundle is not None,
        "gll_readiness_txt": gll_readiness_text is not None,
        "system_integrity_report_txt": system_integrity_text is not None,
        "prelaunch_watchboard_json": prelaunch_watchboard is not None,
    }

    # Try to pull out obvious signals from known text artifacts
    crisis_mode = None
    golden_dome_readiness = None
    fusion_trust = None
    fusion_heat_index = None

    if nuclear_decision_card_text:
        for line in nuclear_decision_card_text.splitlines():
            lower = line.lower()
            if "crisis mode" in lower:
                crisis_mode = line.strip()
            if "golden dome" in lower and "readiness" in lower:
                golden_dome_readiness = line.strip()
            if "fusion trust" in lower:
                fusion_trust = line.strip()
            if "fusion heat" in lower or "heat index" in lower:
                fusion_heat_index = line.strip()

    # Build status summary
    summary: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "artifacts_present": artifacts_present,
        "file_metadata": {
            "golden_dome_daily_watch_json": _file_meta(golden_dome_daily_watch_json),
            "golden_dome_daily_watch_txt": _file_meta(golden_dome_daily_watch_txt),
            "nuclear_decision_card_txt": _file_meta(nuclear_decision_card_txt),
            "treaty_evidence_bundle_json": _file_meta(treaty_evidence_bundle_json),
            "gll_readiness_txt": _file_meta(gll_readiness_txt),
            "system_integrity_report_txt": _file_meta(system_integrity_report_txt),
            "prelaunch_watchboard_json": _file_meta(prelaunch_watchboard_json),
        },
        "nuclear_signals": {
            "crisis_mode_line": crisis_mode,
            "golden_dome_readiness_line": golden_dome_readiness,
            "fusion_trust_line": fusion_trust,
            "fusion_heat_index_line": fusion_heat_index,
        },
        "notes": [],
    }

    # Add notes about coverage
    if all(artifacts_present.values()):
        summary["notes"].append(
            "All core nuclear/treaty artifacts are present for this run."
        )
    else:
        missing = [k for k, v in artifacts_present.items() if not v]
        summary["notes"].append(
            f"Missing artifacts: {', '.join(missing)}"
        )

    # Keep raw (but truncated) excerpts for human context
    def _truncate(text: Optional[str], max_len: int = 400) -> Optional[str]:
        if text is None:
            return None
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    summary["excerpts"] = {
        "nuclear_decision_card_excerpt": _truncate(nuclear_decision_card_text),
        "gll_readiness_excerpt": _truncate(gll_readiness_text),
        "system_integrity_excerpt": _truncate(system_integrity_text),
    }

    # Persist JSON + TXT
    json_path = os.path.join(DOCS_DIR, "nuclear_status_summary.json")
    txt_path = os.path.join(DOCS_DIR, "nuclear_status_summary.txt")

    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(summary, f_json, indent=2, sort_keys=True)

    # Human-readable text version
    lines: List[str] = []
    lines.append("GLL Nuclear Status Summary")
    lines.append("==========================")
    lines.append(f"Generated at (UTC): {summary['generated_at']}")
    lines.append("")
    lines.append("Artifacts Present:")
    for name, present in artifacts_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append("Key Nuclear Signals (parsed from decision card if available):")
    lines.append(f"  Crisis Mode: {crisis_mode or 'UNKNOWN'}")
    lines.append(f"  Golden Dome Readiness: {golden_dome_readiness or 'UNKNOWN'}")
    lines.append(f"  Fusion Trust: {fusion_trust or 'UNKNOWN'}")
    lines.append(f"  Fusion Heat Index: {fusion_heat_index or 'UNKNOWN'}")
    lines.append("")
    lines.append("Notes:")
    for note in summary["notes"]:
        lines.append(f"  - {note}")
    lines.append("")
    lines.append("Excerpts:")
    lines.append("  Nuclear Decision Card:")
    lines.append(
        _truncate(nuclear_decision_card_text, 600) or "  [no decision card available]"
    )
    lines.append("")
    lines.append("  GLL Readiness:")
    lines.append(
        _truncate(gll_readiness_text, 600) or "  [no readiness report available]"
    )
    lines.append("")
    lines.append("  System Integrity Report:")
    lines.append(
        _truncate(system_integrity_text, 600)
        or "  [no system integrity report available]"
    )

    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return summary


if __name__ == "__main__":
    summary = build_nuclear_status_summary()
    print("Nuclear Status Summary generated:")
    print(f"  - {os.path.join(DOCS_DIR, 'nuclear_status_summary.json')}")
    print(f"  - {os.path.join(DOCS_DIR, 'nuclear_status_summary.txt')}")

