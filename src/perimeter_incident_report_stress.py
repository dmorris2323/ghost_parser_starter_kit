"""
perimeter_incident_report_stress.py

Week-2 Base Defense Hardening
Stress test: perimeter_incident_report

Pass criteria:
- No crashes across cases
- Always returns a valid posture
- Writes stress artifact:
  docs/base_defense/perimeter_incident_report_stress_latest.json
  docs/base_defense/perimeter_incident_report_stress_<timestamp>.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from perimeter_incident_report import build_perimeter_incident_report, write_perimeter_incident_report


OUT_DIR = Path("docs") / "base_defense"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _case(incidents: Optional[List[Dict[str, Any]]], comms_state: Optional[str]) -> Dict[str, Any]:
    report = build_perimeter_incident_report(
        incidents=incidents,
        comms_state=comms_state,
        sensor_health={"ok": True},
        operator_notes="stress",
    )
    posture = str(report.get("summary", {}).get("posture", ""))
    degraded = bool(report.get("summary", {}).get("degraded", False))
    total = int(report.get("summary", {}).get("total_incidents", 0) or 0)
    return {"posture": posture, "degraded": degraded, "total": total, "report": report}


def main() -> None:
    crashes = 0
    violations: List[str] = []
    cases_run = 0

    postures_allowed = {
        "ROUTINE_MONITORING",
        "DUTY_OFFICER_NOTIFY",
        "SECURITY_FORCES_DISPATCH",
    }

    test_vectors = [
        (None, "OK"),
        ([], "OK"),
        (None, "NOISY"),
        (None, None),
        ([{"id": "X", "severity": "CRIT", "zone": "RUNWAY", "type": "INTRUSION"}], "OK"),
        ([{"id": "Y", "severity": "HIGH", "zone": "NORTH_GATE", "type": "UAS"}], "OK"),
        ([{"id": "Z", "severity": "MED", "zone": "EAST", "type": "FENCE"}], "NOISY"),
        ([{"id": "W", "severity": "???", "zone": "UNK", "type": "UNK"}], "OK"),
    ]

    for incidents, comms_state in test_vectors:
        cases_run += 1
        try:
            res = _case(incidents, comms_state)
            posture = res["posture"]
            if posture not in postures_allowed:
                violations.append(f"INVALID_POSTURE:{posture}")
        except Exception as e:
            crashes += 1
            violations.append(f"CRASH:{e.__class__.__name__}:{e}")

    verdict = "PASS" if crashes == 0 and len([v for v in violations if v.startswith("INVALID_POSTURE")]) == 0 else "FAIL"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "runs": cases_run,
        "crashes": crashes,
        "violations": violations,
    }

    latest = OUT_DIR / "perimeter_incident_report_stress_latest.json"
    stamped = OUT_DIR / f"perimeter_incident_report_stress_{_ts()}.json"
    _write_json(latest, out)
    _write_json(stamped, out)

    print("Perimeter Incident Report Stress:")
    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))


if __name__ == "__main__":
    main()

