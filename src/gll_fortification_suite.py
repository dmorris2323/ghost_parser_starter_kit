#!/usr/bin/env python3
"""
gll_fortification_suite.py

Ghost Lantern Labs – Day 71 Fortification Suite
-----------------------------------------------

Purpose:
    Run a full integrity + consistency pass across core GLL artifacts,
    without changing any existing behavior. This is a READ-ONLY
    hardening tool that examines docs/ outputs and summarizes:

        1) GLL Schema Sentinel
           - Are the expected docs present and parseable?
           - Are key fields present and well-formed?

        2) Nuclear Pipeline Integrity Check
           - Golden Dome / nuclear watch / decision artifacts present?
           - Do they align and produce a coherent nuclear posture?

        3) Joint Readiness Consistency Scanner
           - Does joint readiness align with nuclear posture?
           - Any contradictions across core readiness metrics?

        4) DCIM Integrity Filter
           - Is the Defensive Cyber Intelligence payload complete and
             well-structured?

        5) GUI Safety Layer (Static Sanity Scan)
           - Are GUI artifact JSON files present and well-formed?

        6) Operator Safety Merge
           - Fuse Fusion Trust, Nuclear, Cyber, and Joint readiness
             into a single “System Readiness Triage” view.

Outputs:
    docs/gll_fortification_suite.json
    docs/gll_fortification_suite.txt

This does NOT:
    - alter any fusion logic
    - write to non-docs config files
    - perform any network or external actions

It is safe to run as often as desired.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


# -------------------------------------------------------------------
# Generic helpers
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
# 1) GLL Schema Sentinel
# -------------------------------------------------------------------

def _run_schema_sentinel() -> Dict[str, Any]:
    """
    Check existence and basic parseability of key docs artifacts.
    This does not validate deep content, only presence + JSON/text.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    # Expected key files – expand as system grows
    json_expected = [
        "golden_dome_daily_watch.json",
        "defensive_cyber_intel_report.json",
        "joint_readiness_board.json",
        "gui_minimap.json",
        "gui_sos_overlay.json",
        "base_defense_storyboard.json",
        "scenario_pack_latest.json",
        "treaty_evidence_bundle.json",
        "run_history.json",
    ]
    text_expected = [
        "daily_mission_brief.txt",
        "nuclear_decision_card.txt",
        "golden_dome_daily_watch.txt",
    ]

    json_results: List[Dict[str, Any]] = []
    text_results: List[Dict[str, Any]] = []

    for fname in json_expected:
        path = os.path.join(DOCS_DIR, fname)
        exists = os.path.exists(path)
        parsed = False
        if exists:
            parsed = _safe_read_json(path) is not None
        json_results.append(
            {
                "file": fname,
                "exists": exists,
                "json_parse_ok": parsed,
            }
        )

    for fname in text_expected:
        path = os.path.join(DOCS_DIR, fname)
        exists = os.path.exists(path)
        parsed = False
        if exists:
            parsed = _safe_read_text(path) is not None
        text_results.append(
            {
                "file": fname,
                "exists": exists,
                "text_read_ok": parsed,
            }
        )

    status = "GREEN"
    notes: List[str] = []

    missing_json = [j["file"] for j in json_results if not j["exists"]]
    bad_json = [j["file"] for j in json_results if j["exists"] and not j["json_parse_ok"]]
    missing_text = [t["file"] for t in text_results if not t["exists"]]
    bad_text = [t["file"] for t in text_results if t["exists"] and not t["text_read_ok"]]

    if missing_json or bad_json or missing_text or bad_text:
        status = "AMBER"
        if missing_json:
            notes.append(f"Missing JSON docs: {', '.join(missing_json)}")
        if bad_json:
            notes.append(f"Unparseable JSON docs: {', '.join(bad_json)}")
        if missing_text:
            notes.append(f"Missing text docs: {', '.join(missing_text)}")
        if bad_text:
            notes.append(f"Unreadable text docs: {', '.join(bad_text)}")
    else:
        notes.append("All monitored docs present and parseable.")

    return {
        "module": "schema_sentinel",
        "status": status,
        "json_files": json_results,
        "text_files": text_results,
        "notes": notes,
    }


# -------------------------------------------------------------------
# 2) Nuclear Pipeline Integrity Check
# -------------------------------------------------------------------

