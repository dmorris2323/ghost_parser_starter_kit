"""
base_defense_storyboard_consistency_gate.py

Week-2 Base Defense Consistency Gate
Validates Base Defense Storyboard alignment with:
- Installation Threat Map
- Sensor Outage Predictor
- Distributed Readiness Snapshot

This gate is "commander sanity":
- No contradictory posture leaps vs risk band
- Required bounded tokens are present
- Missing inputs are explicit violations (no silent pass)

Outputs:
- docs/base_defense/base_defense_storyboard_consistency_latest.json
- docs/base_defense/base_defense_storyboard_consistency_<timestamp>.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


OUT_DIR = Path("docs") / "base_defense"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _load(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> None:
    violations: List[str] = []

    sb_path = OUT_DIR / "base_defense_storyboard_latest.json"
    tm_path = OUT_DIR / "installation_threat_map_latest.json"
    so_path = OUT_DIR / "sensor_outage_predictor_latest.json"
    dr_path = OUT_DIR / "distributed_readiness_snapshot_latest.json"

    storyboard = _load(sb_path)
    threat_map = _load(tm_path)
    outage = _load(so_path)
    readiness = _load(dr_path)

    if not storyboard:
        violations.append("MISSING_STORYBOARD_LATEST")
    if not threat_map:
        violations.append("MISSING_INSTALLATION_THREAT_MAP_LATEST")
    if not outage:
        violations.append("MISSING_SENSOR_OUTAGE_PREDICTOR_LATEST")
    if not readiness:
        violations.append("MISSING_DISTRIBUTED_READINESS_SNAPSHOT_LATEST")

    # If missing anything, still evaluate what we can (but keep violations)
    summary = storyboard.get("summary", {}) if isinstance(storyboard.get("summary", {}), dict) else {}
    posture = summary.get("posture", "ROUTINE_MONITORING")

    tm_summary = threat_map.get("summary", {}) if isinstance(threat_map.get("summary", {}), dict) else {}
    risk_band = tm_summary.get("overall_risk_band", None)

    # Required bounded language tokens must exist somewhere in storyboard JSON
    text = json.dumps(storyboard).lower()
    for tok in ["probabilistic", "bounded", "operator judgment"]:
        if tok not in text:
            violations.append(f"MISSING_REQUIRED_TOKEN:{tok}")

    # Commander sanity rule: if risk is LOW, do not dispatch forces
    if str(risk_band).upper() == "LOW" and posture == "SECURITY_FORCES_DISPATCH":
        violations.append("POSTURE_EXCEEDS_RISK_BAND:LOW->SECURITY_FORCES_DISPATCH")

    verdict = "PASS" if not violations else "FAIL"

    report = {
        "generated_at_utc": _utc_now(),
        "verdict": verdict,
        "violations": violations,
        "inputs": {
            "storyboard_latest": str(sb_path),
            "installation_threat_map_latest": str(tm_path),
            "sensor_outage_predictor_latest": str(so_path),
            "distributed_readiness_snapshot_latest": str(dr_path),
        },
        "observed": {
            "posture": posture,
            "risk_band": risk_band,
        },
    }

    latest = OUT_DIR / "base_defense_storyboard_consistency_latest.json"
    stamped = OUT_DIR / f"base_defense_storyboard_consistency_{_ts()}.json"
    latest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))


if __name__ == "__main__":
    main()

