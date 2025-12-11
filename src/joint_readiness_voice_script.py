#!/usr/bin/env python3
"""
joint_readiness_voice_script.py

Ghost Lantern Labs – Obasi Joint Readiness Voice Script
-------------------------------------------------------

Purpose:
    Generate a concise, Obasi-style voice script summarizing the
    Joint Readiness Board and top risks.

Usage:
    - Feed the text to a TTS engine for an audio brief.
    - Use the JSON to drive a future Obasi/IMF-style copilot.

Inputs:
    docs/joint_readiness_board.json
    docs/joint_risk_register.json

Outputs:
    docs/joint_readiness_voice_script.txt
    docs/joint_readiness_voice_script.json
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


def _fmt_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def _trim(text: str) -> str:
    return " ".join(text.split())


def build_joint_readiness_voice_script() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    board_path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    risk_path = os.path.join(DOCS_DIR, "joint_risk_register.json")

    board = _safe_read_json(board_path) or {}
    risk = _safe_read_json(risk_path) or {}

    generated_at = board.get("generated_at", datetime.utcnow().isoformat() + "Z")

    jr_score = _fmt_float(board.get("joint_readiness_score"), 0.0)
    jr_level = str(board.get("joint_readiness_level", "UNKNOWN")).upper()

    nuclear = board.get("nuclear", {}) or {}
    base_def = board.get("base_defense", {}) or {}
    outage = board.get("outage", {}) or {}
    dist = board.get("distributed_readiness", {}) or {}

    n_level = str(nuclear.get("level", "UNKNOWN")).upper()
    n_score = _fmt_float(nuclear.get("score"))
    n_vol = _fmt_float(nuclear.get("volatility_index"))
    n_drift_conf = _fmt_float(nuclear.get("drift_confidence"))

    b_level = str(base_def.get("level", "UNKNOWN")).upper()
    b_score = _fmt_float(base_def.get("score"))

    o_risk = _fmt_float(outage.get("outage_risk_score"))
    o_crit = int(outage.get("critical_sensors_at_risk", 0))

    d_fusion = _fmt_float(dist.get("fusion_trust_score"))
    d_rel = _fmt_float(dist.get("average_reliability"))

    risks: List[Dict[str, Any]] = []
    if isinstance(risk.get("risks"), list):
        risks = [r for r in risk["risks"] if isinstance(r, dict)]

    # --- Build voice segments (Obasi tone, but neutral content) ---

    opening = (
        "Obasi status check. Delivering joint nuclear and base-defense readiness for Ghost Lantern Labs."
    )

    joint_summary = (
        f"Joint readiness is {jr_level}, scored at {jr_score:.1f} out of 100. "
        "This reflects the combined posture across nuclear early warning, base perimeter and airspace, "
        "sensor outages, and fusion engine health."
    )

    nuclear_summary = (
        f"Nuclear posture is {n_level}, with an early-warning score of {n_score:.1f} out of 100. "
        f"Temporal volatility is {n_vol:.1f} out of 100, and drift confidence is {n_drift_conf:.1f} out of 100. "
        "Higher volatility means more rapid movement in nuclear-relevant signals."
    )

    base_defense_summary = (
        f"Base-defense posture is {b_level}, with a threat score of {b_score:.1f} out of 100. "
        f"Sensor outage risk is {o_risk:.1f} out of 100, with {o_crit} critical sensors flagged at risk. "
        f"The fusion engine trust is {d_fusion:.1f} out of 100, and average sensor reliability is {d_rel:.1f} out of 100."
    )

    # Top 3 risks for voice
    risk_lines: List[str] = []
    if risks:
        first_three = risks[:3]
        for idx, r in enumerate(first_three, start=1):
            severity = str(r.get("severity", "MEDIUM")).upper()
            domain = str(r.get("domain", "JOINT")).upper()
            title = _trim(str(r.get("title", "")))
            detail = _trim(str(r.get("detail", "")))
            risk_lines.append(
                f"Risk {idx}: {severity} in {domain}. {title}. {detail}"
            )
    else:
        risk_lines.append(
            "No major joint risks were elevated by the current board. Maintain routine monitoring."
        )

    risks_block = " ".join(risk_lines)

    closing = (
        "End of Obasi joint readiness update. Recommend commanders review the full scorecard and risk register "
        "inside Ghost Lantern Labs for detailed planning."
    )

    # Combine into one script text
    script_text = " ".join(
        [
            opening,
            joint_summary,
            nuclear_summary,
            base_defense_summary,
            risks_block,
            closing,
        ]
    )

    result: Dict[str, Any] = {
        "generated_at": generated_at,
        "voice_profile": "Obasi",
        "segments": {
            "opening": opening,
            "joint_summary": joint_summary,
            "nuclear_summary": nuclear_summary,
            "base_defense_summary": base_defense_summary,
            "top_risks": risks_block,
            "closing": closing,
        },
        "full_script": script_text,
    }

    # Write JSON
    json_path = os.path.join(DOCS_DIR, "joint_readiness_voice_script.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # Write TXT
    txt_path = os.path.join(DOCS_DIR, "joint_readiness_voice_script.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write(script_text)

    return result


if __name__ == "__main__":
    out = build_joint_readiness_voice_script()
    print("Joint Readiness Voice Script generated:")
    print(f"  - {os.path.join('docs', 'joint_readiness_voice_script.json')}")
    print(f"  - {os.path.join('docs', 'joint_readiness_voice_script.txt')}")

