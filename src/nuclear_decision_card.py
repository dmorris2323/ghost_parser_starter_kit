"""
nuclear_decision_card.py

Day 73 — Module 2: Decision-card confidence under ambiguity
- Pulls latest safe training/validation artifacts (best effort)
- Computes escalation rung (Module 1)
- Computes confidence under ambiguity (Module 2)
- Writes commander-friendly JSON + TXT decision card

SAFE:
- Uses synthetic/abstracted indicators and trust proxies
- Does not attempt real-world missile telemetry
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from escalation_ladder import assess_escalation
from decision_card_confidence import compute_confidence_under_ambiguity


OUT_DIR = Path("docs") / "decision_cards"
LATEST_JSON = OUT_DIR / "nuclear_decision_card_latest.json"
LATEST_TXT = OUT_DIR / "nuclear_decision_card_latest.txt"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write(path: Path, content: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _best_effort_inputs() -> Dict[str, Any]:
    """
    Pull latest artifacts if present. If missing, return safe defaults.
    """
    validation = _read_json(Path("docs") / "validation" / "fusion_validation_report.json") or {}
    curve = _read_json(Path("docs") / "training" / "training_curve_latest.json") or {}
    sis = _read_json(Path("docs") / "integrity" / "system_integrity_report.json") or {}
    sps = _read_json(Path("docs") / "integrity" / "sps_immunity_scan.json") or {}

    # Try to locate gate outputs (best-effort)
    gate_latest = _read_json(Path("docs") / "integrity" / "gate_latest.json") or {}

    return {
        "validation": validation,
        "training_curve": curve,
        "sis": sis,
        "sps": sps,
        "gate_latest": gate_latest,
    }


def _extract_gate_status(bundle: Dict[str, Any]) -> str:
    """
    Attempt to infer gate status. Default = UNKNOWN.
    We only need GREEN vs not GREEN for confidence cap.
    """
    gate = bundle.get("gate_latest") or {}
    if isinstance(gate, dict):
        status = gate.get("status") or gate.get("gate_status") or gate.get("overall_status")
        if isinstance(status, str) and status.strip():
            return status.strip().upper()

    # if no gate_latest, look for common fields in SIS/SPS
    sis = bundle.get("sis") or {}
    sps = bundle.get("sps") or {}

    for obj in (sis, sps):
        if isinstance(obj, dict):
            status = obj.get("overall_status") or obj.get("status")
            if isinstance(status, str) and status.strip():
                return status.strip().upper()

    return "UNKNOWN"


def _extract_trust(bundle: Dict[str, Any]) -> float:
    """
    Prefer fusion_trust result if present inside validation report.
    """
    validation = bundle.get("validation") or {}
    try:
        trust_obj = (
            validation.get("real_module_attempts", {})
            .get("results", {})
            .get("fusion_trust", {})
        )
        if isinstance(trust_obj, dict):
            ft = trust_obj.get("fusion_trust")
            if isinstance(ft, (int, float)):
                return float(ft)
    except Exception:
        pass
    return 0.0


def _extract_osl(bundle: Dict[str, Any]) -> str:
    validation = bundle.get("validation") or {}
    try:
        osl_obj = (
            validation.get("real_module_attempts", {})
            .get("results", {})
            .get("operator_safety_layer", {})
        )
        if isinstance(osl_obj, dict):
            status = osl_obj.get("osl_status") or osl_obj.get("status")
            if isinstance(status, str) and status.strip():
                return status.strip().upper()
    except Exception:
        pass
    return "UNKNOWN"


def _extract_indicators(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce abstracted indicator inputs for escalation/confidence.
    This is intentionally conservative: if we don't have a value, we don't invent it.
    """
    validation = bundle.get("validation") or {}

    # If your validation report includes domain deltas or injected patterns,
    # we can derive a few safe proxy domain scores.
    indicators: Dict[str, Any] = {}

    # Baseline vs injected deltas (safe training proxy)
    delta = validation.get("delta_vs_baseline") or {}
    injected = validation.get("injected_metrics") or {}
    baseline = validation.get("baseline_metrics") or {}

    # Proxy: alert pressure (CYBER/COMMS) and trust drop (multi-domain stress)
    try:
        trust_delta = float(delta.get("trust_proxy_delta", 0.0) or 0.0)
        risk_delta = float(delta.get("risk_score_delta", 0.0) or 0.0)
        alerts_delta = delta.get("alerts_delta") or {}

        # Treat trust drop as multi-domain stress
        stress = max(0.0, min(100.0, abs(trust_delta) * 5.0 + risk_delta))
        if stress > 0:
            indicators["EMS"] = {"score": min(100.0, 40.0 + stress / 2.0), "reliability": 75.0}
            indicators["COMMS"] = {"score": min(100.0, 35.0 + stress / 2.5), "reliability": 75.0}

        # Attack-like alert increases map to CYBER proxy
        if isinstance(alerts_delta, dict):
            atk = float(alerts_delta.get("attack_like", 0.0) or 0.0)
            anom = float(alerts_delta.get("anomaly", 0.0) or 0.0)
            cyber_score = min(100.0, 20.0 + atk * 4.0 + anom * 1.0)
            if cyber_score > 0:
                indicators["CYBER"] = {"score": cyber_score, "reliability": 80.0}

        # If injected metrics show crit/high, treat as escalatory pressure
        inj_alerts = (injected.get("alerts") or {})
        crit = float(inj_alerts.get("crit", 0.0) or 0.0)
        high = float(inj_alerts.get("high", 0.0) or 0.0)
        if crit + high > 0:
            indicators["RADIATION"] = {"score": min(100.0, 10.0 + crit * 15.0 + high * 5.0), "reliability": 70.0}

    except Exception:
        # If we fail to derive indicators, return empty -> confidence will be conservative
        return {}

    return indicators


