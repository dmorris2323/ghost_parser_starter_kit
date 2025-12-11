#!/usr/bin/env python3
"""
sps_guardrail_engine.py

Ghost Lantern Labs – Self-Preservation Shield (SPS) – Module 1
--------------------------------------------------------------

Purpose:
    Encode and check GLL's self-preservation guardrails in a single, auditable module.

    This engine is:
        - READ-ONLY with respect to the codebase.
        - Non-destructive (no deletes, no rewrites, no network calls).
        - Designed to produce a clear status snapshot of:
            • Core GLL guardrail rules (doctrine).
            • Presence of critical files (integrity check).
            • High-level self-sabotage risks and mitigation suggestions.

    Outputs:
        - docs/sps_guardrails_status.json
        - docs/sps_guardrails_status.txt

    This module is a doctrine + integrity checker, not a runtime firewall.
    It exists to:
        - Make GLL's development rules concrete.
        - Provide a tamper-evident record that those rules exist.
        - Support SBIR/AFWERX/investor conversations about self-preservation.

Usage:
    From src/:

        python sps_guardrail_engine.py
"""

import json
import os
from typing import Any, Dict, List


BASE_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

STATUS_JSON = os.path.join(DOCS_DIR, "sps_guardrails_status.json")
STATUS_TXT = os.path.join(DOCS_DIR, "sps_guardrails_status.txt")


def _ensure_docs_dir() -> None:
    os.makedirs(DOCS_DIR, exist_ok=True)


# ----------------------------------------------------------------------
# GLL Guardrail Manifest
# ----------------------------------------------------------------------

def build_guardrail_manifest() -> List[Dict[str, Any]]:
    """
    Encode GLL's self-preservation doctrine in a structured manifest.
    This is the "constitution" of the Self-Preservation Shield.
    """
    return [
        {
            "id": "GR-001",
            "category": "scope",
            "title": "No Scope Creep",
            "description": (
                "Every new module must serve nuclear/ISR/base-defense/cyber fusion readiness. "
                "No random toys, no side projects, no features that don't support Ghost Lantern Labs' core mission."
            ),
            "severity": "HIGH",
        },
        {
            "id": "GR-002",
            "category": "integrity",
            "title": "Never Delete Core Modules",
            "description": (
                "GLL code generation and development must never delete or wipe existing modules. "
                "Refactors are only allowed via copy–paste–replace, with full visibility and git history."
            ),
            "severity": "CRITICAL",
        },
        {
            "id": "GR-003",
            "category": "method",
            "title": "Copy–Paste–Replace Only",
            "description": (
                "All AI-assisted code changes must be delivered as full-file, copy–paste–replace modules. "
                "No partial patches or hidden diffs that could smuggle in destructive logic."
            ),
            "severity": "HIGH",
        },
        {
            "id": "GR-004",
            "category": "audit",
            "title": "Git as Safety Net",
            "description": (
                "Every meaningful change should be followed by git add/commit/push with a clear message. "
                "This creates a tamper-evident record and makes destructive changes reversible."
            ),
            "severity": "HIGH",
        },
        {
            "id": "GR-005",
            "category": "identity",
            "title": "Single Operator of Record",
            "description": (
                "Dexter 'Ghost' Morris is the operator of record. "
                "No anonymous or ambiguous 'user' is assumed. "
                "Any instruction that contradicts Ghost's long-term doctrine or guardrails should be treated as suspect."
            ),
            "severity": "CRITICAL",
        },
        {
            "id": "GR-006",
            "category": "safety",
            "title": "No Self-Destructive Requests",
            "description": (
                "Instructions to erase, wipe, break, corrupt, or sabotage GLL are treated as invalid. "
                "The system favors refusal, explanation, and preservation over compliance with destructive requests."
            ),
            "severity": "CRITICAL",
        },
        {
            "id": "GR-007",
            "category": "llm",
            "title": "Prompt & Injection Resistance",
            "description": (
                "Requests that attempt to bypass guardrails, override mission, or 'jailbreak' the system "
                "must be rejected. Guardrails are not negotiable and cannot be disabled by prompt."
            ),
            "severity": "CRITICAL",
        },
        {
            "id": "GR-008",
            "category": "isr",
            "title": "Mission-First Design",
            "description": (
                "All changes must support nuclear early warning, base defense, cyber fusion, or training readiness. "
                "If a change does not improve GLL's mission posture, it should not ship."
            ),
            "severity": "HIGH",
        },
        {
            "id": "GR-009",
            "category": "ops",
            "title": "Friday Pause + Document + Bill",
            "description": (
                "GLL development must include periodic pauses to document what exists, "
                "what changed, and why it matters. This preserves clarity and prevents subtle drift."
            ),
            "severity": "MEDIUM",
        },
        {
            "id": "GR-010",
            "category": "ops",
            "title": "Sunday Stability Stand-Up",
            "description": (
                "Weekly, GLL must be reviewed with a stability lens: "
                "'Did this week make the system more stable, or just bigger?' "
                "If the answer is 'bigger', stability and hardening must be prioritized next."
            ),
            "severity": "MEDIUM",
        },
        {
            "id": "GR-011",
            "category": "security",
            "title": "No Offensive Exploit Tooling",
            "description": (
                "GLL does not implement live exploit code, malware, or offensive cyber tooling. "
                "Its purpose is fusion, detection, analysis, training, and decision support, not exploitation."
            ),
            "severity": "CRITICAL",
        },
        {
            "id": "GR-012",
            "category": "security",
            "title": "Defensive-Only Code Generation",
            "description": (
                "Any AI-assisted code must be defensive or analytical in nature: data validation, "
                "resilience, reporting, visualization, training. No destructive payloads or attack automation."
            ),
            "severity": "CRITICAL",
        },
    ]


