#!/usr/bin/env python3
"""
sps_behavior_monitor.py

Ghost Lantern Labs – Self-Preservation Shield (SPS) – Module 3
--------------------------------------------------------------

Behavioral Integrity Monitor

Purpose:
    SPS-1 defines guardrails.
    SPS-2 tracks file mutations.
    SPS-3 watches BEHAVIOR:

        - What do recent NOTES.txt entries look like?
        - Are we seeing lots of errors, rollbacks, "do not use" flags?
        - What does the last SPS mutation report say about critical alerts?
        - Are we operating in a "calm" engineering mode or "chaotic" mode?

    This module:
        - Reads the last N lines of src/NOTES.txt (if present).
        - Scans for concerning vs healthy patterns.
        - Reads docs/sps_mutation_report.json (if present).
        - Computes a GREEN / AMBER / RED behavioral status.
        - Writes:
            • docs/sps_behavior_report.json
            • docs/sps_behavior_report.txt

    It does NOT:
        - Modify any source files.
        - Reach the network.
        - Execute shell commands.
"""

from pathlib import Path
from typing import Any, Dict, List
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent              # .../src
DOCS_DIR = BASE_DIR / "docs"

NOTES_PATH = BASE_DIR / "NOTES.txt"
MUTATION_JSON = DOCS_DIR / "sps_mutation_report.json"

BEHAVIOR_JSON = DOCS_DIR / "sps_behavior_report.json"
BEHAVIOR_TXT = DOCS_DIR / "sps_behavior_report.txt"


def _safe_read_tail(path: Path, max_lines: int = 120) -> List[str]:
    """
    Read up to the last `max_lines` from a text file.
    Returns an empty list if file missing or unreadable.
    """
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return lines
    return lines[-max_lines:]


def _analyze_notes_behavior(lines: List[str]) -> Dict[str, Any]:
    """
    Scan NOTES.txt tail for behavioral cues:
        - errors / failures / red flags
        - rollbacks / "do not use"
        - TODO/BUG/XXX heavy noise
        - positive signals (success, passes, stable, warp-upgrade, etc.)
    """
    text = "\n".join(lines).lower()

    negative_markers = [
        "error", "exception", "traceback", "crash",
        "do not use", "broken", "corrupt",
        "rollback", "roll back", "revert",
        "panic", "catastrophic", "severe",
    ]
    caution_markers = [
        "todo", "hack", "bug", "temporary",
        "workaround", "janky", "fix later",
    ]
    positive_markers = [
        "stable", "passed", "qa ok",
        "survived stress", "clean run",
        "ready for demo", "good", "green",
    ]

    negatives = [m for m in negative_markers if m in text]
    cautions = [m for m in caution_markers if m in text]
    positives = [m for m in positive_markers if m in text]

    return {
        "lines_analyzed": len(lines),
        "negatives_found": negatives,
        "cautions_found": cautions,
        "positives_found": positives,
    }


def _load_mutation_summary() -> Dict[str, Any]:
    """
    Load a minimal summary from the last SPS mutation report.
    Returns empty dict if not available.
    """
    if not MUTATION_JSON.exists():
        return {}
    try:
        data = json.loads(MUTATION_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}

    diff = data.get("diff", {}) or {}
    critical_alerts = diff.get("critical_alerts", []) or []
    zero_byte_files = diff.get("zero_byte_files", []) or []
    changed_files = diff.get("changed_files", []) or []
    removed_files = diff.get("removed_files", []) or []
    new_files = diff.get("new_files", []) or []

    return {
        "mode": data.get("mode", "UNKNOWN"),
        "critical_alerts": critical_alerts,
        "zero_byte_files": zero_byte_files,
        "changed_files": changed_files,
        "removed_files": removed_files,
        "new_files": new_files,
    }


