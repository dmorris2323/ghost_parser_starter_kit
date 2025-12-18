from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.spectral_owl_reasoning_templates import render_template, pack_bullets

# Optional demo lock integration (never required)
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:

    def is_demo_locked() -> bool:
        return False

    def demo_lock_banner() -> str:
        return ""


BASE = Path(".")
DOCS = BASE / "docs"
BRIEFS = DOCS / "briefs"
BASEDEF = DOCS / "base_defense"


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def _read_text_best_effort(p: Path, max_chars: int = 120_000) -> str:
    try:
        if not p.exists():
            return ""
        t = p.read_text(encoding="utf-8", errors="ignore")
        return t if len(t) <= max_chars else (t[:max_chars] + "\n\n[TRUNCATED]")
    except Exception:
        return ""


def _s(x: Any, default: str = "") -> str:
    try:
        if x is None:
            return default
        if isinstance(x, str):
            return x.strip()
        return str(x).strip()
    except Exception:
        return default


# ==========================================================
# EXPLAINERS (LOCKED TEMPLATE OUTPUT)
# ==========================================================
def explain_installation_threat_map() -> Dict[str, str]:
    """
    Reads docs/base_defense/installation_threat_map_latest.(json/txt)
    Returns locked template dict. Never crashes.
    """
    j = _read_json_best_effort(BASEDEF / "installation_threat_map_latest.json") or {}
    posture = _s(j.get("posture"), "UNKNOWN")
    band = _s(j.get("overall_risk_band"), _s(j.get("overall_band"), "UNKNOWN"))
    max_score = _s(j.get("max_risk_score"), "N/A")

    zones = j.get("zones") or []
    zone_lines = []
    try:
        for z in zones:
            name = _s(z.get("name") or z.get("zone") or "ZONE")
            rs = _s(z.get("risk_score"), "N/A")
            b = _s(z.get("band"), "UNKNOWN")
            notes = _s(z.get("notes"), "")
            zone_lines.append(f"{name}: risk_score={rs} band={b}" + (f" notes={notes}" if notes else ""))
    except Exception:
        zone_lines = []

    summary = f"Installation Threat Map indicates bounded posture '{posture}' with overall risk band '{band}'."
    what_changed = pack_bullets(
        "Observed zone posture",
        [
            f"posture={posture}",
            f"overall_risk_band={band}",
            f"max_risk_score={max_score}",
        ],
    )
    why_it_matters = (
        "This product provides a bounded installation-level risk snapshot for duty officer awareness. "
        "It does not claim adversary intent or attribution."
    )
    what_we_know = pack_bullets("Zones (bounded)", zone_lines[:12] if zone_lines else ["No zone breakdown present."])
    what_we_do_not_know = (
        "Adversary intent, causality, and attribution cannot be inferred from this map alone. "
        "Corroboration across sensors and operator judgment are required."
    )
    recommended_posture = posture if posture != "UNKNOWN" else "DUTY_OFFICER_NOTIFY (bounded default if elevated signals suspected)"
    confidence = "MODERATE — depends on sensor completeness and freshness of zone inputs."
    next_action = "Open the installation threat map TXT/JSON and confirm zone drivers; verify sensor health before escalation."

    return render_template(
        domain="Installation Threat Map",
        summary=summary,
        what_changed=what_changed,
        why_it_matters=why_it_matters,
        what_we_know=what_we_know,
        what_we_do_not_know=what_we_do_not_know,
        recommended_posture=recommended_posture,
        confidence_bounded=confidence,
        operator_next_action=next_action,
        demo_locked=is_demo_locked(),
        demo_banner=demo_lock_banner(),
    )


