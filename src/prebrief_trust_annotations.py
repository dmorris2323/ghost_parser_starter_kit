"""
prebrief_trust_annotations.py

Day 73 — Module 3: Pre-brief trust annotations

Purpose:
- Convert a decision-card report into a concise "trust annotation block"
  suitable for mission briefs / commander products.
- Write a stable artifact that briefing tools can embed without re-computing logic.

Inputs:
- A decision-card JSON dict (typically docs/decision_cards/nuclear_decision_card_latest.json)

Outputs:
- docs/briefs/prebrief_trust_annotations_latest.json
- docs/briefs/prebrief_trust_annotations_<timestamp>.json
- docs/briefs/prebrief_trust_annotations_latest.txt
- docs/briefs/prebrief_trust_annotations_<timestamp>.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


BRIEFS_DIR = Path("docs") / "briefs"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def build_prebrief_trust_annotations(*, decision_card: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts a commander-briefable trust block from a decision card.

    Returns:
      {
        "generated_at": "...",
        "source": { "decision_card_path": "...", "decision_card_generated_at": "..." },
        "gate_status": "...",
        "fusion_trust": 0-100,
        "operator_safety_layer": "...",
        "escalation": { ... },
        "confidence": { ... },
        "brief_lines": [ "...", ... ],
        "trust_annotations": [ "...", ... ],
        "ambiguity_flags": [ "...", ... ]
      }
    """
    esc = decision_card.get("escalation", {}) or {}
    conf = decision_card.get("confidence", {}) or {}

    gate_status = str(decision_card.get("gate_status", "UNKNOWN")).upper()
    fusion_trust = decision_card.get("fusion_trust", 0.0)
    osl = str(decision_card.get("operator_safety_layer", "UNKNOWN")).upper()

    confidence_label = str(conf.get("confidence_label", "UNKNOWN")).upper()
    confidence_score = conf.get("confidence_score", 0.0)

    esc_label = str(esc.get("escalation_label", "MONITOR")).upper()
    esc_level = esc.get("escalation_level", 0)

    ambiguity_flags = conf.get("ambiguity_flags", []) or []
    trust_notes = conf.get("trust_annotations", []) or []

    # Commander-safe 3–6 line block for briefs
    lines = []
    lines.append(f"TRUST STATUS: Gate={gate_status} | OSL={osl} | FusionTrust={fusion_trust}")
    lines.append(f"DECISION CONFIDENCE: {confidence_label} ({confidence_score}/100)")
    lines.append(f"ESCALATION RUNG: {esc_label} (L{esc_level})")

    if ambiguity_flags:
        # Keep it short: top 3 flags max
        top_flags = ambiguity_flags[:3]
        lines.append("AMBIGUITY: " + ", ".join(top_flags))

    # If gates aren't green, this must be explicit
    if gate_status != "GREEN":
        lines.append("LIMITATION: Integrity gates not GREEN → advisory only until corrected.")

    return {
        "generated_at": _utc_now(),
        "source": {
            "decision_card_generated_at": decision_card.get("generated_at"),
        },
        "gate_status": gate_status,
        "fusion_trust": fusion_trust,
        "operator_safety_layer": osl,
        "escalation": esc,
        "confidence": conf,
        "brief_lines": lines,
        "trust_annotations": trust_notes,
        "ambiguity_flags": ambiguity_flags,
        "safe_notice": "SAFE: Pre-brief trust annotations derived from synthetic/abstracted decision card inputs.",
    }


def write_prebrief_trust_annotations(
    *,
    decision_card: Dict[str, Any],
) -> Dict[str, str]:
    """
    Writes latest + stamped JSON/TXT artifacts to docs/briefs/.
    """
    report = build_prebrief_trust_annotations(decision_card=decision_card)

    latest_json = BRIEFS_DIR / "prebrief_trust_annotations_latest.json"
    stamped_json = BRIEFS_DIR / f"prebrief_trust_annotations_{_ts()}.json"
    latest_txt = BRIEFS_DIR / "prebrief_trust_annotations_latest.txt"
    stamped_txt = BRIEFS_DIR / f"prebrief_trust_annotations_{_ts()}.txt"

    _write_json(latest_json, report)
    _write_json(stamped_json, report)
    _write_txt(latest_txt, _render_txt(report))
    _write_txt(stamped_txt, _render_txt(report))

    return {
        "json_latest": str(latest_json),
        "json_stamped": str(stamped_json),
        "txt_latest": str(latest_txt),
        "txt_stamped": str(stamped_txt),
    }


def load_latest_decision_card() -> Optional[Dict[str, Any]]:
    """
    Convenience helper: loads docs/decision_cards/nuclear_decision_card_latest.json if present.
    """
    return _read_json(Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json")


def _render_txt(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("GLL — PRE-BRIEF TRUST ANNOTATIONS (SAFE TRAINING)")
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append("")
    for bl in report.get("brief_lines", []):
        lines.append(f"- {bl}")
    lines.append("")
    if report.get("trust_annotations"):
        lines.append("Trust Notes:")
        for n in report["trust_annotations"]:
            lines.append(f"  - {n}")
    if report.get("ambiguity_flags"):
        lines.append("")
        lines.append("Ambiguity Flags:")
        for f in report["ambiguity_flags"]:
            lines.append(f"  - {f}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    card = load_latest_decision_card()
    if not card:
        raise SystemExit("No decision card found at docs/decision_cards/nuclear_decision_card_latest.json")
    paths = write_prebrief_trust_annotations(decision_card=card)
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

