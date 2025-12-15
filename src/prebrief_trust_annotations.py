"""
prebrief_trust_annotations.py

Week-1 Nuclear/AFTAC Hardening:
Creates a commander-safe "Pre-Brief Trust Annotations" artifact.

Inputs (preferred):
- docs/nuclear/prelaunch_watchboard_latest.json

Fallback:
- if watchboard missing, emits a minimal annotation with warnings.

Outputs:
- docs/briefs/prebrief_trust_annotations_latest.json
- docs/briefs/prebrief_trust_annotations_latest.txt
- stamped versions
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

WATCHBOARD_PATH = Path("docs") / "nuclear" / "prelaunch_watchboard_latest.json"
OUT_DIR = Path("docs") / "briefs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def build_prebrief_trust_annotations() -> Dict[str, Any]:
    wb = _read_json(WATCHBOARD_PATH)
    has_wb = bool(wb)

    esc = wb.get("escalation", {}) if isinstance(wb.get("escalation"), dict) else {}
    brief = wb.get("brief", {}) if isinstance(wb.get("brief"), dict) else {}
    card = wb.get("decision_card", {}) if isinstance(wb.get("decision_card"), dict) else {}
    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}

    posture = str(esc.get("posture", "ROUTINE_MONITORING"))
    confidence = str(status.get("confidence", "UNKNOWN"))
    risk_band = str(status.get("risk_band", "UNKNOWN"))
    ambiguity_flags = status.get("ambiguity_flags", [])
    ambiguity_flags = ambiguity_flags if isinstance(ambiguity_flags, list) else []
    degraded = bool(status.get("degraded", False))

    bounded = brief.get("what_we_can_say", []) or []
    cannot = brief.get("what_we_cannot_say", []) or []
    unknowns = brief.get("unknowns", []) or []

    annotations = {
        "generated_at": _utc_now_iso(),
        "safe_notice": "This artifact is derived from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "watchboard_present": has_wb,
            "watchboard_path": str(WATCHBOARD_PATH),
        },
        "trust_posture": {
            "posture": posture,
            "confidence": confidence,
            "risk_band": risk_band,
            "degraded": degraded,
            "ambiguity_flags": ambiguity_flags,
            "cap_applied": bool(esc.get("cap_applied", False)),
            "deescalation_blocked": bool(esc.get("deescalation_blocked", False)),
        },
        "prebrief_notes": {
            "what_we_can_say_bounded": list(bounded),
            "what_we_cannot_say": list(cannot),
            "unknowns": list(unknowns),
        },
        "operator_instruction": [
            "Brief only bounded statements.",
            "If confidence is LOW/UNKNOWN or degraded=True, do not expand inference beyond listed text.",
            "If posture ≥ UNIT_COMMANDER_ALERT persists across multiple cycles, initiate operator review and re-run baseline validation.",
        ],
    }

    # If no watchboard, add a loud warning (still produces artifact)
    if not has_wb:
        annotations["operator_instruction"].insert(0, "WARNING: watchboard missing; run prelaunch_watchboard to generate commander-grade context.")

    return annotations


def render_prebrief_txt(a: Dict[str, Any]) -> str:
    tp = a.get("trust_posture", {}) if isinstance(a.get("trust_posture"), dict) else {}
    pn = a.get("prebrief_notes", {}) if isinstance(a.get("prebrief_notes"), dict) else {}

    lines: List[str] = []
    lines.append("GLL PRE-BRIEF TRUST ANNOTATIONS (TRAINING SAFE)")
    lines.append("=" * 52)
    lines.append(f"Generated: {a.get('generated_at')}")
    lines.append(f"Posture: {tp.get('posture')} | Confidence: {tp.get('confidence')} | Risk band: {tp.get('risk_band')}")
    lines.append(f"Degraded: {tp.get('degraded')} | Cap applied: {tp.get('cap_applied')} | De-escalation blocked: {tp.get('deescalation_blocked')}")
    lines.append("")
    lines.append("BOUNDED STATEMENTS (BRIEF THESE):")
    for s in pn.get("what_we_can_say_bounded", []) or []:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("DO NOT CLAIM:")
    for s in pn.get("what_we_cannot_say", []) or []:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("UNKNOWNS:")
    for u in pn.get("unknowns", []) or []:
        lines.append(f"- {u}")
    lines.append("")
    lines.append("OPERATOR INSTRUCTION:")
    for i in a.get("operator_instruction", []) or []:
        lines.append(f"- {i}")
    lines.append("")
    return "\n".join(lines)


def write_prebrief_trust_annotations(a: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()

    json_latest = OUT_DIR / "prebrief_trust_annotations_latest.json"
    txt_latest = OUT_DIR / "prebrief_trust_annotations_latest.txt"
    json_stamped = OUT_DIR / f"prebrief_trust_annotations_{ts}.json"
    txt_stamped = OUT_DIR / f"prebrief_trust_annotations_{ts}.txt"

    _write_json(json_latest, a)
    _write_json(json_stamped, a)
    _write_txt(txt_latest, render_prebrief_txt(a))
    _write_txt(txt_stamped, render_prebrief_txt(a))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


if __name__ == "__main__":
    ann = build_prebrief_trust_annotations()
    paths = write_prebrief_trust_annotations(ann)
    print("Pre-brief trust annotations written:")
    print(json.dumps(paths, indent=2))

