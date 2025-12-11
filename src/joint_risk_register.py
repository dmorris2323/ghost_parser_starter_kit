#!/usr/bin/env python3
"""
joint_risk_register.py

Ghost Lantern Labs – Joint Risk Register
----------------------------------------

Purpose:
    Generate a simple risk register (top risks) from the joint
    nuclear + base-defense readiness view.

Inputs:
    docs/joint_readiness_board.json

Outputs:
    docs/joint_risk_register.json
    docs/joint_risk_register.txt

This is a commander-facing artifact listing key nuclear, base-defense,
sensor, and fusion risks in bullet form.
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


def build_joint_risk_register() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    board_path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    board = _safe_read_json(board_path)

    risks: List[Dict[str, Any]] = []

    if not isinstance(board, dict):
        result = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "error": "joint_readiness_board.json not available – run joint_readiness_board.py first.",
            "risks": [],
        }
        # Write bare text
        txt_path = os.path.join(DOCS_DIR, "joint_risk_register.txt")
        with open(txt_path, "w", encoding="utf-8") as f_txt:
            f_txt.write(
                "Joint Risk Register\n"
                "===================\n"
                f"Generated at (UTC): {result['generated_at']}\n\n"
                "Joint Readiness Board not available – run joint_readiness_board.py first.\n"
            )
        json_path = os.path.join(DOCS_DIR, "joint_risk_register.json")
        with open(json_path, "w", encoding="utf-8") as f_json:
            json.dump(result, f_json, indent=2, sort_keys=True)
        return result

    # Extract slices
    jr_score = _fmt_float(board.get("joint_readiness_score"), 0.0)
    jr_level = str(board.get("joint_readiness_level", "UNKNOWN"))

    nuclear = board.get("nuclear", {}) or {}
    base_def = board.get("base_defense", {}) or {}
    outage = board.get("outage", {}) or {}
    dist = board.get("distributed_readiness", {}) or {}

    n_score = _fmt_float(nuclear.get("score"))
    n_level = str(nuclear.get("level", "UNKNOWN"))
    n_vol = _fmt_float(nuclear.get("volatility_index"))
    n_drift_conf = _fmt_float(nuclear.get("drift_confidence"))

    b_score = _fmt_float(base_def.get("score"))
    b_level = str(base_def.get("level", "UNKNOWN"))
    b_sectors = base_def.get("sectors", 0)

    o_risk = _fmt_float(outage.get("outage_risk_score"))
    o_crit = outage.get("critical_sensors_at_risk", 0)

    d_fusion = _fmt_float(dist.get("fusion_trust_score"))
    d_rel = _fmt_float(dist.get("average_reliability"))

    # Build risk items roughly sorted by severity.

    # 1. Nuclear volatility / escalation risk
    if n_score > 40.0 or n_vol > 40.0:
        risks.append(
            {
                "domain": "NUCLEAR",
                "title": "Elevated nuclear early-warning posture",
                "detail": (
                    f"Nuclear early-warning score {n_score:.1f}/100 (level {n_level}) with "
                    f"temporal volatility {n_vol:.1f}/100 suggests elevated nuclear monitoring requirement."
                ),
                "severity": "HIGH" if n_score >= 70.0 or n_vol >= 70.0 else "MEDIUM",
            }
        )

    # 2. Base-defense threat risk
    if b_score > 30.0:
        risks.append(
            {
                "domain": "BASE_DEFENSE",
                "title": "Base perimeter/airspace threat pressure",
                "detail": (
                    f"Base threat score {b_score:.1f}/100 (level {b_level}) across "
                    f"{b_sectors} sectors indicates sustained base-defense pressure."
                ),
                "severity": "HIGH" if b_score >= 70.0 else "MEDIUM",
            }
        )

    # 3. Sensor outage risk
    if o_risk > 20.0 or o_crit > 0:
        risks.append(
            {
                "domain": "SENSORS",
                "title": "Sensor outage risk impacting early warning",
                "detail": (
                    f"Sensor outage risk {o_risk:.1f}/100 with "
                    f"{o_crit} critical sensors at risk reduces confidence in both nuclear and base-defense posture."
                ),
                "severity": "HIGH" if o_risk >= 60.0 or o_crit >= 2 else "MEDIUM",
            }
        )

    # 4. Fusion trust / reliability risk
    if d_fusion < 60.0 or d_rel < 70.0:
        risks.append(
            {
                "domain": "FUSION",
                "title": "Fusion trust and reliability under target",
                "detail": (
                    f"Fusion trust {d_fusion:.1f}/100 and average reliability {d_rel:.1f}/100 "
                    f"indicate the fusion engine and/or sensors need tuning and validation."
                ),
                "severity": "MEDIUM" if d_fusion >= 40.0 and d_rel >= 50.0 else "HIGH",
            }
        )

    # 5. Overall joint readiness risk if joint score low
    if jr_score < 70.0:
        risks.append(
            {
                "domain": "JOINT",
                "title": "Joint readiness below ideal band",
                "detail": (
                    f"Joint readiness score {jr_score:.1f}/100 (level {jr_level}) indicates "
                    f"the combined nuclear + base-defense posture is not fully in GREEN."
                ),
                "severity": "HIGH" if jr_score < 40.0 else "MEDIUM",
            }
        )

    # Sort by severity (HIGH first)
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    risks_sorted = sorted(
        risks,
        key=lambda r: severity_order.get(r.get("severity", "MEDIUM"), 1),
    )

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "joint_readiness_score": jr_score,
        "joint_readiness_level": jr_level,
        "risks": risks_sorted,
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "joint_risk_register.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Joint Risk Register")
    lines.append("=======================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Joint Readiness: {jr_level} ({jr_score:.1f}/100)")
    lines.append("")
    if not risks_sorted:
        lines.append("No significant risks identified from the current joint readiness board.")
    else:
        lines.append("Top Risks:")
        for idx, r in enumerate(risks_sorted, start=1):
            lines.append(f"{idx}. [{r['severity']}] {r['domain']} – {r['title']}")
            lines.append(f"   {r['detail']}")
    txt_path = os.path.join(DOCS_DIR, "joint_risk_register.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_joint_risk_register()
    print("Joint Risk Register generated:")
    print(f"  - {os.path.join('docs', 'joint_risk_register.json')}")
    print(f"  - {os.path.join('docs', 'joint_risk_register.txt')}")

