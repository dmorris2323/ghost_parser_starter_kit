#!/usr/bin/env python3
"""
gll_training_mode_brief.py

Ghost Lantern Labs – Training Mode Student Brief
-----------------------------------------------

Purpose:
    Turn existing GLL artifacts into a single "training scenario brief"
    suitable for a student/trainee (e.g., 1N0X1 tech school, ISR trainee,
    or nuclear/base-defense exercise participant).

    This module does NOT change any pipeline behavior. It only reads from
    docs/ and writes:

        docs/training_mode_brief.json
        docs/training_mode_brief.txt

Inputs (if available):
    - docs/golden_dome_daily_watch.json
    - docs/defensive_cyber_intel_report.json
    - docs/joint_readiness_board.json
    - docs/base_defense_storyboard.json
    - docs/prelaunch_watchboard.json
    - docs/scenario_pack_latest.json

Outputs:
    JSON: machine-readable training brief
    TXT: human-readable scenario brief for a trainee

Safe to run at any time.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

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


def _fmt_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def _clip_0_100(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 100.0:
        return 100.0
    return x


def _worst_posture(levels: List[str]) -> str:
    """
    Given a list of GREEN/AMBER/RED/UNKNOWN strings, return the 'worst'.
    Ordering: RED > AMBER > GREEN > UNKNOWN.
    """
    rank = {"RED": 3, "AMBER": 2, "GREEN": 1, "UNKNOWN": 0}
    worst = "UNKNOWN"
    worst_score = -1
    for lvl in levels:
        lvl_u = (lvl or "UNKNOWN").upper()
        score = rank.get(lvl_u, 0)
        if score > worst_score:
            worst = lvl_u
            worst_score = score
    return worst


# -------------------------------------------------------------------
# Loaders for training context
# -------------------------------------------------------------------

def _load_golden_dome_watch() -> Dict[str, Any]:
    data = _safe_read_json(os.path.join(DOCS_DIR, "golden_dome_daily_watch.json"))
    return data if isinstance(data, dict) else {}


def _load_dcim() -> Dict[str, Any]:
    data = _safe_read_json(os.path.join(DOCS_DIR, "defensive_cyber_intel_report.json"))
    return data if isinstance(data, dict) else {}


def _load_joint_readiness() -> Dict[str, Any]:
    data = _safe_read_json(os.path.join(DOCS_DIR, "joint_readiness_board.json"))
    return data if isinstance(data, dict) else {}


def _load_base_defense_storyboard() -> Dict[str, Any]:
    data = _safe_read_json(os.path.join(DOCS_DIR, "base_defense_storyboard.json"))
    return data if isinstance(data, dict) else {}


def _load_prelaunch_watchboard() -> Dict[str, Any]:
    data = _safe_read_json(os.path.join(DOCS_DIR, "prelaunch_watchboard.json"))
    return data if isinstance(data, dict) else {}


def _load_scenario_pack() -> Dict[str, Any]:
    data = _safe_read_json(os.path.join(DOCS_DIR, "scenario_pack_latest.json"))
    return data if isinstance(data, dict) else {}


# -------------------------------------------------------------------
# Core training brief builder
# -------------------------------------------------------------------

def build_training_mode_brief() -> Dict[str, Any]:
    """
    Build a unified training-mode brief from existing artifacts.
    Returns the JSON payload that is also written to docs/.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    golden = _load_golden_dome_watch()
    dcim = _load_dcim()
    joint = _load_joint_readiness()
    storyboard = _load_base_defense_storyboard()
    prelaunch = _load_prelaunch_watchboard()
    scenario_pack = _load_scenario_pack()

    # --- Extract scores and posture levels ---

    fusion_trust = _clip_0_100(
        _fmt_float(golden.get("fusion_trust_score", golden.get("fusion_trust", 0.0)), 0.0)
    )
    fusion_posture = str(golden.get("fusion_posture_level", "UNKNOWN"))

    nuclear_score = _clip_0_100(
        _fmt_float(
            golden.get("nuclear_pressure_score", golden.get("nuclear_score", 0.0)), 0.0
        )
    )
    nuclear_level = str(
        golden.get("nuclear_level", golden.get("golden_dome_level", "UNKNOWN"))
    )

    drift_index = _fmt_float(golden.get("drift_index", golden.get("drift_score", 0.0)), 0.0)
    temporal_volatility = _fmt_float(
        golden.get("temporal_volatility", 0.0),
        0.0,
    )

    cyber_score = _clip_0_100(_fmt_float(dcim.get("cyber_threat_score", 0.0), 0.0))
    cyber_level = str(dcim.get("cyber_posture_level", "UNKNOWN"))

    joint_score = _clip_0_100(_fmt_float(joint.get("joint_readiness_score", 0.0), 0.0))
    joint_level = str(joint.get("joint_readiness_level", "UNKNOWN"))

    # Overall posture (for training triage)
    overall_posture = _worst_posture(
        [fusion_posture, nuclear_level, cyber_level, joint_level]
    )

    # --- Scenario summarization ---

    scenario_summary: Dict[str, Any] = {}
    if scenario_pack:
        scenario_summary["keys_present"] = list(scenario_pack.keys())
        # Try to expose count of scenarios if it looks like a list
        if isinstance(scenario_pack.get("scenarios"), list):
            scenario_summary["scenario_count"] = len(scenario_pack["scenarios"])
        else:
            scenario_summary["scenario_count"] = 0
    else:
        scenario_summary["note"] = "No scenario_pack_latest.json present – generic training prompt."

    # --- Base-defense / prelaunch high-level notes ---

    base_defense_note = ""
    if isinstance(storyboard.get("phases"), list) and storyboard["phases"]:
        base_defense_note = "Base-defense storyboard present – trainee should review Detection → Assessment → Response → Recovery phases."
    else:
        base_defense_note = "Base-defense storyboard not present or has no phases."

    prelaunch_note = "Pre-launch watchboard present." if prelaunch else "Pre-launch watchboard not available."

    # --- Training focus recommendation ---

    focus_reason = ""
    training_focus = "GENERAL_FUSION"

    # Simple prioritization logic:
    # If nuclear_level is RED/AMBER or nuclear_score high -> nuclear focus.
    # Else if cyber posture is RED/AMBER or cyber_score high -> cyber focus.
    # Else if joint readiness is RED/AMBER -> joint/base-defense focus.
    nuk = nuclear_level.upper()
    cyb = cyber_level.upper()
    jnt = joint_level.upper()

    if nuk in ("RED", "AMBER") or nuclear_score >= 70.0:
        training_focus = "NUCLEAR_EARLY_WARNING"
        focus_reason = (
            "Nuclear posture elevated; trainee should focus on Golden Dome, drift, "
            "and temporal volatility interpretation."
        )
    elif cyb in ("RED", "AMBER") or cyber_score >= 70.0:
        training_focus = "DEFENSIVE_CYBER_INTEL"
        focus_reason = (
            "Cyber threat posture elevated; trainee should focus on DCIM, MITRE-style "
            "tactics, and beaconing/auth anomalies."
        )
    elif jnt in ("RED", "AMBER"):
        training_focus = "JOINT_BASE_DEFENSE"
        focus_reason = (
            "Joint readiness degraded; trainee should focus on base-defense storyboard "
            "and cross-domain readiness interpretation."
        )
    else:
        training_focus = "GENERAL_FUSION"
        focus_reason = (
            "No single domain heavily elevated; trainee should practice synthesizing "
            "fusion trust, nuclear, cyber, and joint readiness into a single narrative."
        )

    # --- Student prompts ---

    student_prompts: List[str] = []

    student_prompts.append(
        "1) Based on the nuclear score and level, would you characterize the current "
        "nuclear environment as stable, elevated, or critical? Defend your answer using "
        "drift and temporal volatility."
    )
    student_prompts.append(
        "2) Look at the cyber threat score and posture. Which MITRE ATT&CK-style "
        "tactics appear most likely, and what additional collection would you request?"
    )
    student_prompts.append(
        "3) Joint readiness vs nuclear posture: do they agree on the level of concern? "
        "If not, which one would you brief as the primary driver and why?"
    )
    student_prompts.append(
        "4) If a commander asked you, 'Is my base more threatened from the air, the "
        "network, or the nuclear domain today?', how would you answer in one paragraph?"
    )
    student_prompts.append(
        "5) Assume this scenario is a training inject for a 1N0X1/1A8X2 team. What "
        "three follow-on products would you build from GLL (e.g., mission brief, "
        "base-defense storyboard, treaty evidence bundle) to support decision-making?"
    )

    # --- Build payload ---

    generated_at = datetime.utcnow().isoformat() + "Z"

    payload: Dict[str, Any] = {
        "module": "gll_training_mode_brief",
        "generated_at": generated_at,
        "training_focus": training_focus,
        "training_focus_reason": focus_reason,
        "overall_posture": overall_posture,
        "scores": {
            "fusion_trust_score": fusion_trust,
            "fusion_posture_level": fusion_posture,
            "nuclear_score": nuclear_score,
            "nuclear_level": nuclear_level,
            "drift_index": drift_index,
            "temporal_volatility": temporal_volatility,
            "cyber_threat_score": cyber_score,
            "cyber_posture_level": cyber_level,
            "joint_readiness_score": joint_score,
            "joint_readiness_level": joint_level,
        },
        "scenario_summary": scenario_summary,
        "base_defense_note": base_defense_note,
        "prelaunch_note": prelaunch_note,
        "student_prompts": student_prompts,
    }

    # --- Write JSON ---

    json_path = os.path.join(DOCS_DIR, "training_mode_brief.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(payload, f_json, indent=2, sort_keys=True)

    # --- Write TXT (human-readable) ---

    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Training Mode Student Brief")
    lines.append("================================================")
    lines.append(f"Generated at (UTC): {generated_at}")
    lines.append("")
    lines.append(f"Training Focus: {training_focus}")
    lines.append(f"Why this focus: {focus_reason}")
    lines.append("")
    lines.append(f"Overall Posture (worst of fusion/nuclear/cyber/joint): {overall_posture}")
    lines.append("")
    lines.append("Key Scores")
    lines.append("----------")
    lines.append(f"Fusion Trust:       {fusion_trust:.1f} ({fusion_posture})")
    lines.append(f"Nuclear Score:      {nuclear_score:.1f} ({nuclear_level})")
    lines.append(f"  • Drift Index:    {drift_index:.1f}")
    lines.append(f"  • Volatility:     {temporal_volatility:.1f}")
    lines.append(f"Cyber Threat:       {cyber_score:.1f} ({cyber_level})")
    lines.append(f"Joint Readiness:    {joint_score:.1f} ({joint_level})")
    lines.append("")
    lines.append("Context Notes")
    lines.append("-------------")
    lines.append(f"- Scenario Pack:    {scenario_summary}")
    lines.append(f"- Base-Defense:     {base_defense_note}")
    lines.append(f"- Pre-launch:       {prelaunch_note}")
    lines.append("")
    lines.append("Student Prompts")
    lines.append("---------------")
    for p in student_prompts:
        lines.append(p)
    lines.append("")
    lines.append(
        "Instructor Note: This brief is generated from GLL artifacts and is not an "
        "authoritative real-world product. It is designed for training, simulation, "
        "and rehearsal only."
    )

    txt_path = os.path.join(DOCS_DIR, "training_mode_brief.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return payload


if __name__ == "__main__":
    result = build_training_mode_brief()
    print("Training Mode Student Brief generated:")
    print(f"  - {os.path.join('docs', 'training_mode_brief.json')}")
    print(f"  - {os.path.join('docs', 'training_mode_brief.txt')}")
    print("")
    print(json.dumps(result, indent=2))

