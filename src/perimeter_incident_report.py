"""
perimeter_incident_report.py

Week-2 Base Defense Hardening
Perimeter Incident Report (SAFE / SYNTHETIC)

Goals:
- Flawless outputs without perfect inputs
- Always write commander-usable report (bounded language)
- Write both:
  (A) canonical artifacts -> docs/base_defense/
  (B) legacy artifacts    -> src/docs/ (backward compatibility)

Outputs:
- docs/base_defense/perimeter_incident_report_latest.json
- docs/base_defense/perimeter_incident_report_latest.txt
- docs/base_defense/perimeter_incident_report_<timestamp>.json
- docs/base_defense/perimeter_incident_report_<timestamp>.txt
- (legacy) src/docs/perimeter_incident_report.json
- (legacy) src/docs/perimeter_incident_report.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


OUT_DIR = Path("docs") / "base_defense"
LEGACY_DIR = Path("src") / "docs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _bounded_language(degraded: bool, unknowns: List[str]) -> List[str]:
    lines = [
        "This product is generated from synthetic training telemetry.",
        "Assessment is probabilistic and bounded; operator judgment applies.",
    ]
    if degraded:
        lines.append("Degraded conditions detected; confidence is bounded downward.")
    if unknowns:
        lines.append("Unknowns present; do not infer intent from missing fields.")
    return lines


def _default_incidents() -> List[Dict[str, Any]]:
    # SAFE synthetic examples only
    return [
        {
            "id": "INC-001",
            "zone": "NORTH_GATE",
            "type": "UAS_SIGHTING",
            "severity": "HIGH",
            "timestamp_utc": _utc_now_iso(),
            "details": {"alt_m": 60, "bearing_deg": 20, "duration_s": 45},
        },
        {
            "id": "INC-002",
            "zone": "PERIMETER_EAST",
            "type": "FENCE_TAMPER",
            "severity": "MED",
            "timestamp_utc": _utc_now_iso(),
            "details": {"sensor_id": "FENCE-E-12", "repeat_hits": 3},
        },
    ]


def build_perimeter_incident_report(
    *,
    incidents: Optional[List[Dict[str, Any]]] = None,
    comms_state: Optional[str] = "OK",
    sensor_health: Optional[Dict[str, Any]] = None,
    operator_notes: Optional[str] = None,
) -> Dict[str, Any]:
    incidents = incidents if isinstance(incidents, list) and incidents else _default_incidents()
    sensor_health = sensor_health if isinstance(sensor_health, dict) else {}

    unknowns: List[str] = []
    if comms_state is None:
        unknowns.append("comms_state")

    degraded = False
    if str(comms_state or "").upper() not in {"OK", "NOMINAL"}:
        degraded = True

    # Aggregate counts safely
    sev_counts = {"CRIT": 0, "HIGH": 0, "MED": 0, "LOW": 0, "UNK": 0}
    for inc in incidents:
        sev = str(inc.get("severity", "UNK")).upper()
        if sev not in sev_counts:
            sev = "UNK"
        sev_counts[sev] += 1

    # Commander posture (bounded)
    posture = "ROUTINE_MONITORING"
    if sev_counts["CRIT"] > 0:
        posture = "SECURITY_FORCES_DISPATCH"
    elif sev_counts["HIGH"] >= 1:
        posture = "DUTY_OFFICER_NOTIFY"
    elif degraded and (sev_counts["MED"] + sev_counts["LOW"]) > 0:
        posture = "DUTY_OFFICER_NOTIFY"

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "type": "perimeter_incident_report",
        "safe_notice": "Synthetic training artifact. Do not use as real-world intel.",
        "inputs": {
            "comms_state": comms_state,
            "sensor_health": sensor_health,
            "operator_notes_present": bool(operator_notes),
        },
        "summary": {
            "posture": posture,
            "degraded": degraded,
            "incident_counts": sev_counts,
            "total_incidents": sum(sev_counts.values()),
        },
        "incidents": incidents,
        "bounded_statements": _bounded_language(degraded=degraded, unknowns=unknowns),
        "unknowns": unknowns,
    }

    if operator_notes:
        report["operator_notes"] = str(operator_notes)[:2000]

    return report


def write_perimeter_incident_report(report: Dict[str, Any]) -> Dict[str, str]:
    ts = _ts()
    json_latest = OUT_DIR / "perimeter_incident_report_latest.json"
    txt_latest = OUT_DIR / "perimeter_incident_report_latest.txt"
    json_stamped = OUT_DIR / f"perimeter_incident_report_{ts}.json"
    txt_stamped = OUT_DIR / f"perimeter_incident_report_{ts}.txt"

    legacy_json = LEGACY_DIR / "perimeter_incident_report.json"
    legacy_txt = LEGACY_DIR / "perimeter_incident_report.txt"

    _write_json(json_latest, report)
    _write_json(json_stamped, report)
    _write_txt(txt_latest, json.dumps(report, indent=2))
    _write_txt(txt_stamped, json.dumps(report, indent=2))

    # legacy compatibility
    _write_json(legacy_json, report)
    _write_txt(legacy_txt, json.dumps(report, indent=2))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
        "legacy_json": str(legacy_json),
        "legacy_txt": str(legacy_txt),
    }


def main() -> None:
    report = build_perimeter_incident_report()
    paths = write_perimeter_incident_report(report)
    print("Perimeter Incident Report written:")
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

