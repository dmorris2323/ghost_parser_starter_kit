#!/usr/bin/env python3
"""
joint_readiness_integrity_guard.py

Ghost Lantern Labs – Joint Readiness Integrity Guard
----------------------------------------------------

Purpose:
    Harden the joint nuclear + base-defense stack by validating that all
    critical artifacts are present and structurally sane.

Scope:
    This module is READ-ONLY on upstream artifacts. It does NOT modify
    or regenerate any products. It simply inspects and reports.

Inputs checked (all under src/docs/):

    JSON (dict expected):
        - nuclear_early_warning_summary.json
        - installation_threat_map.json
        - sensor_outage_predictor.json
        - distributed_readiness_snapshot.json
        - base_defense_storyboard.json
        - joint_readiness_board.json
        - joint_risk_register.json
        - joint_readiness_voice_script.json

    Text / HTML:
        - joint_readiness_scorecard.txt
        - joint_readiness_brief.html

Outputs:

    - docs/joint_readiness_integrity_report.json
    - docs/joint_readiness_integrity_report.txt

Health model:
    - Each check produces:
        * status: OK / WARN / ERROR
        * component: which artifact / field
        * message: human-readable explanation
    - Overall health_score 0–100 and health_level GREEN/AMBER/RED.

This is a pure hardening module that commanders, evaluators, or Ghost
can run to answer: "Is my joint readiness stack structurally healthy?"
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


# -------------------------
# Basic I/O helpers
# -------------------------

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


# -------------------------
# Check machinery
# -------------------------

def _add_check(results: List[Dict[str, Any]], status: str, component: str, message: str) -> None:
    results.append(
        {
            "status": status.upper(),
            "component": component,
            "message": message,
        }
    )


def _status_weight(status: str) -> int:
    """
    Weight for severity aggregation:
        OK    -> 0
        WARN  -> 1
        ERROR -> 2
    """
    s = status.upper()
    if s == "ERROR":
        return 2
    if s == "WARN":
        return 1
    return 0


# -------------------------
# Artifact-specific checks
# -------------------------

def _check_nuclear_summary(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "nuclear_early_warning_summary.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    required_keys = [
        "overall_nuclear_early_warning_level",
        "drift_adjusted_early_warning_score",
        "volatility_index",
        "drift_confidence",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        _add_check(
            results,
            "WARN",
            comp,
            f"Missing expected keys: {', '.join(missing)}.",
        )
    else:
        _add_check(results, "OK", comp, "Core nuclear summary keys present.")

    # Range sanity
    score = _fmt_float(data.get("drift_adjusted_early_warning_score"), -1)
    if score < 0 or score > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"drift_adjusted_early_warning_score out of [0,100] range: {score}.",
        )
    else:
        _add_check(results, "OK", comp, f"Nuclear early-warning score in range: {score:.1f}/100.")

    vol = _fmt_float(data.get("volatility_index"), -1)
    if vol < 0 or vol > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"volatility_index out of [0,100] range: {vol}.",
        )
    drift_conf = _fmt_float(data.get("drift_confidence"), -1)
    if drift_conf < 0 or drift_conf > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"drift_confidence out of [0,100] range: {drift_conf}.",
        )


def _check_installation_threat_map(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "installation_threat_map.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    score = _fmt_float(data.get("overall_threat_score"), -1)
    if score < 0 or score > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"overall_threat_score out of [0,100] range or missing: {score}.",
        )
    else:
        _add_check(results, "OK", comp, f"Base threat score in range: {score:.1f}/100.")

    sectors = data.get("sectors")
    if sectors is None:
        _add_check(results, "WARN", comp, "No 'sectors' key present; base-defense mapping may be incomplete.")
    elif not isinstance(sectors, list):
        _add_check(results, "WARN", comp, "'sectors' is not a list; unexpected structure.")
    elif not sectors:
        _add_check(results, "WARN", comp, "Sectors list is empty; threat map has no sectors to track.")
    else:
        _add_check(results, "OK", comp, f"{len(sectors)} sectors tracked in installation threat map.")


def _check_sensor_outage_predictor(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "sensor_outage_predictor.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    risk = _fmt_float(data.get("global_outage_risk_score"), -1)
    if risk < 0 or risk > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"global_outage_risk_score out of [0,100] range or missing: {risk}.",
        )
    else:
        _add_check(results, "OK", comp, f"Global outage risk score in range: {risk:.1f}/100.")

    crit = data.get("critical_sensors_at_risk")
    if crit is None:
        _add_check(results, "WARN", comp, "No 'critical_sensors_at_risk' list; cannot highlight critical outages.")
    elif not isinstance(crit, list):
        _add_check(results, "WARN", comp, "'critical_sensors_at_risk' is not a list; unexpected structure.")
    else:
        _add_check(results, "OK", comp, f"{len(crit)} critical sensors flagged at risk.")


def _check_distributed_readiness(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "distributed_readiness_snapshot.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    fusion_trust = _fmt_float(data.get("fusion_trust_score"), -1)
    avg_rel = _fmt_float(data.get("average_reliability"), -1)

    if fusion_trust < 0 or fusion_trust > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"fusion_trust_score out of [0,100] range or missing: {fusion_trust}.",
        )
    else:
        _add_check(results, "OK", comp, f"Fusion trust in range: {fusion_trust:.1f}/100.")

    if avg_rel < 0 or avg_rel > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"average_reliability out of [0,100] range or missing: {avg_rel}.",
        )

    units = data.get("units") or data.get("elements")
    if units is None:
        _add_check(results, "WARN", comp, "No 'units' or 'elements' array; distributed readiness granularity missing.")
    elif not isinstance(units, list):
        _add_check(results, "WARN", comp, "'units' / 'elements' is not a list; unexpected structure.")
    elif not units:
        _add_check(results, "WARN", comp, "Units list is empty; no wing/group/squadron elements tracked.")
    else:
        _add_check(results, "OK", comp, f"{len(units)} units tracked in distributed readiness snapshot.")


def _check_base_defense_storyboard(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "base_defense_storyboard.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    phases = data.get("phases")
    if phases is None:
        _add_check(results, "WARN", comp, "No 'phases' key; storyboard may not be structured.")
    elif not isinstance(phases, list):
        _add_check(results, "WARN", comp, "'phases' is not a list; unexpected storyboard structure.")
    elif len(phases) < 3:
        _add_check(results, "WARN", comp, f"Storyboard phases < 3; detected {len(phases)} phases.")
    else:
        _add_check(results, "OK", comp, f"{len(phases)} storyboard phases present.")


def _check_joint_readiness_board(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "joint_readiness_board.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    jr_score = _fmt_float(data.get("joint_readiness_score"), -1)
    jr_level = str(data.get("joint_readiness_level", "UNKNOWN"))
    if jr_score < 0 or jr_score > 100:
        _add_check(
            results,
            "WARN",
            comp,
            f"joint_readiness_score out of [0,100] range or missing: {jr_score}.",
        )
    else:
        _add_check(results, "OK", comp, f"Joint readiness score in range: {jr_score:.1f}/100.")
    if jr_level == "UNKNOWN":
        _add_check(
            results,
            "WARN",
            comp,
            "joint_readiness_level is 'UNKNOWN'; ensure joint readiness board is being built from real upstream data.",
        )


def _check_joint_risk_register(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "joint_risk_register.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    risks = data.get("risks")
    if risks is None:
        _add_check(results, "WARN", comp, "No 'risks' array; risk register may be empty.")
        return

    if not isinstance(risks, list):
        _add_check(results, "WARN", comp, "'risks' is not a list; unexpected structure.")
        return

    if not risks:
        _add_check(results, "WARN", comp, "Risks list is empty; joint risk register identifies no risks.")
    else:
        _add_check(results, "OK", comp, f"{len(risks)} risks recorded in joint risk register.")


def _check_voice_script(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "joint_readiness_voice_script.json"
    data = _safe_read_json(path)
    if data is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if not isinstance(data, dict):
        _add_check(results, "ERROR", comp, "File exists but is not a JSON object.")
        return

    profile = str(data.get("voice_profile", "UNKNOWN"))
    full_script = data.get("full_script")
    segments = data.get("segments")

    if profile.upper() != "OBASI":
        _add_check(results, "WARN", comp, f"voice_profile is '{profile}', expected 'Obasi'.")
    else:
        _add_check(results, "OK", comp, "voice_profile set to Obasi as expected.")

    if not isinstance(full_script, str) or not full_script.strip():
        _add_check(results, "WARN", comp, "full_script missing or empty; voice script may not be usable.")
    else:
        length = len(full_script.split())
        if length < 40:
            _add_check(results, "WARN", comp, f"full_script is very short ({length} words); may be too thin for a brief.")
        else:
            _add_check(results, "OK", comp, f"full_script length looks reasonable ({length} words).")

    if not isinstance(segments, dict):
        _add_check(results, "WARN", comp, "segments object missing or not a dict; structured voice segments unavailable.")
    else:
        required_segments = [
            "opening",
            "joint_summary",
            "nuclear_summary",
            "base_defense_summary",
            "top_risks",
            "closing",
        ]
        missing = [s for s in required_segments if s not in segments]
        if missing:
            _add_check(
                results,
                "WARN",
                comp,
                f"Missing expected voice segments: {', '.join(missing)}.",
            )
        else:
            _add_check(results, "OK", comp, "All expected voice script segments present.")


def _check_scorecard_txt(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "joint_readiness_scorecard.txt"
    txt = _safe_read_text(path)
    if txt is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if "Joint Readiness Scorecard" not in txt:
        _add_check(results, "WARN", comp, "Scorecard header not detected; verify the scorecard generator ran correctly.")
    else:
        _add_check(results, "OK", comp, "Scorecard header detected.")

    if "NUCLEAR POSTURE" not in txt or "BASE DEFENSE POSTURE" not in txt:
        _add_check(results, "WARN", comp, "Scorecard missing nuclear or base-defense sections.")
    else:
        _add_check(results, "OK", comp, "Scorecard includes both nuclear and base-defense sections.")


def _check_html_brief(path: str, results: List[Dict[str, Any]]) -> None:
    comp = "joint_readiness_brief.html"
    html = _safe_read_text(path)
    if html is None:
        _add_check(results, "ERROR", comp, "File missing or unreadable.")
        return

    if "<title>Ghost Lantern Labs – Joint Readiness Brief</title>" not in html:
        _add_check(results, "WARN", comp, "HTML brief title not detected; verify HTML generator layout.")
    else:
        _add_check(results, "OK", comp, "HTML brief title present.")

    # Look for key headings
    required_snippets = ["Top Joint Risks", "Scorecard (Text View)"]
    missing = [s for s in required_snippets if s not in html]
    if missing:
        _add_check(
            results,
            "WARN",
            comp,
            f"HTML brief missing expected sections: {', '.join(missing)}.",
        )
    else:
        _add_check(results, "OK", comp, "HTML brief includes key sections for risks and scorecard.")


# -------------------------
# Aggregate health scoring
# -------------------------

def _compute_health(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute overall health_score 0–100 and health_level GREEN/AMBER/RED.

    Simple model:
        - Start at 100.
        - Each WARN deducts 3 points.
        - Each ERROR deducts 12 points.
        - Never below 0.
    """
    score = 100.0
    for r in results:
        w = _status_weight(r.get("status", "OK"))
        if w == 1:
            score -= 3.0
        elif w == 2:
            score -= 12.0

    score = max(0.0, min(100.0, score))

    if score >= 80.0:
        level = "GREEN"
    elif score >= 50.0:
        level = "AMBER"
    else:
        level = "RED"

    return {
        "health_score": score,
        "health_level": level,
    }


