#!/usr/bin/env python3
"""
defensive_cyber_intel_module.py

Ghost Lantern Labs – Defensive Cyber Intelligence Module (DCIM)
---------------------------------------------------------------

Purpose:
    Provide a passive, defensive cyber-intelligence layer on top of the
    existing fusion pipeline outputs. This module:

        • Reads fused/scored telemetry from docs/*.csv (if present).
        • Derives simple category scores for:
            - Beaconing / C2 suspicion
            - Auth & identity anomalies
            - Inbound threat pressure (firewall/IDS-like signals)
            - Sensor tampering / integrity anomalies
            - Configuration / posture drift
        • Maps those categories into a high-level MITRE ATT&CK-style
          view (tactics that appear to be in play).
        • Produces a single cyber_threat_score (0–100) and a posture
          level (GREEN/AMBER/RED).

    This is READ-ONLY with respect to external systems. It does NOT
    perform any active scanning, probing, or exploitation. It only
    analyzes internal GLL telemetry and historical run artifacts.

Inputs (best-effort, all optional):

    - docs/scored_output.csv        (preferred if available)
    - docs/fused_output.csv         (fallback)
    - docs/run_history.json         (optional; qualitative hints)
    - docs/system_integrity_report.json (optional; config/integrity hints)

Outputs:

    - docs/defensive_cyber_intel_report.json
    - docs/defensive_cyber_intel_report.txt

This module is suitable for inclusion in:
    - CLI (ghost_cli.py)
    - HTML briefs
    - Streamlit dashboards
    - SBIR/AFWERX demo flows
"""

import csv
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