def _compute_behavior_status(
    notes_analysis: Dict[str, Any],
    mutation_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Derive GREEN / AMBER / RED based on:
        - Presence of severe negative markers in NOTES.
        - SPS mutation critical alerts / zero-byte files.
        - Volume of changed/removed files.
    """
    neg = notes_analysis.get("negatives_found", []) or []
    cautions = notes_analysis.get("cautions_found", []) or []
    positives = notes_analysis.get("positives_found", []) or []

    crit_alerts = mutation_summary.get("critical_alerts", []) or []
    zero_bytes = mutation_summary.get("zero_byte_files", []) or []
    changed = mutation_summary.get("changed_files", []) or []
    removed = mutation_summary.get("removed_files", []) or []

    # Default assumptions
    level = "GREEN"
    summary = (
        "Behavior looks stable. No critical SPS alerts and NOTES.txt does not "
        "show severe failures or rollback language."
    )
    reasons: List[str] = []

    # RED conditions – serious trouble
    if crit_alerts or zero_bytes:
        level = "RED"
        summary = (
            "Behavioral integrity is in a RED state – SPS has critical alerts "
            "and/or zero-byte files, and the system should NOT be trusted for "
            "serious ISR/nuclear/base-defense analysis until resolved."
        )
        if crit_alerts:
            reasons.append(
                f"SPS Mutation Watcher reported {len(crit_alerts)} critical alerts."
            )
        if zero_bytes:
            reasons.append(
                f"SPS Mutation Watcher found {len(zero_bytes)} zero-byte files."
            )

    # AMBER conditions – elevated caution
    elif neg or cautions or removed or len(changed) > 10:
        level = "AMBER"
        summary = (
            "Behavioral integrity is in an AMBER state – recent activity shows "
            "risk markers. Investigate before using GLL for high-stakes analysis."
        )
        if neg:
            reasons.append(
                f"NOTES.txt contains severe error markers: {sorted(set(neg))}"
            )
        if cautions:
            reasons.append(
                f"NOTES.txt contains caution markers (TODO/BUG/etc.): {sorted(set(cautions))}"
            )
        if removed:
            reasons.append(
                f"SPS Mutation Watcher reports {len(removed)} removed files in the last diff."
            )
        if len(changed) > 10:
            reasons.append(
                f"SPS Mutation Watcher reports {len(changed)} changed files, which is high."
            )

    # GREEN refinement
    else:
        if positives:
            reasons.append(
                f"NOTES.txt includes positive stability markers: {sorted(set(positives))}"
            )
        if not mutation_summary:
            reasons.append(
                "No SPS mutation report found yet – treating behavior as GREEN "
                "but recommend running SPS Mutation Watcher to baseline."
            )

    return {
        "level": level,
        "summary": summary,
        "reasons": reasons,
    }


def build_behavior_report() -> Dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    notes_tail = _safe_read_tail(NOTES_PATH, max_lines=160)
    notes_analysis = _analyze_notes_behavior(notes_tail)
    mutation_summary = _load_mutation_summary()
    status = _compute_behavior_status(notes_analysis, mutation_summary)

    report: Dict[str, Any] = {
        "title": "Ghost Lantern Labs – SPS Module 3 – Behavioral Integrity Monitor",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes_path": str(NOTES_PATH),
        "mutation_report_path": str(MUTATION_JSON) if MUTATION_JSON.exists() else None,
        "status": status,
        "notes_analysis": notes_analysis,
        "mutation_summary": mutation_summary,
    }
    return report


def _format_text_report(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Self-Preservation Shield (SPS)")
    lines.append("Module 3 – Behavioral Integrity Monitor")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Generated at       : {report.get('generated_at')}")
    lines.append(f"NOTES.txt path     : {report.get('notes_path')}")
    lines.append(f"Mutation report    : {report.get('mutation_report_path')}")
    lines.append("")

    status = report.get("status", {}) or {}
    lines.append("Behavioral Status")
    lines.append("-----------------")
    lines.append(f"Level   : {status.get('level', 'UNKNOWN')}")
    lines.append(f"Summary : {status.get('summary', '')}")
    reasons = status.get("reasons", []) or []
    if reasons:
        lines.append("Reasons :")
        for r in reasons:
            lines.append(f"  - {r}")
    else:
        lines.append("Reasons : (none recorded)")
    lines.append("")

    notes_analysis = report.get("notes_analysis", {}) or {}
    lines.append("Recent NOTES.txt Analysis")
    lines.append("-------------------------")
    lines.append(f"Lines analyzed   : {notes_analysis.get('lines_analyzed', 0)}")
    lines.append(
        f"Negative markers : {sorted(set(notes_analysis.get('negatives_found', []) or []))}"
    )
    lines.append(
        f"Caution markers  : {sorted(set(notes_analysis.get('cautions_found', []) or []))}"
    )
    lines.append(
        f"Positive markers : {sorted(set(notes_analysis.get('positives_found', []) or []))}"
    )
    lines.append("")

    mutation = report.get("mutation_summary", {}) or {}
    lines.append("SPS Mutation Summary (from last report)")
    lines.append("---------------------------------------")
    if mutation:
        lines.append(f"Mode            : {mutation.get('mode', 'UNKNOWN')}")
        lines.append(
            f"Critical alerts : {len(mutation.get('critical_alerts', []) or [])}"
        )
        lines.append(
            f"Zero-byte files : {len(mutation.get('zero_byte_files', []) or [])}"
        )
        lines.append(
            f"Changed files   : {len(mutation.get('changed_files', []) or [])}"
        )
        lines.append(
            f"Removed files   : {len(mutation.get('removed_files', []) or [])}"
        )
        lines.append(
            f"New files       : {len(mutation.get('new_files', []) or [])}"
        )
    else:
        lines.append("No mutation report found. Run SPS Mutation Watcher first.")
    lines.append("")

    lines.append("Recommended Use")
    lines.append("----------------")
    lines.append(
        "• Use this report before major demos, training exercises, or AFWERX/SBIR "
        "reviews to demonstrate that GLL's behavior is being monitored and "
        "assessed, not just its files."
    )
    lines.append(
        "• Treat RED as a hard stop for serious ISR/nuclear/base-defense use "
        "until issues are resolved."
    )
    lines.append(
        "• Treat AMBER as a caution flag – investigate NOTES.txt and SPS mutation "
        "reports before trusting analysis."
    )
    lines.append(
        "• Treat GREEN as 'stable enough for training and demos' but still under "
        "human supervision."
    )
    lines.append("")

    return "\n".join(lines)


def write_behavior_report() -> Dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report = build_behavior_report()

    BEHAVIOR_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    text = _format_text_report(report)
    BEHAVIOR_TXT.write_text(text, encoding="utf-8")

    return {
        "json_path": str(BEHAVIOR_JSON),
        "txt_path": str(BEHAVIOR_TXT),
        "report": report,
    }


if __name__ == "__main__":
    result = write_behavior_report()
    print("SPS Behavioral Integrity report written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

