# src/spectral_owl_reasoning_templates.py
"""
Spectral Owl Reasoning Templates (LOCKED)
----------------------------------------
Purpose:
- Provide deterministic, commander-safe explanation sections for demo artifacts.
- Never crash (best effort).
- Return a stable dict[str, str] with consistent keys for UI rendering.

This is NOT an LLM. It's a bounded "explainability formatter" that converts
known artifact fields into a safe narrative.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


MAX_BULLETS_DEFAULT = 8
MAX_TEXT_CHARS_DEFAULT = 1200


def _safe_str(x: Any) -> str:
    try:
        if x is None:
            return ""
        s = str(x)
        return s
    except Exception:
        return ""


def _truncate(s: str, max_chars: int = MAX_TEXT_CHARS_DEFAULT) -> str:
    s = _safe_str(s)
    if not s:
        return ""
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3] + "..."


def pack_bullets(items: Optional[Iterable[Any]], max_items: int = MAX_BULLETS_DEFAULT) -> str:
    """
    Convert items into '- bullet' lines. Never crashes.
    """
    try:
        if not items:
            return "- None"
        out: List[str] = []
        for i, it in enumerate(list(items)[: max_items]):
            t = _safe_str(it).strip()
            if not t:
                continue
            out.append(f"- {t}")
        return "\n".join(out) if out else "- None"
    except Exception:
        return "- None"


def _get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    try:
        return data.get(key, default)
    except Exception:
        return default


def _stable_sections(
    *,
    headline: str,
    summary: str,
    what_we_know: List[str],
    what_we_do_not_know: List[str],
    recommended_posture: str,
    assumptions: List[str],
    uncertainties: List[str],
    operator_actions: List[str],
    confidence: str,
) -> Dict[str, str]:
    """
    Standard locked format: fixed keys, fixed ordering.
    """
    return {
        "headline": _truncate(headline, 180) or "Spectral Owl Explanation",
        "summary": _truncate(summary, 800) or "Bounded summary unavailable.",
        "confidence": _truncate(confidence, 120) or "UNKNOWN",
        "what_we_know": pack_bullets(what_we_know),
        "what_we_do_not_know": pack_bullets(what_we_do_not_know),
        "recommended_posture": _truncate(recommended_posture, 240) or "MAINTAIN_CURRENT_POSTURE",
        "assumptions": pack_bullets(assumptions),
        "uncertainties": pack_bullets(uncertainties),
        "operator_actions": pack_bullets(operator_actions),
        "notice": "Assessment is probabilistic and bounded; operator judgment applies.",
    }


def render_template(template_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Produce commander-safe explanation sections for a given template_id.
    Never raises.
    """
    data = data or {}
    try:
        tid = (_safe_str(template_id) or "").strip().lower()

        if tid in {"installation_threat_map", "radar", "threat_map"}:
            posture = _safe_str(_get(data, "posture", "DUTY_OFFICER_NOTIFY")) or "DUTY_OFFICER_NOTIFY"
            band = _safe_str(_get(data, "overall_risk_band", "UNKNOWN")) or "UNKNOWN"
            max_score = _safe_str(_get(data, "max_risk_score", ""))

            zones = _get(data, "zones", []) or []
            zone_lines: List[str] = []
            try:
                for z in zones:
                    if isinstance(z, dict):
                        name = _safe_str(z.get("zone") or z.get("name") or z.get("id") or "ZONE")
                        rs = _safe_str(z.get("risk_score", ""))
                        b = _safe_str(z.get("band", ""))
                        note = _safe_str(z.get("notes", ""))
                        zone_lines.append(f"{name}: risk_score={rs} band={b} notes={note}".strip())
                    else:
                        zone_lines.append(_safe_str(z))
            except Exception:
                zone_lines = []

            headline = "Installation Threat Map — Spectral Owl Explanation"
            summary = (
                f"Radar/Threat Map indicates posture '{posture}' with overall risk band '{band}'. "
                f"Max observed risk score: {max_score or 'Unavailable'}. "
                "This is a bounded posture recommendation derived from zone-level risk only."
            )
            what_we_know = [
                f"Recommended posture: {posture}",
                f"Overall risk band: {band}",
                f"Max risk score: {max_score or 'Unavailable'}",
                "Zone scoring is bounded to visible inputs; it is not attribution.",
            ]
            if zone_lines:
                what_we_know.append("Zone details (best effort):")
                what_we_know.extend(zone_lines[:6])

            what_we_do_not_know = [
                "Adversary intent cannot be inferred from this product alone.",
                "Causality/attribution require corroborating sensors and operator judgment.",
                "This is not a targeting product.",
            ]
            assumptions = [
                "Zone risk scores represent bounded confidence estimates.",
                "Missing sensors can distort zone scoring; validate outages.",
            ]
            uncertainties = [
                "Unobserved conditions outside the sensor picture may exist.",
                "Zone notes may be incomplete or synthetic during demo.",
            ]
            operator_actions = [
                "Check sensor outage predictor for degraded coverage.",
                "Cross-check anomalies with other products before escalation.",
                "If risk is elevated, notify duty officer per SOP.",
            ]
            confidence = "MEDIUM (bounded zone scoring; corroboration required)"
            return _stable_sections(
                headline=headline,
                summary=summary,
                what_we_know=what_we_know,
                what_we_do_not_know=what_we_do_not_know,
                recommended_posture=posture,
                assumptions=assumptions,
                uncertainties=uncertainties,
                operator_actions=operator_actions,
                confidence=confidence,
            )

        if tid in {"commander_brief", "brief"}:
            fusion_status = _safe_str(_get(data, "fusion_validation_status", "UNKNOWN")) or "UNKNOWN"
            degraded_status = _safe_str(_get(data, "degraded_validation_status", "UNKNOWN")) or "UNKNOWN"
            posture = _safe_str(_get(data, "recommended_posture", "MAINTAIN_CURRENT_POSTURE")) or "MAINTAIN_CURRENT_POSTURE"

            headline = "Commander Brief — Spectral Owl Explanation"
            summary = (
                "Commander Brief is a packaged, bounded snapshot using best-effort artifacts. "
                "It is designed to survive missing inputs and still provide a safe posture recommendation."
            )
            what_we_know = [
                f"Fusion validation status (best effort): {fusion_status}",
                f"Degraded validation status (best effort): {degraded_status}",
                f"Recommended posture: {posture}",
                "Brief statements are bounded and do not imply attribution.",
            ]
            what_we_do_not_know = [
                "Intent, causality, and attribution are not inferred from synthetic telemetry.",
                "Severity beyond bounded posture requires operator corroboration.",
            ]
            assumptions = [
                "Upstream artifacts reflect the latest run and were not tampered with.",
                "Operator will verify any escalation triggers.",
            ]
            uncertainties = [
                "Brief may contain synthetic/demo inputs.",
                "Missing artifacts can reduce confidence of posture.",
            ]
            operator_actions = [
                "Review prebrief trust annotations before external escalation.",
                "Confirm validation gates are current (timestamps).",
                "If any status is FAIL, verify root cause and rerun gates.",
            ]
            confidence = "MEDIUM-HIGH (bounded packaging; depends on upstream gate health)"
            return _stable_sections(
                headline=headline,
                summary=summary,
                what_we_know=what_we_know,
                what_we_do_not_know=what_we_do_not_know,
                recommended_posture=posture,
                assumptions=assumptions,
                uncertainties=uncertainties,
                operator_actions=operator_actions,
                confidence=confidence,
            )

        if tid in {"legal_snapshot", "legal", "shari"}:
            band = _safe_str(_get(data, "risk_band", "UNKNOWN")) or "UNKNOWN"
            score = _safe_str(_get(data, "risk_score", ""))
            posture = _safe_str(_get(data, "recommended_posture", "HOLD_ACTION_PENDING_REVIEW")) or "HOLD_ACTION_PENDING_REVIEW"
            flags = _get(data, "ambiguity_flags", []) or []

            headline = "Legal Case Snapshot — Spectral Owl Explanation"
            summary = (
                f"Legal Snapshot is a demo-safe, bounded risk triage view. "
                f"Risk band '{band}' (score={score or 'Unavailable'}). "
                "It recommends posture but does not replace attorney/operator judgment."
            )
            what_we_know = [
                f"Risk band: {band}",
                f"Risk score: {score or 'Unavailable'}",
                f"Recommended posture: {posture}",
                "Ambiguity flags reflect missing/unknown case fields.",
            ]
            if flags:
                what_we_know.append("Ambiguity flags (best effort):")
                for f in list(flags)[:8]:
                    what_we_know.append(_safe_str(f))

            what_we_do_not_know = [
                "This output does not determine liability or legal outcome.",
                "Missing party/jurisdiction data prevents confident escalation.",
            ]
            assumptions = [
                "Inputs may be synthetic for demo/training.",
                "Risk score is a heuristic, not a legal conclusion.",
            ]
            uncertainties = [
                "Underlying documents/evidence are not validated by this snapshot.",
                "Jurisdiction/party ambiguity can materially change posture.",
            ]
            operator_actions = [
                "Verify party identity and jurisdiction from the account file.",
                "Confirm evidentiary posture before any escalation.",
                "Treat as triage; attorney review required.",
            ]
            confidence = "MEDIUM (triage heuristic; attorney review required)"
            return _stable_sections(
                headline=headline,
                summary=summary,
                what_we_know=what_we_know,
                what_we_do_not_know=what_we_do_not_know,
                recommended_posture=posture,
                assumptions=assumptions,
                uncertainties=uncertainties,
                operator_actions=operator_actions,
                confidence=confidence,
            )

        # Fallback
        return _stable_sections(
            headline="Spectral Owl Explanation (Fallback)",
            summary="Template not recognized. Returning bounded fallback explanation.",
            what_we_know=["Template id was not recognized."],
            what_we_do_not_know=["No additional inference made."],
            recommended_posture="MAINTAIN_CURRENT_POSTURE",
            assumptions=["No assumptions applied."],
            uncertainties=["Unknown template."],
            operator_actions=["Select a supported explanation template."],
            confidence="LOW",
        )

    except Exception:
        # Absolute safety
        return {
            "headline": "Spectral Owl Explanation (Error-safe)",
            "summary": "Explanation generation failed safely. Operator judgment applies.",
            "confidence": "LOW",
            "what_we_know": "- Unavailable",
            "what_we_do_not_know": "- Unavailable",
            "recommended_posture": "MAINTAIN_CURRENT_POSTURE",
            "assumptions": "- Unavailable",
            "uncertainties": "- Unavailable",
            "operator_actions": "- Rerun generation",
            "notice": "Assessment is probabilistic and bounded; operator judgment applies.",
        }