def _safe_read_csv(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception:
        pass
    return rows


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


# -------------------------------------------------------------------
# Core analysis
# -------------------------------------------------------------------

def _load_primary_telemetry() -> List[Dict[str, Any]]:
    """
    Try scored_output.csv first, then fused_output.csv.
    If neither exists, return an empty list.
    """
    scored_path = os.path.join(DOCS_DIR, "scored_output.csv")
    fused_path = os.path.join(DOCS_DIR, "fused_output.csv")

    if os.path.exists(scored_path):
        return _safe_read_csv(scored_path)
    if os.path.exists(fused_path):
        return _safe_read_csv(fused_path)
    return []


def _extract_category_scores(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Heuristic: scan column names for cyber-relevant signals.
    This is deliberately simple and tolerant of missing fields:

        beaconing_score:
            any column name containing "beacon", "c2", "cnc"

        auth_anomaly_score:
            column name contains "auth", "login", "credential"

        inbound_threat_score:
            "firewall", "ids", "ips", "inbound", "probe"

        tamper_score:
            "tamper", "integrity", "spoof", "fake"

        config_drift_score:
            "config_drift", "policy_drift", "posture_gap"
    """
    beacon_vals: List[float] = []
    auth_vals: List[float] = []
    inbound_vals: List[float] = []
    tamper_vals: List[float] = []
    drift_vals: List[float] = []

    for row in rows:
        for col, raw_val in row.items():
            if col is None:
                continue
            col_l = col.lower()
            val = _fmt_float(raw_val, None)
            if val is None:
                continue

            # Beaconing / C2
            if any(key in col_l for key in ["beacon", "c2", "cnc", "command_and_control"]):
                beacon_vals.append(val)

            # Auth / identity
            if any(key in col_l for key in ["auth", "login", "credential", "identity"]):
                auth_vals.append(val)

            # Inbound threats
            if any(key in col_l for key in ["firewall", "ids", "ips", "inbound", "scan", "probe"]):
                inbound_vals.append(val)

            # Tampering / integrity
            if any(key in col_l for key in ["tamper", "integrity", "spoof", "fake", "forged"]):
                tamper_vals.append(val)

            # Config / posture drift
            if any(key in col_l for key in ["config_drift", "posture_drift", "policy_drift", "hardening_gap"]):
                drift_vals.append(val)

    def avg_or_zero(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    return {
        "beaconing_score": _clip_0_100(avg_or_zero(beacon_vals)),
        "auth_anomaly_score": _clip_0_100(avg_or_zero(auth_vals)),
        "inbound_threat_score": _clip_0_100(avg_or_zero(inbound_vals)),
        "tamper_score": _clip_0_100(avg_or_zero(tamper_vals)),
        "config_drift_score": _clip_0_100(avg_or_zero(drift_vals)),
    }


def _pull_integrity_hints() -> Dict[str, Any]:
    """
    Optionally pull hints from system_integrity_report.json and run_history.json
    to adjust confidence and contextual notes.
    """
    hints: Dict[str, Any] = {
        "integrity_flags": [],
        "recent_anomaly_runs": 0,
        "total_runs": 0,
    }

    integ_path = os.path.join(DOCS_DIR, "system_integrity_report.json")
    integ = _safe_read_json(integ_path)
    if isinstance(integ, dict):
        flags = integ.get("flags") or integ.get("issues") or []
        if isinstance(flags, list):
            hints["integrity_flags"] = flags[:10]

    rh_path = os.path.join(DOCS_DIR, "run_history.json")
    rh = _safe_read_json(rh_path)
    if isinstance(rh, list):
        hints["total_runs"] = len(rh)
        anomaly_runs = 0
        for r in rh[-20:]:  # last 20 runs
            if not isinstance(r, dict):
                continue
            if r.get("status") == "ANOMALY" or r.get("cyber_anomaly_flag") is True:
                anomaly_runs += 1
        hints["recent_anomaly_runs"] = anomaly_runs

    return hints


def _derive_mitre_tactics(categories: Dict[str, float]) -> List[str]:
    """
    Very simple mapping from category scores to MITRE ATT&CK-style tactics.
    This is not exhaustive, but gives commanders a recognizable frame.

    Threshold model:
        > 60 = strong signal
        30–60 = moderate
    """
    mitre: List[str] = []

    beacon = categories["beaconing_score"]
    auth = categories["auth_anomaly_score"]
    inbound = categories["inbound_threat_score"]
    tamper = categories["tamper_score"]
    drift = categories["config_drift_score"]

    if beacon >= 30.0:
        mitre.append("Command and Control (C2)")
    if inbound >= 30.0:
        mitre.append("Reconnaissance / Resource Development")
    if auth >= 30.0:
        mitre.append("Credential Access / Privilege Escalation")
    if tamper >= 30.0:
        mitre.append("Defense Evasion / Impact")
    if drift >= 30.0:
        mitre.append("Persistence / Defense Evasion (Configuration Drift)")

    # De-duplicate while preserving order
    seen = set()
    ordered: List[str] = []
    for t in mitre:
        if t not in seen:
            ordered.append(t)
            seen.add(t)
    return ordered


def _compute_cyber_threat_score(categories: Dict[str, float], hints: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate category scores and hints into a single threat score and posture.
    Simple model:

        base_score = weighted average of categories:
            - 30% beaconing
            - 25% auth anomalies
            - 20% inbound threats
            - 15% tamper
            - 10% config drift

        Adjust up slightly if many recent anomaly runs are present.

    Returns:
        {
            "cyber_threat_score": float (0–100),
            "cyber_posture_level": "GREEN" | "AMBER" | "RED",
            "confidence": float (0–100),
        }
    """
    beacon = categories["beaconing_score"]
    auth = categories["auth_anomaly_score"]
    inbound = categories["inbound_threat_score"]
    tamper = categories["tamper_score"]
    drift = categories["config_drift_score"]

    base = (
        0.30 * beacon
        + 0.25 * auth
        + 0.20 * inbound
        + 0.15 * tamper
        + 0.10 * drift
    )

    # Adjust based on recent anomalies
    anomaly_runs = hints.get("recent_anomaly_runs", 0)
    total_runs = hints.get("total_runs", 0)

    # If there have been many anomalies in the last 20 runs, bump score by 0–10 points
    if total_runs > 0 and anomaly_runs > 0:
        ratio = anomaly_runs / min(total_runs, 20)
        bump = min(10.0, 10.0 * ratio)
        base += bump

    score = _clip_0_100(base)

    if score >= 70.0:
        level = "RED"
    elif score >= 40.0:
        level = "AMBER"
    else:
        level = "GREEN"

    # Confidence: if we had telemetry rows, confidence is higher
    confidence = 50.0
    # rough proxy: number of rows and presence of multiple categories
    # (this is intentionally simple and safe)
    telemetry_present = any(v > 0.0 for v in categories.values())
    if telemetry_present:
        confidence += 25.0
    if total_runs >= 10:
        confidence += 10.0
    if hints.get("integrity_flags"):
        confidence -= 10.0

    confidence = max(0.0, min(100.0, confidence))

    return {
        "cyber_threat_score": score,
        "cyber_posture_level": level,
        "confidence": confidence,
    }


# -------------------------------------------------------------------
# Public entrypoint
# -------------------------------------------------------------------

def analyze_defensive_cyber_intel() -> Dict[str, Any]:
    """
    Main entrypoint for GLL.

    Returns a dictionary payload and writes JSON/TXT reports under docs/.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    telemetry_rows = _load_primary_telemetry()
    categories = _extract_category_scores(telemetry_rows)
    hints = _pull_integrity_hints()
    mitre_tactics = _derive_mitre_tactics(categories)
    summary = _compute_cyber_threat_score(categories, hints)

    payload: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "module": "defensive_cyber_intel_module",
        "cyber_threat_score": summary["cyber_threat_score"],
        "cyber_posture_level": summary["cyber_posture_level"],
        "confidence": summary["confidence"],
        "category_scores": categories,
        "mitre_tactics_suspected": mitre_tactics,
        "integrity_hints": hints,
    }

    # JSON output
    json_path = os.path.join(DOCS_DIR, "defensive_cyber_intel_report.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(payload, f_json, indent=2, sort_keys=True)

    # TXT output
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Defensive Cyber Intelligence Report")
    lines.append("=======================================================")
    lines.append(f"Generated at (UTC): {payload['generated_at']}")
    lines.append("")
    lines.append(f"Overall Cyber Threat Score: {payload['cyber_threat_score']:.1f} / 100")
    lines.append(f"Cyber Posture Level: {payload['cyber_posture_level']}")
    lines.append(f"Assessment Confidence: {payload['confidence']:.1f} / 100")
    lines.append("")
    lines.append("Category Scores:")
    lines.append(f"  • Beaconing / C2 suspicion: {categories['beaconing_score']:.1f} / 100")
    lines.append(f"  • Auth & identity anomalies: {categories['auth_anomaly_score']:.1f} / 100")
    lines.append(f"  • Inbound threat pressure:  {categories['inbound_threat_score']:.1f} / 100")
    lines.append(f"  • Sensor tampering signals: {categories['tamper_score']:.1f} / 100")
    lines.append(f"  • Config / posture drift:   {categories['config_drift_score']:.1f} / 100")
    lines.append("")
    if mitre_tactics:
        lines.append("MITRE ATT&CK–style Tactics Suspected:")
        for t in mitre_tactics:
            lines.append(f"  • {t}")
    else:
        lines.append("MITRE ATT&CK–style Tactics Suspected: None confidently indicated.")
    lines.append("")
    lines.append("Integrity Hints:")
    lines.append(f"  • Recent anomaly runs (last 20): {hints['recent_anomaly_runs']}")
    lines.append(f"  • Total runs in history:         {hints['total_runs']}")
    if hints["integrity_flags"]:
        lines.append("  • Integrity flags / issues:")
        for flag in hints["integrity_flags"]:
            lines.append(f"      - {flag}")
    else:
        lines.append("  • Integrity flags / issues: None recorded.")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("  This report reflects defensive cyber intelligence derived from internal GLL telemetry.")
    lines.append("  It does not rely on any active scanning, exploitation, or offensive cyber actions.")
    lines.append("  It is suitable for ISR, DCO, and commander-facing briefs.")

    txt_path = os.path.join(DOCS_DIR, "defensive_cyber_intel_report.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return payload


if __name__ == "__main__":
    result = analyze_defensive_cyber_intel()
    print("Defensive Cyber Intelligence Report generated:")
    print(f"  - {os.path.join('docs', 'defensive_cyber_intel_report.json')}")
    print(f"  - {os.path.join('docs', 'defensive_cyber_intel_report.txt')}")
    print("")
    print(json.dumps(result, indent=2))

