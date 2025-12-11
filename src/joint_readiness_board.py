#!/usr/bin/env python3
"""
joint_readiness_board.py

Ghost Lantern Labs – Joint Nuclear + Base-Defense Readiness Board
-----------------------------------------------------------------

Purpose:
    Fuse GLL's nuclear early-warning picture and base-defense picture
    into a single "Joint Readiness Board" for commanders and reviewers.

Inputs (all optional, defensive):

    docs/nuclear_early_warning_summary.json
    docs/installation_threat_map.json
    docs/sensor_outage_predictor.json
    docs/distributed_readiness_snapshot.json
    docs/base_defense_storyboard.json

Outputs:

    docs/joint_readiness_board.json
    docs/joint_readiness_board.txt

This module is aggregation-only. It does NOT modify upstream files.
It provides a concise 0–100 joint readiness score and a GREEN/AMBER/RED
style level, with narrative rationale.
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


def _load(path: str) -> Any:
    return _safe_read_json(path)


def _extract_nuclear_block(ne: Any) -> Dict[str, Any]:
    """
    Extract the nuclear early-warning posture from nuclear_early_warning_summary.json
    """
    if not isinstance(ne, dict):
        return {
            "level": "UNKNOWN",
            "score": 0.0,
            "volatility_index": 0.0,
            "drift_confidence": 0.0,
            "alignment": "UNKNOWN",
        }

    level = ne.get("overall_nuclear_early_warning_level") or ne.get(
        "base_early_warning_level", "UNKNOWN"
    )
    try:
        score = float(
            ne.get("drift_adjusted_early_warning_score")
            or ne.get("base_early_warning_score", 0.0)
        )
    except Exception:
        score = 0.0

    try:
        volatility_index = float(ne.get("volatility_index", 0.0))
    except Exception:
        volatility_index = 0.0

    try:
        drift_confidence = float(ne.get("drift_confidence", 0.0))
    except Exception:
        drift_confidence = 0.0

    alignment = ne.get("alignment", "UNKNOWN")

    return {
        "level": str(level),
        "score": max(0.0, min(100.0, score)),
        "volatility_index": max(0.0, min(100.0, volatility_index)),
        "drift_confidence": max(0.0, min(100.0, drift_confidence)),
        "alignment": str(alignment),
    }


def _extract_base_threat_block(bt: Any) -> Dict[str, Any]:
    """
    Extract a base-defense threat score+level from installation_threat_map.json
    """
    if not isinstance(bt, dict):
        return {"level": "UNKNOWN", "score": 0.0, "sectors": 0}

    try:
        threat_score = float(bt.get("overall_threat_score", 0.0))
    except Exception:
        threat_score = 0.0

    level = bt.get("overall_threat_level")
    if not level:
        # Simple threshold mapping if not present
        if threat_score < 20:
            level = "LOW"
        elif threat_score < 50:
            level = "MODERATE"
        elif threat_score < 75:
            level = "ELEVATED"
        else:
            level = "SEVERE"

    sectors = 0
    if isinstance(bt.get("sectors"), list):
        sectors = len(bt["sectors"])

    return {
        "level": str(level),
        "score": max(0.0, min(100.0, threat_score)),
        "sectors": sectors,
    }


def _extract_outage_block(so: Any) -> Dict[str, Any]:
    """
    Extract a sensor outage risk from sensor_outage_predictor.json
    """
    if not isinstance(so, dict):
        return {"outage_risk_score": 0.0, "critical_sensors_at_risk": 0}

    try:
        risk_score = float(so.get("global_outage_risk_score", 0.0))
    except Exception:
        risk_score = 0.0

    critical_at_risk = 0
    crit_list = so.get("critical_sensors_at_risk")
    if isinstance(crit_list, list):
        critical_at_risk = len(crit_list)

    return {
        "outage_risk_score": max(0.0, min(100.0, risk_score)),
        "critical_sensors_at_risk": critical_at_risk,
    }


def _extract_distributed_readiness(dr: Any) -> Dict[str, Any]:
    """
    Extract wing/group/squadron readiness summary from distributed_readiness_snapshot.json
    """
    if not isinstance(dr, dict):
        return {
            "fusion_trust_score": 0.0,
            "average_reliability": 0.0,
            "units_tracked": 0,
        }

    try:
        fusion_trust = float(dr.get("fusion_trust_score", 0.0))
    except Exception:
        fusion_trust = 0.0

    try:
        avg_rel = float(dr.get("average_reliability", 0.0))
    except Exception:
        avg_rel = 0.0

    units_tracked = 0
    units = dr.get("units") or dr.get("elements")
    if isinstance(units, list):
        units_tracked = len(units)

    return {
        "fusion_trust_score": max(0.0, min(100.0, fusion_trust)),
        "average_reliability": max(0.0, min(100.0, avg_rel)),
        "units_tracked": units_tracked,
    }


def _extract_storyboard_tone(sb: Any) -> str:
    """
    Pull a very coarse tone from base_defense_storyboard.json
    """
    if not isinstance(sb, dict):
        return "UNKNOWN"

    text_blob = json.dumps(sb).lower()
    if "contained" in text_blob or "resolved" in text_blob:
        return "CONTAINED"
    if "ongoing" in text_blob or "active response" in text_blob:
        return "ACTIVE"
    if "overwhelmed" in text_blob or "critical failure" in text_blob:
        return "CRITICAL"
    return "UNKNOWN"


def _compute_joint_readiness_level(
    nuclear_score: float,
    nuclear_level: str,
    base_score: float,
    outage_risk: float,
    fusion_trust: float,
) -> Dict[str, Any]:
    """
    Combine the domains into a single 0–100 joint readiness score and
    a GREEN/AMBER/RED level.

    Simple model:
        - Start from 100 (perfect).
        - Subtract weighted nuclear pressure.
        - Subtract weighted base threat.
        - Subtract outage risk fraction.
        - Add a small bonus for strong fusion_trust.

    Then map to level:
        >= 70 => GREEN
        40–69 => AMBER
        < 40  => RED
    """
    # Nuclear penalty: higher nuclear_score => more penalty
    nuclear_penalty = nuclear_score * 0.5  # up to -50
    base_penalty = base_score * 0.3        # up to -30
    outage_penalty = outage_risk * 0.2     # up to -20
    trust_bonus = (fusion_trust - 50.0) * 0.2  # if >50, small positive; if <50, negative

    joint_score = 100.0 - (nuclear_penalty + base_penalty + outage_penalty) + trust_bonus
    joint_score = max(0.0, min(100.0, joint_score))

    if joint_score >= 70.0:
        level = "GREEN"
    elif joint_score >= 40.0:
        level = "AMBER"
    else:
        level = "RED"

    rationale: List[str] = []
    rationale.append(
        f"Nuclear early-warning score {nuclear_score:.1f}/100 (level {nuclear_level}) applies a strong penalty."
    )
    rationale.append(
        f"Base-defense threat score {base_score:.1f}/100 increases penalty when the base perimeter/airspace is stressed."
    )
    rationale.append(
        f"Sensor outage risk score {outage_risk:.1f}/100 further reduces confidence in the joint picture."
    )
    rationale.append(
        f"Fusion trust score {fusion_trust:.1f}/100 provides a modest bonus when the fusion engine is performing well."
    )
    rationale.append(
        f"Resulting joint readiness score: {joint_score:.1f}/100 → level {level}."
    )

    return {
        "joint_readiness_score": joint_score,
        "joint_readiness_level": level,
        "rationale": rationale,
    }


def build_joint_readiness_board() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    nuclear_path = os.path.join(DOCS_DIR, "nuclear_early_warning_summary.json")
    inst_path = os.path.join(DOCS_DIR, "installation_threat_map.json")
    outage_path = os.path.join(DOCS_DIR, "sensor_outage_predictor.json")
    dist_path = os.path.join(DOCS_DIR, "distributed_readiness_snapshot.json")
    story_path = os.path.join(DOCS_DIR, "base_defense_storyboard.json")

    nuclear = _load(nuclear_path)
    inst = _load(inst_path)
    outage = _load(outage_path)
    dist = _load(dist_path)
    story = _load(story_path)

    inputs_present = {
        "nuclear_early_warning_summary_json": nuclear is not None,
        "installation_threat_map_json": inst is not None,
        "sensor_outage_predictor_json": outage is not None,
        "distributed_readiness_snapshot_json": dist is not None,
        "base_defense_storyboard_json": story is not None,
    }

    n_block = _extract_nuclear_block(nuclear)
    b_block = _extract_base_threat_block(inst)
    o_block = _extract_outage_block(outage)
    d_block = _extract_distributed_readiness(dist)
    storyboard_tone = _extract_storyboard_tone(story)

    joint = _compute_joint_readiness_level(
        nuclear_score=n_block["score"],
        nuclear_level=n_block["level"],
        base_score=b_block["score"],
        outage_risk=o_block["outage_risk_score"],
        fusion_trust=d_block["fusion_trust_score"],
    )

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "nuclear": n_block,
        "base_defense": b_block,
        "outage": o_block,
        "distributed_readiness": d_block,
        "storyboard_tone": storyboard_tone,
        "joint_readiness_score": joint["joint_readiness_score"],
        "joint_readiness_level": joint["joint_readiness_level"],
        "joint_rationale": joint["rationale"],
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Joint Readiness Board – Nuclear + Base Defense")
    lines.append("==================================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Joint Readiness Score: {result['joint_readiness_score']:.1f}/100")
    lines.append(f"Joint Readiness Level: {result['joint_readiness_level']}")
    lines.append("")
    lines.append("Domain Snapshots:")
    lines.append(
        f"  • Nuclear: level {n_block['level']}, score {n_block['score']:.1f}/100, "
        f"volatility {n_block['volatility_index']:.1f}/100, drift confidence {n_block['drift_confidence']:.1f}/100, "
        f"alignment {n_block['alignment']}."
    )
    lines.append(
        f"  • Base Defense: level {b_block['level']}, threat score {b_block['score']:.1f}/100, "
        f"sectors tracked: {b_block['sectors']}."
    )
    lines.append(
        f"  • Sensor Outage: outage risk {o_block['outage_risk_score']:.1f}/100, "
        f"critical sensors at risk: {o_block['critical_sensors_at_risk']}."
    )
    lines.append(
        f"  • Distributed Readiness: fusion trust {d_block['fusion_trust_score']:.1f}/100, "
        f"avg reliability {d_block['average_reliability']:.1f}/100, "
        f"units tracked: {d_block['units_tracked']}."
    )
    lines.append(f"  • Storyboard Tone: {storyboard_tone}")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append("Joint Rationale:")
    for r in joint["rationale"]:
        lines.append(f"  - {r}")

    txt_path = os.path.join(DOCS_DIR, "joint_readiness_board.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_joint_readiness_board()
    print("Joint Readiness Board generated:")
    print(f"  - {os.path.join('docs', 'joint_readiness_board.json')}")
    print(f"  - {os.path.join('docs', 'joint_readiness_board.txt')}")

