from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from demo_lock import is_demo_locked, demo_lock_banner, enforce_demo_lock


BRIEF_MODE = True
BRIEFS_DIR = Path("docs") / "briefs"

# Latest sources we try to include (best-effort)
SRC_TRAINING_CURVE = Path("src") / "docs" / "training" / "training_curve_latest.json"
SRC_TRAINING_FEEDBACK = Path("src") / "docs" / "training" / "training_feedback_latest.json"
SRC_FUSION_VALIDATION = Path("src") / "docs" / "validation" / "fusion_validation_report.json"
SRC_DEGRADED_VALIDATION = Path("src") / "docs" / "validation" / "degraded_fusion_validation_latest.json"
SRC_SIS_REPORT = Path("src") / "docs" / "system_integrity_report.txt"
SRC_SPS_BEHAVIOR_TXT = Path("src") / "docs" / "sps_behavior_report.txt"

# Extra Week-1/2 artifacts (best-effort)
SRC_WATCHBOARD = Path("docs") / "nuclear" / "prelaunch_watchboard_latest.json"
SRC_DECISION_CARD = Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json"
SRC_PREBRIEF = Path("docs") / "briefs" / "prebrief_trust_annotations_latest.json"

# Optional Owl reasoning trace (best-effort; doesn’t have to exist)
SRC_OWL_REASONING = Path("docs") / "briefs" / "spectral_owl_reasoning_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read_json(path: Path) -> Optional[dict]:
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
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, txt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8")


def render_brief_mode(sections: Dict[str, str]) -> str:
    """
    Enforced commander-safe brief format.
    Pure formatting only (no logic).
    """
    out = (
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
    )

    # Optional extra section (best-effort)
    if sections.get("spectral_owl_reasoning_trace"):
        out += "\n6. Spectral Owl reasoning (best effort):\n"
        out += sections["spectral_owl_reasoning_trace"].strip() + "\n"

    # Demo notice (if present)
    if sections.get("demo_notice"):
        out += "\n" + sections["demo_notice"].strip() + "\n"

    return out


def build_traceability(inputs: Dict[str, Any]) -> Dict[str, Any]:
    included = []
    missing = []
    for k, v in inputs.items():
        if isinstance(v, dict) and v.get("present") is True:
            included.append({"key": k, "path": v.get("path")})
        else:
            missing.append({"key": k, "path": (v.get("path") if isinstance(v, dict) else None)})
    return {"included": included, "missing": missing}


def _coerce_status(obj: Optional[dict]) -> Tuple[str, str]:
    """
    Normalize status/message fields across various artifact shapes.
    """
    if not isinstance(obj, dict):
        return ("UNKNOWN", "No report present.")
    if "status" in obj and isinstance(obj.get("status"), str):
        return (obj.get("status") or "UNKNOWN", str(obj.get("message") or ""))
    if "verdict" in obj and isinstance(obj.get("verdict"), str):
        return (obj.get("verdict") or "UNKNOWN", str(obj.get("message") or ""))
    # common pattern: {"ok": true}
    if "ok" in obj and isinstance(obj.get("ok"), bool):
        return ("PASS" if obj["ok"] else "FAIL", str(obj.get("details") or ""))
    return ("UNKNOWN", "Unrecognized report schema.")


def _summarize_inputs(inputs: Dict[str, Any]) -> str:
    bullets = []
    for k, v in inputs.items():
        if not isinstance(v, dict):
            continue
        present = v.get("present") is True
        if present:
            bullets.append(f"- {k.replace('_', ' ').title()} is present.")
    if not bullets:
        return "No source artifacts were detected. Brief is operating in degraded best-effort mode."
    return "\n".join(bullets)


