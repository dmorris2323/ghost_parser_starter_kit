"""
escalation_ladder.py

Day 73 — Module 1: Nuclear/AFTAC Escalation Ladder Hardening

Purpose
- Provide a conservative, commander-trust escalation ladder that behaves
  correctly under ambiguity, partial data, and sensor disagreement.

Key properties
- Monotonic escalation (no jumping to high levels without evidence)
- Minimum evidence gates per rung
- Explicit blocking factors explaining why escalation stopped
- Safe defaults (missing data lowers confidence / blocks escalation)

This module is SAFE: it uses abstracted indicator scores, not real telemetry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Ladder definition
# -----------------------------

@dataclass(frozen=True)
class LadderRung:
    level: int
    label: str
    min_total_evidence: float
    min_domains: int
    min_reliability_avg: float
    allow_single_domain: bool = False


DEFAULT_LADDER: List[LadderRung] = [
    LadderRung(level=0, label="MONITOR",  min_total_evidence=0.0,  min_domains=0, min_reliability_avg=0.0),
    LadderRung(level=1, label="WATCH",    min_total_evidence=25.0, min_domains=1, min_reliability_avg=50.0, allow_single_domain=True),
    LadderRung(level=2, label="ELEVATED", min_total_evidence=45.0, min_domains=2, min_reliability_avg=60.0),
    LadderRung(level=3, label="SERIOUS",  min_total_evidence=65.0, min_domains=2, min_reliability_avg=70.0),
    LadderRung(level=4, label="CRITICAL", min_total_evidence=80.0, min_domains=3, min_reliability_avg=75.0),
]


# -----------------------------
# Public API
# -----------------------------

def assess_escalation(
    *,
    indicators: Dict[str, Any],
    ladder: Optional[List[LadderRung]] = None,
    prior_level: int = 0,
) -> Dict[str, Any]:
    """
    Compute an escalation level conservatively based on abstract indicators.

    indicators: dict keyed by domain name (e.g., "EMS", "CYBER", "COMMS", "SEISMIC", "RADIATION", "OPTICAL")
      Each value may be:
        - number score 0-100
        - dict with:
            score: 0-100
            reliability: 0-100
            status: optional str
            notes: optional str

    prior_level:
      - used to enforce monotonic escalation (never drop below prior in this call)
      - used to prevent sudden multi-step escalation without evidence

    Returns a dict safe to embed in decision cards / briefs:
      {
        "escalation_level": int,
        "escalation_label": str,
        "blocking_factors": [..],
        "evidence": { ... },
        "confidence_floor_applied": bool
      }
    """
    ladder = ladder or DEFAULT_LADDER

    # Normalize indicator inputs
    norm = _normalize_indicators(indicators)
    evidence = _compute_evidence(norm)

    # Determine highest rung we can justify
    chosen = ladder[0]
    blocking: List[str] = []
    confidence_floor_applied = False

    # We only allow moving up by at most +1 rung per evaluation unless
    # there is strong multi-domain evidence (a "step-up proof").
    step_up_proof = _step_up_proof(evidence)

    for rung in ladder[1:]:
        ok, reasons = _meets_rung(rung, evidence)
        if not ok:
            # stop at last chosen rung
            blocking = reasons
            break

        # enforce monotonicity and anti-jump
        if rung.level > prior_level + 1 and not step_up_proof:
            blocking = [
                f"Anti-jump rule: prior_level={prior_level} blocks escalation to {rung.label} without multi-domain proof.",
                "Add corroboration across domains or improve reliability before escalating multiple rungs at once.",
            ]
            confidence_floor_applied = True
            break

        chosen = rung
        blocking = []

    # Never drop below prior_level in this single assessment (monotonic)
    if chosen.level < prior_level:
        chosen = _get_rung_by_level(ladder, prior_level) or chosen
        confidence_floor_applied = True

    return {
        "escalation_level": chosen.level,
        "escalation_label": chosen.label,
        "blocking_factors": blocking,
        "evidence": evidence,
        "confidence_floor_applied": bool(confidence_floor_applied),
    }


# -----------------------------
# Internal helpers
# -----------------------------

def _normalize_indicators(indicators: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    norm: Dict[str, Dict[str, Any]] = {}
    for domain, raw in (indicators or {}).items():
        d = str(domain).strip().upper()

        score = 0.0
        reliability = 0.0
        status = "UNKNOWN"
        notes = ""

        if isinstance(raw, (int, float)):
            score = float(raw)
            reliability = 70.0  # conservative default if only a score is given
            status = "OK"
        elif isinstance(raw, dict):
            score = float(raw.get("score", raw.get("value", 0.0)) or 0.0)
            reliability = float(raw.get("reliability", 0.0) or 0.0)
            status = str(raw.get("status", "OK"))
            notes = str(raw.get("notes", "")) if raw.get("notes") is not None else ""
        else:
            # unknown types -> treat as missing
            score = 0.0
            reliability = 0.0
            status = "MISSING"

        # clamp
        score = max(0.0, min(100.0, score))
        reliability = max(0.0, min(100.0, reliability))

        norm[d] = {
            "score": score,
            "reliability": reliability,
            "status": status,
            "notes": notes,
        }
    return norm


def _compute_evidence(norm: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evidence model (conservative):
    - Domain evidence = score * (reliability/100)
    - Total evidence = sum(domain evidence) / max(1, number_of_domains_present) * 1.2
      (scaled modestly; still bounded)
    - Domain count = domains with domain_evidence >= 15
    - Reliability avg = mean reliability of present domains
    - Disagreement penalty: if top score high but others near zero, reduce total evidence slightly
    """
    present = list(norm.keys())
    if not present:
        return {
            "domains_present": 0,
            "domains_contributing": 0,
            "reliability_avg": 0.0,
            "domain_evidence": {},
            "total_evidence": 0.0,
            "disagreement_penalty": 0.0,
            "notes": ["No indicators provided."],
        }

    domain_evidence: Dict[str, float] = {}
    reliabilities: List[float] = []
    scores: List[float] = []

    for d, v in norm.items():
        s = float(v.get("score", 0.0) or 0.0)
        r = float(v.get("reliability", 0.0) or 0.0)
        scores.append(s)
        reliabilities.append(r)
        domain_evidence[d] = round(s * (r / 100.0), 2)

    reliability_avg = sum(reliabilities) / max(1, len(reliabilities))
    raw_total = sum(domain_evidence.values()) / max(1, len(present)) * 1.2

    # disagreement penalty
    top = max(scores) if scores else 0.0
    second = sorted(scores, reverse=True)[1] if len(scores) >= 2 else 0.0
    # If one domain is screaming and the rest are dead, penalize slightly.
    penalty = 0.0
    if top >= 70.0 and second <= 20.0:
        penalty = min(10.0, (top - second) / 10.0)  # bounded

    total_evidence = max(0.0, min(100.0, raw_total - penalty))
    domains_contributing = sum(1 for v in domain_evidence.values() if v >= 15.0)

    notes: List[str] = []
    if penalty > 0:
        notes.append("Cross-domain disagreement detected; applying conservative penalty.")

    return {
        "domains_present": len(present),
        "domains_contributing": int(domains_contributing),
        "reliability_avg": round(reliability_avg, 2),
        "domain_evidence": domain_evidence,
        "total_evidence": round(total_evidence, 2),
        "disagreement_penalty": round(penalty, 2),
        "notes": notes,
    }


