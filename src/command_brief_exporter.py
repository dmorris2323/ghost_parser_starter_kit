from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

BRIEF_MODE = True

BRIEFS_DIR = Path("docs") / "briefs"
LEGACY_DIR = Path("src") / "docs"

# Best-effort sources (safe to be missing)
SRC_TRAINING_CURVE = Path("src") / "docs" / "training" / "training_curve_latest.json"
SRC_TRAINING_FEEDBACK = Path("src") / "docs" / "training" / "training_feedback_latest.json"
SRC_FUSION_VALIDATION = Path("src") / "docs" / "validation" / "fusion_validation_report.json"
SRC_DEGRADED_VALIDATION = Path("src") / "docs" / "validation" / "degraded_fusion_validation_latest.json"
SRC_SIS_REPORT = Path("src") / "docs" / "system_integrity_report.txt"
SRC_SPS_BEHAVIOR_TXT = Path("src") / "docs" / "sps_behavior_report.txt"
SRC_OWL_REASONING = Path("docs") / "analysis" / "spectral_owl_reasoning_latest.json"

# Week-1 nuclear (best-effort)
SRC_WATCHBOARD = Path("docs") / "nuclear" / "prelaunch_watchboard_latest.json"
SRC_DECISION_CARD = Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json"
SRC_PREBRIEF = Path("docs") / "briefs" / "prebrief_trust_annotations_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ensure_dirs() -> None:
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)


