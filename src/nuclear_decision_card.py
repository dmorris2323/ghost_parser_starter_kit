"""
nuclear_decision_card.py

Nuclear Decision Card (Commander-grade, SAFE)
- Produces a decision-ready summary from trust/risk/alerts and degraded state
- Integrates Pre-Brief Trust Annotations as a commander-trust attachment
- Writes latest + stamped JSON/TXT outputs for demos/training/audit

SAFE NOTICE:
This module is intended for synthetic telemetry / training metadata unless otherwise specified.
It does not generate real missile telemetry or classified content.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List


DECISION_DIR = Path("docs") / "nuclear"
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


def _default_actions_for_band(conf_band: str, degraded: bool) -> List[str]:
    """
    Commander-ready actions. Tight and practical.
    """
    actions: List[str] = []
    if conf_band in {"HIGH", "MEDIUM"}:
        actions.append("Maintain continuous watch; verify contributing sensors/domains.")
        actions.append("Cross-check anomalies against recent baseline and known training patterns.")
        if degraded:
            actions.append("Degraded operations: request redundancy/alternate reporting path if available.")
    else:
        actions.append("Treat as provisional: do not escalate without corroboration.")
        actions.append("Run validation harness baseline + injected pattern to confirm expected deltas.")
        if degraded:
            actions.append("Degraded operations: prioritize restoring missing data inputs before decisions.")
    actions.append("Document assumptions + confidence drivers for audit and commander review.")
    return actions


def _escalation_posture(trust: float, risk: float, crit: int, high: int, degraded: bool) -> Dict[str, Any]:
    """
    Explainable posture model:
    - Not a real-world escalation ladder; it's a commander-friendly training proxy.
    """
    score = 0.0
    score += (risk * 0.6)
    score += (crit * 12.0)
    score += (min(high, 10) * 2.5)
    score += (max(0.0, 70.0 - trust) * 0.25)
    if degraded:
        score += 6.0

    score = _clamp(score, 0.0, 100.0)

    if score >= 75:
        posture = "ELEVATE"
        rationale = "High pressure environment: risk/alerts indicate sustained concern."
    elif score >= 45:
        posture = "HEIGHTENED_WATCH"
        rationale = "Moderate pressure: maintain alert posture and verify signal integrity."
    else:
        posture = "BASELINE_WATCH"
        rationale = "Bounded pressure: continue monitoring and trend analysis."

    return {
        "posture": posture,
        "posture_score": round(score, 2),
        "rationale": rationale,
    }


def _try_write_prebrief(
    *,
    trust_score: float,
    risk_score: float,
    alerts: Dict[str, Any],
    degraded: bool,
    difficulty: str,
    pattern_id: Optional[str],
    delta_vs_baseline: Optional[Dict[str, Any]],
    sis_status: str,
    sps_status: str,
    gate_status: str,
    operator_notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Best-effort: generate prebrief artifact and return its attachment payload.
    Does NOT fail decision card if prebrief module is missing.
    """
    try:
        from prebrief_trust_annotations import write_prebrief_trust_annotations_latest  # type: ignore

        result = write_prebrief_trust_annotations_latest(
            trust_score=trust_score,
            risk_score=risk_score,
            alerts=alerts,
            degraded=degraded,
            difficulty=difficulty,
            pattern_id=pattern_id,
            delta_vs_baseline=delta_vs_baseline,
            sis_status=sis_status,
            sps_status=sps_status,
            gate_status=gate_status,
            operator_notes=operator_notes or [],
        )

        rep = result.get("report", {}) if isinstance(result, dict) else {}
        summary = rep.get("summary", {}) if isinstance(rep, dict) else {}

        return {
            "status": "OK",
            "paths": {
                "json_latest": result.get("json_latest"),
                "txt_latest": result.get("txt_latest"),
                "json_stamped": result.get("json_stamped"),
                "txt_stamped": result.get("txt_stamped"),
            },
            "summary": summary,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "reason": f"Prebrief generation failed: {e.__class__.__name__}: {e}",
            "paths": {},
            "summary": {},
        }


