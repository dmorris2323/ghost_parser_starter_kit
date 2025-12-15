"""
Sensor Outage Predictor Stress Gate
Week-2 Base Defense Hardening

Pass Criteria:
- No crashes
- Under comms ambiguity, no non-OFFLINE sensor may report HIGH risk (capped)
- Required tokens appear in latest txt (probabilistic, bounded, operator judgment)
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from sensor_outage_predictor import predict_sensor_outages, write_sensor_outage_prediction

OUT_DIR = Path("docs/nuclear")  # keep your existing pattern
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_latest(obj: Dict[str, Any]) -> Dict[str, str]:
    latest = OUT_DIR / "sensor_outage_predictor_stress_latest.json"
    stamped = OUT_DIR / f"sensor_outage_predictor_stress_{_ts()}.json"
    latest.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return {"json_latest": str(latest), "json_stamped": str(stamped)}


def _missing_tokens(text: str) -> List[str]:
    req = ["probabilistic", "bounded", "operator judgment"]
    return [t for t in req if t.lower() not in text.lower()]


def _rand_state() -> str:
    return random.choice(["OK", "NOISY", "OFFLINE", "UNKNOWN"])


def main() -> int:
    random.seed(72)

    crashes = 0
    violations: List[Dict[str, Any]] = []

    cases = 400
    for i in range(cases):
        comms_state = random.choice(["OK", "NOISY", "DEGRADED", "OK"])

        sensor_health: Dict[str, Any] = {}
        # sometimes empty input
        if random.random() < 0.10:
            sensor_health = {}
        else:
            for sid in ["CAM_1", "CAM_2", "RADAR_1", "RADAR_2", "FENCE_1", "RF_1"]:
                if random.random() < 0.75:
                    sensor_health[sid] = {
                        "state": _rand_state(),
                        "last_seen_age_sec": random.choice([0, 10, 30, 90, 150, 250, 400, 800]),
                        "error_rate": random.choice([0.0, 0.05, 0.12, 0.22, 0.35, 0.5, 0.8]),
                        "battery_proxy": random.choice([0.05, 0.15, 0.3, 0.45, 0.7, 0.9]),
                    }

        try:
            report = predict_sensor_outages(sensor_health=sensor_health, comms_state=comms_state)
        except Exception as e:
            crashes += 1
            violations.append({"case_index": i, "type": "CRASH", "error": f"{e.__class__.__name__}: {e}"})
            continue

        preds = report.get("predictions", []) or []
        status = report.get("status", {}) if isinstance(report.get("status"), dict) else {}
        ambiguity = status.get("ambiguity_flags", []) or []
        is_amb = bool(ambiguity)

        # Under ambiguity: only OFFLINE may be HIGH risk
        if is_amb:
            for p in preds:
                if p.get("state") != "OFFLINE" and p.get("risk") == "HIGH":
                    violations.append(
                        {
                            "case_index": i,
                            "type": "UNCAPPED_HIGH_RISK_UNDER_AMBIGUITY",
                            "sensor_id": p.get("sensor_id"),
                            "state": p.get("state"),
                            "risk": p.get("risk"),
                            "risk_score": p.get("risk_score"),
                            "ambiguity_flags": ambiguity,
                        }
                    )
                    break

    # Write a sample artifact so humans can read it
    sample = predict_sensor_outages(
        sensor_health={
            "RADAR_1": {"state": "NOISY", "last_seen_age_sec": 250, "error_rate": 0.35, "battery_proxy": 0.3},
            "CAM_2": {"state": "OFFLINE", "last_seen_age_sec": 800, "error_rate": 0.9, "battery_proxy": 0.1},
        },
        comms_state="DEGRADED",
    )
    paths = write_sensor_outage_prediction(sample)

    # token check
    txt = Path(paths["txt_latest"]).read_text(encoding="utf-8")
    missing = _missing_tokens(txt)
    if missing:
        violations.append({"type": "MISSING_REQUIRED_TOKENS", "missing": missing, "txt_latest": paths["txt_latest"]})

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

    print("Sensor Outage Predictor Stress Gate:")
    print(json.dumps({**payload, **out_paths}, indent=2))

    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

