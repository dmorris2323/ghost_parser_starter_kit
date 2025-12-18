# src/spectral_owl_explain.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from spectral_owl_reasoning_templates import render_template, pack_bullets

# -----------------------------
# Repo paths (safe, no Streamlit assumptions)
# -----------------------------
_THIS = Path(__file__).resolve()
SRC_DIR = _THIS.parent
REPO_ROOT = SRC_DIR.parent

BRIEFS_DIR = REPO_ROOT / "docs" / "briefs"
BASE_DEF_DIR = REPO_ROOT / "docs" / "base_defense"

# Artifacts (best-effort)
INSTALLATION_THREAT_MAP_TXT = BASE_DEF_DIR / "installation_threat_map_latest.txt"
INSTALLATION_THREAT_MAP_TXT_FALLBACK = BRIEFS_DIR / "installation_threat_map_latest.txt"

COMMANDER_BRIEF_TXT = BRIEFS_DIR / "commander_brief_latest.txt"
LEGAL_SNAPSHOT_TXT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"


def _safe_read_text(path: Path, limit: int = 9000) -> Tuple[bool, str]:
    try:
        if not path.exists():
            return False, f"(missing) {path}"
        s = path.read_text(encoding="utf-8", errors="replace")
        if len(s) > limit:
            s = s[:limit] + "\n\n[...truncated...]"
        return True, s
    except Exception as e:
        return False, f"(error reading {path}): {e}"


def _pick_installation_map_path() -> Path:
    if INSTALLATION_THREAT_MAP_TXT.exists():
        return INSTALLATION_THREAT_MAP_TXT
    if INSTALLATION_THREAT_MAP_TXT_FALLBACK.exists():
        return INSTALLATION_THREAT_MAP_TXT_FALLBACK
    return INSTALLATION_THREAT_MAP_TXT