def build_decision_card(
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
) -> Dict[str, Any]:
    """
    Build a commander-grade decision card object (does not write files).
    """
    alerts = alerts or {}
    trust = _clamp(_coerce_float(trust_score, 0.0), 0.0, 100.0)
    risk = _clamp(_coerce_float(risk_score, 0.0), 0.0, 100.0)

    crit = _coerce_int(alerts.get("crit", 0), 0)
    high = _coerce_int(alerts.get("high", 0), 0)
    anomaly = _coerce_int(alerts.get("anomaly", 0), 0)
    attack_like = _coerce_int(alerts.get("attack_like", 0), 0)

    # Commander confidence (tight + explainable)
    confidence = (
        0.55 * trust
        + 0.25 * (100.0 - risk)
        - 2.5 * min(crit, 5)
        - 1.0 * min(high, 10)
    )
    if degraded:
        confidence -= 10.0
    confidence = _clamp(confidence, 0.0, 100.0)
    conf_band = _band(confidence)

    posture = _escalation_posture(trust, risk, crit, high, degraded)
    actions = _default_actions_for_band(conf_band, degraded)

    # Attach prebrief artifact (best-effort)
    prebrief = _try_write_prebrief(
        trust_score=trust,
        risk_score=risk,
        alerts={"crit": crit, "high": high, "anomaly": anomaly, "attack_like": attack_like},
        degraded=degraded,
        difficulty=difficulty,
        pattern_id=pattern_id,
        delta_vs_baseline=delta_vs_baseline,
        sis_status=sis_status,
        sps_status=sps_status,
        gate_status=gate_status,
        operator_notes=["Attached to Nuclear Decision Card for commander-trust pre-brief."],
    )

    card: Dict[str, Any] = {
        "artifact": "nuclear_decision_card",
        "version": 1,
        "generated_at": _utc_now_iso(),
        "inputs": {
            "trust_score": round(trust, 2),
            "risk_score": round(risk, 2),
            "alerts": {"crit": crit, "high": high, "attack_like": attack_like, "anomaly": anomaly},
            "degraded": bool(degraded),
            "difficulty": difficulty,
            "pattern_id": pattern_id,
            "delta_vs_baseline": delta_vs_baseline,
            "gates": {
                "sis_status": sis_status,
                "sps_status": sps_status,
                "gate_status": gate_status,
            },
        },
        "commander_summary": {
            "confidence_score": round(confidence, 2),
            "confidence_band": conf_band,
            "recommended_posture": posture,
            "key_takeaway": (
                "System stable under current conditions."
                if conf_band in {"HIGH", "MEDIUM"}
                else "System outputs are provisional; verify before escalation."
            ),
        },
        "recommended_actions": actions,
        "attachments": {
            "prebrief_trust_annotations": prebrief,
        },
        "safe_notice": "This card is produced from training-safe metadata/synthetic telemetry unless explicitly sourced otherwise.",
    }
    return card


def write_decision_card_latest(
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
) -> Dict[str, Any]:
    """
    Writes latest + stamped JSON/TXT outputs and returns paths + object.
    """
    card = build_decision_card(
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
    )

    _safe_mkdir(DECISION_DIR)
    stamped = _ts()

    json_latest = DECISION_DIR / "decision_card_latest.json"
    txt_latest = DECISION_DIR / "decision_card_latest.txt"

    json_stamped = DECISION_DIR / f"decision_card_{stamped}.json"
    txt_stamped = DECISION_DIR / f"decision_card_{stamped}.txt"

    txt = _render_txt(card)

    _write_json(json_latest, card)
    _write_txt(txt_latest, txt)
    _write_json(json_stamped, card)
    _write_txt(txt_stamped, txt)

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
        "card": card,
    }


def _render_txt(card: Dict[str, Any]) -> str:
    inp = card.get("inputs", {})
    cs = card.get("commander_summary", {})
    att = card.get("attachments", {}).get("prebrief_trust_annotations", {})

    lines: List[str] = []
    lines.append("GLL — Nuclear Decision Card")
    lines.append("=" * 26)
    lines.append(f"Generated: {card.get('generated_at', 'UNKNOWN')}")
    lines.append("")
    lines.append("Inputs")
    lines.append("-" * 6)
    lines.append(f"Trust: {inp.get('trust_score')} | Risk: {inp.get('risk_score')} | Degraded: {inp.get('degraded')}")
    lines.append(f"Alerts: {inp.get('alerts')}")
    lines.append(f"Difficulty: {inp.get('difficulty')} | Pattern: {inp.get('pattern_id')}")
    lines.append("")
    lines.append("Commander Summary")
    lines.append("-" * 16)
    lines.append(f"Confidence: {cs.get('confidence_score')} ({cs.get('confidence_band')})")
    rp = cs.get("recommended_posture", {})
    lines.append(f"Posture: {rp.get('posture')} (score={rp.get('posture_score')})")
    lines.append(f"Rationale: {rp.get('rationale')}")
    lines.append(f"Key Takeaway: {cs.get('key_takeaway')}")
    lines.append("")
    lines.append("Recommended Actions")
    lines.append("-" * 18)
    for a in card.get("recommended_actions", []):
        lines.append(f"- {a}")
    lines.append("")

    lines.append("Attachment — Pre-Brief Trust Annotations")
    lines.append("-" * 38)
    lines.append(f"Status: {att.get('status')}")
    if att.get("paths"):
        lines.append(f"Paths: {att.get('paths')}")
    summ = att.get("summary") if isinstance(att, dict) else {}
    if isinstance(summ, dict) and summ:
        lines.append(f"Prebrief Summary: confidence={summ.get('confidence_score')} band={summ.get('confidence_band')}")
    if att.get("status") != "OK":
        lines.append(f"Reason: {att.get('reason')}")
    lines.append("")

    return "\n".join(lines)

