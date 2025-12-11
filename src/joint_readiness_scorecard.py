#!/usr/bin/env python3
"""
joint_readiness_scorecard.py

Ghost Lantern Labs – Joint Readiness Scorecard
----------------------------------------------

Purpose:
    Convert joint_readiness_board.json into a very clean, commander-
    friendly "scorecard" for briefings, AFWERX/SBIR decks, and
    Shari demo day.

Inputs:
    docs/joint_readiness_board.json

Outputs:
    docs/joint_readiness_scorecard.txt

This is a text-only, human-facing product.
"""

import json
import os
from datetime import datetime
from typing import Any, Optional

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def build_joint_readiness_scorecard() -> str:
    os.makedirs(DOCS_DIR, exist_ok=True)

    board_path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    board = _safe_read_json(board_path)

    if not isinstance(board, dict):
        # minimal stub output
        txt_path = os.path.join(DOCS_DIR, "joint_readiness_scorecard.txt")
        with open(txt_path, "w", encoding="utf-8") as f_txt:
            f_txt.write(
                "Joint Readiness Scorecard\n"
                "==========================\n"
                f"Generated at (UTC): {datetime.utcnow().isoformat()}Z\n\n"
                "Joint Readiness Board not available – run joint_readiness_board.py first.\n"
            )
        return txt_path

    jr_score = board.get("joint_readiness_score", 0.0)
    jr_level = board.get("joint_readiness_level", "UNKNOWN")

    nuclear = board.get("nuclear", {}) or {}
    base_def = board.get("base_defense", {}) or {}
    outage = board.get("outage", {}) or {}
    dist = board.get("distributed_readiness", {}) or {}

    def _fmt_float(val: Any, default: float = 0.0) -> float:
        try:
            return float(val)
        except Exception:
            return default

    n_score = _fmt_float(nuclear.get("score"))
    n_level = nuclear.get("level", "UNKNOWN")
    n_drift_conf = _fmt_float(nuclear.get("drift_confidence"))
    n_vol = _fmt_float(nuclear.get("volatility_index"))

    b_score = _fmt_float(base_def.get("score"))
    b_level = base_def.get("level", "UNKNOWN")
    b_sectors = base_def.get("sectors", 0)

    o_risk = _fmt_float(outage.get("outage_risk_score"))
    o_crit = outage.get("critical_sensors_at_risk", 0)

    d_fusion = _fmt_float(dist.get("fusion_trust_score"))
    d_rel = _fmt_float(dist.get("average_reliability"))
    d_units = dist.get("units_tracked", 0)

    # Build the scorecard text
    lines = []
    lines.append("Joint Readiness Scorecard – Ghost Lantern Labs")
    lines.append("==============================================")
    lines.append(f"Generated at (UTC): {board.get('generated_at', datetime.utcnow().isoformat() + 'Z')}")
    lines.append("")
    lines.append(f"JOINT READINESS: {jr_level}  ({jr_score:.1f}/100)")
    lines.append("")
    lines.append("NUCLEAR POSTURE")
    lines.append("----------------")
    lines.append(f"  • Nuclear Early-Warning Level: {n_level}")
    lines.append(f"  • Nuclear Early-Warning Score: {n_score:.1f}/100")
    lines.append(f"  • Drift Confidence: {n_drift_conf:.1f}/100")
    lines.append(f"  • Temporal Volatility: {n_vol:.1f}/100")
    lines.append("")
    lines.append("BASE DEFENSE POSTURE")
    lines.append("---------------------")
    lines.append(f"  • Base Threat Level: {b_level}")
    lines.append(f"  • Base Threat Score: {b_score:.1f}/100")
    lines.append(f"  • Sectors Tracked: {b_sectors}")
    lines.append("")
    lines.append("SENSOR & FUSION HEALTH")
    lines.append("------------------------")
    lines.append(f"  • Sensor Outage Risk: {o_risk:.1f}/100")
    lines.append(f"  • Critical Sensors at Risk: {o_crit}")
    lines.append(f"  • Fusion Trust Score: {d_fusion:.1f}/100")
    lines.append(f"  • Avg Sensor Reliability: {d_rel:.1f}/100")
    lines.append(f"  • Units / Elements Tracked: {d_units}")
    lines.append("")
    lines.append("INTERPRETATION GUIDE")
    lines.append("---------------------")
    lines.append("  • GREEN (70–100): System is ready; nuclear + base-defense posture aligned and stable.")
    lines.append("  • AMBER (40–69): System is under stress; commanders should increase monitoring and prepare contingencies.")
    lines.append("  • RED (<40): System is degraded or under significant threat; immediate command attention required.")
    lines.append("")
    lines.append("NOTE:")
    lines.append("  This scorecard fuses nuclear early warning, base-defense threat, sensor outage risk,")
    lines.append("  and fusion health into a single view suitable for commanders, evaluators, and demos.")

    txt_path = os.path.join(DOCS_DIR, "joint_readiness_scorecard.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return txt_path


if __name__ == "__main__":
    out_path = build_joint_readiness_scorecard()
    print("Joint Readiness Scorecard generated:")
    print(f"  - {os.path.join('docs', 'joint_readiness_scorecard.txt')}")

