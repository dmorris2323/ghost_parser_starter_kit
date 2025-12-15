"""
installation_threat_map_stress.py

Stress test for Week-2 Base Defense — Installation Threat Map.

Purpose:
- Ensure no crashes under imperfect inputs
- Ensure ambiguity flags capture non-numeric sensor inputs
- Produce deterministic PASS/FAIL artifact

Output:
- docs/base_defense/installation_threat_map_stress_latest.json
- docs/base_defense/installation_threat_map_stress_<timestamp>.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from installation_threat_map import build_installation_threat_map


OUT_DIR = Path("docs") / "base_defense"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(p: Path, obj: Any) -> None:
    _safe_mkdir(p.parent)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _load_report_latest() -> Dict[str, Any]:
    p = OUT_DIR / "installation_threat_map_latest.json"
    return json.loads(p.read_text(encoding="utf-8"))


def run_stress(runs: int = 5) -> Dict[str, Any]:
    crashes = 0
    violations: List[str] = []

    test_vectors: List[Dict[str, Any]] = [
        # Normal
        {"zones": [{"zone": "A", "risk": 10}, {"zone": "B", "risk": 40}], "comms_state": "OK"},
        # Missing comms_state
        {"zones": [{"zone": "A", "risk": 10}], "comms_state": None},
        # BAD_DATA risk
        {"zones": [{"zone": "A", "risk": "BAD_DATA"}], "comms_state": "OK"},
        # zones not list
        {"zones": "NOT_A_LIST", "comms_state": "OK"},
        # weird zone item
        {"zones": [{"zone": "A", "risk": 10}, "NOT_A_DICT"], "comms_state": "OK"},
    ]

    for i in range(runs):
        vec = test_vectors[i % len(test_vectors)]
        try:
            build_installation_threat_map(
                zones=vec.get("zones"),
                comms_state=vec.get("comms_state"),
                include_legacy_writes=False,  # keep stress quiet
            )
            rpt = _load_report_latest()

            # Minimal required shape checks
            if "summary" not in rpt or "zones" not in rpt:
                violations.append("MISSING_KEYS:summary_or_zones")

            amb = rpt.get("ambiguity_flags", None)
            if not isinstance(amb, list):
                violations.append("AMBIGUITY_FLAGS_NOT_LIST")

            # If we injected BAD_DATA, we must see NON_NUMERIC_SENSOR_INPUT
            if vec.get("zones") and isinstance(vec.get("zones"), list):
                if any(isinstance(z, dict) and z.get("risk") == "BAD_DATA" for z in vec.get("zones")):
                    if "NON_NUMERIC_SENSOR_INPUT" not in (amb or []):
                        violations.append("MISSING_FLAG:NON_NUMERIC_SENSOR_INPUT")

        except Exception as e:
            crashes += 1
            violations.append(f"CRASH:{e.__class__.__name__}:{e}")

    verdict = "PASS" if crashes == 0 and len(violations) == 0 else "FAIL"

    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "runs": runs,
        "crashes": crashes,
        "violations": violations,
    }

    latest = OUT_DIR / "installation_threat_map_stress_latest.json"
    stamped = OUT_DIR / f"installation_threat_map_stress_{_ts()}.json"
    _write_json(latest, result)
    _write_json(stamped, result)

    return {
        "verdict": verdict,
        "latest": str(latest),
        "stamped": str(stamped),
    }


if __name__ == "__main__":
    print(json.dumps(run_stress(runs=5), indent=2))

