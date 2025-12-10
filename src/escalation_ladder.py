#!/usr/bin/env python3
"""
escalation_ladder.py

Day 66 – Ghost Lantern Labs

Builds a simple, rule-based Nuclear Escalation Ladder assessment using
signals derived from existing artifacts:

- docs/nuclear_status_summary.json (primary)
- docs/nuclear_decision_card.txt (fallback)

Outputs:
- docs/escalation_ladder.json
- docs/escalation_ladder.txt

Ladder Levels:
- STEADY
- TENSE
- BRINK
- FLASHPOINT

This is deliberately conservative and explainable: no ML, just clear
rule-based thresholds based on crisis mode, fusion trust, and heat.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _parse_numeric_from_line(line: Optional[str]) -> Optional[float]:
    if not line:
        return None
    # Grab the first number-like token we find.
    import re

    matches = re.findall(r"[-+]?\d+(\.\d+)?", line)
    if not matches:
        return None
    try:
        # Take the first full match
        num_str = re.findall(r"[-+]?\d+(?:\.\d+)?", line)[0]
        return float(num_str)
    except Exception:
        return None


def _infer_crisis_and_scores(
    status_summary: Optional[Dict[str, Any]],
    decision_card_text: Optional[str],
) -> Tuple[bool, Optional[float], Optional[float]]:
    """
    Returns:
        crisis_on (bool)
        fusion_trust_score (0-100, optional)
        fusion_heat_index (0-100+, optional)
    """
    crisis_on = False
    fusion_trust_score: Optional[float] = None
    fusion_heat_index: Optional[float] = None

    # Try structured signals from status summary first
    if status_summary:
        signals = status_summary.get("nuclear_signals", {})
        crisis_line = signals.get("crisis_mode_line")
        trust_line = signals.get("fusion_trust_line")
        heat_line = signals.get("fusion_heat_index_line")

        if crisis_line and "on" in crisis_line.lower():
            crisis_on = True

        trust_val = _parse_numeric_from_line(trust_line)
        heat_val = _parse_numeric_from_line(heat_line)

        if trust_val is not None:
            fusion_trust_score = trust_val
        if heat_val is not None:
            fusion_heat_index = heat_val

    # Fallback: parse directly from decision card text if necessary
    if decision_card_text:
        lines = decision_card_text.splitlines()
        for line in lines:
            lower = line.lower()
            if "crisis mode" in lower and "on" in lower:
                crisis_on = True
            if fusion_trust_score is None and "fusion trust" in lower:
                fusion_trust_score = _parse_numeric_from_line(line)
            if fusion_heat_index is None and (
                "fusion heat" in lower or "heat index" in lower
            ):
                fusion_heat_index = _parse_numeric_from_line(line)

    return crisis_on, fusion_trust_score, fusion_heat_index


def _determine_level(
    crisis_on: bool,
    trust: Optional[float],
    heat: Optional[float],
) -> Tuple[str, str]:
    """
    Returns (level, rationale)
    """

    # Defaults if we have almost no information
    if trust is None and heat is None:
        if crisis_on:
            return (
                "TENSE",
                "Crisis mode is ON, but trust/heat scores are unavailable. Defaulting to TENSE.",
            )
        return (
            "STEADY",
            "No crisis flag and no quantitative scores available. Defaulting to STEADY.",
        )

    # Normalize defaults
    t = trust if trust is not None else 70.0
    h = heat if heat is not None else 50.0

    # FLASHPOINT – worst conditions
    if crisis_on and (t < 40 or h >= 85):
        return (
            "FLASHPOINT",
            f"Crisis ON with low fusion trust ({t:.1f}) and/or high heat ({h:.1f}).",
        )

    # BRINK – dangerous but not fully escalated
    if crisis_on and (40 <= t < 60 or 70 <= h < 85):
        return (
            "BRINK",
            f"Crisis ON with mid-range trust ({t:.1f}) and elevated heat ({h:.1f}).",
        )

    # TENSE – elevated concern but not brinkmanship
    if (not crisis_on and (t < 60 or h >= 60)) or (crisis_on and (t >= 60 and h < 70)):
        return (
            "TENSE",
            f"Crisis flag = {crisis_on}, trust = {t:.1f}, heat = {h:.1f}. Elevated concern.",
        )

    # STEADY – conditions relatively calm
    return (
        "STEADY",
        f"Crisis flag = {crisis_on}, trust = {t:.1f}, heat = {h:.1f}. Conditions appear stable.",
    )


def build_escalation_ladder() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    status_path = os.path.join(DOCS_DIR, "nuclear_status_summary.json")
    decision_card_path = os.path.join(DOCS_DIR, "nuclear_decision_card.txt")

    status_summary = _safe_read_json(status_path)
    decision_card_text = _safe_read_text(decision_card_path)

    crisis_on, trust, heat = _infer_crisis_and_scores(status_summary, decision_card_text)
    level, rationale = _determine_level(crisis_on, trust, heat)

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "crisis_mode_on": crisis_on,
        "fusion_trust_score": trust,
        "fusion_heat_index": heat,
        "escalation_level": level,
        "rationale": rationale,
        "inputs": {
            "nuclear_status_summary_present": status_summary is not None,
            "nuclear_decision_card_present": decision_card_text is not None,
        },
    }

    json_path = os.path.join(DOCS_DIR, "escalation_ladder.json")
    txt_path = os.path.join(DOCS_DIR, "escalation_ladder.txt")

    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    lines = []
    lines.append("GLL Nuclear Escalation Ladder")
    lines.append("================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Escalation Level: {level}")
    lines.append(f"Rationale: {rationale}")
    lines.append("")
    lines.append(f"Crisis Mode ON: {crisis_on}")
    lines.append(f"Fusion Trust Score: {trust if trust is not None else 'UNKNOWN'}")
    lines.append(f"Fusion Heat Index: {heat if heat is not None else 'UNKNOWN'}")
    lines.append("")
    lines.append("Inputs:")
    lines.append(
        f"  Nuclear Status Summary present: {result['inputs']['nuclear_status_summary_present']}"
    )
    lines.append(
        f"  Nuclear Decision Card present: {result['inputs']['nuclear_decision_card_present']}"
    )

    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    ladder = build_escalation_ladder()
    print("Escalation Ladder generated:")
    print(f"  - {os.path.join(DOCS_DIR, 'escalation_ladder.json')}")
    print(f"  - {os.path.join(DOCS_DIR, 'escalation_ladder.txt')}")