def _run_nuclear_integrity_check() -> Dict[str, Any]:
    """
    Inspect Golden Dome / nuclear artifacts for coherence and completeness.
    """
    golden = _safe_read_json(os.path.join(DOCS_DIR, "golden_dome_daily_watch.json"))
    prelaunch = _safe_read_json(os.path.join(DOCS_DIR, "prelaunch_watchboard.json"))
    treaty_bundle = _safe_read_json(os.path.join(DOCS_DIR, "treaty_evidence_bundle.json"))
    nuclear_card_txt = _safe_read_text(os.path.join(DOCS_DIR, "nuclear_decision_card.txt"))

    issues: List[str] = []
    nuclear_level = "UNKNOWN"
    nuclear_score = 0.0
    drift_index = 0.0
    volatility = 0.0

    if isinstance(golden, dict):
        nuclear_level = str(
            golden.get("nuclear_level", golden.get("golden_dome_level", "UNKNOWN"))
        )
        nuclear_score = _fmt_float(
            golden.get("nuclear_pressure_score", golden.get("nuclear_score", 0.0)), 0.0
        )
        drift_index = _fmt_float(golden.get("drift_index", golden.get("drift_score", 0.0)), 0.0)
        volatility = _fmt_float(golden.get("temporal_volatility", 0.0), 0.0)
    else:
        issues.append("golden_dome_daily_watch.json missing or malformed.")

    if not isinstance(prelaunch, dict):
        issues.append("prelaunch_watchboard.json missing or malformed.")

    if not isinstance(treaty_bundle, dict):
        issues.append("treaty_evidence_bundle.json missing or malformed.")

    if not nuclear_card_txt:
        issues.append("nuclear_decision_card.txt missing or unreadable.")

    if issues:
        status = "AMBER"
    else:
        status = "GREEN"

    return {
        "module": "nuclear_pipeline_integrity",
        "status": status,
        "nuclear_level": nuclear_level,
        "nuclear_score": nuclear_score,
        "drift_index": drift_index,
        "temporal_volatility": volatility,
        "issues": issues,
    }


# -------------------------------------------------------------------
# 3) Joint Readiness Consistency Scanner
# -------------------------------------------------------------------

def _run_joint_readiness_consistency() -> Dict[str, Any]:
    """
    Compare joint readiness vs nuclear posture and detect contradictions.
    """
    golden = _safe_read_json(os.path.join(DOCS_DIR, "golden_dome_daily_watch.json"))
    joint = _safe_read_json(os.path.join(DOCS_DIR, "joint_readiness_board.json"))

    inconsistencies: List[str] = []

    nuclear_level = "UNKNOWN"
    nuclear_score = 0.0
    jr_level = "UNKNOWN"
    jr_score = 0.0

    if isinstance(golden, dict):
        nuclear_level = str(
            golden.get("nuclear_level", golden.get("golden_dome_level", "UNKNOWN"))
        )
        nuclear_score = _fmt_float(
            golden.get("nuclear_pressure_score", golden.get("nuclear_score", 0.0)), 0.0
        )
    else:
        inconsistencies.append("Golden Dome nuclear posture unavailable for comparison.")

    if isinstance(joint, dict):
        jr_level = str(joint.get("joint_readiness_level", "UNKNOWN"))
        jr_score = _fmt_float(joint.get("joint_readiness_score", 0.0), 0.0)
    else:
        inconsistencies.append("Joint readiness board unavailable for comparison.")

    # Simple contradiction rule:
    # If nuclear posture is RED and joint readiness is GREEN, flag it.
    # If nuclear posture is GREEN but joint readiness is RED, flag it.
    nuk = nuclear_level.upper()
    jr = jr_level.upper()
    if nuk == "RED" and jr == "GREEN":
        inconsistencies.append("Nuclear posture RED but joint readiness GREEN (potential mismatch).")
    if nuk == "GREEN" and jr == "RED":
        inconsistencies.append("Nuclear posture GREEN but joint readiness RED (potential mismatch).")

    status = "GREEN" if not inconsistencies else "AMBER"

    return {
        "module": "joint_readiness_consistency",
        "status": status,
        "nuclear_level": nuclear_level,
        "nuclear_score": nuclear_score,
        "joint_readiness_level": jr_level,
        "joint_readiness_score": jr_score,
        "inconsistencies": inconsistencies,
    }


