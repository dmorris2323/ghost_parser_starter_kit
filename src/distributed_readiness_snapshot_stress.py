"""
distributed_readiness_snapshot_stress.py

Stress test: ensures snapshot never crashes and stays bounded under degraded inputs.
SAFE / SYNTHETIC only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from distributed_readiness_snapshot import build_distributed_readiness_snapshot


OUT = Path("docs") / "base_defense"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def main() -> None:
    cases: List[Dict[str, Any]] = [
        {},  # totally missing
        {"comms_ok": False, "power_ok": False},
        {"sensor_coverage_pct": -10, "staffing_pct": 120},  # out of bounds
        {"open_incidents": 999, "incident_severity_max": 5},
        {"cyber_alerts_high": 50, "perimeter_events": 999},
        {"comms_ok": "yes", "power_ok": "no", "staffing_pct": "70"},
    ]

    crashes = 0
    violations: List[str] = []

    for i, inp in enumerate(cases):
        try:
            prod = build_distributed_readiness_snapshot(inputs=inp)
            score = float(prod["readiness"]["score_0_100"])
            if not (0.0 <= score <= 100.0):
                violations.append(f"CASE_{i}: SCORE_OUT_OF_BOUNDS:{score}")
            band = str(prod["readiness"]["band"])
            if band not in {"GREEN", "AMBER", "RED"}:
                violations.append(f"CASE_{i}: UNKNOWN_BAND:{band}")
        except Exception as e:
            crashes += 1
            violations.append(f"CASE_{i}: CRASH:{e.__class__.__name__}:{e}")

    verdict = "PASS" if crashes == 0 and len(violations) == 0 else "FAIL"

    report = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "cases": len(cases),
        "crashes": crashes,
        "violations": violations,
    }

    latest = OUT / "distributed_readiness_snapshot_stress_latest.json"
    stamped = OUT / f"distributed_readiness_snapshot_stress_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    _write_json(latest, report)
    _write_json(stamped, report)

    print("Distributed Readiness Snapshot Stress:")
    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))


if __name__ == "__main__":
    main()

