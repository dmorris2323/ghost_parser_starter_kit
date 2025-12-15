"""
distributed_readiness_snapshot.py

Commander-grade "Distributed Readiness Snapshot" (SAFE / SYNTHETIC)

Goal (Week-2 Base Defense hardening):
- Produce useful readiness outputs even with incomplete inputs.
- Degrade gracefully; never crash.
- Write latest + stamped artifacts under docs/base_defense/.

Inputs are safe training proxies (NOT real base data).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        return default


def _coerce_bool(x: Any, default: bool = False) -> bool:
    try:
        if x is None:
            return default
        if isinstance(x, bool):
            return x
        if isinstance(x, (int, float)):
            return bool(x)
        if isinstance(x, str):
            return x.strip().lower() in {"true", "1", "yes", "y", "ok"}
        return default
    except Exception:
        return default


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _band(score_0_100: float) -> str:
    if score_0_100 >= 85:
        return "GREEN"
    if score_0_100 >= 70:
        return "AMBER"
    return "RED"


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


@dataclass(frozen=True)
class SnapshotInputs:
    # All optional; missing values should NOT crash anything.
    comms_ok: Optional[bool] = None
    power_ok: Optional[bool] = None
    sensor_coverage_pct: Optional[float] = None     # 0..100
    open_incidents: Optional[int] = None
    incident_severity_max: Optional[int] = None     # 0..5
    staffing_pct: Optional[float] = None            # 0..100
    cyber_alerts_high: Optional[int] = None
    perimeter_events: Optional[int] = None
    notes: Optional[List[str]] = None


def build_distributed_readiness_snapshot(
    *,
    inputs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a readiness snapshot from safe proxy inputs.
    Never throws; always returns a bounded, commander-readable product.
    """
    raw = inputs if isinstance(inputs, dict) else {}

    s_inputs = SnapshotInputs(
        comms_ok=raw.get("comms_ok"),
        power_ok=raw.get("power_ok"),
        sensor_coverage_pct=raw.get("sensor_coverage_pct"),
        open_incidents=raw.get("open_incidents"),
        incident_severity_max=raw.get("incident_severity_max"),
        staffing_pct=raw.get("staffing_pct"),
        cyber_alerts_high=raw.get("cyber_alerts_high"),
        perimeter_events=raw.get("perimeter_events"),
        notes=_safe_list(raw.get("notes")),
    )

    # Coerce + bound
    comms_ok = _coerce_bool(s_inputs.comms_ok, default=False) if s_inputs.comms_ok is not None else None
    power_ok = _coerce_bool(s_inputs.power_ok, default=False) if s_inputs.power_ok is not None else None
    sensor_cov = _clamp(_coerce_float(s_inputs.sensor_coverage_pct, 0.0), 0.0, 100.0) if s_inputs.sensor_coverage_pct is not None else None
    open_inc = max(0, _coerce_int(s_inputs.open_incidents, 0)) if s_inputs.open_incidents is not None else None
    sev_max = _clamp(_coerce_float(s_inputs.incident_severity_max, 0.0), 0.0, 5.0) if s_inputs.incident_severity_max is not None else None
    staffing = _clamp(_coerce_float(s_inputs.staffing_pct, 0.0), 0.0, 100.0) if s_inputs.staffing_pct is not None else None
    cyber_hi = max(0, _coerce_int(s_inputs.cyber_alerts_high, 0)) if s_inputs.cyber_alerts_high is not None else None
    perim = max(0, _coerce_int(s_inputs.perimeter_events, 0)) if s_inputs.perimeter_events is not None else None

    missing: List[str] = []
    if comms_ok is None:
        missing.append("comms_ok")
    if power_ok is None:
        missing.append("power_ok")
    if sensor_cov is None:
        missing.append("sensor_coverage_pct")
    if open_inc is None:
        missing.append("open_incidents")
    if sev_max is None:
        missing.append("incident_severity_max")
    if staffing is None:
        missing.append("staffing_pct")
    if cyber_hi is None:
        missing.append("cyber_alerts_high")
    if perim is None:
        missing.append("perimeter_events")

    degraded = len(missing) > 0

    # Scoring (bounded 0..100). Conservative when data missing.
    # Start with 80 and apply penalties.
    score = 80.0

    # Infrastructure penalties
    if comms_ok is False:
        score -= 18.0
    if power_ok is False:
        score -= 25.0

    # Coverage: low coverage hits readiness
    if sensor_cov is not None:
        if sensor_cov < 60.0:
            score -= (60.0 - sensor_cov) * 0.4  # up to -24
        elif sensor_cov < 80.0:
            score -= (80.0 - sensor_cov) * 0.2

    # Incidents: more incidents + higher severity reduce readiness
    if open_inc is not None:
        score -= min(20.0, open_inc * 1.5)
    if sev_max is not None:
        score -= sev_max * 3.0

    # Staffing: below 70% starts hurting
    if staffing is not None:
        if staffing < 70.0:
            score -= (70.0 - staffing) * 0.5  # up to -35 if staffing=0
        elif staffing < 85.0:
            score -= (85.0 - staffing) * 0.2

    # Cyber and perimeter activity
    if cyber_hi is not None:
        score -= min(15.0, cyber_hi * 2.0)
    if perim is not None:
        score -= min(10.0, perim * 0.3)

    # Data-quality penalty (degraded operations)
    if degraded:
        score -= min(12.0, len(missing) * 1.5)

    score = _clamp(score, 0.0, 100.0)
    band = _band(score)

    # Commander actions (bounded)
    recommended_actions: List[str] = []
    if band == "GREEN":
        recommended_actions.append("Maintain routine monitoring; verify sensor coverage and staffing at next shift change.")
    elif band == "AMBER":
        recommended_actions.append("Notify duty officer; validate comms/power status; prioritize clearing high-severity incidents.")
        recommended_actions.append("Increase watch cadence; confirm cyber/perimeter event triage is staffed.")
    else:
        recommended_actions.append("Duty officer notify immediately; treat as degraded readiness until proven otherwise.")
        recommended_actions.append("Initiate focused checks: comms/power restoration, sensor coverage recovery, incident surge response.")
        recommended_actions.append("Escalate to installation leadership if critical services are confirmed down.")

    unknowns: List[str] = []
    if degraded:
        unknowns.append("Snapshot is probabilistic and bounded due to missing inputs.")
        unknowns.append("Operator judgment is required before making escalation decisions beyond duty-officer notification.")
        if missing:
            unknowns.append(f"Missing fields: {', '.join(missing)}")

    product: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "This artifact is derived from synthetic training inputs and is safe for demos/training.",
        "degraded": degraded,
        "missing_inputs": missing,
        "readiness": {
            "score_0_100": round(score, 2),
            "band": band,
        },
        "inputs_used": {
            "comms_ok": comms_ok,
            "power_ok": power_ok,
            "sensor_coverage_pct": sensor_cov,
            "open_incidents": open_inc,
            "incident_severity_max": sev_max,
            "staffing_pct": staffing,
            "cyber_alerts_high": cyber_hi,
            "perimeter_events": perim,
            "notes": _safe_list(s_inputs.notes),
        },
        "recommended_actions": recommended_actions,
        "unknowns": unknowns,
    }

    return product