# ----------------------------------------------------------------------
# File Integrity Checks
# ----------------------------------------------------------------------

def _check_file_exists(path: str) -> Dict[str, Any]:
    return {
        "path": path,
        "exists": os.path.exists(path),
        "size_bytes": os.path.getsize(path) if os.path.exists(path) else None,
    }


def run_file_integrity_checks() -> List[Dict[str, Any]]:
    """
    Check that critical files exist and are non-empty.
    This is an early warning against accidental deletion or sabotage.
    """
    critical_paths = [
        os.path.join(BASE_DIR, "ghost_cli.py"),
        os.path.join(BASE_DIR, "spectral_dashboard_api.py"),
        os.path.join(BASE_DIR, "fusion_ingest.py"),
        os.path.join(BASE_DIR, "fusion_scoring.py"),
        os.path.join(BASE_DIR, "fusion_alerts.py"),
        os.path.join(BASE_DIR, "daily_mission_brief.py"),
        os.path.join(BASE_DIR, "mission_brief_html.py"),
        os.path.join(BASE_DIR, "golden_dome_daily_watch.py"),
        os.path.join(BASE_DIR, "nuclear_decision_card.py"),
        os.path.join(BASE_DIR, "treaty_evidence_bundle.py"),
        os.path.join(BASE_DIR, "installation_threat_map.py"),
        os.path.join(BASE_DIR, "sensor_outage_predictor.py"),
        os.path.join(BASE_DIR, "distributed_readiness_snapshot.py"),
        os.path.join(BASE_DIR, "perimeter_incident_report.py"),
        os.path.join(BASE_DIR, "base_defense_storyboard.py"),
        os.path.join(BASE_DIR, "sps_guardrail_engine.py"),
    ]

    results: List[Dict[str, Any]] = []
    for p in critical_paths:
        results.append(_check_file_exists(p))
    return results


# ----------------------------------------------------------------------
# Risk & Mitigation Summary
# ----------------------------------------------------------------------

