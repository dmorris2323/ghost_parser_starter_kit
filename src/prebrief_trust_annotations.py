"""
prebrief_trust_annotations.py

Pre-Brief Trust Annotations (Commander-Trust Artifact)
- Produces a human-readable, commander-grade explanation of trust/confidence drivers
- Captures degraded-mode penalties, missing data, assumptions, gates, and audit metadata
- Writes latest + stamped JSON/TXT outputs for demos/training/audit

SAFE: This module is designed to work with synthetic or real-but-nonclassified metadata.
It does not create or infer any real-world missile telemetry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BRIEFS_DIR = Path("docs") / "briefs"


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


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _band(score_0_100: float) -> str:
    s = _clamp(score_0_100, 0.0, 100.0)
    if s >= 85:
        return "HIGH"
    if s >= 70:
        return "MEDIUM"
    if s >= 50:
        return "LOW"
    return "VERY_LOW"


@dataclass
class PrebriefInputs:
    trust_score: float
    risk_score: float
    alerts: Dict[str, Any]
    degraded: bool = False

    # Optional context
    difficulty: str = "UNKNOWN"
    pattern_id: Optional[str] = None
    delta_vs_baseline: Optional[Dict[str, Any]] = None

    # Gate state (SIS/SPS)
    sis_status: str = "UNKNOWN"  # e.g., GREEN/YELLOW/RED
    sps_status: str = "UNKNOWN"  # e.g., GREEN/YELLOW/RED
    gate_status: str = "UNKNOWN"  # e.g., PASS/FAIL

    # Operator-facing metadata
    assumptions: Optional[List[str]] = None
    missing_data: Optional[List[str]] = None
    data_quality_notes: Optional[List[str]] = None
    operator_notes: Optional[List[str]] = None


def build_prebrief_trust_annotations(
    *,
    trust_score: Any,
    risk_score: Any,
    alerts: Optional[Dict[str, Any]] = None,
    degraded: bool = False,
    difficulty: str = "UNKNOWN",
    pattern_id: Optional[str] = None,
    delta_vs_baseline: Optional[Dict[str, Any]] = None,
    sis_status: str = "UNKNOWN",
    sps_status: str = "UNKNOWN",
    gate_status: str = "UNKNOWN",
    assumptions: Optional[List[str]] = None,
    missing_data: Optional[List[str]] = None,
    data_quality_notes: Optional[List[str]] = None,
    operator_notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Returns a commander-grade trust annotation object.
    """
    alerts = alerts or {}
    trust = _clamp(_coerce_float(trust_score, 0.0), 0.0, 100.0)
    risk = _clamp(_coerce_float(risk_score, 0.0), 0.0, 100.0)

    crit = _coerce_int(alerts.get("crit", 0), 0)
    high = _coerce_int(alerts.get("high", 0), 0)
    anomaly = _coerce_int(alerts.get("anomaly", 0), 0)
    attack_like = _coerce_int(alerts.get("attack_like", 0), 0)

    # Confidence model (simple + explainable; tuned for commander narrative)
    # - trust raises confidence
    # - risk reduces confidence
    # - degraded applies explicit penalty (uncertainty)
    # - crit/high alerts reduce confidence (pressure)
    confidence = (
        0.55 * trust
        + 0.25 * (100.0 - risk)
        - 2.5 * min(crit, 5)
        - 1.0 * min(high, 10)
    )
    if degraded:
        confidence -= 10.0  # explicit uncertainty penalty

    confidence = _clamp(confidence, 0.0, 100.0)

    # Key drivers for the commander (ranked narrative)
    drivers: List[str] = []
    if trust >= 85:
        drivers.append("High trust score indicates stable sensor reliability + consistent scoring behavior.")
    elif trust >= 70:
        drivers.append("Moderate trust score; system stable but requires continued validation under stress.")
    else:
        drivers.append("Low trust score; treat outputs as provisional and verify before escalation.")

    if risk >= 70:
        drivers.append("Elevated risk score; prioritizing containment/verification actions.")
    elif risk >= 40:
        drivers.append("Moderate risk; maintain heightened watch while verifying signal consistency.")
    else:
        drivers.append("Low risk; baseline watch posture is acceptable unless new signals emerge.")

    if crit > 0:
        drivers.append(f"{crit} CRIT alerts present; commander review recommended before major decisions.")
    if high > 0 and crit == 0:
        drivers.append(f"{high} HIGH alerts present; elevate watch and verify contributing factors.")
    if degraded:
        drivers.append("Degraded operations are active; uncertainty increased and confidence is explicitly penalized.")

    # Delta narrative if pattern injection / baseline comparison exists
    delta_notes: List[str] = []
    if isinstance(delta_vs_baseline, dict) and delta_vs_baseline:
        tp = delta_vs_baseline.get("trust_proxy_delta")
        rs = delta_vs_baseline.get("risk_score_delta")
        if tp is not None:
            delta_notes.append(f"Delta vs baseline: trust_proxy_delta={tp}")
        if rs is not None:
            delta_notes.append(f"Delta vs baseline: risk_score_delta={rs}")
        ad = delta_vs_baseline.get("alerts_delta")
        if isinstance(ad, dict):
            delta_notes.append(f"Delta vs baseline: alerts_delta={ad}")

    # Defaults
    assumptions = assumptions or [
        "This pre-brief is derived from safe metadata/synthetic telemetry for training/demos unless otherwise noted.",
        "Confidence reflects system behavior and data quality, not ground truth certainty.",
    ]
    missing_data = missing_data or []
    data_quality_notes = data_quality_notes or []
    operator_notes = operator_notes or []

    # Commander-facing summary (tight, explicit)
    summary = {
        "confidence_score": round(confidence, 2),
        "confidence_band": _band(confidence),
        "trust_score": round(trust, 2),
        "risk_score": round(risk, 2),
        "degraded": bool(degraded),
        "alerts": {
            "crit": crit,
            "high": high,
            "attack_like": attack_like,
            "anomaly": anomaly,
        },
        "gates": {
            "sis_status": (sis_status or "UNKNOWN"),
            "sps_status": (sps_status or "UNKNOWN"),
            "gate_status": (gate_status or "UNKNOWN"),
        },
        "training_context": {
            "difficulty": (difficulty or "UNKNOWN"),
            "pattern_id": pattern_id,
        },
    }

    report: Dict[str, Any] = {
        "artifact": "prebrief_trust_annotations",
        "version": 1,
        "generated_at": _utc_now_iso(),
        "summary": summary,
        "confidence_drivers": drivers,
        "delta_notes": delta_notes,
        "assumptions": assumptions,
        "missing_data": missing_data,
        "data_quality_notes": data_quality_notes,
        "operator_notes": operator_notes,
    }
    return report


