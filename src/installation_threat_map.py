"""
Installation Threat Map
Week-2 Base Defense Hardening

Purpose:
- Fuse partial base-defense telemetry
- Produce bounded threat posture
- Remain stable under missing inputs
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

OUT_DIR = Path("docs/base_defense")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_POSTURES = {
    "ROUTINE_MONITORING",
    "HEIGHTENED_AWARENESS",
    "SECURITY_FORCES_NOTIFY",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _safe_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _compute_confidence(ambiguity_flags: List[str], threat_score: int) -> str:
    """
    Confidence is bounded. We do NOT let it become "HIGH" under ambiguity.
    """
    if ambiguity_flags:
        return "LOW" if threat_score >= 5 else "MEDIUM"
    # no ambiguity
    if threat_score == 0:
        return "HIGH"
    if threat_score < 5:
        return "MEDIUM"
    return "MEDIUM"


def _threat_band(threat_score: int) -> str:
    if threat_score == 0:
        return "GREEN"
    if threat_score < 5:
        return "AMBER"
    return "RED"


def build_installation_threat_map(
    perimeter_events: Optional[List[Dict[str, Any]]] = None,
    sensor_status: Optional[Dict[str, str]] = None,
    patrol_reports: Optional[List[Dict[str, Any]]] = None,
    comms_state: str = "OK",
) -> Dict[str, Any]:
    """
    All inputs optional.
    System must remain stable under partial data.
    """

    perimeter_events = _safe_list(perimeter_events)
    patrol_reports = _safe_list(patrol_reports)
    sensor_status = _safe_dict(sensor_status)

    ambiguity_flags: List[str] = []

    comms_state_norm = str(comms_state or "OK").upper().strip()
    if comms_state_norm != "OK":
        ambiguity_flags.append("DEGRADED_COMMS")

    offline_sensors = [k for k, v in sensor_status.items() if str(v).upper().strip() != "OK"]
    if offline_sensors:
        ambiguity_flags.append("SENSOR_OUTAGE")

    # ----- bounded scoring (simple proxy; no intent inference) -----
    threat_score = 0
    threat_score += len(perimeter_events) * 2
    threat_score += len(patrol_reports)

    # bounded increase only — loss of sensors slightly increases uncertainty but does not spike posture
    if offline_sensors:
        threat_score += 1

    # ----- posture selection -----
    if threat_score == 0:
        posture = "ROUTINE_MONITORING"
    elif threat_score < 5:
        posture = "HEIGHTENED_AWARENESS"
    else:
        posture = "SECURITY_FORCES_NOTIFY"

    # 🔒 Cap escalation under ambiguity (base-defense version)
    cap_applied = False
    if ambiguity_flags and posture not in {"ROUTINE_MONITORING", "HEIGHTENED_AWARENESS"}:
        posture = "HEIGHTENED_AWARENESS"
        cap_applied = True

    if posture not in ALLOWED_POSTURES:
        posture = "HEIGHTENED_AWARENESS"
        ambiguity_flags.append("POSTURE_SANITIZED")

    confidence = _compute_confidence(ambiguity_flags, threat_score)
    band = _threat_band(threat_score)

    bounded_tokens = "Assessment is probabilistic and bounded; operator judgment applies."

    return {
        "generated_at_utc": _utc_now(),
        "inputs": {
            "counts": {
                "perimeter_events": len(perimeter_events),
                "patrol_reports": len(patrol_reports),
                "sensors_reported": len(sensor_status),
                "sensors_offline": len(offline_sensors),
            },
            "comms_state": comms_state_norm,
        },
        "status": {
            "posture": posture,
            "confidence": confidence,
            "threat_band": band,
            "threat_score": threat_score,
            "ambiguity_flags": ambiguity_flags,
            "cap_applied": cap_applied,
        },
        "what_we_can_say": [
            f"Installation posture is {posture} with confidence={confidence}.",
            f"Threat is assessed in a bounded band (threat_band={band}).",
            bounded_tokens,
        ],
        "what_we_cannot_say": [
            "Cannot infer adversary intent.",
            "Cannot confirm coordinated attack.",
            "Cannot attribute activity to a specific actor based on this product alone.",
        ],
        "operator_notes": [
            "If comms are degraded or sensors are offline, validate with Security Forces and cross-check manual reports.",
            "Escalation beyond SECURITY_FORCES_NOTIFY requires corroboration and command direction.",
        ],
    }


def _render_txt(report: Dict[str, Any]) -> str:
    s = report.get("status", {}) if isinstance(report.get("status"), dict) else {}
    inputs = report.get("inputs", {}) if isinstance(report.get("inputs"), dict) else {}
    counts = inputs.get("counts", {}) if isinstance(inputs.get("counts"), dict) else {}

    lines = [
        "INSTALLATION THREAT MAP",
        f"Generated: {report.get('generated_at_utc', '')}",
        "",
        f"Posture: {s.get('posture', 'UNKNOWN')}",
        f"Confidence: {s.get('confidence', 'UNKNOWN')}",
        f"Threat Band: {s.get('threat_band', 'UNKNOWN')}",
        f"Threat Score: {s.get('threat_score', 0)}",
        f"Ambiguity Flags: {', '.join(s.get('ambiguity_flags', []) or [])}",
        f"Cap Applied: {bool(s.get('cap_applied', False))}",
        "",
        "INPUT COUNTS:",
        f"- perimeter_events: {counts.get('perimeter_events', 0)}",
        f"- patrol_reports: {counts.get('patrol_reports', 0)}",
        f"- sensors_reported: {counts.get('sensors_reported', 0)}",
        f"- sensors_offline: {counts.get('sensors_offline', 0)}",
        f"- comms_state: {inputs.get('comms_state', 'UNKNOWN')}",
        "",
        "WHAT WE CAN SAY:",
    ]
    for x in report.get("what_we_can_say", []) or []:
        lines.append(f"- {x}")

    lines += ["", "WHAT WE CANNOT SAY:"]
    for x in report.get("what_we_cannot_say", []) or []:
        lines.append(f"- {x}")

    lines += ["", "OPERATOR NOTES:"]
    for x in report.get("operator_notes", []) or []:
        lines.append(f"- {x}")

    return "\n".join(lines)


def write_installation_threat_map(report: Dict[str, Any]) -> Dict[str, str]:
    import json

    ts = _ts()

    latest_json = OUT_DIR / "installation_threat_map_latest.json"
    stamped_json = OUT_DIR / f"installation_threat_map_{ts}.json"

    latest_txt = OUT_DIR / "installation_threat_map_latest.txt"
    stamped_txt = OUT_DIR / f"installation_threat_map_{ts}.txt"

    latest_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    stamped_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    txt = _render_txt(report)
    latest_txt.write_text(txt, encoding="utf-8")
    stamped_txt.write_text(txt, encoding="utf-8")

    return {
        "json_latest": str(latest_json),
        "txt_latest": str(latest_txt),
        "json_stamped": str(stamped_json),
        "txt_stamped": str(stamped_txt),
    }


if __name__ == "__main__":
    report = build_installation_threat_map(
        perimeter_events=[{"zone": "NORTH"}],
        sensor_status={"CAM_1": "OK", "RADAR_2": "OFFLINE"},
        patrol_reports=[{"unit": "SF-3"}],
        comms_state="NOISY",
    )
    paths = write_installation_threat_map(report)
    print(paths)

