#!/usr/bin/env python3
"""
Perimeter Incident Report (Week-2 Base Defense hardening)

Artifact standard (non-negotiable):
- docs/base_defense/perimeter_incident_report_latest.json
- docs/base_defense/perimeter_incident_report_latest.txt
- docs/base_defense/perimeter_incident_report_YYYYMMDD_HHMMSS.json
- docs/base_defense/perimeter_incident_report_YYYYMMDD_HHMMSS.txt
- Legacy compatibility:
  - src/docs/perimeter_incident_report.json
  - src/docs/perimeter_incident_report.txt

Hardening goals:
- Flawless outputs without perfect inputs
- No crash on missing fields / non-numeric values / empty events
- Posture bounded
- Ambiguity flags populate
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ----------------------------
# Paths (standard + legacy)
# ----------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_BASE = REPO_ROOT / "docs" / "base_defense"
LEGACY_DIR = REPO_ROOT / "src" / "docs"

LATEST_JSON = DOCS_BASE / "perimeter_incident_report_latest.json"
LATEST_TXT = DOCS_BASE / "perimeter_incident_report_latest.txt"

LEGACY_JSON = LEGACY_DIR / "perimeter_incident_report.json"
LEGACY_TXT = LEGACY_DIR / "perimeter_incident_report.txt"


# ----------------------------
# Helpers
# ----------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    if val is None:
        return default
    try:
        if isinstance(val, bool):
            return default
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip()
        if s == "":
            return default
        return float(s)
    except Exception:
        return default


def _safe_int(val: Any, default: Optional[int] = None) -> Optional[int]:
    if val is None:
        return default
    try:
        if isinstance(val, bool):
            return default
        if isinstance(val, int):
            return int(val)
        s = str(val).strip()
        if s == "":
            return default
        return int(float(s))
    except Exception:
        return default


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _risk_band(score: float) -> str:
    # score in [0,100]
    if score >= 80:
        return "SEVERE"
    if score >= 55:
        return "ELEVATED"
    if score >= 30:
        return "GUARDED"
    return "LOW"


def _bounded_posture(overall_band: str, ambiguity_flags: List[str]) -> str:
    """
    Bounded posture rule:
    - SEVERE -> SECURITY_FORCES_DISPATCH (unless ambiguity forces cap)
    - ELEVATED/GUARDED -> DUTY_OFFICER_NOTIFY
    - LOW -> ROUTINE_MONITORING

    Escalation cap under ambiguity: never exceed DUTY_OFFICER_NOTIFY when ambiguous.
    """
    posture = "ROUTINE_MONITORING"
    if overall_band == "SEVERE":
        posture = "SECURITY_FORCES_DISPATCH"
    elif overall_band in {"ELEVATED", "GUARDED"}:
        posture = "DUTY_OFFICER_NOTIFY"

    # 🔒 Cap escalation under ambiguity
    if ambiguity_flags and posture == "SECURITY_FORCES_DISPATCH":
        posture = "DUTY_OFFICER_NOTIFY"

    return posture


def _ensure_dirs() -> None:
    DOCS_BASE.mkdir(parents=True, exist_ok=True)
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False), encoding="utf-8")


# ----------------------------
# Core model
# ----------------------------

@dataclass
class Incident:
    incident_id: str
    zone: str
    sensor: str
    severity: str
    confidence: Optional[float]
    timestamp_utc: str
    description: str
    raw: Dict[str, Any]


def _normalize_severity(raw: Any) -> str:
    if raw is None:
        return "UNKNOWN"
    s = str(raw).strip().upper()
    if s in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        return s
    # common noise
    if s in {"MED", "MID"}:
        return "MEDIUM"
    return "UNKNOWN"


def _severity_weight(sev: str) -> float:
    return {
        "LOW": 10.0,
        "MEDIUM": 25.0,
        "HIGH": 45.0,
        "CRITICAL": 70.0,
        "UNKNOWN": 20.0,
    }.get(sev, 20.0)


def _sensor_weight(sensor: str) -> float:
    s = (sensor or "UNKNOWN").strip().upper()
    # Weighted so we can handle missing/unknown gracefully
    if "CAM" in s:
        return 1.0
    if "RADAR" in s:
        return 1.15
    if "RF" in s or "SIG" in s:
        return 1.1
    if "MOTION" in s:
        return 1.05
    return 1.0


def _parse_incident(i: Dict[str, Any], idx: int, ambiguity_flags: List[str]) -> Incident:
    raw = dict(i or {})

    incident_id = str(raw.get("incident_id") or raw.get("id") or f"INC_{idx:04d}")
    zone = str(raw.get("zone") or raw.get("sector") or "UNKNOWN").strip() or "UNKNOWN"
    sensor = str(raw.get("sensor") or raw.get("source") or "UNKNOWN").strip() or "UNKNOWN"
    severity = _normalize_severity(raw.get("severity"))

    # confidence: optional numeric 0..1
    conf = _safe_float(raw.get("confidence"), default=None)
    if raw.get("confidence") is not None and conf is None:
        ambiguity_flags.append("NON_NUMERIC_CONFIDENCE")
    if conf is not None:
        conf = _clamp(conf, 0.0, 1.0)

    ts = str(raw.get("timestamp_utc") or raw.get("timestamp") or _utc_now_iso())
    desc = str(raw.get("description") or raw.get("details") or "").strip()

    # If core fields are missing -> ambiguity
    if zone == "UNKNOWN":
        ambiguity_flags.append("MISSING_ZONE")
    if sensor == "UNKNOWN":
        ambiguity_flags.append("MISSING_SENSOR")
    if severity == "UNKNOWN":
        ambiguity_flags.append("UNKNOWN_SEVERITY")

    return Incident(
        incident_id=incident_id,
        zone=zone,
        sensor=sensor,
        severity=severity,
        confidence=conf,
        timestamp_utc=ts,
        description=desc,
        raw=raw,
    )


def _compute_risk(events: List[Incident], ambiguity_flags: List[str]) -> Tuple[float, str, Dict[str, Any]]:
    """
    Returns:
      (risk_score_0_100, risk_band, rollup_details)
    """
    if not events:
        ambiguity_flags.append("EMPTY_EVENTS")
        return 0.0, "LOW", {"note": "No events provided; default LOW risk."}

    zone_max: Dict[str, float] = {}
    roll = {"zone_scores": {}, "event_count": len(events)}

    for e in events:
        sev_w = _severity_weight(e.severity)
        sen_w = _sensor_weight(e.sensor)

        # confidence if missing -> assume 0.6 but flag ambiguity
        conf = e.confidence
        if conf is None:
            ambiguity_flags.append("MISSING_CONFIDENCE")
            conf = 0.6

        score = sev_w * sen_w * conf
        score = _clamp(score, 0.0, 100.0)

        prev = zone_max.get(e.zone, 0.0)
        zone_max[e.zone] = max(prev, score)

    # overall risk = max zone score (bounded, simple)
    max_risk = max(zone_max.values()) if zone_max else 0.0
    band = _risk_band(max_risk)

    roll["zone_scores"] = {z: round(s, 2) for z, s in zone_max.items()}
    roll["max_risk_score"] = round(max_risk, 2)
    roll["risk_band"] = band

    return float(max_risk), band, roll


def build_perimeter_incident_report(
    events: Optional[List[Dict[str, Any]]] = None,
    installation: str = "INSTALLATION",
    comms_state: Optional[str] = "OK",
) -> Dict[str, Any]:
    """
    Build report object. Must never crash.
    """
    ambiguity_flags: List[str] = []
    unknowns: List[str] = []

    if comms_state is None:
        unknowns.append("comms_state")
        ambiguity_flags.append("MISSING_COMMS_STATE")
    else:
        cs = str(comms_state).strip().upper()
        if cs == "":
            unknowns.append("comms_state")
            ambiguity_flags.append("MISSING_COMMS_STATE")
        elif cs not in {"OK", "DEGRADED", "DOWN"}:
            ambiguity_flags.append("UNKNOWN_COMMS_STATE")

    raw_events = events if isinstance(events, list) else []
    if events is None:
        ambiguity_flags.append("MISSING_EVENTS_LIST")

    parsed: List[Incident] = []
    for idx, item in enumerate(raw_events):
        try:
            parsed.append(_parse_incident(item if isinstance(item, dict) else {"value": item}, idx, ambiguity_flags))
        except Exception as ex:
            ambiguity_flags.append(f"EVENT_PARSE_ERROR:{type(ex).__name__}")

    risk_score, risk_band, rollup = _compute_risk(parsed, ambiguity_flags)
    posture = _bounded_posture(risk_band, ambiguity_flags)

    # What we can say (bounded)
    what_we_can_say = [
        f"Perimeter posture is {posture} with risk_band={risk_band}.",
        f"Risk score is bounded (risk_score={round(risk_score, 2)}).",
        "Assessment is probabilistic and bounded; operator judgment applies.",
    ]
    if ambiguity_flags:
        what_we_can_say.append(f"Ambiguity flags present ({len(set(ambiguity_flags))}); escalation is capped under ambiguity.")

    what_we_cannot_say = [
        "Cannot infer adversary intent or attribution from perimeter signals alone.",
        "Cannot confirm breach without corroboration (human verification / security forces confirmation).",
    ]

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "Derived from synthetic/base-defense telemetry; safe for training/demos.",
        "installation": str(installation or "INSTALLATION"),
        "inputs": {
            "event_count_input": len(raw_events),
            "comms_state": comms_state,
        },
        "status": {
            "posture": posture,
            "risk_band": risk_band,
            "risk_score": round(float(risk_score), 2),
            "degraded": bool(comms_state in {"DEGRADED", "DOWN"} or comms_state is None),
            "ambiguity_flags": sorted(set(ambiguity_flags)),
            "unknowns": sorted(set(unknowns)),
        },
        "rollup": rollup,
        "events": [
            {
                "incident_id": e.incident_id,
                "zone": e.zone,
                "sensor": e.sensor,
                "severity": e.severity,
                "confidence": e.confidence,
                "timestamp_utc": e.timestamp_utc,
                "description": e.description,
            }
            for e in parsed
        ],
        "what_we_can_say": what_we_can_say,
        "what_we_cannot_say": what_we_cannot_say,
    }

    return report


def _render_txt(report: Dict[str, Any]) -> str:
    s = report.get("status", {}) or {}
    lines: List[str] = []
    lines.append("GLL — Perimeter Incident Report")
    lines.append(f"generated_at_utc: {report.get('generated_at_utc')}")
    lines.append(f"installation: {report.get('installation')}")
    lines.append("")
    lines.append(f"POSTURE: {s.get('posture')}")
    lines.append(f"RISK_BAND: {s.get('risk_band')}")
    lines.append(f"RISK_SCORE: {s.get('risk_score')}")
    lines.append(f"DEGRADED: {s.get('degraded')}")
    lines.append("")
    af = s.get("ambiguity_flags", []) or []
    if af:
        lines.append("AMBIGUITY_FLAGS:")
        for a in af:
            lines.append(f"- {a}")
        lines.append("")
    lines.append("WHAT WE CAN SAY (BOUNDED):")
    for w in (report.get("what_we_can_say", []) or []):
        lines.append(f"- {w}")
    lines.append("")
    lines.append("WHAT WE CANNOT SAY:")
    for w in (report.get("what_we_cannot_say", []) or []):
        lines.append(f"- {w}")
    lines.append("")
    lines.append("EVENTS:")
    ev = report.get("events", []) or []
    if not ev:
        lines.append("- (none)")
    else:
        for e in ev[:25]:
            lines.append(
                f"- [{e.get('timestamp_utc')}] {e.get('incident_id')} zone={e.get('zone')} "
                f"sev={e.get('severity')} sensor={e.get('sensor')} conf={e.get('confidence')} "
                f"desc={e.get('description') or ''}"
            )
        if len(ev) > 25:
            lines.append(f"- … truncated ({len(ev)} total)")
    return "\n".join(lines) + "\n"


def write_perimeter_incident_report(report: Dict[str, Any]) -> Dict[str, str]:
    _ensure_dirs()
    stamp = _stamp()

    stamped_json = DOCS_BASE / f"perimeter_incident_report_{stamp}.json"
    stamped_txt = DOCS_BASE / f"perimeter_incident_report_{stamp}.txt"

    txt = _render_txt(report)

    # Standard outputs
    _write_json(LATEST_JSON, report)
    _write_text(LATEST_TXT, txt)
    _write_json(stamped_json, report)
    _write_text(stamped_txt, txt)

    # Legacy outputs (backward compatibility)
    _write_json(LEGACY_JSON, report)
    _write_text(LEGACY_TXT, txt)

    return {
        "json_latest": str(LATEST_JSON),
        "txt_latest": str(LATEST_TXT),
        "json_stamped": str(stamped_json),
        "txt_stamped": str(stamped_txt),
        "legacy_json": str(LEGACY_JSON),
        "legacy_txt": str(LEGACY_TXT),
    }


def main() -> None:
    # Default demo payload (safe)
    demo_events = [
        {
            "incident_id": "INC_0001",
            "zone": "NORTH_PERIMETER",
            "sensor": "CAMERA_A1",
            "severity": "MEDIUM",
            "confidence": 0.72,
            "timestamp_utc": _utc_now_iso(),
            "description": "Motion detected near fence line; no visual confirmation yet.",
        },
        {
            "incident_id": "INC_0002",
            "zone": "EAST_GATE",
            "sensor": "RF_SENSOR_B2",
            "severity": "HIGH",
            "confidence": 0.64,
            "timestamp_utc": _utc_now_iso(),
            "description": "RF anomaly coincident with badge reader retries.",
        },
    ]
    report = build_perimeter_incident_report(
        events=demo_events,
        installation="PATRICK_SFB_TRAINING",
        comms_state="OK",
    )
    paths = write_perimeter_incident_report(report)
    print("Perimeter Incident Report written:")
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