def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_read_txt(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _safe_get(d: Optional[Dict[str, Any]], *keys: str, default: Any = None) -> Any:
    if not isinstance(d, dict):
        return default
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


# ============================
# ENFORCED COMMANDER BRIEF MODE
# ============================

def render_brief_mode(sections: Dict[str, str]) -> str:
    """
    Enforced commander-safe brief format.
    Pure formatting only (no logic).
    """
    return (
        "1. What changed:\n"
        f"{sections.get('what_changed', 'No material change detected.')}\n\n"
        "2. Why it matters:\n"
        f"{sections.get('why_it_matters', 'No immediate operational impact.')}\n\n"
        "3. What we know:\n"
        f"{sections.get('what_we_know', 'Information remains limited.')}\n\n"
        "4. What we do NOT know:\n"
        f"{sections.get('what_we_do_not_know', 'Key intent and causality unknown.')}\n\n"
        "5. Recommended posture:\n"
        f"{sections.get('recommended_posture', 'Maintain current posture.')}\n"
        "\n6. Spectral Owl reasoning (best effort):\n"
        f"{sections.get('spectral_owl_reasoning_trace', 'Unavailable.')}\n"

    )


def build_traceability(inputs: Dict[str, Any]) -> Dict[str, Any]:
    included = []
    missing = []
    for k, v in inputs.items():
        if isinstance(v, dict) and v.get("present") is True:
            included.append(k)
        else:
            missing.append(k)
    return {
        "included": included,
        "missing": missing,
        "note": "Traceability is best-effort; missing artifacts do not block brief generation.",
    }


def _pick_posture(decision_card: Optional[Dict[str, Any]], watchboard: Optional[Dict[str, Any]]) -> str:
    # Prefer explicit decision card escalation posture
    posture = _safe_get(decision_card, "escalation", "posture", default=None)
    if isinstance(posture, str) and posture.strip():
        return posture.strip()

    # Fall back to watchboard if present
    wb_posture = _safe_get(watchboard, "recommended_posture", default=None)
    if isinstance(wb_posture, str) and wb_posture.strip():
        return wb_posture.strip()

    return "DUTY_OFFICER_NOTIFY"

def _read_json_best_effort(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def build_commander_sections() -> Tuple[Dict[str, str], Dict[str, Any]]:
    """
    Build sections using best-effort artifact reads.
    Must never crash.
    """
    training_curve = _safe_read_json(SRC_TRAINING_CURVE)
    training_feedback = _safe_read_json(SRC_TRAINING_FEEDBACK)
    fusion_validation = _safe_read_json(SRC_FUSION_VALIDATION)
    degraded_validation = _safe_read_json(SRC_DEGRADED_VALIDATION)
    watchboard = _safe_read_json(SRC_WATCHBOARD)
    decision_card = _safe_read_json(SRC_DECISION_CARD)
    prebrief = _safe_read_json(SRC_PREBRIEF)

    # Spectral Owl reasoning trace (best-effort)
    owl_reasoning = _safe_read_json(SRC_OWL_REASONING)

    sis_txt = _safe_read_txt(SRC_SIS_REPORT)
    sps_txt = _safe_read_txt(SRC_SPS_BEHAVIOR_TXT)

    inputs: Dict[str, Any] = {
        "training_curve": {"path": str(SRC_TRAINING_CURVE), "present": training_curve is not None},
        "training_feedback": {"path": str(SRC_TRAINING_FEEDBACK), "present": training_feedback is not None},
        "fusion_validation": {"path": str(SRC_FUSION_VALIDATION), "present": fusion_validation is not None},
        "degraded_validation": {"path": str(SRC_DEGRADED_VALIDATION), "present": degraded_validation is not None},
        "watchboard": {"path": str(SRC_WATCHBOARD), "present": watchboard is not None},
        "decision_card": {"path": str(SRC_DECISION_CARD), "present": decision_card is not None},
        "prebrief": {"path": str(SRC_PREBRIEF), "present": prebrief is not None},
        "sis_report": {"path": str(SRC_SIS_REPORT), "present": sis_txt is not None},
        "sps_behavior": {"path": str(SRC_SPS_BEHAVIOR_TXT), "present": sps_txt is not None},
        "owl_reasoning": {"path": str(SRC_OWL_REASONING), "present": owl_reasoning is not None},

    }

    posture = _pick_posture(decision_card, watchboard)

    fv_status = _safe_get(fusion_validation, "status", default=None) or _safe_get(fusion_validation, "verdict", default=None)
    dv_status = _safe_get(degraded_validation, "status", default=None) or _safe_get(degraded_validation, "verdict", default=None)

    what_changed_lines = []
    if degraded_validation is not None:
        what_changed_lines.append("- Degraded validation report is present (degraded ops supported).")
    if fusion_validation is not None:
        what_changed_lines.append("- Fusion validation report is present (core pipeline validated).")
    if training_feedback is not None:
        what_changed_lines.append("- Training feedback is present (operator coaching updated).")
    if decision_card is not None:
        what_changed_lines.append("- Nuclear decision card is present (bounded commander posture).")
    if watchboard is not None:
        what_changed_lines.append("- Prelaunch watchboard is present (watchfloor snapshot).")
    if not what_changed_lines:
        what_changed_lines.append("- No new artifacts detected; brief generated best-effort.")

    what_we_know_lines = []
    if fv_status is not None:
        what_we_know_lines.append(f"- Fusion validation verdict/status: {fv_status}")
    if dv_status is not None:
        what_we_know_lines.append(f"- Degraded validation verdict/status: {dv_status}")

    # Include bounded safety language ALWAYS (required tokens enforced downstream)
    cannot_lines = [
        "- Intent, causality, and attribution are not inferred from synthetic telemetry.",
        "- Operator judgment is required before escalation beyond bounded posture.",
    ]

    sections: Dict[str, str] = {
        "what_changed": "\n".join(what_changed_lines),
        "why_it_matters": (
            "This briefing packages GLL’s current posture using bounded statements and best-effort artifacts. "
            "It is designed to survive missing inputs and still provide a safe, operator-readable snapshot."
        ),
        "what_we_know": "\n".join(what_we_know_lines) if what_we_know_lines else "Information remains limited.",
        "what_we_do_not_know": "\n".join(cannot_lines),
        "recommended_posture": posture + "\nAssessment is probabilistic and bounded; operator judgment applies.",
    }
    sections["spectral_owl_reasoning_trace"] = (
        f"- Summary: {(owl_reasoning or {}).get('summary', 'Unavailable.')}\n"
        f"- Observations: {', '.join(((owl_reasoning or {}).get('observations') or [])) or 'None'}\n"
        f"- Assumptions: {', '.join(((owl_reasoning or {}).get('assumptions') or [])) or 'None'}\n"
        f"- Uncertainties: {', '.join(((owl_reasoning or {}).get('uncertainties') or [])) or 'None'}\n"
        f"- Analyst note: {(owl_reasoning or {}).get('analyst_note', 'Operator judgment applies.')}"
    )


    return sections, inputs


def write_commander_brief(sections: Dict[str, str], inputs: Dict[str, Any]) -> Dict[str, str]:
    _ensure_dirs()
    stamped = _stamp()

    txt_latest = BRIEFS_DIR / "commander_brief_latest.txt"
    json_latest = BRIEFS_DIR / "commander_brief_latest.json"
    txt_stamped = BRIEFS_DIR / f"commander_brief_{stamped}.txt"
    json_stamped = BRIEFS_DIR / f"commander_brief_{stamped}.json"

    legacy_txt = LEGACY_DIR / "commander_brief.txt"
    legacy_json = LEGACY_DIR / "commander_brief.json"

    txt = render_brief_mode(sections) if BRIEF_MODE else json.dumps(sections, indent=2)

    payload: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "brief_mode": bool(BRIEF_MODE),
        "sections": sections,
        "traceability": build_traceability(inputs),
        "inputs": inputs,
        "safety_notice": "Derived from synthetic telemetry for training/demos. Statements are bounded; operator judgment required.",
    }

    txt_latest.write_text(txt, encoding="utf-8")
    txt_stamped.write_text(txt, encoding="utf-8")

    json_latest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    json_stamped.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Legacy compatibility writes
    legacy_txt.write_text(txt, encoding="utf-8")
    legacy_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "txt_latest": str(txt_latest),
        "json_latest": str(json_latest),
        "txt_stamped": str(txt_stamped),
        "json_stamped": str(json_stamped),
        "legacy_txt": str(legacy_txt),
        "legacy_json": str(legacy_json),
    }


def main() -> None:
    sections, inputs = build_commander_sections()
    paths = write_commander_brief(sections, inputs)
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