# -------------------------
# Main entrypoint
# -------------------------

def run_joint_readiness_integrity_guard() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    results: List[Dict[str, Any]] = []

    # Paths
    nuclear_path = os.path.join(DOCS_DIR, "nuclear_early_warning_summary.json")
    inst_path = os.path.join(DOCS_DIR, "installation_threat_map.json")
    outage_path = os.path.join(DOCS_DIR, "sensor_outage_predictor.json")
    dist_path = os.path.join(DOCS_DIR, "distributed_readiness_snapshot.json")
    story_path = os.path.join(DOCS_DIR, "base_defense_storyboard.json")
    board_path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    risk_path = os.path.join(DOCS_DIR, "joint_risk_register.json")
    voice_path = os.path.join(DOCS_DIR, "joint_readiness_voice_script.json")
    scorecard_path = os.path.join(DOCS_DIR, "joint_readiness_scorecard.txt")
    brief_path = os.path.join(DOCS_DIR, "joint_readiness_brief.html")

    # Run checks
    _check_nuclear_summary(nuclear_path, results)
    _check_installation_threat_map(inst_path, results)
    _check_sensor_outage_predictor(outage_path, results)
    _check_distributed_readiness(dist_path, results)
    _check_base_defense_storyboard(story_path, results)
    _check_joint_readiness_board(board_path, results)
    _check_joint_risk_register(risk_path, results)
    _check_voice_script(voice_path, results)
    _check_scorecard_txt(scorecard_path, results)
    _check_html_brief(brief_path, results)

    health = _compute_health(results)

    summary: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "component": "joint_readiness_stack",
        "health_score": health["health_score"],
        "health_level": health["health_level"],
        "checks": results,
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "joint_readiness_integrity_report.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(summary, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Joint Readiness Integrity Report")
    lines.append("====================================")
    lines.append(f"Generated at (UTC): {summary['generated_at']}")
    lines.append("")
    lines.append(f"Overall Health Score: {summary['health_score']:.1f}/100")
    lines.append(f"Health Level: {summary['health_level']}")
    lines.append("")
    lines.append("Check Results:")
    for r in results:
        lines.append(f"- [{r['status']}] {r['component']}: {r['message']}")

    txt_path = os.path.join(DOCS_DIR, "joint_readiness_integrity_report.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return summary


if __name__ == "__main__":
    out = run_joint_readiness_integrity_guard()
    print("Joint Readiness Integrity Report generated:")
    print(f"  - {os.path.join('docs', 'joint_readiness_integrity_report.json')}")
    print(f"  - {os.path.join('docs', 'joint_readiness_integrity_report.txt')}")