# -------------------------------------------------------------------
# 4) DCIM Integrity Filter
# -------------------------------------------------------------------

def _run_dcim_integrity_filter() -> Dict[str, Any]:
    """
    Validate the structure of Defensive Cyber Intelligence Report (DCIM).
    """
    dcim = _safe_read_json(os.path.join(DOCS_DIR, "defensive_cyber_intel_report.json"))
    issues: List[str] = []

    if not isinstance(dcim, dict):
        return {
            "module": "dcim_integrity_filter",
            "status": "AMBER",
            "issues": ["defensive_cyber_intel_report.json missing or malformed."],
        }

    required_top = ["cyber_threat_score", "cyber_posture_level", "confidence", "category_scores"]
    for key in required_top:
        if key not in dcim:
            issues.append(f"Missing required DCIM field: {key}")

    cats = dcim.get("category_scores", {})
    expected_cats = [
        "beaconing_score",
        "auth_anomaly_score",
        "inbound_threat_score",
        "tamper_score",
        "config_drift_score",
    ]
    if not isinstance(cats, dict):
        issues.append("category_scores field is not a dict.")
    else:
        for c in expected_cats:
            if c not in cats:
                issues.append(f"Missing DCIM category score: {c}")

    status = "GREEN" if not issues else "AMBER"

    return {
        "module": "dcim_integrity_filter",
        "status": status,
        "issues": issues,
    }


# -------------------------------------------------------------------
# 5) GUI Safety Layer (Static Sanity Scan)
# -------------------------------------------------------------------

def _run_gui_sanity_scan() -> Dict[str, Any]:
    """
    Ensure GUI JSON artifacts exist and are parseable.
    """
    minimap = _safe_read_json(os.path.join(DOCS_DIR, "gui_minimap.json"))
    sos = _safe_read_json(os.path.join(DOCS_DIR, "gui_sos_overlay.json"))

    issues: List[str] = []
    if minimap is None:
        issues.append("gui_minimap.json missing or malformed.")
    if sos is None:
        issues.append("gui_sos_overlay.json missing or malformed.")

    status = "GREEN" if not issues else "AMBER"

    return {
        "module": "gui_sanity_scan",
        "status": status,
        "issues": issues,
    }


# -------------------------------------------------------------------
# 6) Operator Safety Merge (System Readiness Triage)
# -------------------------------------------------------------------

def _run_operator_safety_merge() -> Dict[str, Any]:
    """
    Combine Fusion, Nuclear, Cyber, and Joint readiness into a single triage view.
    """
    golden = _safe_read_json(os.path.join(DOCS_DIR, "golden_dome_daily_watch.json"))
    dcim = _safe_read_json(os.path.join(DOCS_DIR, "defensive_cyber_intel_report.json"))
    joint = _safe_read_json(os.path.join(DOCS_DIR, "joint_readiness_board.json"))

    fusion_trust = 0.0
    fusion_posture = "UNKNOWN"
    nuclear_score = 0.0
    nuclear_level = "UNKNOWN"
    cyber_score = 0.0
    cyber_level = "UNKNOWN"
    joint_score = 0.0
    joint_level = "UNKNOWN"

    if isinstance(golden, dict):
        fusion_trust = _fmt_float(
            golden.get("fusion_trust_score", golden.get("fusion_trust", 0.0)), 0.0
        )
        fusion_posture = str(golden.get("fusion_posture_level", "UNKNOWN"))
        nuclear_score = _fmt_float(
            golden.get("nuclear_pressure_score", golden.get("nuclear_score", 0.0)), 0.0
        )
        nuclear_level = str(
            golden.get("nuclear_level", golden.get("golden_dome_level", "UNKNOWN"))
        )

    if isinstance(dcim, dict):
        cyber_score = _fmt_float(dcim.get("cyber_threat_score", 0.0), 0.0)
        cyber_level = str(dcim.get("cyber_posture_level", "UNKNOWN"))

    if isinstance(joint, dict):
        joint_score = _fmt_float(joint.get("joint_readiness_score", 0.0), 0.0)
        joint_level = str(joint.get("joint_readiness_level", "UNKNOWN"))

    # Overall posture is the "worst" of the four
    overall_posture = _worst_posture(
        [fusion_posture, nuclear_level, cyber_level, joint_level]
    )

    return {
        "module": "operator_safety_merge",
        "status": "GREEN",  # this is a pure view; no internal error here
        "fusion_trust_score": _clip_0_100(fusion_trust),
        "fusion_posture_level": fusion_posture,
        "nuclear_score": _clip_0_100(nuclear_score),
        "nuclear_level": nuclear_level,
        "cyber_threat_score": _clip_0_100(cyber_score),
        "cyber_posture_level": cyber_level,
        "joint_readiness_score": _clip_0_100(joint_score),
        "joint_readiness_level": joint_level,
        "overall_system_posture": overall_posture,
    }


