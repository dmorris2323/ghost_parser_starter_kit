"""
nuclear_watch_snapshot.py

Command-grade synthesis artifact.
Combines:
- Golden Dome Daily Watch
- Nuclear Decision Card
- Pre-brief Trust Annotations

Purpose:
- Single authoritative nuclear ISR snapshot
- Safe under ambiguity
- No over-claiming
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


WATCH_LATEST = Path("docs") / "nuclear" / "golden_dome_daily_watch_latest.json"
DECISION_LATEST = Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json"
PREBRIEF_LATEST = Path("docs") / "briefs" / "prebrief_trust_annotations_latest.json"

OUT_DIR = Path("docs") / "nuclear"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def build_nuclear_watch_snapshot() -> Dict[str, Any]:
    watch = _safe_read(WATCH_LATEST)
    decision = _safe_read(DECISION_LATEST)
    prebrief = _safe_read(PREBRIEF_LATEST)

    posture = (
        decision.get("escalation", {}) or {}
    ).get("posture", "UNKNOWN")

    summary = prebrief.get("summary", {})

    snapshot = {
        "generated_at_utc": _utc_now(),
        "artifact": "NUCLEAR_WATCH_SNAPSHOT",
        "posture": posture,
        "confidence": summary.get("confidence", "UNKNOWN"),
        "risk_band": summary.get("risk_band", "UNKNOWN"),
        "degraded": summary.get("degraded", False),
        "alerts": summary.get("alerts", {}),
        "missing_signal_count": summary.get("missing_signal_count", 0),
        "safe_notice": "May be generated from synthetic telemetry. Not confirmation.",
        "what_we_can_say": prebrief.get("annotations", {}).get("claims_allowed", []),
        "what_we_cannot_say": prebrief.get("annotations", {}).get("claims_forbidden", []),
        "known_unknowns": prebrief.get("annotations", {}).get("known_unknowns", []),
        "next_collection_tasks": prebrief.get("annotations", {}).get("collection_tasks", []),
        "sources": {
            "golden_dome_watch": str(WATCH_LATEST),
            "decision_card": str(DECISION_LATEST),
            "prebrief_annotations": str(PREBRIEF_LATEST),
        },
    }

    return snapshot


def write_snapshot(snapshot: Dict[str, Any]) -> Dict[str, str]:
    ts = _ts()
    json_latest = OUT_DIR / "nuclear_watch_snapshot_latest.json"
    txt_latest = OUT_DIR / "nuclear_watch_snapshot_latest.txt"
    json_stamp = OUT_DIR / f"nuclear_watch_snapshot_{ts}.json"
    txt_stamp = OUT_DIR / f"nuclear_watch_snapshot_{ts}.txt"

    _write(json_latest, snapshot)
    _write(json_stamp, snapshot)

    lines = [
        "GLL — NUCLEAR WATCH SNAPSHOT (LATEST)",
        f"Generated (UTC): {snapshot['generated_at_utc']}",
        "",
        f"Posture: {snapshot['posture']}",
        f"Confidence: {snapshot['confidence']}",
        f"Risk Band: {snapshot['risk_band']}",
        f"Degraded Ops: {snapshot['degraded']}",
        f"Missing Signals: {snapshot['missing_signal_count']}",
        "",
        "WHAT WE CAN SAY:",
        *[f"- {x}" for x in snapshot["what_we_can_say"]],
        "",
        "WHAT WE CANNOT SAY:",
        *[f"- {x}" for x in snapshot["what_we_cannot_say"]],
        "",
        "KNOWN UNKNOWNS:",
        *[f"- {x}" for x in snapshot["known_unknowns"]],
        "",
        "NEXT COLLECTION TASKS:",
        *[f"- {x}" for x in snapshot["next_collection_tasks"]],
    ]

    _write_txt(txt_latest, lines)
    _write_txt(txt_stamp, lines)

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamp),
        "txt_stamped": str(txt_stamp),
    }


if __name__ == "__main__":
    snap = build_nuclear_watch_snapshot()
    paths = write_snapshot(snap)
    print("Nuclear Watch Snapshot written:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print("Posture:", snap["posture"])