def _meets_rung(rung: LadderRung, evidence: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []

    total = float(evidence.get("total_evidence", 0.0) or 0.0)
    contributing = int(evidence.get("domains_contributing", 0) or 0)
    rel_avg = float(evidence.get("reliability_avg", 0.0) or 0.0)

    if total < rung.min_total_evidence:
        reasons.append(
            f"Insufficient total evidence: {total:.2f} < {rung.min_total_evidence:.2f} required for {rung.label}."
        )

    # domain rule
    if rung.allow_single_domain:
        if contributing < 1:
            reasons.append(
                f"No contributing domain evidence: domains_contributing={contributing} required >= 1 for {rung.label}."
            )
    else:
        if contributing < rung.min_domains:
            reasons.append(
                f"Insufficient cross-domain corroboration: domains_contributing={contributing} < {rung.min_domains} for {rung.label}."
            )

    if rel_avg < rung.min_reliability_avg:
        reasons.append(
            f"Reliability too low: reliability_avg={rel_avg:.2f} < {rung.min_reliability_avg:.2f} for {rung.label}."
        )

    return (len(reasons) == 0), reasons


def _step_up_proof(evidence: Dict[str, Any]) -> bool:
    """
    Proof that allows multi-rung step-ups (rare):
    - at least 3 contributing domains
    - total evidence >= 85
    - reliability avg >= 80
    """
    contributing = int(evidence.get("domains_contributing", 0) or 0)
    total = float(evidence.get("total_evidence", 0.0) or 0.0)
    rel_avg = float(evidence.get("reliability_avg", 0.0) or 0.0)
    return bool(contributing >= 3 and total >= 85.0 and rel_avg >= 80.0)


def _get_rung_by_level(ladder: List[LadderRung], level: int) -> Optional[LadderRung]:
    for r in ladder:
        if r.level == level:
            return r
    return None


# -----------------------------
# CLI smoke test (safe)
# -----------------------------

def _demo() -> None:
    cases = [
        ("Empty", {}, 0),
        ("Single strong domain", {"CYBER": {"score": 85, "reliability": 75}}, 0),
        ("Cross-domain moderate", {"CYBER": {"score": 60, "reliability": 80}, "EMS": {"score": 55, "reliability": 75}}, 0),
        ("Disagreement", {"CYBER": {"score": 90, "reliability": 80}, "EMS": {"score": 10, "reliability": 80}, "COMMS": {"score": 5, "reliability": 70}}, 0),
        ("Prior level monotonic", {"CYBER": {"score": 10, "reliability": 70}}, 2),
    ]
    for name, indicators, prior in cases:
        out = assess_escalation(indicators=indicators, prior_level=prior)
        print("\n===", name, "===")
        print(out)


if __name__ == "__main__":
    _demo()

