#!/usr/bin/env python3
"""
Perimeter Incident Report Stress Harness (Week-2 Base Defense)

Must prove:
- No crash under bad inputs
- Posture is bounded
- Ambiguity flags populate when expected

Writes:
- docs/base_defense/perimeter_incident_report_stress_latest.json
- docs/base_defense/perimeter_incident_report_stress_YYYYMMDD_HHMMSS.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# local import (repo root path handled by user via sys.path insert in CLI)
from perimeter_incident_report import build_perimeter_incident_report, write_perimeter_incident_report  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "docs" / "base_defense"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


ALLOWED_POSTURES = {"ROUTINE_MONITORING", "DUTY_OFFICER_NOTIFY", "SECURITY_FORCES_DISPATCH"}


def _case_matrix() -> List[Dict[str, Any]]:
    return [
        {
            "name": "empty_events_list",
            "events": [],
            "comms_state": "OK",
            "expect_ambiguity": True,
        },
        {
            "name": "missing_events_none",
            "events": None,
            "comms_state": "OK",
            "expect_ambiguity": True,
        },
        {
            "name": "bad_types_in_events",
            "events": ["BAD", 123, None, {"zone": "NORTH", "severity": "HIGH"}],
            "comms_state": "OK",
            "expect_ambiguity": True,
        },
        {
            "name": "non_numeric_confidence",
            "events": [
                {"zone": "EAST", "sensor": "CAM_A", "severity": "HIGH", "confidence": "BAD_DATA"},
            ],
            "comms_state": "OK",
            "expect_ambiguity": True,
        },
        {
            "name": "unknown_fields_everywhere",
            "events": [
                {"incident_id": "X1", "confidence": 0.4, "description": "No zone/sensor/severity"},
            ],
            "comms_state": "OK",
            "expect_ambiguity": True,
        },
        {
            "name": "comms_state_missing",
            "events": [
                {"zone": "GATE", "sensor": "RF", "severity": "MEDIUM", "confidence": 0.6},
            ],
            "comms_state": None,
            "expect_ambiguity": True,
        },
        {
            "name": "severe_signal_but_ambiguous_caps",
            "events": [
                {"zone": "NORTH", "sensor": "RADAR", "severity": "CRITICAL", "confidence": None},  # missing conf triggers ambiguity
            ],
            "comms_state": "OK",
            "expect_ambiguity": True,
            "expect_cap": True,
        },
        {
            "name": "nominal_clean",
            "events": [
                {"zone": "NORTH", "sensor": "CAM", "severity": "LOW", "confidence": 0.9},
                {"zone": "EAST", "sensor": "RF", "severity": "MEDIUM", "confidence": 0.7},
            ],
            "comms_state": "OK",
            "expect_ambiguity": False,
        },
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    crashes = 0
    violations: List[str] = []
    runs = 0

    for c in _case_matrix():
        runs += 1
        name = c["name"]
        events = c.get("events")
        comms_state = c.get("comms_state")
        expect_ambiguity = bool(c.get("expect_ambiguity", False))
        expect_cap = bool(c.get("expect_cap", False))

        try:
            report = build_perimeter_incident_report(
                events=events,
                installation="BASE_DEFENSE_STRESS",
                comms_state=comms_state,
            )
            # also write artifacts (proves write paths don't crash)
            write_perimeter_incident_report(report)

            status = report.get("status", {}) or {}
            posture = status.get("posture")
            af = status.get("ambiguity_flags", []) or []

            if posture not in ALLOWED_POSTURES:
                violations.append(f"{name}:UNBOUNDED_POSTURE:{posture}")

            if expect_ambiguity and len(af) == 0:
                violations.append(f"{name}:MISSING_AMBIGUITY_FLAGS")

            if (not expect_ambiguity) and len(af) > 0:
                # not fatal in practice, but we track it
                violations.append(f"{name}:UNEXPECTED_AMBIGUITY_FLAGS:{len(af)}")

            if expect_cap:
                # must not dispatch under ambiguity
                if posture == "SECURITY_FORCES_DISPATCH":
                    violations.append(f"{name}:AMBIGUITY_CAP_FAILED")

        except Exception as ex:
            crashes += 1
            violations.append(f"CRASH:{name}:{type(ex).__name__}:{str(ex)[:160]}")

    verdict = "PASS" if crashes == 0 and len([v for v in violations if v.startswith("CRASH")]) == 0 and not any(
        ("UNBOUNDED_POSTURE" in v) or ("MISSING_AMBIGUITY_FLAGS" in v) or ("AMBIGUITY_CAP_FAILED" in v)
        for v in violations
    ) else "FAIL"

    latest = OUT_DIR / "perimeter_incident_report_stress_latest.json"
    stamped = OUT_DIR / f"perimeter_incident_report_stress_{_stamp()}.json"

    out = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "runs": runs,
        "crashes": crashes,
        "violations": violations,
    }

    _write_json(latest, out)
    _write_json(stamped, out)

    print("Perimeter Incident Report Stress:")
    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))


if __name__ == "__main__":
    main()

