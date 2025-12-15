"""
prebrief_trust_annotations.py

Pre-brief trust annotations artifact:
- Explains trust/confidence under ambiguity
- Designed for commander briefing "pre-read"
- Never crashes; safe for synthetic demos
- Writes latest artifact in docs/briefs/

Public API:
- build_prebrief_trust_annotations(...)
- write_prebrief_trust_annotations(...)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


BRIEFS_DIR = Path("docs") / "briefs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def build_prebrief_trust_annotations(
    *,
    trust_score: Any,
    risk_score: Any,
    confidence: str,
    degraded: bool,
    ambiguity_flags: Optional[list] = None,
    top_unknowns: Optional[list] = None,
    source_note: str = "Synthetic / Training",
) -> Dict[str, Any]:
    trust = _coerce_float(trust_score, 0.0)
    risk = _coerce_float(risk_score, 0.0)

    flags = [str(x) for x in (ambiguity_flags or [])][:12]
    unknowns = [str(x) for x in (top_unknowns or [])][:12]

    commander_takeaway = (
        "Confidence is bounded; treat this as a decision-support product, not a single-source verdict."
        if confidence in {"LOW", "VERY_LOW"} or degraded
        else "Confidence is acceptable for watch posture decisions; continue multi-source verification."
    )

    return {
        "generated_at_utc": _utc_now_iso(),
        "type": "PREBRIEF_TRUST_ANNOTATIONS",
        "source_note": source_note,
        "safe_notice": "May be generated from synthetic telemetry for training/demos.",
        "summary": {
            "trust_score": trust,
            "risk_score": risk,
            "confidence": confidence,
            "degraded": bool(degraded),
        },
        "commander_takeaway": commander_takeaway,
        "ambiguity": {
            "flags": flags,
            "unknowns": unknowns,
            "rules": [
                "Do not escalate on single-domain spikes.",
                "Confirm signal continuity before interpreting anomalies.",
                "If degraded, prioritize restoration of missing signals.",
                "If confidence is LOW/VERY_LOW, treat recommendations as provisional.",
            ],
        },
        "briefing_language": {
            "approved_phrases": [
                "We assess with {CONFIDENCE} confidence…",
                "Indicators are consistent with training-proxy risk elevation, not confirmation.",
                "Primary uncertainty stems from missing or degraded signals.",
                "Recommendation is to increase verification rather than assume intent.",
            ],
            "avoid_phrases": [
                "Confirmed",
                "Certain",
                "Definitive proof",
                "Single-source confirmation",
            ],
        },
    }


def write_prebrief_trust_annotations(obj: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(BRIEFS_DIR)
    json_path = BRIEFS_DIR / "prebrief_trust_annotations_latest.json"
    txt_path = BRIEFS_DIR / "prebrief_trust_annotations_latest.txt"

    json_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    # small, human-readable txt
    s = obj.get("summary", {})
    lines = []
    lines.append("GLL — PREBRIEF TRUST ANNOTATIONS (LATEST)")
    lines.append(f"Generated (UTC): {obj.get('generated_at_utc','')}")
    lines.append("")
    lines.append(f"Confidence: {s.get('confidence','')}")
    lines.append(f"Trust:      {s.get('trust_score',0)}")
    lines.append(f"Risk:       {s.get('risk_score',0)}")
    lines.append(f"Degraded:   {s.get('degraded', False)}")
    lines.append("")
    lines.append("Commander Takeaway:")
    lines.append(f"- {obj.get('commander_takeaway','')}")
    lines.append("")
    lines.append("Ambiguity Flags:")
    for f in (obj.get("ambiguity", {}).get("flags", []) or []):
        lines.append(f"- {f}")
    lines.append("")
    lines.append("Top Unknowns:")
    for u in (obj.get("ambiguity", {}).get("unknowns", []) or []):
        lines.append(f"- {u}")
    lines.append("")
    lines.append("Rules:")
    for r in (obj.get("ambiguity", {}).get("rules", []) or []):
        lines.append(f"- {r}")

    txt_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    return {"json_path": str(json_path), "txt_path": str(txt_path)}