def _best_effort_owl_trace() -> Optional[str]:
    owl = _safe_read_json(SRC_OWL_REASONING)
    if not isinstance(owl, dict):
        return None

    obs = owl.get("observations") or []
    ass = owl.get("assumptions") or []
    unc = owl.get("uncertainties") or []

    return (
        f"- Summary: {owl.get('summary', 'Unavailable.')}\n"
        f"- Observations: {', '.join(obs) if isinstance(obs, list) and obs else 'None'}\n"
        f"- Assumptions: {', '.join(ass) if isinstance(ass, list) and ass else 'None'}\n"
        f"- Uncertainties: {', '.join(unc) if isinstance(unc, list) and unc else 'None'}\n"
        f"- Analyst note: {owl.get('analyst_note', 'Operator judgment applies.')}"
    )


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
        "sis_report_txt": {"path": str(SRC_SIS_REPORT), "present": sis_txt is not None},
        "sps_behavior_txt": {"path": str(SRC_SPS_BEHAVIOR_TXT), "present": sps_txt is not None},
    }

    fv_status, fv_msg = _coerce_status(fusion_validation)
    dv_status, dv_msg = _coerce_status(degraded_validation)

    sections: Dict[str, str] = {
        "what_changed": _summarize_inputs(inputs),
        "why_it_matters": (
            "This briefing packages GLL’s current posture using bounded statements and best-effort artifacts. "
            "It is designed to survive missing inputs and still provide a safe, operator-readable snapshot."
        ),
        "what_we_know": (
            f"- Fusion validation verdict/status: {fv_status}\n"
            f"- Degraded validation verdict/status: {dv_status}"
        ),
        "what_we_do_not_know": (
            "- Intent, causality, and attribution are not inferred from synthetic telemetry.\n"
            "- Operator judgment is required before escalation beyond bounded posture."
        ),
        "recommended_posture": "DUTY_OFFICER_NOTIFY\nAssessment is probabilistic and bounded; operator judgment applies.",
    }

    owl_trace = _best_effort_owl_trace()
    if owl_trace:
        sections["spectral_owl_reasoning_trace"] = owl_trace

    # ============================
    # DEMO LOCK ENFORCEMENT
    # ============================
    if is_demo_locked():
        sections["demo_notice"] = demo_lock_banner()

    return sections, inputs


def write_commander_brief(sections: Dict[str, str], inputs: Dict[str, Any], context: str = "commander_brief_export") -> Dict[str, str]:
    """
    Writes:
      - docs/briefs/commander_brief_latest.{txt,json}
      - stamped versions
      - legacy src/docs/commander_brief.{txt,json}
    Must never crash.
    """
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    latest_txt = BRIEFS_DIR / "commander_brief_latest.txt"
    latest_json = BRIEFS_DIR / "commander_brief_latest.json"
    stamped_txt = BRIEFS_DIR / f"commander_brief_{_stamp()}.txt"
    stamped_json = BRIEFS_DIR / f"commander_brief_{_stamp()}.json"

    legacy_txt = Path("src") / "docs" / "commander_brief.txt"
    legacy_json = Path("src") / "docs" / "commander_brief.json"

    txt = render_brief_mode(sections)

    # OPTIONAL: ensure banner visible even if caller forgets sections["demo_notice"]
    if is_demo_locked():
        txt += "\n\n" + demo_lock_banner() + "\n"

    envelope: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "context": context,
        "brief_mode": bool(BRIEF_MODE),
        "sections": sections,
        "traceability": build_traceability(inputs),
    }

    if is_demo_locked():
        envelope.update(enforce_demo_lock(context))

    _write_txt(latest_txt, txt)
    _write_json(latest_json, envelope)
    _write_txt(stamped_txt, txt)
    _write_json(stamped_json, envelope)

    # legacy writes (backward compatibility)
    _write_txt(legacy_txt, txt)
    _write_json(legacy_json, envelope)

    return {
        "txt_latest": str(latest_txt),
        "json_latest": str(latest_json),
        "txt_stamped": str(stamped_txt),
        "json_stamped": str(stamped_json),
        "legacy_txt": str(legacy_txt),
        "legacy_json": str(legacy_json),
    }


def main() -> int:
    sections, inputs = build_commander_sections()
    paths = write_commander_brief(sections, inputs, context="commander_brief_exporter")
    print(json.dumps(paths, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