# -------------------------------------------------------------------
# Master entrypoint
# -------------------------------------------------------------------

def run_gll_fortification_suite() -> Dict[str, Any]:
    """
    Execute all six fortification checks and emit JSON/TXT reports.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    schema = _run_schema_sentinel()
    nuclear = _run_nuclear_integrity_check()
    joint = _run_joint_readiness_consistency()
    dcim = _run_dcim_integrity_filter()
    gui = _run_gui_sanity_scan()
    op_merge = _run_operator_safety_merge()

    modules = [schema, nuclear, joint, dcim, gui, op_merge]

    # Overall fortification posture = worst of module statuses
    module_statuses = [m.get("status", "UNKNOWN") for m in modules]
    overall_posture = _worst_posture(module_statuses)

    payload: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "module": "gll_fortification_suite",
        "overall_posture": overall_posture,
        "module_results": modules,
    }

    # Write JSON
    json_path = os.path.join(DOCS_DIR, "gll_fortification_suite.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(payload, f_json, indent=2, sort_keys=True)

    # Write TXT summary
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Fortification Suite Report")
    lines.append("=============================================")
    lines.append(f"Generated at (UTC): {payload['generated_at']}")
    lines.append("")
    lines.append(f"Overall Fortification Posture: {overall_posture}")
    lines.append("")

    for m in modules:
        name = str(m.get("module", "unknown"))
        status = str(m.get("status", "UNKNOWN"))
        lines.append(f"[{name}] – Status: {status}")
        if name == "schema_sentinel":
            notes = m.get("notes", [])
            for n in notes:
                lines.append(f"  - {n}")
        elif name == "nuclear_pipeline_integrity":
            issues = m.get("issues", [])
            if issues:
                lines.append("  Issues:")
                for i in issues:
                    lines.append(f"    - {i}")
        elif name == "joint_readiness_consistency":
            inconsistencies = m.get("inconsistencies", [])
            if inconsistencies:
                lines.append("  Inconsistencies:")
                for i in inconsistencies:
                    lines.append(f"    - {i}")
        elif name == "dcim_integrity_filter":
            issues = m.get("issues", [])
            if issues:
                lines.append("  Issues:")
                for i in issues:
                    lines.append(f"    - {i}")
        elif name == "gui_sanity_scan":
            issues = m.get("issues", [])
            if issues:
                lines.append("  Issues:")
                for i in issues:
                    lines.append(f"    - {i}")
        elif name == "operator_safety_merge":
            lines.append(
                f"  Fusion trust: {m.get('fusion_trust_score', 0.0):.1f} "
                f"({m.get('fusion_posture_level', 'UNKNOWN')})"
            )
            lines.append(
                f"  Nuclear score: {m.get('nuclear_score', 0.0):.1f} "
                f"({m.get('nuclear_level', 'UNKNOWN')})"
            )
            lines.append(
                f"  Cyber threat: {m.get('cyber_threat_score', 0.0):.1f} "
                f"({m.get('cyber_posture_level', 'UNKNOWN')})"
            )
            lines.append(
                f"  Joint readiness: {m.get('joint_readiness_score', 0.0):.1f} "
                f"({m.get('joint_readiness_level', 'UNKNOWN')})"
            )
            lines.append(
                f"  Overall system posture: {m.get('overall_system_posture', 'UNKNOWN')}"
            )
        lines.append("")

    txt_path = os.path.join(DOCS_DIR, "gll_fortification_suite.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return payload


if __name__ == "__main__":
    result = run_gll_fortification_suite()
    print("GLL Fortification Suite report generated:")
    print(f"  - {os.path.join('docs', 'gll_fortification_suite.json')}")
    print(f"  - {os.path.join('docs', 'gll_fortification_suite.txt')}")
    print("")
    print(json.dumps(result, indent=2))

