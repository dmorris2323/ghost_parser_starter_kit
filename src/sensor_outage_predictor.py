"""
Sensor Outage Predictor
Week-2 Base Defense Hardening

Goal:
- Predict which sensors are at risk of outage soon (bounded, probabilistic)
- Remain stable under partial/missing inputs
- Never claim certainty; never infer adversary intent
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OUT_DIR = Path("docs/base_defense")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_RISK = {"LOW", "MEDIUM", "HIGH"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _risk_bucket(score: float) -> str:
    # score in [0, 1] conceptually
    if score >= 0.70:
        return "HIGH"
    if score >= 0.35:
        return "MEDIUM"
    return "LOW"


def _bounded_tokens() -> str:
    return "Assessment is probabilistic and bounded; operator judgment applies."


@dataclass(frozen=True)
class SensorHealth:
    sensor_id: str
    state: str  # "OK" | "NOISY" | "OFFLINE" | unknown
    last_seen_age_sec: float  # age since last contact
    error_rate: float  # 0..1 proxy
    battery_proxy: float  # 0..1 proxy


def _normalize_state(state: Any) -> str:
    s = str(state or "UNKNOWN").upper().strip()
    if s not in {"OK", "NOISY", "OFFLINE"}:
        return "UNKNOWN"
    return s


def _parse_sensor_row(sensor_id: str, row: Dict[str, Any]) -> SensorHealth:
    """
    row can be arbitrarily shaped; we coerce safely.
    """
    row = _safe_dict(row)
    return SensorHealth(
        sensor_id=str(sensor_id),
        state=_normalize_state(row.get("state") or row.get("status") or "UNKNOWN"),
        last_seen_age_sec=_coerce_float(row.get("last_seen_age_sec") or row.get("age_sec") or 0.0, 0.0),
        error_rate=max(0.0, min(1.0, _coerce_float(row.get("error_rate") or row.get("err") or 0.0, 0.0))),
        battery_proxy=max(0.0, min(1.0, _coerce_float(row.get("battery_proxy") or row.get("battery") or 1.0, 1.0))),
    )


def _outage_risk_score(h: SensorHealth) -> Tuple[float, List[str]]:
    """
    Returns (score, flags)
    Score is bounded 0..1 and represents outage likelihood proxy.
    """
    flags: List[str] = []

    # base risk
    score = 0.05

    if h.state == "OFFLINE":
        score = 0.95
        flags.append("ALREADY_OFFLINE")
        return score, flags

    if h.state == "NOISY":
        score += 0.25
        flags.append("NOISY_STATE")

    if h.last_seen_age_sec >= 300:
        score += 0.25
        flags.append("STALE_LAST_SEEN>=300S")
    elif h.last_seen_age_sec >= 120:
        score += 0.15
        flags.append("STALE_LAST_SEEN>=120S")

    if h.error_rate >= 0.40:
        score += 0.20
        flags.append("HIGH_ERROR_RATE")
    elif h.error_rate >= 0.20:
        score += 0.10
        flags.append("ELEVATED_ERROR_RATE")

    if h.battery_proxy <= 0.20:
        score += 0.20
        flags.append("LOW_BATTERY_PROXY")
    elif h.battery_proxy <= 0.40:
        score += 0.10
        flags.append("MID_BATTERY_PROXY")

    # clamp
    score = max(0.0, min(1.0, score))
    return score, flags


def predict_sensor_outages(
    sensor_health: Optional[Dict[str, Any]] = None,
    comms_state: str = "OK",
) -> Dict[str, Any]:
    """
    sensor_health: dict keyed by sensor_id -> health row
    comms_state: OK/NOISY/DEGRADED (affects ambiguity)
    """

    sensor_health = _safe_dict(sensor_health)

    ambiguity_flags: List[str] = []
    comms_state_norm = str(comms_state or "OK").upper().strip()
    if comms_state_norm != "OK":
        ambiguity_flags.append("DEGRADED_COMMS")

    sensors: List[SensorHealth] = []
    for sid, row in sensor_health.items():
        sensors.append(_parse_sensor_row(str(sid), _safe_dict(row)))

    # If nothing provided, we still return a stable, bounded product
    if not sensors:
        ambiguity_flags.append("NO_SENSOR_TELEMETRY")

    predictions: List[Dict[str, Any]] = []
    for h in sensors:
        score, flags = _outage_risk_score(h)

        # Under ambiguity (degraded comms) we cap risk at MEDIUM unless already offline
        capped = False
        risk = _risk_bucket(score)
        if ambiguity_flags and h.state != "OFFLINE" and risk == "HIGH":
            risk = "MEDIUM"
            capped = True

        predictions.append(
            {
                "sensor_id": h.sensor_id,
                "state": h.state,
                "risk": risk,
                "risk_score": round(score, 3),
                "capped": capped,
                "flags": flags,
                "last_seen_age_sec": round(h.last_seen_age_sec, 1),
                "error_rate": round(h.error_rate, 3),
                "battery_proxy": round(h.battery_proxy, 3),
            }
        )

    # Sort: highest risk first (then score)
    predictions.sort(key=lambda x: (x.get("risk") != "HIGH", x.get("risk") != "MEDIUM", -float(x.get("risk_score", 0.0))))

    # Topline posture: only about maintenance priority, not threat attribution
    high_count = sum(1 for p in predictions if p.get("risk") == "HIGH")
    med_count = sum(1 for p in predictions if p.get("risk") == "MEDIUM")

    if high_count > 0:
        posture = "MAINT_PRIORITY_NOW"
    elif med_count > 0:
        posture = "MAINT_PRIORITY_SOON"
    else:
        posture = "ROUTINE_MAINT"

    confidence = "LOW" if ambiguity_flags else "MEDIUM"
    if not ambiguity_flags and high_count == 0 and med_count == 0:
        confidence = "HIGH"

    report = {
        "generated_at_utc": _utc_now(),
        "safe_notice": "Derived from synthetic/base-defense telemetry for training/demos.",
        "inputs": {
            "sensor_count": len(sensors),
            "comms_state": comms_state_norm,
        },
        "status": {
            "posture": posture,
            "confidence": confidence,
            "ambiguity_flags": ambiguity_flags,
        },
        "summary": {
            "high_risk": high_count,
            "medium_risk": med_count,
            "low_risk": max(0, len(predictions) - high_count - med_count),
        },
        "predictions": predictions,
        "what_we_can_say": [
            f"Maintenance posture is {posture} with confidence={confidence}.",
            f"{high_count} sensors are HIGH outage risk; {med_count} are MEDIUM outage risk.",
            _bounded_tokens(),
        ],
        "what_we_cannot_say": [
            "Cannot attribute outages to adversary action.",
            "Cannot confirm root cause without maintenance diagnostics.",
        ],
        "operator_notes": [
            "Prioritize sensors marked HIGH risk for inspection/repair.",
            "If comms are degraded, treat predictions as more uncertain and corroborate via local checks.",
        ],
    }

    return report


def _render_txt(report: Dict[str, Any]) -> str:
    s = report.get("status", {}) if isinstance(report.get("status"), dict) else {}
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}

    lines = [
        "SENSOR OUTAGE PREDICTOR",
        f"Generated: {report.get('generated_at_utc', '')}",
        "",
        f"Posture: {s.get('posture', 'UNKNOWN')}",
        f"Confidence: {s.get('confidence', 'UNKNOWN')}",
        f"Ambiguity Flags: {', '.join(s.get('ambiguity_flags', []) or [])}",
        "",
        "SUMMARY:",
        f"- HIGH: {summary.get('high_risk', 0)}",
        f"- MEDIUM: {summary.get('medium_risk', 0)}",
        f"- LOW: {summary.get('low_risk', 0)}",
        "",
        "TOP PREDICTIONS (first 10):",
    ]

    preds = report.get("predictions", []) or []
    for p in preds[:10]:
        lines.append(
            f"- {p.get('sensor_id')}: state={p.get('state')} risk={p.get('risk')} score={p.get('risk_score')} capped={p.get('capped')}"
        )

    lines += ["", "WHAT WE CAN SAY:"]
    for x in report.get("what_we_can_say", []) or []:
        lines.append(f"- {x}")

    lines += ["", "WHAT WE CANNOT SAY:"]
    for x in report.get("what_we_cannot_say", []) or []:
        lines.append(f"- {x}")

    lines += ["", "OPERATOR NOTES:"]
    for x in report.get("operator_notes", []) or []:
        lines.append(f"- {x}")

    return "\n".join(lines)


def write_sensor_outage_prediction(report: Dict[str, Any]) -> Dict[str, str]:
    import json

    ts = _ts()
    latest_json = OUT_DIR / "sensor_outage_predictor_latest.json"
    stamped_json = OUT_DIR / f"sensor_outage_predictor_{ts}.json"
    latest_txt = OUT_DIR / "sensor_outage_predictor_latest.txt"
    stamped_txt = OUT_DIR / f"sensor_outage_predictor_{ts}.txt"

    latest_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    stamped_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    txt = _render_txt(report)
    latest_txt.write_text(txt, encoding="utf-8")
    stamped_txt.write_text(txt, encoding="utf-8")

    return {
        "json_latest": str(latest_json),
        "txt_latest": str(latest_txt),
        "json_stamped": str(stamped_json),
        "txt_stamped": str(stamped_txt),
    }


if __name__ == "__main__":
    demo = {
        "RADAR_1": {"state": "OK", "last_seen_age_sec": 30, "error_rate": 0.05, "battery_proxy": 0.85},
        "RADAR_2": {"state": "NOISY", "last_seen_age_sec": 180, "error_rate": 0.25, "battery_proxy": 0.35},
        "CAM_1": {"state": "OK", "last_seen_age_sec": 400, "error_rate": 0.12, "battery_proxy": 0.65},
        "CAM_2": {"state": "OFFLINE", "last_seen_age_sec": 999, "error_rate": 0.9, "battery_proxy": 0.10},
    }
    r = predict_sensor_outages(sensor_health=demo, comms_state="DEGRADED")
    print(write_sensor_outage_prediction(r))

