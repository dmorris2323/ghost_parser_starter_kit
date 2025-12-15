"""
nuclear_status_summary.py

Shift-change nuclear ISR rollup.
Consumes Nuclear Watch Snapshot and emits:
- One-line status
- Bounded posture
- Safe confidence language

Designed for watch floors and handover briefs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


SNAPSHOT_LATEST = Path("docs") / "nuclear" / "nuclear_watch_snapshot_latest.json"
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


def _write_txt(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def build_nuclear_status_summary() -> Dict[str, Any]:
    snap = _safe_read(SNAPSHOT_LATEST)

    posture = snap.get("posture", "UNKNOWN")
    confidence = snap.get("confidence", "UNKNOWN")
    risk_band = snap.get("risk_band", "UNKNOWN")
    degraded = bool(snap.get("degraded", False))
    missing = int(snap.get("missing_signal_count", 0))

    line = (
        f"NUCLEAR STATUS: {posture} | "
        f"CONFIDENCE={confidence} | "
        f"RISK={risk_band} | "
        f"DEGRADED={'YES' if degraded else 'NO'} | "
        f"MISSING_SIGNALS={missing}"
    )

    summary = {
        "generated_at_utc": _utc_now(),
        "artifact": "NUCLEAR_STATUS_SUMMARY",
        "status_line": line,
        "posture": posture,
        "confidence": confidence,
        "risk_band": risk_band,
        "degraded": degraded,
        "missing_signal_count": missing,
        "safe_notice": "Bounded assessment. No confirmation implied.",
        "source": str(SNAPSHOT_LATEST),
    }

    return summary


def write_status(summary: Dict[str, Any]) -> Dict[str, str]:
    ts = _ts()
    json_latest = OUT_DIR / "nuclear_status_summary_latest.json"
    txt_latest = OUT_DIR / "nuclear_status_summary_latest.txt"
    json_stamp = OUT_DIR / f"nuclear_status_summary_{ts}.json"
    txt_stamp = OUT_DIR / f"nuclear_status_summary_{ts}.txt"

    _write(json_latest, summary)
    _write(json_stamp, summary)

    text = (
        "GLL — NUCLEAR STATUS SUMMARY (SHIFT CHANGE)\n"
        f"Generated (UTC): {summary['generated_at_utc']}\n\n"
        f"{summary['status_line']}\n\n"
        "Notes:\n"
        "- Assessment is bounded and probabilistic\n"
        "- Degraded operations handled gracefully\n"
        "- Escalation posture unchanged unless stated above\n"
    )

    _write_txt(txt_latest, text)
    _write_txt(txt_stamp, text)

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamp),
        "txt_stamped": str(txt_stamp),
    }


if __name__ == "__main__":
    status = build_nuclear_status_summary()
    paths = write_status(status)
    print("Nuclear Status Summary written:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print("STATUS LINE:")
    print(status["status_line"])

