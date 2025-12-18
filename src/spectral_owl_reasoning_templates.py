# src/spectral_owl_reasoning_templates.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

TEMPLATE_VERSION = "10E.1"
TEMPLATE_LOCKED = True  # Module 10E: stable templates only

DEFAULT_ORDER: List[str] = [
    "headline",
    "summary",
    "confidence",
    "recommended_posture",
    "what_we_know",
    "what_we_do_not_know",
    "assumptions",
    "uncertainties",
    "operator_actions",
    "notice",
]

DEFAULT_NOTICE = "Assessment is probabilistic and bounded; operator judgment applies."


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pack_bullets(items: Any, *, max_items: int = 9) -> List[str]:
    """
    Normalize a list-ish input into a list[str], capped.
    Accepts:
      - list/tuple/set of anything
      - a single string
      - None
    """
    if items is None:
        return []
    if isinstance(items, str):
        s = items.strip()
        return [s] if s else []
    if isinstance(items, (list, tuple, set)):
        out: List[str] = []
        for x in list(items)[: max_items]:
            if x is None:
                continue
            sx = str(x).strip()
            if sx:
                out.append(sx)
        return out
    # fallback scalar
    sx = str(items).strip()
    return [sx] if sx else []


def _clip_text(s: str, limit: int = 900) -> str:
    s = (s or "").strip()
    if len(s) <= limit:
        return s
    return s[:limit].rstrip() + " …"


def render_template(
    *,
    target: str,
    headline: str,
    summary: str,
    confidence: str,
    recommended_posture: str,
    what_we_know: Any = None,
    what_we_do_not_know: Any = None,
    assumptions: Any = None,
    uncertainties: Any = None,
    operator_actions: Any = None,
    notice: Optional[str] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Contract-stable “reasoning template” output for the Owl Drawer.
    Returns keys the GUI expects, in a consistent format.

    IMPORTANT: This is NOT “ChatGPT”.
    It is a bounded, deterministic template packer that transforms
    system artifacts into a commander-safe explanation structure.
    """
    payload: Dict[str, Any] = {
        "template_version": TEMPLATE_VERSION,
        "template_locked": TEMPLATE_LOCKED,
        "generated_at_utc": utc_now_iso(),
        "target": (target or "").strip(),
        "headline": _clip_text(headline, 220),
        "summary": _clip_text(summary, 900),
        "confidence": _clip_text(confidence, 140),
        "recommended_posture": _clip_text(recommended_posture, 120),
        "what_we_know": pack_bullets(what_we_know),
        "what_we_do_not_know": pack_bullets(what_we_do_not_know),
        "assumptions": pack_bullets(assumptions),
        "uncertainties": pack_bullets(uncertainties),
        "operator_actions": pack_bullets(operator_actions),
        "notice": (notice or DEFAULT_NOTICE).strip(),
    }
    if extra:
        # Extra fields are allowed, but do not replace contract keys
        payload["extra"] = dict(extra)
    return payload