def _parse_installation_map(txt: str) -> Dict[str, Any]:
    """
    Parse the simple text format you showed:
      Installation Threat Map
      generated_at_utc: ...
      posture: ...
      overall_risk_band: ...
      max_risk_score: ...
      zones:
      - NORTH: risk_score=...
    """
    out: Dict[str, Any] = {
        "generated_at_utc": None,
        "posture": None,
        "overall_risk_band": None,
        "max_risk_score": None,
        "zones": [],
    }

    lines = [ln.rstrip() for ln in (txt or "").splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("generated_at_utc:"):
            out["generated_at_utc"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("posture:"):
            out["posture"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("overall_risk_band:"):
            out["overall_risk_band"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("max_risk_score:"):
            out["max_risk_score"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("- ") and "risk_score=" in ln and "band=" in ln:
            # "- NORTH: risk_score=12.0 band=LOW notes=..."
            out["zones"].append(ln[2:].strip())

    return out


def _parse_legal_snapshot(txt: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "generated_at_utc": None,
        "risk_band": None,
        "recommended_posture": None,
        "ambiguity_flags": [],
        "demo_lock_present": False,
    }
    lines = [ln.rstrip() for ln in (txt or "").splitlines()]
    for ln in lines:
        if ln.startswith("generated_at_utc:"):
            out["generated_at_utc"] = ln.split(":", 1)[1].strip()
        if "Risk Band:" in ln:
            # "Risk Score: 99.9 | Risk Band: CRITICAL"
            parts = ln.split("Risk Band:", 1)
            if len(parts) == 2:
                out["risk_band"] = parts[1].strip()
        if ln.startswith("Recommended posture:"):
            out["recommended_posture"] = ln.split(":", 1)[1].strip()
        if ln.startswith("- ") and "UNKNOWN_" in ln:
            out["ambiguity_flags"].append(ln[2:].strip())
        if "DEMO MODE ACTIVE" in ln:
            out["demo_lock_present"] = True
    return out


def _parse_commander_brief(txt: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"generated_at_utc": None, "top_lines": []}
    lines = [ln.rstrip() for ln in (txt or "").splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("generated_at_utc:"):
            out["generated_at_utc"] = ln.split(":", 1)[1].strip()
            break
    out["top_lines"] = lines[:18]
    return out


# -----------------------------
# PUBLIC API (these must exist)
# -----------------------------
def explain_installation_threat_map() -> Dict[str, Any]:
    path = _pick_installation_map_path()
    ok, txt = _safe_read_text(path, limit=7000)
    parsed = _parse_installation_map(txt if ok else "")

    posture = parsed.get("posture") or "UNKNOWN"
    band = parsed.get("overall_risk_band") or "UNKNOWN"
    max_score = parsed.get("max_risk_score") or "UNKNOWN"
    zones = parsed.get("zones") or []

    headline = f"Installation posture: {posture} | Band: {band} | Max risk: {max_score}"
    summary = (
        "This product summarizes zone-based risk into a bounded posture call for the duty officer. "
        "It is not attribution, not intent, and not a claim of attack — it’s a triage signal."
    )
    confidence = "MED (bounded computation + limited sensors; corroboration required)"
    recommended_posture = posture

    what_we_know = [
        f"Overall band appears as {band} with max score {max_score}.",
        f"Zones listed: {len(zones)}.",
        f"Source file: {path.name} ({'OK' if ok else 'MISSING'})",
    ]
    if zones:
        what_we_know.append("Top zone lines:")
        what_we_know.extend(zones[:3])

    what_we_do_not_know = [
        "Adversary intent or attribution (not supported by this product).",
        "Causality (needs corroborating sensors and operator judgment).",
    ]
    assumptions = [
        "Zone scoring rules are calibrated and stable for demo mode.",
        "Sensors are not spoofed/jammed in ways that invalidate scoring.",
    ]
    uncertainties = [
        "Single-source artifacts can be noisy; validate with additional telemetry.",
        "False positives can occur when patterns break, not when a single sensor fires.",
    ]
    operator_actions = [
        "Open the latest map text and verify zone notes against sensor status.",
        "Cross-check SOUTH/ELEVATED zones with comms/radiation/outage predictors if available.",
        "If posture is DUTY_OFFICER_NOTIFY, notify and document — no escalation without corroboration.",
    ]

    return render_template(
        target="Radar / Threat Map",
        headline=headline,
        summary=summary,
        confidence=confidence,
        recommended_posture=recommended_posture,
        what_we_know=what_we_know,
        what_we_do_not_know=what_we_do_not_know,
        assumptions=assumptions,
        uncertainties=uncertainties,
        operator_actions=operator_actions,
        notice="Cannot infer adversary intent from this product. Operator judgment applies.",
        extra={"source_path": str(path), "parsed": parsed},
    )


def explain_commander_brief() -> Dict[str, Any]:
    ok, txt = _safe_read_text(COMMANDER_BRIEF_TXT, limit=9000)
    parsed = _parse_commander_brief(txt if ok else "")

    headline = "Commander Brief: what it is and how to read it (bounded)"
    summary = (
        "This brief is a commander-safe rollup: it turns multiple bounded products into a single "
        "decision-oriented narrative. It reduces workload by structuring attention, not by replacing judgment."
    )
    confidence = "MED (depends on upstream artifacts; verify before acting)"
    recommended_posture = "COMMAND_REVIEW"

    what_we_know = [
        f"Source file: {COMMANDER_BRIEF_TXT.name} ({'OK' if ok else 'MISSING'})",
    ]
    if parsed.get("generated_at_utc"):
        what_we_know.append(f"Brief generated_at_utc: {parsed['generated_at_utc']}")
    if parsed.get("top_lines"):
        what_we_know.append("Top lines (preview):")
        what_we_know.extend(parsed["top_lines"][:6])

    what_we_do_not_know = [
        "Ground truth behind each upstream signal (requires corroboration).",
        "Causality/attribution beyond what the artifacts explicitly state.",
    ]
    assumptions = [
        "Demo lock / freeze mode prevents mutation of baselines.",
        "Inputs are representative of the mission scenario, not real-world live feeds.",
    ]
    uncertainties = [
        "If any upstream artifact is stale/missing, conclusions degrade.",
        "Some sections are advisory and may be conservative by design.",
    ]
    operator_actions = [
        "Scan the executive summary first; then drill into any ELEVATED/CRITICAL calls.",
        "Confirm timestamps + sensor health before any notification posture.",
        "Use the Owl Drawer to explain bounded claims vs what we cannot say.",
    ]

    return render_template(
        target="Commander Brief",
        headline=headline,
        summary=summary,
        confidence=confidence,
        recommended_posture=recommended_posture,
        what_we_know=what_we_know,
        what_we_do_not_know=what_we_do_not_know,
        assumptions=assumptions,
        uncertainties=uncertainties,
        operator_actions=operator_actions,
        notice="This is a decision support product, not an autonomous decision maker.",
        extra={"source_path": str(COMMANDER_BRIEF_TXT), "parsed": parsed},
    )


def explain_legal_snapshot() -> Dict[str, Any]:
    ok, txt = _safe_read_text(LEGAL_SNAPSHOT_TXT, limit=9000)
    parsed = _parse_legal_snapshot(txt if ok else "")

    risk_band = parsed.get("risk_band") or "UNKNOWN"
    posture = parsed.get("recommended_posture") or "UNKNOWN"

    headline = f"Legal Snapshot: {risk_band} risk | posture: {posture}"
    summary = (
        "This snapshot is a bounded triage view for a collections/legal workflow. "
        "It highlights ambiguity flags and recommends a safe posture before escalation."
    )
    confidence = "MED (bounded scoring + ambiguity flags; file review required)"
    recommended_posture = posture

    what_we_know = [
        f"Source file: {LEGAL_SNAPSHOT_TXT.name} ({'OK' if ok else 'MISSING'})",
        f"Risk band: {risk_band}",
        f"Recommended posture: {posture}",
    ]
    if parsed.get("ambiguity_flags"):
        what_we_know.append("Ambiguity flags present:")
        what_we_know.extend(parsed["ambiguity_flags"][:6])

    what_we_do_not_know = [
        "Exact party identity or jurisdiction if marked UNKNOWN.",
        "Evidentiary posture without reviewing the account file and filings.",
    ]
    assumptions = [
        "Demo matter fields are synthetic and safe for display.",
        "Risk score is a triage tool, not a court-ready conclusion.",
    ]
    uncertainties = [
        "Unknown fields may flip posture after basic verification.",
        "A single data error can inflate risk; confirm source documents.",
    ]
    operator_actions = [
        "Verify party + jurisdiction before any escalation.",
        "Confirm balance/DPD from source system or documents.",
        "Use HOLD_ACTION_PENDING_REVIEW posture until ambiguity clears.",
    ]

    notice = "Assessment is probabilistic and bounded; operator judgment applies."
    if parsed.get("demo_lock_present"):
        notice = "DEMO MODE ACTIVE — READ ONLY. " + notice

    return render_template(
        target="Legal Snapshot",
        headline=headline,
        summary=summary,
        confidence=confidence,
        recommended_posture=recommended_posture,
        what_we_know=what_we_know,
        what_we_do_not_know=what_we_do_not_know,
        assumptions=assumptions,
        uncertainties=uncertainties,
        operator_actions=operator_actions,
        notice=notice,
        extra={"source_path": str(LEGAL_SNAPSHOT_TXT), "parsed": parsed},
    )


__all__ = [
    "explain_installation_threat_map",
    "explain_commander_brief",
    "explain_legal_snapshot",
]

