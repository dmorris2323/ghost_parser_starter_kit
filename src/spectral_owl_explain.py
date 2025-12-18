# src/spectral_owl_explain.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from spectral_owl_reasoning_templates import render_template

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIEFS_DIR = REPO_ROOT / "docs" / "briefs"
BASEDEF_DIR = REPO_ROOT / "docs" / "base_defense"


def _read_text_best_effort(p: Path) -> str:
    try:
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_json_best_effort(p: Path) -> Dict[str, Any]:
    try:
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def explain_installation_threat_map() -> Dict[str, str]:
    txt = ""
    for cand in [
        BASEDEF_DIR / "installation_threat_map_latest.txt",
        BRIEFS_DIR / "installation_threat_map_latest.txt",
    ]:
        txt = _read_text_best_effort(cand).strip()
        if txt:
            break

    return render_template(
        headline="Installation Threat Map — Bounded Zone Posture",
        summary=(
            "This product summarizes installation risk by zone using bounded scoring. "
            "It is not attribution or intent detection."
        ),
        confidence="Medium (bounded; depends on sensor coverage + freshness).",
        recommended_posture="DUTY_OFFICER_NOTIFY if any zone reaches ELEVATED+ (bounded policy).",
        what_we_know=[
            "Zone risk bands are derived from bounded scoring, not narrative attribution.",
            "Max zone score drives overall band and posture recommendation.",
            "Outputs are safe even when inputs are incomplete (bounded defaults).",
        ],
        what_we_do_not_know=[
            "We cannot infer adversary intent from this map alone.",
            "We cannot attribute causality without corroborating sensors and operator judgment.",
            "We cannot confirm persistence vs. transient anomalies without time-series context.",
        ],
        assumptions=[
            "The latest artifact is the most relevant snapshot.",
            "Risk scoring rules are consistent across zones.",
            "Operator will validate sensor availability before escalation.",
        ],
        uncertainties=[
            "Sensor outage / latency may understate true risk.",
            "Zone boundaries may not align to actual facility layout in demo mode.",
        ],
        operator_actions=[
            "Open the artifact text and validate zone notes against other products.",
            "If ELEVATED+, verify sensor health and request corroboration (bounded escalation).",
            "Document decision trail: what changed, what’s confirmed, what remains unknown.",
        ],
        notice="Assessment is probabilistic and bounded; operator judgment applies.",
    )


def explain_commander_brief() -> Dict[str, str]:
    txt = _read_text_best_effort(BRIEFS_DIR / "commander_brief_latest.txt").strip()
    j = _read_json_best_effort(BRIEFS_DIR / "commander_brief_latest.json")

    posture = "UNKNOWN"
    try:
        posture = str(j.get("recommended_posture") or j.get("posture") or "UNKNOWN")
    except Exception:
        posture = "UNKNOWN"

    return render_template(
        headline="Commander Brief — What changed / Why it matters / What’s next",
        summary=(
            "This is the executive wrapper: it turns multiple artifacts into a bounded, "
            "operator-readable snapshot designed to survive missing inputs."
        ),
        confidence="Medium-High (if readiness gate PASS; otherwise bounded/limited).",
        recommended_posture=posture,
        what_we_know=[
            "The brief is generated from available artifacts at runtime.",
            "It is designed to be safe under degraded conditions (no crashes).",
            "It uses bounded language and explicitly states what we cannot say.",
        ],
        what_we_do_not_know=[
            "Intent, causality, and attribution are not inferred from synthetic telemetry.",
            "Single-product conclusions are not allowed—corroboration required.",
        ],
        assumptions=[
            "Artifacts are current and generated from the same demo run window.",
            "Operator reviews violations/gates before using for decisions.",
        ],
        uncertainties=[
            "If any upstream artifacts are stale, posture could lag reality.",
            "If a module was run out of order, dependencies may mislead.",
        ],
        operator_actions=[
            "Verify readiness gate status before briefing.",
            "Use this brief as a starting point—then open supporting artifacts.",
            "Escalate only after corroboration or policy threshold is met.",
        ],
        notice="Assessment is probabilistic and bounded; operator judgment applies.",
    )


def explain_legal_snapshot() -> Dict[str, str]:
    txt = _read_text_best_effort(BRIEFS_DIR / "legal_case_snapshot_latest.txt").strip()
    j = _read_json_best_effort(BRIEFS_DIR / "legal_case_snapshot_latest.json")

    band = "UNKNOWN"
    posture = "HOLD_ACTION_PENDING_REVIEW"
    try:
        band = str(j.get("risk_band") or j.get("risk", {}).get("band") or "UNKNOWN")
        posture = str(j.get("recommended_posture") or posture)
    except Exception:
        pass

    return render_template(
        headline="Legal Snapshot — Demo-Safe Case Triage (Bounded)",
        summary=(
            "This product demonstrates bounded decision support: it highlights missing data, "
            "risk banding, and a conservative posture to prevent overreach."
        ),
        confidence="Low-Medium (demo inputs; unknown party/jurisdiction triggers ambiguity flags).",
        recommended_posture=posture,
        what_we_know=[
            f"Risk band is reported as: {band}.",
            "Ambiguity flags signal missing critical facts (party/jurisdiction).",
            "Recommended posture is conservative by design (prevents incorrect action).",
        ],
        what_we_do_not_know=[
            "We cannot recommend escalation without verified account file + jurisdiction.",
            "We cannot assert legal sufficiency or evidentiary posture from demo data.",
        ],
        assumptions=[
            "Missing facts are treated as high-risk until verified.",
            "Operator will review source documentation before action.",
        ],
        uncertainties=[
            "Demo values may exaggerate risk to prove guardrails.",
            "Real workflows require firm-specific policy and attorney review.",
        ],
        operator_actions=[
            "Verify party identity, jurisdiction, and evidentiary posture.",
            "Confirm debt details and chain of documentation.",
            "Keep posture HOLD until required facts are confirmed.",
        ],
        notice="Assessment is probabilistic and bounded; operator judgment applies.",
    )

