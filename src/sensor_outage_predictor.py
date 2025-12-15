"""
sensor_outage_predictor.py

Week-2 Base Defense — Sensor Outage Predictor (SAFE)
Purpose:
- Produce a bounded, commander-readable snapshot of sensor outage risk.
- Must behave gracefully with missing/partial history (real-world condition).
- Outputs latest + stamped JSON/TXT to docs/base_defense/.

Notes:
- Uses synthetic/operationally-neutral fields (no classified assumptions).
- Risk is bounded [0,100]. No crashes. Always returns a well-formed report.

Artifacts:
- docs/base_defense/sensor_outage_predictor_latest.json
- docs/base_defense/sensor_outage_predictor_latest.txt
- docs/base_defense/sensor_outage_predictor_<timestamp>.json
- docs/base_defense/sensor_outage_predictor_<timestamp>.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


OUT_DIR = Path("docs") / "base_defense"


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


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _norm_health_state(state: Any) -> str:
    s = str(state or "").strip().upper()
    if s in {"OK", "GREEN"}:
        return "OK"
    if s in {"DEGRADED", "YELLOW", "WARN", "WARNING"}:
        return "DEGRADED"
    if s in {"DOWN", "RED", "FAIL", "FAILED", "OFFLINE"}:
        return "DOWN"
    if s in {"UNKNOWN", ""}:
        return "UNKNOWN"
    # tolerate arbitrary values
    return s[:32]


def _risk_band(score: float) -> str:
    if score < 20:
        return "LOW"
    if score < 45:
        return "GUARDED"
    if score < 70:
        return "ELEVATED"
    return "HIGH"


def _confidence(quality: str, missing_fields: int) -> str:
    # Quality input is one of: HIGH/MED/LOW/UNKNOWN (we normalize lightly)
    q = str(quality or "UNKNOWN").strip().upper()
    if q not in {"HIGH", "MED", "LOW", "UNKNOWN"}:
        q = "UNKNOWN"

    # Missing data penalizes confidence.
    if missing_fields >= 3:
        return "LOW"
    if missing_fields == 2:
        return "LOW" if q in {"LOW", "UNKNOWN"} else "MED"
    if missing_fields == 1:
        return "MED" if q in {"HIGH", "MED"} else "LOW"
    # no missing fields
    return q if q != "UNKNOWN" else "MED"


@dataclass(frozen=True)
class SensorTelemetry:
    sensor_id: str
    health_state: str  # OK/DEGRADED/DOWN/UNKNOWN
    last_seen_minutes: float  # minutes since last heartbeat/telemetry
    packet_loss_pct: float  # 0..100 (optional; can be 0 if unknown)
    jitter_ms: float  # optional; can be 0 if unknown
    battery_pct: Optional[float]  # optional; can be None
    tamper_flag: bool  # optional
    maint_window: bool  # optional


def _parse_sensor_row(row: Dict[str, Any]) -> SensorTelemetry:
    sid = str(row.get("sensor_id") or row.get("id") or "UNKNOWN_SENSOR").strip()
    if not sid:
        sid = "UNKNOWN_SENSOR"

    health = _norm_health_state(row.get("health_state") or row.get("state") or row.get("health"))
    last_seen = _coerce_float(row.get("last_seen_minutes"), _coerce_float(row.get("last_seen_min"), 999.0))
    packet_loss = _coerce_float(row.get("packet_loss_pct"), _coerce_float(row.get("loss_pct"), 0.0))
    jitter = _coerce_float(row.get("jitter_ms"), _coerce_float(row.get("latency_jitter_ms"), 0.0))

    batt_raw = row.get("battery_pct", row.get("battery", None))
    battery = None
    if batt_raw is not None:
        b = _coerce_float(batt_raw, -1.0)
        if b >= 0:
            battery = _clamp(b, 0.0, 100.0)

    tamper = bool(row.get("tamper_flag", row.get("tamper", False)))
    maint = bool(row.get("maintenance_window", row.get("maint_window", False)))

    # guardrails: last_seen cannot be negative
    last_seen = max(0.0, last_seen)
    packet_loss = _clamp(packet_loss, 0.0, 100.0)
    jitter = max(0.0, jitter)

    return SensorTelemetry(
        sensor_id=sid[:64],
        health_state=health,
        last_seen_minutes=last_seen,
        packet_loss_pct=packet_loss,
        jitter_ms=jitter,
        battery_pct=battery,
        tamper_flag=tamper,
        maint_window=maint,
    )


def _sensor_risk_score(s: SensorTelemetry) -> Tuple[float, List[str]]:
    """
    Heuristic risk model (bounded) with explicit reasons.
    """
    reasons: List[str] = []
    score = 0.0

    # Health state base
    if s.health_state == "OK":
        score += 5.0
    elif s.health_state == "DEGRADED":
        score += 25.0
        reasons.append("Health state degraded")
    elif s.health_state == "DOWN":
        score += 55.0
        reasons.append("Health state down/offline")
    else:  # UNKNOWN or other
        score += 20.0
        reasons.append("Health state unknown")

    # Recency / heartbeat staleness
    # Normal sensors may report frequently; we use soft thresholds.
    if s.last_seen_minutes >= 180:
        score += 30.0
        reasons.append("Telemetry stale (>=180 min)")
    elif s.last_seen_minutes >= 60:
        score += 18.0
        reasons.append("Telemetry stale (>=60 min)")
    elif s.last_seen_minutes >= 15:
        score += 8.0
        reasons.append("Telemetry delayed (>=15 min)")

    # Network quality signals
    if s.packet_loss_pct >= 15:
        score += 18.0
        reasons.append("High packet loss (>=15%)")
    elif s.packet_loss_pct >= 5:
        score += 8.0
        reasons.append("Moderate packet loss (>=5%)")

    if s.jitter_ms >= 200:
        score += 12.0
        reasons.append("High jitter (>=200ms)")
    elif s.jitter_ms >= 80:
        score += 6.0
        reasons.append("Moderate jitter (>=80ms)")

    # Battery risk (if known)
    if s.battery_pct is not None:
        if s.battery_pct <= 10:
            score += 18.0
            reasons.append("Battery critically low (<=10%)")
        elif s.battery_pct <= 25:
            score += 8.0
            reasons.append("Battery low (<=25%)")

    # Tamper + maintenance
    if s.tamper_flag:
        score += 25.0
        reasons.append("Tamper flag set")

    if s.maint_window:
        # Maintenance window should reduce escalation, but still note it.
        score -= 10.0
        reasons.append("Maintenance window active (risk dampened)")

    score = _clamp(score, 0.0, 100.0)
    return score, reasons


def build_sensor_outage_predictor(
    *,
    sensors: Optional[List[Dict[str, Any]]] = None,
    site_id: str = "INSTALLATION_ALPHA",
    time_horizon_minutes: int = 120,
    data_quality: str = "MED",
) -> Dict[str, Any]:
    """
    Build outage prediction report.

    sensors: list of dict rows (safe). If None or empty, report still returns.
    time_horizon_minutes: used for narrative only (bounded forecast window).
    data_quality: HIGH/MED/LOW/UNKNOWN, affects confidence only.
    """
    rows = sensors or []
    parsed: List[SensorTelemetry] = []
    parse_errors: List[str] = []

    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            parse_errors.append(f"Row {i}: not a dict")
            continue
        try:
            parsed.append(_parse_sensor_row(r))
        except Exception as e:
            parse_errors.append(f"Row {i}: parse failed: {e.__class__.__name__}")

    # Missing fields proxy: if we have no sensors or many UNKNOWN fields, confidence drops
    missing_fields = 0
    if len(parsed) == 0:
        missing_fields += 3
    else:
        unknown_health = sum(1 for s in parsed if s.health_state in {"UNKNOWN"} or not s.health_state)
        stale_unknown = sum(1 for s in parsed if s.last_seen_minutes >= 999.0)
        if unknown_health > 0:
            missing_fields += 1
        if stale_unknown > 0:
            missing_fields += 1
        # if battery missing across most sensors, count one missing bucket
        batt_known = sum(1 for s in parsed if s.battery_pct is not None)
        if batt_known == 0 and len(parsed) >= 3:
            missing_fields += 1

    conf = _confidence(data_quality, missing_fields)

    per_sensor: List[Dict[str, Any]] = []
    site_risk_scores: List[float] = []
    high_risk = 0
    down = 0
    degraded = 0
    unknown = 0

    for s in parsed:
        score, reasons = _sensor_risk_score(s)
        site_risk_scores.append(score)

        if s.health_state == "DOWN":
            down += 1
        elif s.health_state == "DEGRADED":
            degraded += 1
        elif s.health_state == "UNKNOWN":
            unknown += 1

        if score >= 70:
            high_risk += 1

        per_sensor.append(
            {
                "sensor_id": s.sensor_id,
                "health_state": s.health_state,
                "last_seen_minutes": round(s.last_seen_minutes, 2),
                "packet_loss_pct": round(s.packet_loss_pct, 2),
                "jitter_ms": round(s.jitter_ms, 2),
                "battery_pct": None if s.battery_pct is None else round(float(s.battery_pct), 2),
                "tamper_flag": bool(s.tamper_flag),
                "maintenance_window": bool(s.maint_window),
                "outage_risk_score": round(score, 2),
                "risk_band": _risk_band(score),
                "reasons": reasons[:8],  # bounded
            }
        )

    # Site-level aggregation (bounded)
    if site_risk_scores:
        avg_risk = sum(site_risk_scores) / max(1, len(site_risk_scores))
        peak_risk = max(site_risk_scores)
    else:
        avg_risk = 0.0
        peak_risk = 0.0

    # Site posture: bounded and conservative
    # - HIGH if many sensors are high risk or any DOWN with stale heartbeat
    posture = "ROUTINE_MONITORING"
    if down >= 1 and any(s.last_seen_minutes >= 60 for s in parsed if s.health_state == "DOWN"):
        posture = "DUTY_OFFICER_NOTIFY"
    if high_risk >= 2:
        posture = "DUTY_OFFICER_NOTIFY"
    if high_risk >= 4 or down >= 3:
        posture = "ELEVATED_WATCH"

    # Always keep posture bounded (no “national” language here)
    allowed = {"ROUTINE_MONITORING", "DUTY_OFFICER_NOTIFY", "ELEVATED_WATCH"}
    if posture not in allowed:
        posture = "ROUTINE_MONITORING"

    summary = {
        "site_id": str(site_id)[:64],
        "time_horizon_minutes": int(max(15, min(720, _coerce_int(time_horizon_minutes, 120)))),
        "sensor_count": len(parsed),
        "counts": {
            "down": down,
            "degraded": degraded,
            "unknown": unknown,
            "high_risk": high_risk,
        },
        "avg_outage_risk_score": round(_clamp(avg_risk, 0.0, 100.0), 2),
        "peak_outage_risk_score": round(_clamp(peak_risk, 0.0, 100.0), 2),
        "site_risk_band": _risk_band(avg_risk),
        "posture": posture,
        "confidence": conf,
    }

    what_we_can_say = [
        f"Sensor outage risk is assessed as {summary['site_risk_band']} (avg_score={summary['avg_outage_risk_score']}).",
        f"Posture is {posture} with confidence={conf}.",
        f"Assessment is bounded to the next {summary['time_horizon_minutes']} minutes and is probabilistic.",
    ]
    unknowns_list: List[str] = []
    if len(parsed) == 0:
        unknowns_list.append("No sensor telemetry provided; risk is based on absence of data.")
    if parse_errors:
        unknowns_list.append("Some inputs could not be parsed; see parse_errors.")
    if unknown > 0:
        unknowns_list.append("Some sensors report UNKNOWN health; confirm comms and power status.")
    if conf == "LOW":
        unknowns_list.append("Low confidence due to missing/partial inputs; operator judgment required.")

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "This artifact uses safe, synthetic/operationally-neutral sensor status fields. It is intended for training/demos.",
        "summary": summary,
        "per_sensor": per_sensor,
        "parse_errors": parse_errors,
        "what_we_can_say": what_we_can_say,
        "unknowns": unknowns_list,
        "operator_actions": [
            "Confirm power/comms for sensors flagged DOWN or stale.",
            "Check maintenance windows before escalation.",
            "If tamper_flag present, initiate physical security check.",
        ],
    }
    return report


def _render_txt(report: Dict[str, Any]) -> str:
    s = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    counts = s.get("counts", {}) if isinstance(s.get("counts"), dict) else {}
    lines: List[str] = []
    lines.append("GLL Base Defense — Sensor Outage Predictor (SAFE)")
    lines.append(f"generated_at_utc: {report.get('generated_at_utc','')}")
    lines.append("")
    lines.append(f"site_id: {s.get('site_id','')}")
    lines.append(f"time_horizon_minutes: {s.get('time_horizon_minutes','')}")
    lines.append(f"posture: {s.get('posture','')}")
    lines.append(f"confidence: {s.get('confidence','')}")
    lines.append(f"avg_outage_risk_score: {s.get('avg_outage_risk_score','')}")
    lines.append(f"peak_outage_risk_score: {s.get('peak_outage_risk_score','')}")
    lines.append("")
    lines.append("counts:")
    lines.append(f"  down: {counts.get('down',0)}")
    lines.append(f"  degraded: {counts.get('degraded',0)}")
    lines.append(f"  unknown: {counts.get('unknown',0)}")
    lines.append(f"  high_risk: {counts.get('high_risk',0)}")
    lines.append("")
    lines.append("What we can say (bounded):")
    for x in report.get("what_we_can_say", []) or []:
        lines.append(f"- {x}")
    lines.append("")
    if report.get("unknowns"):
        lines.append("Unknowns / caveats:")
        for x in report.get("unknowns", []) or []:
            lines.append(f"- {x}")
        lines.append("")
    lines.append("Top sensors (by risk):")
    per = report.get("per_sensor", []) or []
    if isinstance(per, list) and per:
        per_sorted = sorted(per, key=lambda r: _coerce_float(r.get("outage_risk_score"), 0.0), reverse=True)[:10]
        for r in per_sorted:
            lines.append(
                f"- {r.get('sensor_id','?')}: "
                f"state={r.get('health_state','?')}, "
                f"risk={r.get('outage_risk_score','?')} ({r.get('risk_band','?')}), "
                f"last_seen_min={r.get('last_seen_minutes','?')}"
            )
    else:
        lines.append("- (no sensors provided)")
    return "\n".join(lines) + "\n"


def write_sensor_outage_predictor(report: Dict[str, Any]) -> Dict[str, str]:
    """
    Write latest + stamped outputs.
    """
    _safe_mkdir(OUT_DIR)
    stamp = _ts()

    json_latest = OUT_DIR / "sensor_outage_predictor_latest.json"
    txt_latest = OUT_DIR / "sensor_outage_predictor_latest.txt"
    json_stamped = OUT_DIR / f"sensor_outage_predictor_{stamp}.json"
    txt_stamped = OUT_DIR / f"sensor_outage_predictor_{stamp}.txt"

    _write_json(json_latest, report)
    _write_txt(txt_latest, _render_txt(report))
    _write_json(json_stamped, report)
    _write_txt(txt_stamped, _render_txt(report))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def _demo_inputs() -> List[Dict[str, Any]]:
    """
    Safe demo inputs with mixed states.
    """
    return [
        {"sensor_id": "PERIM_CAM_01", "health_state": "OK", "last_seen_minutes": 2, "packet_loss_pct": 0.5, "jitter_ms": 12, "battery_pct": None, "tamper_flag": False, "maintenance_window": False},
        {"sensor_id": "PERIM_CAM_02", "health_state": "DEGRADED", "last_seen_minutes": 18, "packet_loss_pct": 7.5, "jitter_ms": 95, "battery_pct": None, "tamper_flag": False, "maintenance_window": False},
        {"sensor_id": "RF_NODE_07", "health_state": "DOWN", "last_seen_minutes": 125, "packet_loss_pct": 0.0, "jitter_ms": 0.0, "battery_pct": 9.0, "tamper_flag": False, "maintenance_window": False},
        {"sensor_id": "GATE_MAG_03", "health_state": "UNKNOWN", "last_seen_minutes": 61, "packet_loss_pct": 12.0, "jitter_ms": 210, "battery_pct": 45.0, "tamper_flag": True, "maintenance_window": False},
        {"sensor_id": "SEISMIC_02", "health_state": "OK", "last_seen_minutes": 8, "packet_loss_pct": 1.0, "jitter_ms": 40, "battery_pct": 22.0, "tamper_flag": False, "maintenance_window": True},
    ]


def main() -> None:
    report = build_sensor_outage_predictor(
        sensors=_demo_inputs(),
        site_id="INSTALLATION_ALPHA",
        time_horizon_minutes=120,
        data_quality="MED",
    )
    paths = write_sensor_outage_predictor(report)
    print("Sensor outage predictor written:")
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