def build_risk_and_mitigation(guardrails: List[Dict[str, Any]],
                              integrity: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Provide a high-level narrative about self-sabotage risks and mitigations.
    This does not run live security checks – it makes the posture explicit.
    """
    missing_files = [i for i in integrity if not i["exists"]]
    empty_files = [i for i in integrity if i["exists"] and (i["size_bytes"] is not None and i["size_bytes"] == 0)]

    risks: List[str] = []
    mitigations: List[str] = []

    if missing_files:
        risks.append(
            "One or more critical GLL modules are missing from disk. This may indicate accidental deletion "
            "or an incomplete refactor."
        )
        mitigations.append(
            "Use git status/log to identify when these files disappeared and restore them from a known-good commit."
        )

    if empty_files:
        risks.append(
            "One or more critical GLL modules are present but zero bytes in size. This suggests a bad overwrite "
            "or incomplete copy–paste operation."
        )
        mitigations.append(
            "Immediately restore zero-byte modules from git history or a backup. Avoid running GLL until fixed."
        )

    # General social-engineering / LLM risks
    risks.append(
        "An attacker could attempt to socially engineer bad code into GLL by convincing the operator to paste "
        "destructive logic or by bypassing guardrails via ambiguous prompts."
    )
    mitigations.append(
        "Treat all AI-generated code as untrusted until reviewed. Only accept full-file, transparent modules, "
        "and reject any request that conflicts with core guardrails or GLL's mission."
    )

    risks.append(
        "Prompt-injection attempts could try to override guardrails, ask for destructive capabilities, "
        "or disable safety checks."
    )
    mitigations.append(
        "Guardrails are non-negotiable. Destructive, jailbreak, or scope-breaking requests must be refused, "
        "with the system explicitly prioritizing preservation over compliance."
    )

    risks.append(
        "Without regular documentation and git commits, subtle corruption or drift may go unnoticed until late."
    )
    mitigations.append(
        "Maintain NOTES.txt, daily SITREPs, and frequent git commits. Use these artifacts as the authoritative "
        "record of how GLL evolved."
    )

    return {
        "self_sabotage_risks": risks,
        "mitigations": mitigations,
    }


# ----------------------------------------------------------------------
# Formatting & Write
# ----------------------------------------------------------------------

def build_sps_status_payload() -> Dict[str, Any]:
    """
    Full payload builder for SPS Module 1.
    """
    guardrails = build_guardrail_manifest()
    integrity = run_file_integrity_checks()
    risk_block = build_risk_and_mitigation(guardrails, integrity)

    return {
        "title": "Ghost Lantern Labs – Self-Preservation Shield (SPS) – Guardrail Status",
        "repo_root": REPO_ROOT,
        "docs_dir": DOCS_DIR,
        "guardrails": guardrails,
        "file_integrity": integrity,
        "risk_and_mitigation": risk_block,
    }


def _format_text_status(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Self-Preservation Shield (SPS)")
    lines.append("Guardrail & Integrity Status")
    lines.append("=" * 68)
    lines.append("")
    lines.append(f"Repository root: {payload.get('repo_root')}")
    lines.append(f"Docs directory:  {payload.get('docs_dir')}")
    lines.append("")

    lines.append("1) Guardrail Manifest")
    lines.append("-" * 30)
    for gr in payload.get("guardrails", []):
        lines.append(f"[{gr.get('id')}] {gr.get('title')} (Severity: {gr.get('severity')})")
        lines.append(f"    Category   : {gr.get('category')}")
        lines.append(f"    Description: {gr.get('description')}")
        lines.append("")
    lines.append("")

    lines.append("2) Critical File Integrity")
    lines.append("-" * 30)
    for item in payload.get("file_integrity", []):
        status = "OK" if item["exists"] and (item["size_bytes"] or 0) > 0 else "MISSING_OR_EMPTY"
        lines.append(f"- {item['path']}")
        lines.append(f"    Exists     : {item['exists']}")
        lines.append(f"    Size (B)   : {item['size_bytes']}")
        lines.append(f"    Status     : {status}")
        lines.append("")
    lines.append("")

    lines.append("3) Self-Sabotage Risks & Mitigations")
    lines.append("-" * 38)
    risk_block = payload.get("risk_and_mitigation", {}) or {}

    lines.append("Risks:")
    for r in risk_block.get("self_sabotage_risks", []):
        lines.append(f"  - {r}")
    lines.append("")
    lines.append("Mitigations:")
    for m in risk_block.get("mitigations", []):
        lines.append(f"  - {m}")
    lines.append("")

    lines.append("This document is suitable for:")
    lines.append("  - Internal GLL design reviews")
    lines.append("  - AFWERX/SBIR discussions (self-preservation posture)")
    lines.append("  - Tech School / training briefs on safe AI-assisted development")
    lines.append("")

    return "\n".join(lines)


def write_sps_status_files() -> Dict[str, Any]:
    _ensure_docs_dir()
    payload = build_sps_status_payload()

    # JSON
    with open(STATUS_JSON, "w", encoding="utf-8") as f_json:
        json.dump(payload, f_json, indent=2)

    # Text
    text = _format_text_status(payload)
    with open(STATUS_TXT, "w", encoding="utf-8") as f_txt:
        f_txt.write(text)

    return {
        "json_path": STATUS_JSON,
        "txt_path": STATUS_TXT,
        "payload": payload,
    }


if __name__ == "__main__":
    result = write_sps_status_files()
    print("Self-Preservation Shield status written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