def _render_txt(product: Dict[str, Any]) -> str:
    r = product.get("readiness", {})
    band = str(r.get("band", "UNKNOWN"))
    score = r.get("score_0_100", "NA")
    degraded = bool(product.get("degraded", False))
    missing = product.get("missing_inputs", [])

    lines: List[str] = []
    lines.append("Distributed Readiness Snapshot (SAFE/SYNTHETIC)")
    lines.append(f"generated_at_utc: {product.get('generated_at_utc')}")
    lines.append(f"readiness_band: {band}")
    lines.append(f"readiness_score_0_100: {score}")
    lines.append(f"degraded: {degraded}")
    if missing:
        lines.append(f"missing_inputs: {', '.join([str(x) for x in missing])}")

    lines.append("")
    lines.append("Recommended actions:")
    for a in product.get("recommended_actions", []) or []:
        lines.append(f"- {a}")

    unk = product.get("unknowns", []) or []
    if unk:
        lines.append("")
        lines.append("Unknowns / bounds:")
        for u in unk:
            lines.append(f"- {u}")

    return "\n".join(lines) + "\n"


def write_distributed_readiness_snapshot(product: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(OUT_DIR)
    stamped = _ts()

    json_latest = OUT_DIR / "distributed_readiness_snapshot_latest.json"
    txt_latest = OUT_DIR / "distributed_readiness_snapshot_latest.txt"
    json_stamped = OUT_DIR / f"distributed_readiness_snapshot_{stamped}.json"
    txt_stamped = OUT_DIR / f"distributed_readiness_snapshot_{stamped}.txt"

    _write_json(json_latest, product)
    _write_txt(txt_latest, _render_txt(product))
    _write_json(json_stamped, product)
    _write_txt(txt_stamped, _render_txt(product))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def main() -> None:
    # Safe default synthetic input profile (can be overridden by callers).
    sample_inputs = {
        "comms_ok": True,
        "power_ok": True,
        "sensor_coverage_pct": 78.0,
        "open_incidents": 4,
        "incident_severity_max": 2,
        "staffing_pct": 82.0,
        "cyber_alerts_high": 2,
        "perimeter_events": 6,
        "notes": ["Synthetic base-defense readiness proxy. Not real-world data."],
    }
    product = build_distributed_readiness_snapshot(inputs=sample_inputs)
    paths = write_distributed_readiness_snapshot(product)
    print("Distributed readiness snapshot written:")
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

