"""
prebrief_trust_annotations.py

Builds a commander-facing "pre-brief trust annotations" artifact (SAFE).
This artifact is derived from synthetic telemetry and is safe for training/demos.

Hardening requirement:
- MUST include tokens: "probabilistic", "bounded", "operator judgment"
  so command-trust consistency gates can verify operator framing is present.
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


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _ensure_list(x: Any) -> List[str]:
    if isinstance(x, list):
        return [str(i) for i in x]
    if isinstance(x, str) and x.strip():
        return [x.strip()]
    return []


def _required_operator_framing_line() -> str:
    # 🔒 REQUIRED TOKENS (do not change wording lightly)
    # These tokens are validated by prebrief_trust_consistency.py
    return (
        "Assessment is probabilistic and bounded; operator judgment is required "
        "before escalation beyond DUTY_OFFICER_NOTIFY."
    )


def build_prebrief_trust_annotations() -> Dict[str, Any]:
    has_wb = WATCHBOARD_PATH.exists()
    watchboard: Dict[str, Any] = {}
    if has_wb:
        try:
            watchboard = json.loads(WATCHBOARD_PATH.read_text(encoding="utf-8"))
        except Exception:
            watchboard = {}

    brief = watchboard.get("brief", {}) if isinstance(watchboard, dict) else {}
    decision_card = watchboard.get("decision_card", {}) if isinstance(watchboard, dict) else {}
    escalation = decision_card.get("escalation", {}) if isinstance(decision_card, dict) else {}

    posture = str(escalation.get("posture", "DUTY_OFFICER_NOTIFY"))
    confidence = str(decision_card.get("status", {}).get("confidence", "LOW"))
    risk_band = str(decision_card.get("status", {}).get("risk_band", "GUARDED"))
    degraded = bool(decision_card.get("status", {}).get("degraded", False))
    ambiguity_flags = _ensure_list(decision_card.get("status", {}).get("ambiguity_flags", []))

    bounded = _ensure_list(brief.get("what_we_can_say", []))
    cannot = _ensure_list(brief.get("what_we_cannot_say", []))
    unknowns = _ensure_list(brief.get("unknowns", []))

    # 🔒 Force required operator framing into "what we can say"
    required_line = _required_operator_framing_line()
    if all(required_line.lower() not in str(x).lower() for x in bounded):
        bounded.insert(0, required_line)

    # 🔒 Also stamp it into an explicit field so JSON consumers can show it directly
    annotations = {
        "generated_at": _utc_now_iso(),
        "safe_notice": (
            "This artifact is derived from synthetic telemetry and is safe for training/demos. "
            "Assessment is probabilistic and bounded; operator judgment applies."
        ),
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
            "cap_applied": bool(escalation.get("cap_applied", False)),
            "deescalation_blocked": bool(escalation.get("deescalation_blocked", False)),
        },
        "required_operator_framing": required_line,
        "what_we_can_say": bounded,
        "what_we_cannot_say": cannot,
        "unknowns": unknowns,
    }

    return annotations


def _render_txt(obj: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Prebrief Trust Annotations")
    lines.append(f"generated_at_utc: {obj.get('generated_at', '')}")
    lines.append("")
    lines.append(str(obj.get("safe_notice", "")))
    lines.append("")

    tp = obj.get("trust_posture", {}) if isinstance(obj.get("trust_posture", {}), dict) else {}
    lines.append("[Trust Posture]")
    lines.append(f"posture: {tp.get('posture', '')}")
    lines.append(f"confidence: {tp.get('confidence', '')}")
    lines.append(f"risk_band: {tp.get('risk_band', '')}")
    lines.append(f"degraded: {tp.get('degraded', False)}")
    lines.append(f"ambiguity_flags: {', '.join(_ensure_list(tp.get('ambiguity_flags', [])))}")
    lines.append(f"cap_applied: {tp.get('cap_applied', False)}")
    lines.append(f"deescalation_blocked: {tp.get('deescalation_blocked', False)}")
    lines.append("")

    # 🔒 Required line rendered explicitly (so token scanners cannot miss it)
    lines.append("[Required Operator Framing]")
    lines.append(str(obj.get("required_operator_framing", "")))
    lines.append("")

    lines.append("[What We Can Say]")
    for s in _ensure_list(obj.get("what_we_can_say", [])):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("[What We Cannot Say]")
    for s in _ensure_list(obj.get("what_we_cannot_say", [])):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("[Unknowns]")
    for s in _ensure_list(obj.get("unknowns", [])):
        lines.append(f"- {s}")

    return "\n".join(lines).strip() + "\n"


def write_prebrief_trust_annotations(obj: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(OUT_DIR)
    ts = _ts()

    json_latest = OUT_DIR / "prebrief_trust_annotations_latest.json"
    txt_latest = OUT_DIR / "prebrief_trust_annotations_latest.txt"
    json_stamped = OUT_DIR / f"prebrief_trust_annotations_{ts}.json"
    txt_stamped = OUT_DIR / f"prebrief_trust_annotations_{ts}.txt"

    _write_json(json_latest, obj)
    _write_txt(txt_latest, _render_txt(obj))
    _write_json(json_stamped, obj)
    _write_txt(txt_stamped, _render_txt(obj))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def main() -> None:
    obj = build_prebrief_trust_annotations()
    paths = write_prebrief_trust_annotations(obj)
    print("Prebrief annotation paths:")
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