def explain_commander_brief() -> Dict[str, str]:
    """
    Reads docs/briefs/commander_brief_latest.(json/txt)
    Returns locked template dict. Never crashes.
    """
    txt = _read_text_best_effort(BRIEFS / "commander_brief_latest.txt")
    j = _read_json_best_effort(BRIEFS / "commander_brief_latest.json") or {}

    posture = _s(j.get("recommended_posture") or j.get("posture"), "UNKNOWN")
    what_changed = _s(j.get("what_changed"), "")
    why_it_matters = _s(j.get("why_it_matters"), "")
    what_we_know = _s(j.get("what_we_know"), "")
    what_we_do_not_know = _s(j.get("what_we_do_not_know"), "")

    if not any([what_changed, why_it_matters, what_we_know, what_we_do_not_know]) and txt:
        head = "\n".join(txt.splitlines()[:40])
        what_changed = head

    summary = "Commander Brief explanation synthesized from the latest exported commander brief artifact."
    if posture != "UNKNOWN":
        summary = f"Commander Brief indicates posture '{posture}' using bounded statements."

    wc = what_changed or "No material change detected from available brief sections."
    wim = why_it_matters or "Operational impact bounded; maintain guardrails."
    wwk = what_we_know or "Information remains limited."
    wwdk = what_we_do_not_know or "Intent, causality, and attribution remain unknown."

    recommended_posture = posture if posture != "UNKNOWN" else "Maintain current posture."
    confidence = "MODERATE — depends on the completeness of upstream validation artifacts feeding the brief."
    next_action = "Review commander brief sections; corroborate with validation reports before any escalation."

    return render_template(
        domain="Commander Brief",
        summary=summary,
        what_changed=wc,
        why_it_matters=wim,
        what_we_know=wwk,
        what_we_do_not_know=wwdk,
        recommended_posture=recommended_posture,
        confidence_bounded=confidence,
        operator_next_action=next_action,
        demo_locked=is_demo_locked(),
        demo_banner=demo_lock_banner(),
    )


def explain_legal_snapshot() -> Dict[str, str]:
    """
    Reads docs/briefs/legal_case_snapshot_latest.(json/txt)
    Returns locked template dict. Never crashes.
    """
    j = _read_json_best_effort(BRIEFS / "legal_case_snapshot_latest.json") or {}
    txt = _read_text_best_effort(BRIEFS / "legal_case_snapshot_latest.txt")

    risk_band = _s(j.get("risk_band"), "UNKNOWN")
    posture = _s(j.get("recommended_posture") or j.get("posture"), "UNKNOWN")
    flags = j.get("ambiguity_flags") or []

    summary = f"Legal snapshot indicates risk band '{risk_band}' with bounded recommended posture '{posture}'."
    what_changed = pack_bullets(
        "Snapshot fields",
        [
            f"risk_band={risk_band}",
            f"posture={posture}",
            f"ambiguity_flags_count={len(flags) if isinstance(flags, list) else 'N/A'}",
        ],
    )
    why_it_matters = (
        "This is a demo-safe, bounded legal triage snapshot. "
        "It does not replace attorney judgment or case file review."
    )
    what_we_know = pack_bullets(
        "Bounded facts",
        [
            f"risk_band={risk_band}",
            f"recommended_posture={posture}",
            f"ambiguity_flags={', '.join([_s(x) for x in flags]) if isinstance(flags, list) and flags else 'None'}",
        ],
    )
    what_we_do_not_know = (
        "Jurisdiction-specific requirements, evidentiary posture, and party identity may be unknown or incomplete. "
        "Operator/attorney review required before action."
    )
    recommended_posture = posture if posture != "UNKNOWN" else "HOLD_ACTION_PENDING_REVIEW"
    confidence = "LOW to MODERATE — bounded by missing case facts and intentionally conservative defaults."
    next_action = "Open the legal snapshot TXT; confirm party/jurisdiction and evidence posture before escalation."

    _ = txt  # reserved for future use

    return render_template(
        domain="Legal Case Snapshot",
        summary=summary,
        what_changed=what_changed,
        why_it_matters=why_it_matters,
        what_we_know=what_we_know,
        what_we_do_not_know=what_we_do_not_know,
        recommended_posture=recommended_posture,
        confidence_bounded=confidence,
        operator_next_action=next_action,
        demo_locked=is_demo_locked(),
        demo_banner=demo_lock_banner(),
    )

