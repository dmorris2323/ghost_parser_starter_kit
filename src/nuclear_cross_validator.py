#!/usr/bin/env python3
"""
nuclear_cross_validator.py

Ghost Lantern Labs – Nuclear Hardening Block
--------------------------------------------

Purpose:
    Cross-check nuclear early-warning indicators across multiple
    upstream artifacts to reduce false positives and produce a
    simple "cross-validation" confidence picture.

Inputs (all optional, defensive):
    docs/golden_dome_daily_watch.json
    docs/prelaunch_watchboard.json
    docs/nuclear_decision_card.txt (text only, best-effort parse)

Outputs:
    docs/nuclear_cross_validation.json
    docs/nuclear_cross_validation.txt

This module does NOT modify any upstream files. It is read-only and
adds a layer of validation and explainability on top of existing
nuclear products.
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


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _extract_watchboard_level(wb: Any) -> Dict[str, Any]:
    if not isinstance(wb, dict):
        return {"level": "UNKNOWN", "score": 0.0}
    level = wb.get("early_warning_level", "UNKNOWN")
    score = wb.get("early_warning_score", 0.0)
    try:
        score = float(score)
    except Exception:
        score = 0.0
    return {"level": level, "score": score}


def _extract_golden_dome_level(gd: Any) -> Dict[str, Any]:
    """
    Try to infer a readiness level from Golden Dome daily watch JSON.

    We keep this generic: look for 'golden_dome_level' or similar;
    if not found, fall back to heuristic text inspection.
    """
    if not isinstance(gd, dict):
        return {"level": "UNKNOWN", "notes": ["Golden Dome JSON not structured as dict."]}

    # Direct level field
    level = gd.get("golden_dome_level") or gd.get("readiness_level")
    notes: List[str] = []

    if not level:
        # Fallback: look for textual hints
        text_blob = json.dumps(gd).lower()
        if "green" in text_blob:
            level = "GREEN"
        elif "amber" in text_blob or "yellow" in text_blob:
            level = "AMBER"
        elif "red" in text_blob:
            level = "RED"
        else:
            level = "UNKNOWN"
            notes.append("No explicit Golden Dome readiness level; used heuristic scan.")

    return {"level": str(level), "notes": notes}


def _extract_decision_card_tone(dc_text: Optional[str]) -> Dict[str, str]:
    """
    Best-effort extraction of tone from nuclear_decision_card.txt.

    We don't rely on a rigid schema; just scan for words that suggest
    calm / elevated / severe posture.
    """
    if not dc_text:
        return {"tone": "UNKNOWN", "notes": "Decision card not available."}

    t = dc_text.lower()
    notes = []

    if any(x in t for x in ["no significant nuclear activity", "steady", "normal posture"]):
        tone = "STEADY"
    elif any(x in t for x in ["heightened", "elevated", "increased monitoring"]):
        tone = "ELEVATED"
    elif any(x in t for x in ["high concern", "potential escalation", "serious", "crisis"]):
        tone = "SEVERE"
    else:
        tone = "UNKNOWN"
        notes.append("Could not infer tone explicitly from decision card text.")

    return {"tone": tone, "notes": "; ".join(notes) if notes else ""}


def _compute_alignment(
    watchboard_level: str,
    golden_dome_level: str,
    decision_tone: str,
) -> Dict[str, Any]:
    """
    Very simple rule-based "alignment" rating.

    We classify alignment as:
        - HIGH: all agree or differ by at most one notch logically
        - MEDIUM: partial alignment
        - LOW: conflicting signals
    """
    rationale: List[str] = []

    wb = watchboard_level.upper()
    gd = golden_dome_level.upper()
    dc = decision_tone.upper()

    levels = {
        "UNKNOWN": 0,
        "STEADY": 1,
        "GREEN": 1,
        "TENSE": 2,
        "ELEVATED": 2,
        "AMBER": 2,
        "ALERT": 3,
        "RED": 4,
        "CRITICAL": 4,
        "SEVERE": 4,
    }

    wb_val = levels.get(wb, 0)
    gd_val = levels.get(gd, 0)
    dc_val = levels.get(dc, 0)

    vals = [wb_val, gd_val, dc_val]
    non_zero_vals = [v for v in vals if v > 0]

    if not non_zero_vals:
        alignment = "UNKNOWN"
        score = 0.0
        rationale.append("Insufficient structured levels to compute cross-alignment.")
    else:
        spread = max(non_zero_vals) - min(non_zero_vals)
        if spread == 0:
            alignment = "HIGH"
            score = 90.0
            rationale.append("All nuclear indicators are at roughly the same level.")
        elif spread == 1:
            alignment = "HIGH"
            score = 75.0
            rationale.append("Indicators differ slightly but remain within one band.")
        elif spread == 2:
            alignment = "MEDIUM"
            score = 50.0
            rationale.append("Indicators show moderate disagreement across nuclear posture.")
        else:
            alignment = "LOW"
            score = 20.0
            rationale.append("Indicators significantly disagree; heightened analyst review needed.")

    rationale.append(
        f"Levels observed – Watchboard: {wb}, Golden Dome: {gd}, Decision Card: {dc}."
    )

    return {
        "alignment": alignment,
        "alignment_score": score,
        "rationale": rationale,
    }


def build_nuclear_cross_validation() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    golden_dome_path = os.path.join(DOCS_DIR, "golden_dome_daily_watch.json")
    watchboard_path = os.path.join(DOCS_DIR, "prelaunch_watchboard.json")
    decision_card_path = os.path.join(DOCS_DIR, "nuclear_decision_card.txt")

    golden_dome = _safe_read_json(golden_dome_path)
    watchboard = _safe_read_json(watchboard_path)
    decision_card_txt = _safe_read_text(decision_card_path)

    inputs_present = {
        "golden_dome_daily_watch_json": golden_dome is not None,
        "prelaunch_watchboard_json": watchboard is not None,
        "nuclear_decision_card_txt": decision_card_txt is not None,
    }

    wb_info = _extract_watchboard_level(watchboard)
    gd_info = _extract_golden_dome_level(golden_dome)
    dc_info = _extract_decision_card_tone(decision_card_txt)

    align_info = _compute_alignment(
        watchboard_level=wb_info["level"],
        golden_dome_level=gd_info["level"],
        decision_tone=dc_info["tone"],
    )

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "watchboard_level": wb_info["level"],
        "watchboard_score": wb_info["score"],
        "golden_dome_level": gd_info["level"],
        "golden_dome_notes": gd_info["notes"],
        "decision_card_tone": dc_info["tone"],
        "decision_card_notes": dc_info["notes"],
        "alignment": align_info["alignment"],
        "alignment_score": align_info["alignment_score"],
        "alignment_rationale": align_info["rationale"],
    }

    # Write JSON
    json_path = os.path.join(DOCS_DIR, "nuclear_cross_validation.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # Write TXT
    lines: List[str] = []
    lines.append("GLL Nuclear Cross-Validation Summary")
    lines.append("====================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append(f"Watchboard Level: {result['watchboard_level']} ({result['watchboard_score']:.1f}/100)")
    lines.append(f"Golden Dome Level: {result['golden_dome_level']}")
    lines.append(f"Decision Card Tone: {result['decision_card_tone']}")
    lines.append("")
    lines.append(f"Alignment: {result['alignment']} ({result['alignment_score']:.1f}/100)")
    lines.append("Rationale:")
    for r in result["alignment_rationale"]:
        lines.append(f"  - {r}")

    txt_path = os.path.join(DOCS_DIR, "nuclear_cross_validation.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_nuclear_cross_validation()
    print("Nuclear cross-validation generated:")
    print(f"  - {os.path.join('docs', 'nuclear_cross_validation.json')}")
    print(f"  - {os.path.join('docs', 'nuclear_cross_validation.txt')}")