def generate_nuclear_decision_card(*, prior_escalation_level: int = 0) -> Dict[str, Any]:
    """
    Primary generator used by CLI/GUI hooks.
    Writes latest + stamped artifacts and returns a summary dict.
    """
    bundle = _best_effort_inputs()
    gate_status = _extract_gate_status(bundle)
    fusion_trust = _extract_trust(bundle)
    osl_status = _extract_osl(bundle)

    indicators = _extract_indicators(bundle)

    # Module 1: escalation rung
    escalation = assess_escalation(indicators=indicators, prior_level=int(prior_escalation_level))

    # Module 2: confidence under ambiguity
    confidence = compute_confidence_under_ambiguity(
        indicators=indicators,
        fusion_trust=fusion_trust if fusion_trust > 0 else None,
        operator_safety=osl_status if osl_status else None,
        gate_status=gate_status,
        escalation_level=int(escalation.get("escalation_level", 0)),
        escalation_label=str(escalation.get("escalation_label", "MONITOR")),
    )

    report = {
        "generated_at": _utc_now(),
        "safe_notice": "SAFE: This decision card is generated from synthetic/abstracted indicators for training/demo.",
        "gate_status": gate_status,
        "fusion_trust": fusion_trust,
        "operator_safety_layer": osl_status,
        "inputs": {
            "indicators": indicators,
            "sources_present": {
                "validation_report": bool((bundle.get("validation") or {}).get("report_version")),
                "training_curve": bool((bundle.get("training_curve") or {}).get("AGI") is not None),
                "sis": bool(bundle.get("sis")),
                "sps": bool(bundle.get("sps")),
                "gate_latest": bool(bundle.get("gate_latest")),
            },
        },
        "escalation": escalation,
        "confidence": confidence,
        "commander_notes": [
            "If confidence is LOW/MEDIUM: treat as advisory and request corroboration.",
            "If gate_status is not GREEN: do not operationalize outputs—fix integrity first.",
            "Escalation ladder is conservative by design (anti-jump + evidence gates).",
        ],
    }

    # Write outputs
    stamped_json = OUT_DIR / f"nuclear_decision_card_{_ts()}.json"
    stamped_txt = OUT_DIR / f"nuclear_decision_card_{_ts()}.txt"
    _write_json(LATEST_JSON, report)
    _write_json(stamped_json, report)
    _write(LATEST_TXT, _render_txt(report))
    _write(stamped_txt, _render_txt(report))

    return {
        "json_latest": str(LATEST_JSON),
        "txt_latest": str(LATEST_TXT),
        "json_stamped": str(stamped_json),
        "txt_stamped": str(stamped_txt),
        "escalation_level": report["escalation"]["escalation_level"],
        "confidence_score": report["confidence"]["confidence_score"],
        "gate_status": gate_status,
    }


# Backward-compatible aliases (so old CLI hooks still work)
def write_nuclear_decision_card() -> Dict[str, Any]:
    return generate_nuclear_decision_card()


def write_decision_card() -> Dict[str, Any]:
    return generate_nuclear_decision_card()


def build_decision_card() -> Dict[str, Any]:
    return generate_nuclear_decision_card()


def _render_txt(report: Dict[str, Any]) -> str:
    esc = report.get("escalation", {})
    conf = report.get("confidence", {})

    lines = []
    lines.append("GLL — NUCLEAR DECISION CARD (SAFE TRAINING)")
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append(f"Gate Status: {report.get('gate_status')}")
    lines.append(f"Fusion Trust: {report.get('fusion_trust')}")
    lines.append(f"OSL: {report.get('operator_safety_layer')}")
    lines.append("")
    lines.append(f"Escalation: {esc.get('escalation_label')} (L{esc.get('escalation_level')})")
    if esc.get("blocking_factors"):
        lines.append("Blocking Factors:")
        for b in esc["blocking_factors"]:
            lines.append(f"  - {b}")
    lines.append("")
    lines.append(f"Confidence: {conf.get('confidence_label')} ({conf.get('confidence_score')}/100)")
    if conf.get("ambiguity_flags"):
        lines.append("Ambiguity Flags:")
        for f in conf["ambiguity_flags"]:
            lines.append(f"  - {f}")
    lines.append("")
    if conf.get("trust_annotations"):
        lines.append("Trust Annotations:")
        for n in conf["trust_annotations"]:
            lines.append(f"  - {n}")
    lines.append("")
    lines.append("Commander Notes:")
    for n in report.get("commander_notes", []):
        lines.append(f"  - {n}")
    return "\n".join(lines) + "\n"


def main() -> None:
    out = generate_nuclear_decision_card()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

