#!/usr/bin/env python3
"""
temporal_volatility_filter.py

Ghost Lantern Labs – Nuclear Hardening Block
--------------------------------------------

Purpose:
    Estimate temporal volatility in nuclear/ISR signals to help
    distinguish genuine escalation from noisy spikes.

Inputs (best-effort):
    docs/run_history_intel.json
      - This is assumed to contain a list of events or runs with timestamps.
      - This module is defensive and will work with partial or unknown structure.

Outputs:
    docs/nuclear_temporal_volatility.json
    docs/nuclear_temporal_volatility.txt

We compute a simple volatility index (0–100) based on:
    - Total events in recent window vs older history.
    - Signs of clustering or rapid-fire events.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _extract_events(data: Any) -> List[Dict[str, Any]]:
    """
    Try to normalize run_history_intel into a list of events.
    """
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    if isinstance(data, dict):
        for key in ("events", "runs", "history"):
            v = data.get(key)
            if isinstance(v, list):
                return [e for e in v if isinstance(e, dict)]
    return []


def _compute_volatility(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simplified volatility proxy:
        - If few events, volatility is low.
        - If many events, and especially if many recent events, volatility rises.
    We don't rely on exact timestamps; we just look for generic "recent" flags,
    or fallback to sheer count.
    """
    notes: List[str] = []
    total = len(events)

    if total == 0:
        return {"volatility_index": 0.0, "notes": ["No events in run_history_intel."]}

    # Basic total-based volatility
    if total < 10:
        base = 15.0
        notes.append("Low total event count – baseline volatility low.")
    elif total < 30:
        base = 40.0
        notes.append("Moderate event count – medium baseline volatility.")
    else:
        base = 70.0
        notes.append("High event count – elevated baseline volatility.")

    # Look for "recent" flags in events (e.g., 'recent': true or tag strings)
    recent_hits = 0
    for e in events:
        if isinstance(e, dict):
            if e.get("recent") is True:
                recent_hits += 1
            else:
                # fallback: look for 'recent' or 'last_24h' or similar in tags or notes
                text_blob = json.dumps(e).lower()
                if any(w in text_blob for w in ["last 24h", "recent", "last_12h", "spike"]):
                    recent_hits += 1

    if recent_hits == 0:
        bonus = 0.0
        notes.append("No explicit recent-event markers detected.")
    elif recent_hits < 5:
        bonus = 10.0
        notes.append("Some events flagged as recent – modest volatility bump.")
    else:
        bonus = 25.0
        notes.append("Cluster of recent events detected – strong volatility bump.")

    volatility_index = max(0.0, min(100.0, base + bonus))

    return {"volatility_index": volatility_index, "notes": notes}


def build_nuclear_temporal_volatility() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    run_history_path = os.path.join(DOCS_DIR, "run_history_intel.json")
    data = _safe_read_json(run_history_path)

    inputs_present = {"run_history_intel_json": data is not None}

    events = _extract_events(data) if data is not None else []
    vol_info = _compute_volatility(events)

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "event_count": len(events),
        "volatility_index": vol_info["volatility_index"],
        "rationale": vol_info["notes"],
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "nuclear_temporal_volatility.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Nuclear Temporal Volatility Report")
    lines.append("======================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Event Count in History: {result['event_count']}")
    lines.append(f"Volatility Index: {result['volatility_index']:.1f}/100")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append("Rationale:")
    for r in result["rationale"]:
        lines.append(f"  - {r}")

    txt_path = os.path.join(DOCS_DIR, "nuclear_temporal_volatility.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_nuclear_temporal_volatility()
    print("Nuclear temporal volatility report generated:")
    print(f"  - {os.path.join('docs', 'nuclear_temporal_volatility.json')}")
    print(f"  - {os.path.join('docs', 'nuclear_temporal_volatility.txt')}")

