"""
sensor_outage_predictor_stress.py

Week-2 Base Defense — Stress test for Sensor Outage Predictor (SAFE)
Goal:
- No crashes across randomized degraded inputs
- Risk always bounded [0,100]
- Posture always one of {ROUTINE_MONITORING, DUTY_OFFICER_NOTIFY, ELEVATED_WATCH}
- Confidence always one of {HIGH, MED, LOW}
- Writes latest + stamped JSON to docs/base_defense/

Artifacts:
- docs/base_defense/sensor_outage_predictor_stress_latest.json
- docs/base_defense/sensor_outage_predictor_stress_<timestamp>.json
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from sensor_outage_predictor import build_sensor_outage_predictor


OUT_DIR = Path("docs") / "base_defense"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _rand_sensor(i: int) -> Dict[str, Any]:
    sid = f"SENSOR_{i:03d}"
    health = random.choice(["OK", "DEGRADED", "DOWN", "UNKNOWN", None, "green", "red"])
    # sometimes missing last_seen
    if random.random() < 0.12:
        last_seen = None
    else:
        # skew toward realistic values but include outliers
        last_seen = random.choice([0.5, 2, 8, 16, 45, 75, 120, 240, 999])

    loss = random.choice([0, 0.2, 1.0, 4.9, 5.1, 12.0, 18.0, 55.0, None])
    jitter = random.choice([0, 10, 45, 85, 140, 210, 400, None])
    batt = random.choice([None, 5, 9, 12, 24, 50, 88, 110])  # 110 should clamp
    tamper = random.choice([False, False, False, True])
    maint = random.choice([False, False, True])

    row: Dict[str, Any] = {"sensor_id": sid, "health_state": health}
    if last_seen is not None:
        row["last_seen_minutes"] = last_seen
    if loss is not None:
        row["packet_loss_pct"] = loss
    if jitter is not None:
        row["jitter_ms"] = jitter
    row["battery_pct"] = batt
    row["tamper_flag"] = tamper
    row["maintenance_window"] = maint
    return row


def main() -> None:
    random.seed(42)

    allowed_posture = {"ROUTINE_MONITORING", "DUTY_OFFICER_NOTIFY", "ELEVATED_WATCH"}
    allowed_conf = {"HIGH", "MED", "LOW"}

    runs = 120
    crashes = 0
    violations: List[str] = []

    for r in range(runs):
        # sometimes zero sensors (hard case)
        if random.random() < 0.08:
            sensors: List[Dict[str, Any]] = []
        else:
            n = random.randint(1, 25)
            sensors = [_rand_sensor(i) for i in range(n)]

        dq = random.choice(["HIGH", "MED", "LOW", "UNKNOWN", None])

        try:
            report = build_sensor_outage_predictor(
                sensors=sensors,
                site_id="INSTALLATION_ALPHA",
                time_horizon_minutes=random.choice([30, 60, 120, 240, 999]),
                data_quality=str(dq) if dq is not None else "UNKNOWN",
            )
        except Exception as e:
            crashes += 1
            violations.append(f"CRASH[{r}]: {e.__class__.__name__}: {e}")
            continue

        # Validate invariants
        summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
        posture = str(summary.get("posture", "")).strip()
        conf = str(summary.get("confidence", "")).strip()
        avg_score = float(summary.get("avg_outage_risk_score", 0.0) or 0.0)
        peak_score = float(summary.get("peak_outage_risk_score", 0.0) or 0.0)

        if posture not in allowed_posture:
            violations.append(f"BAD_POSTURE[{r}]: {posture}")
        if conf not in allowed_conf:
            violations.append(f"BAD_CONF[{r}]: {conf}")

        if not (0.0 <= avg_score <= 100.0):
            violations.append(f"AVG_OOB[{r}]: {avg_score}")
        if not (0.0 <= peak_score <= 100.0):
            violations.append(f"PEAK_OOB[{r}]: {peak_score}")

        # Per-sensor scores bounded
        per = report.get("per_sensor", [])
        if isinstance(per, list):
            for j, row in enumerate(per[:100]):  # bounded
                s = float(row.get("outage_risk_score", 0.0) or 0.0)
                if s != _clamp(s, 0.0, 100.0):
                    violations.append(f"SCORE_OOB[{r}:{j}]: {s}")

    verdict = "PASS" if crashes == 0 and len(violations) == 0 else "FAIL"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "runs": runs,
        "crashes": crashes,
        "violations_count": len(violations),
        "violations": violations[:200],  # bounded
    }

    _safe_mkdir(OUT_DIR)
    stamped = OUT_DIR / f"sensor_outage_predictor_stress_{_ts()}.json"
    latest = OUT_DIR / "sensor_outage_predictor_stress_latest.json"
    _write_json(stamped, out)
    _write_json(latest, out)

    print("Sensor Outage Predictor Stress:")
    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))


if __name__ == "__main__":
    main()

