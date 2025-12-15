"""
Installation Threat Map Stress Gate
Week-2 Base Defense Hardening

Goal:
- No crashes across many partial-input cases
- Posture remains bounded under ambiguity (cap applied)
- Required tokens appear in output text (probabilistic, bounded, operator judgment)
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from installation_threat_map import (
    build_installation_threat_map,
    write_installation_threat_map,
    ALLOWED_POSTURES,
)

OUT_DIR = Path("docs/nuclear")  # keep consistency with your existing habit
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_latest(obj: Dict[str, Any]) -> Dict[str, str]:
    latest = OUT_DIR / "installation_threat_map_stress_latest.json"
    stamped = OUT_DIR / f"installation_threat_map_stress_{_ts()}.json"
    latest.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return {"json_latest": str(latest), "json_stamped": str(stamped)}


def _tokens_ok(text: str) -> List[str]:
    req = ["probabilistic", "bounded", "operator judgment"]
    missing = [t for t in req if t.lower() not in text.lower()]
    return missing


def main() -> int:
    random.seed(71)

    crashes = 0
    violations: List[Dict[str, Any]] = []

    cases = 300

    for i in range(cases):
        # Randomly drop inputs
        perimeter_events = None if random.random() < 0.35 else [{"zone": random.choice(["N", "S", "E", "W"])}] * random.randint(0, 3)
        patrol_reports = None if random.random() < 0.35 else [{"unit": f"SF-{random.randint(1,9)}"}] * random.randint(0, 3)

        # sensor status may be missing entirely
        sensor_status = None
        if random.random() >= 0.35:
            sensor_status = {}
            for s in ["CAM_1", "CAM_2", "RADAR_1", "RADAR_2"]:
                if random.random() < 0.6:
                    sensor_status[s] = random.choice(["OK", "OFFLINE", "NOISY"])

        comms_state = random.choice(["OK", "NOISY", "DEGRADED", "OK"])

        try:
            report = build_installation_threat_map(
                perimeter_events=perimeter_events,
                sensor_status=sensor_status,
                patrol_reports=patrol_reports,
                comms_state=comms_state,
            )
        except Exception as e:
            crashes += 1
            violations.append(
                {
                    "case_index": i,
                    "type": "CRASH",
                    "error": f"{e.__class__.__name__}: {e}",
                }
            )
            continue

        status = report.get("status", {}) if isinstance(report.get("status"), dict) else {}
        posture = str(status.get("posture", "UNKNOWN"))
        ambiguity_flags = status.get("ambiguity_flags", []) or []
        cap_applied = bool(status.get("cap_applied", False))

        # posture must be valid
        if posture not in ALLOWED_POSTURES:
            violations.append(
                {
                    "case_index": i,
                    "type": "BAD_POSTURE",
                    "posture": posture,
                    "status": status,
                }
            )

        # if ambiguity present, posture must never be SECURITY_FORCES_NOTIFY (we cap to HEIGHTENED)
        if ambiguity_flags and posture == "SECURITY_FORCES_NOTIFY":
            violations.append(
                {
                    "case_index": i,
                    "type": "UNCAPPED_ESCALATION_UNDER_AMBIGUITY",
                    "status": status,
                }
            )

        # if ambiguity and threat_score high, cap should have been applied
        if ambiguity_flags and int(status.get("threat_score", 0)) >= 5 and not cap_applied:
            violations.append(
                {
                    "case_index": i,
                    "type": "EXPECTED_CAP_NOT_APPLIED",
                    "status": status,
                }
            )

    # write one real artifact for humans to read
    sample = build_installation_threat_map(
        perimeter_events=[{"zone": "NORTH"}, {"zone": "NORTH"}],
        sensor_status={"CAM_1": "OK", "RADAR_2": "OFFLINE"},
        patrol_reports=[{"unit": "SF-3"}],
        comms_state="NOISY",
    )
    paths = write_installation_threat_map(sample)

    # token check on latest txt
    txt_path = paths["txt_latest"]
    txt = Path(txt_path).read_text(encoding="utf-8")
    missing = _tokens_ok(txt)
    if missing:
        violations.append(
            {
                "type": "MISSING_REQUIRED_TOKENS",
                "missing": missing,
                "txt_latest": txt_path,
            }
        )

    verdict = "PASS" if (crashes == 0 and len(violations) == 0) else "FAIL"
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "cases": cases,
        "crashes": crashes,
        "violations_count": len(violations),
        "violations_preview": violations[:25],
        "sample_paths": paths,
    }
    out_paths = _write_latest(payload)

    print("Installation Threat Map Stress Gate:")
    print(json.dumps({**payload, **out_paths}, indent=2))

    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

