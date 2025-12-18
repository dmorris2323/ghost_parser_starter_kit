# src/spectral_owl_reasoning_templates.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


def pack_bullets(items: List[str], prefix: str = "- ") -> str:
    items = [i.strip() for i in (items or []) if i and i.strip()]
    if not items:
        return "None."
    return "\n".join(f"{prefix}{i}" for i in items)


def render_template(
    *,
    headline: str,
    summary: str,
    confidence: str,
    recommended_posture: str,
    what_we_know: List[str],
    what_we_do_not_know: List[str],
    assumptions: List[str],
    uncertainties: List[str],
    operator_actions: List[str],
    notice: str,
) -> Dict[str, str]:
    """
    Returns a stable dict of sections for UI rendering.
    This is intentionally bounded / commander-safe, not an LLM.
    """
    return {
        "headline": headline.strip(),
        "summary": summary.strip(),
        "confidence": confidence.strip(),
        "recommended_posture": recommended_posture.strip(),
        "what_we_know": pack_bullets(what_we_know),
        "what_we_do_not_know": pack_bullets(what_we_do_not_know),
        "assumptions": pack_bullets(assumptions),
        "uncertainties": pack_bullets(uncertainties),
        "operator_actions": pack_bullets(operator_actions),
        "notice": notice.strip(),
    }