def write_prebrief_trust_annotations_latest(
    *,
    trust_score: Any,
    risk_score: Any,
    alerts: Optional[Dict[str, Any]] = None,
    degraded: bool = False,
    difficulty: str = "UNKNOWN",
    pattern_id: Optional[str] = None,
    delta_vs_baseline: Optional[Dict[str, Any]] = None,
    sis_status: str = "UNKNOWN",
    sps_status: str = "UNKNOWN",
    gate_status: str = "UNKNOWN",
    assumptions: Optional[List[str]] = None,
    missing_data: Optional[List[str]] = None,
    data_quality_notes: Optional[List[str]] = None,
    operator_notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Writes latest + stamped JSON/TXT files and returns paths + object.
    """
    report = build_prebrief_trust_annotations(
        trust_score=trust_score,
        risk_score=risk_score,
        alerts=alerts or {},
        degraded=degraded,
        difficulty=difficulty,
        pattern_id=pattern_id,
        delta_vs_baseline=delta_vs_baseline,
        sis_status=sis_status,
        sps_status=sps_status,
        gate_status=gate_status,
        assumptions=assumptions,
        missing_data=missing_data,
        data_quality_notes=data_quality_notes,
        operator_notes=operator_notes,
    )

    _safe_mkdir(BRIEFS_DIR)
    stamped = _ts()

    json_latest = BRIEFS_DIR / "prebrief_trust_annotations_latest.json"
    txt_latest = BRIEFS_DIR / "prebrief_trust_annotations_latest.txt"

    json_stamped = BRIEFS_DIR / f"prebrief_trust_annotations_{stamped}.json"
    txt_stamped = BRIEFS_DIR / f"prebrief_trust_annotations_{stamped}.txt"

    txt = _render_txt(report)

    _write_json(json_latest, report)
    _write_txt(txt_latest, txt)
    _write_json(json_stamped, report)
    _write_txt(txt_stamped, txt)

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
        "report": report,
    }


def _render_txt(report: Dict[str, Any]) -> str:
    s = report.get("summary", {})
    gates = s.get("gates", {})
    ctx = s.get("training_context", {})

    lines: List[str] = []
    lines.append("GLL — Pre-Brief Trust Annotations")
    lines.append("=" * 34)
    lines.append(f"Generated: {report.get('generated_at', 'UNKNOWN')}")
    lines.append("")
    lines.append("Commander Summary")
    lines.append("-" * 16)
    lines.append(f"Confidence: {s.get('confidence_score')} ({s.get('confidence_band')})")
    lines.append(f"Trust Score: {s.get('trust_score')}")
    lines.append(f"Risk Score:  {s.get('risk_score')}")
    lines.append(f"Degraded:    {s.get('degraded')}")
    lines.append(f"Alerts:      {s.get('alerts')}")
    lines.append("")
    lines.append("Gates (SIS/SPS)")
    lines.append("-" * 13)
    lines.append(f"SIS: {gates.get('sis_status')} | SPS: {gates.get('sps_status')} | Gate: {gates.get('gate_status')}")
    lines.append("")
    lines.append("Training Context")
    lines.append("-" * 16)
    lines.append(f"Difficulty: {ctx.get('difficulty')}")
    lines.append(f"Pattern ID: {ctx.get('pattern_id')}")
    lines.append("")
    lines.append("Confidence Drivers")
    lines.append("-" * 18)
    for d in report.get("confidence_drivers", []):
        lines.append(f"- {d}")
    lines.append("")
    dn = report.get("delta_notes", [])
    if dn:
        lines.append("Delta Notes (Baseline vs Injected)")
        lines.append("-" * 33)
        for x in dn:
            lines.append(f"- {x}")
        lines.append("")

    lines.append("Assumptions")
    lines.append("-" * 11)
    for a in report.get("assumptions", []):
        lines.append(f"- {a}")
    lines.append("")

    md = report.get("missing_data", [])
    if md:
        lines.append("Missing Data")
        lines.append("-" * 12)
        for m in md:
            lines.append(f"- {m}")
        lines.append("")

    dq = report.get("data_quality_notes", [])
    if dq:
        lines.append("Data Quality Notes")
        lines.append("-" * 18)
        for q in dq:
            lines.append(f"- {q}")
        lines.append("")

    on = report.get("operator_notes", [])
    if on:
        lines.append("Operator Notes")
        lines.append("-" * 14)
        for n in on:
            lines.append(f"- {n}")
        lines.append("")

    return "\n".join(lines)

