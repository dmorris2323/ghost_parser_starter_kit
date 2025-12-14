"""
decision_card_confidence.py

Day 73 — Module 2: Decision-card confidence under ambiguity

Goal:
- Turn messy / incomplete / conflicting inputs into a commander-safe confidence score
- Explain WHY confidence is what it is (ambiguity factors)
- Produce trust annotations that can be stamped into the decision card

SAFE: This operates on abstracted indicators / reports (not real telemetry).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class ConfidenceResult:
    confidence_score: float  # 0-100
    label: str               # "LOW" / "MEDIUM" / "HIGH"
    ambiguity_flags: List[str]
    trust_annotations: List[str]


def compute_confidence_under_ambiguity(
    *,
    indicators: Dict[str, Any],
    fusion_trust: float | None = None,
    operator_safety: str | None = None,
    gate_status: str | None = None,
    escalation_level: int | None = None,
    escalation_label: str | None = None,
) -> Dict[str, Any]:
    """
    Returns a dict safe to embed in decision cards:
      {
        "confidence_score": 0-100,
        "confidence_label": "LOW|MEDIUM|HIGH",
        "ambiguity_flags": [...],
        "trust_annotations": [...]
      }

    Scoring philosophy (conservative):
    - Start from fusion_trust if provided (or infer from indicators)
    - Penalize missing domains, low reliability, and cross-domain disagreement
    - If gates are not GREEN, cap confidence hard
    - If escalation is high but evidence is thin, penalize
    """
    flags: List[str] = []
    notes: List[str] = []

    # Normalize domain presence & reliability
    norm = _normalize_indicators(indicators)
    domains_present = len(norm)

    if domains_present == 0:
        flags.append("NO_INDICATORS")
        base = 0.0
    else:
        # base trust
        base = float(fusion_trust) if fusion_trust is not None else _infer_base_from_indicators(norm)

    # Reliability avg
    rels = [float(v.get("reliability", 0.0) or 0.0) for v in norm.values()]
    rel_avg = sum(rels) / max(1, len(rels))

    if rel_avg < 60:
        flags.append("LOW_RELIABILITY_AVG")
    if domains_present < 2:
        flags.append("LOW_DOMAIN_COVERAGE")

    # Disagreement check
    scores = [float(v.get("score", 0.0) or 0.0) for v in norm.values()]
    if scores:
        top = max(scores)
        second = sorted(scores, reverse=True)[1] if len(scores) >= 2 else 0.0
        if top >= 70 and second <= 20:
            flags.append("CROSS_DOMAIN_DISAGREEMENT")

    # Gate enforcement (hard cap)
    if gate_status and str(gate_status).upper() != "GREEN":
        flags.append(f"GATE_NOT_GREEN:{gate_status}")
        notes.append("Gates not GREEN: confidence capped for commander safety.")
        base = min(base, 55.0)

    # Operator safety layer influence
    if operator_safety:
        osl = str(operator_safety).upper()
        if osl in {"RED"}:
            flags.append("OSL_RED")
            base = min(base, 45.0)
        elif osl in {"AMBER", "YELLOW"}:
            flags.append("OSL_AMBER")
            base = min(base, 65.0)

    # Escalation sanity: high escalation needs high confidence
    if escalation_level is not None and escalation_label is not None:
        if escalation_level >= 3 and base < 70:
            flags.append("HIGH_ESCALATION_LOW_CONFIDENCE_TENSION")
            notes.append("Escalation indicates seriousness, but confidence is not yet high—seek corroboration before decisive action.")

    # Apply penalties (bounded)
    penalty = 0.0
    if "LOW_DOMAIN_COVERAGE" in flags:
        penalty += 8.0
    if "LOW_RELIABILITY_AVG" in flags:
        penalty += 10.0
    if "CROSS_DOMAIN_DISAGREEMENT" in flags:
        penalty += 8.0
    if "NO_INDICATORS" in flags:
        penalty += 30.0

    score = max(0.0, min(100.0, base - penalty))

    label = "LOW"
    if score >= 75:
        label = "HIGH"
    elif score >= 55:
        label = "MEDIUM"

    # Trust annotations (what the commander needs)
    notes.extend(_build_trust_annotations(
        score=score,
        label=label,
        flags=flags,
        rel_avg=rel_avg,
        domains_present=domains_present,
        escalation_level=escalation_level,
        escalation_label=escalation_label,
    ))

    return {
        "confidence_score": round(score, 1),
        "confidence_label": label,
        "ambiguity_flags": flags,
        "trust_annotations": notes,
    }


def _normalize_indicators(indicators: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    norm: Dict[str, Dict[str, Any]] = {}
    for domain, raw in (indicators or {}).items():
        d = str(domain).strip().upper()
        score = 0.0
        reliability = 0.0
        if isinstance(raw, (int, float)):
            score = float(raw)
            reliability = 70.0
        elif isinstance(raw, dict):
            score = float(raw.get("score", raw.get("value", 0.0)) or 0.0)
            reliability = float(raw.get("reliability", 0.0) or 0.0)
        score = max(0.0, min(100.0, score))
        reliability = max(0.0, min(100.0, reliability))
        norm[d] = {"score": score, "reliability": reliability}
    return norm


def _infer_base_from_indicators(norm: Dict[str, Dict[str, Any]]) -> float:
    # Conservative proxy: avg(score * reliability) scaled
    vals: List[float] = []
    for v in norm.values():
        s = float(v.get("score", 0.0) or 0.0)
        r = float(v.get("reliability", 0.0) or 0.0) / 100.0
        vals.append(s * r)
    if not vals:
        return 0.0
    avg = sum(vals) / max(1, len(vals))
    # scale into a trust-like range
    return max(0.0, min(100.0, avg))


def _build_trust_annotations(
    *,
    score: float,
    label: str,
    flags: List[str],
    rel_avg: float,
    domains_present: int,
    escalation_level: int | None,
    escalation_label: str | None,
) -> List[str]:
    out: List[str] = []
    out.append(f"Confidence: {label} ({score:.1f}/100).")
    out.append(f"Domains present: {domains_present}. Reliability avg: {rel_avg:.1f}.")

    if escalation_level is not None and escalation_label is not None:
        out.append(f"Escalation rung: {escalation_label} (L{escalation_level}).")

    if not flags:
        out.append("Ambiguity: none detected. Conditions are clean for decision support.")
        return out

    # Translate flags into commander language
    if any(f.startswith("GATE_NOT_GREEN") for f in flags):
        out.append("Integrity gates are not GREEN → treat outputs as advisory only until corrected.")
    if "LOW_DOMAIN_COVERAGE" in flags:
        out.append("Limited corroboration across domains → request additional sources before escalation.")
    if "LOW_RELIABILITY_AVG" in flags:
        out.append("Sensor/telemetry reliability is degraded → widen uncertainty bounds.")
    if "CROSS_DOMAIN_DISAGREEMENT" in flags:
        out.append("Cross-domain disagreement detected → prioritize reconciliation and re-run validation.")
    if "HIGH_ESCALATION_LOW_CONFIDENCE_TENSION" in flags:
        out.append("High severity indicators without matching confidence → hold escalation until corroborated.")

    return out

