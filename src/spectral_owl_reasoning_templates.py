from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, Optional


# ============================
# Template Lock (single source of truth)
# ============================
TEMPLATE_KEYS = [
    "Summary",
    "What changed",
    "Why it matters",
    "What we know",
    "What we do NOT know",
    "Recommended posture",
    "Confidence (bounded)",
    "Operator next action",
    "Guardrails",
    "Demo notice",
]


def _s(x: Any, default: str = "") -> str:
    try:
        if x is None:
            return default
        if isinstance(x, str):
            return x.strip()
        return str(x).strip()
    except Exception:
        return default


def _cap(s: str, n: int = 1200) -> str:
    s = _s(s, "")
    if len(s) <= n:
        return s
    return s[:n] + " …[truncated]"


def _join_lines(lines) -> str:
    out = []
    for l in lines or []:
        t = _s(l, "")
        if t:
            out.append(t)
    return "\n- " + "\n- ".join(out) if out else "None."


def _default_guardrails() -> str:
    return (
        "• No intent/attribution inference from single-source artifacts.\n"
        "• Outputs are best-effort; missing inputs do not crash the system.\n"
        "• Assessment is probabilistic and bounded; operator judgment applies."
    )


def _default_demo_notice(demo_locked: bool, banner: str) -> str:
    if demo_locked and banner:
        return banner
    return "None."


def render_template(
    *,
    domain: str,
    summary: str,
    what_changed: str,
    why_it_matters: str,
    what_we_know: str,
    what_we_do_not_know: str,
    recommended_posture: str,
    confidence_bounded: str,
    operator_next_action: str,
    guardrails: Optional[str] = None,
    demo_locked: bool = False,
    demo_banner: str = "",
) -> Dict[str, str]:
    """
    Returns an ORDERED dict with locked keys, commander-safe language, and bounded claims.
    Must never throw.
    """
    try:
        g = _s(guardrails, _default_guardrails())
        d = _default_demo_notice(demo_locked, _s(demo_banner, ""))

        payload = OrderedDict()
        payload["Summary"] = _cap(summary or f"{domain}: bounded explanation generated from available artifacts.")
        payload["What changed"] = _cap(what_changed or "No material change detected from available artifacts.")
        payload["Why it matters"] = _cap(why_it_matters or "Operational relevance unclear; maintain bounded posture.")
        payload["What we know"] = _cap(what_we_know or "Information remains limited.")
        payload["What we do NOT know"] = _cap(what_we_do_not_know or "Intent, causality, and attribution unknown.")
        payload["Recommended posture"] = _cap(recommended_posture or "Maintain current posture.")
        payload["Confidence (bounded)"] = _cap(confidence_bounded or "LOW to MODERATE — bounded by artifact completeness.")
        payload["Operator next action"] = _cap(operator_next_action or "Review source artifacts; corroborate before escalation.")
        payload["Guardrails"] = _cap(g)
        payload["Demo notice"] = _cap(d)

        # Ensure all keys exist even if upstream changes
        for k in TEMPLATE_KEYS:
            payload.setdefault(k, "Unavailable.")
        return dict(payload)
    except Exception:
        return {k: "Unavailable." for k in TEMPLATE_KEYS}


def pack_bullets(title: str, bullets) -> str:
    """
    Helper for explainers: stable bullet formatting.
    """
    try:
        return f"{_s(title)}:{_join_lines(bullets)}"
    except Exception:
        return f"{_s(title)}: None."

