# aar_generator.py
# Module 5 — After Action Review (AAR) Generator (SAFE)
#
# Builds an instructor-ready AAR from:
#   - scenario packet (synthetic)
#   - rubric grade (Module 4 output)
#   - trainee inputs (called patterns, OSL, commander summary, notes)
#
# Outputs:
#   - src/docs/training/aars/<scenario>_aar_<ts>.json
#   - src/docs/training/aars/<scenario>_aar_<ts>.txt
#   - src/docs/training/aars/aar_latest.json

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return str(path)


def _write_txt(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")
    return str(path)


def build_aar(
    scenario_packet: Dict[str, Any],
    grade_packet: Dict[str, Any],
    trainee_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    scenario_packet: loaded scenario json (Module 3)
    grade_packet: rubric grade json (Module 4)
    trainee_payload: {
        "trainee": str,
        "called_patterns": [str],
        "osl": str,
        "commander_summary": str,
        "analyst_notes": str
    }
    """
    truth = scenario_packet.get("patterns_used", []) or []
    grade_details = (grade_packet.get("details") or {}).get("pattern_details") or {}
    correct = grade_details.get("correct", [])
    missed = grade_details.get("missed", [])
    extras = grade_details.get("extras", [])

    subs = grade_packet.get("subscores", {}) or {}
    score = grade_packet.get("score", 0)

    # Build a clean improvement plan (next reps)
    next_reps: List[str] = []
    if subs.get("pattern_identification", 0) < 30:
        next_reps.append("Rep: call fewer patterns. Anchor on the strongest signal first; then expand.")
    if subs.get("osl_posture", 0) < 12:
        next_reps.append("Rep: align OSL to complexity (1–2 patterns=AMBER, 3+=RED).")
    if subs.get("commander_summary", 0) < 18:
        next_reps.append("Rep: write 5 sentences: (1) event, (2) impact, (3) assessment, (4) action, (5) confidence.")
    if subs.get("discipline", 0) < 6:
        next_reps.append("Rep: add verification language: validate, cross-check, baseline before escalation.")
    if not next_reps:
        next_reps.append("Rep: maintain consistency across 3 runs; then promote difficulty one tier.")

    aar = {
        "aar_version": 1,
        "generated_at": datetime.utcnow().isoformat(),
        "scenario": {
            "scenario_id": scenario_packet.get("scenario_id"),
            "difficulty_used": scenario_packet.get("difficulty_used"),
            "patterns_truth": truth,
            "telemetry_json_path": scenario_packet.get("telemetry_json_path"),
            "scenario_json_path": trainee_payload.get("scenario_json_path"),
            "safe_notice": scenario_packet.get("safe_notice", "Synthetic-only training scenario."),
        },
        "trainee": {
            "name": trainee_payload.get("trainee", "Ghost"),
            "called_patterns": trainee_payload.get("called_patterns", []),
            "osl": trainee_payload.get("osl", ""),
            "commander_summary": trainee_payload.get("commander_summary", ""),
            "analyst_notes": trainee_payload.get("analyst_notes", ""),
        },
        "grading": {
            "score": score,
            "subscores": subs,
            "pattern_results": {
                "correct": correct,
                "missed": missed,
                "extras": extras,
            },
            "instructor_feedback": grade_packet.get("instructor_feedback", []),
        },
        "analysis": {
            "what_happened": (
                f"Synthetic scenario generated with patterns: {', '.join(truth) if truth else 'none'} "
                f"at difficulty {scenario_packet.get('difficulty_used')}."
            ),
            "what_you_did_well": (
                "Correctly identified: " + (", ".join(correct) if correct else "none")
            ),
            "what_to_fix": (
                "Missed: " + (", ".join(missed) if missed else "none") +
                " | Extras: " + (", ".join(extras) if extras else "none")
            ),
            "next_reps": next_reps,
        },
    }

    return aar


def write_aar_files(aar: Dict[str, Any]) -> Dict[str, str]:
    out_dir = Path("src/docs/training/aars")
    out_dir.mkdir(parents=True, exist_ok=True)

    scenario_id = (aar.get("scenario") or {}).get("scenario_id") or "unknown"
    ts = int(datetime.utcnow().timestamp())

    json_path = out_dir / f"{scenario_id}_aar_{ts}.json"
    txt_path = out_dir / f"{scenario_id}_aar_{ts}.txt"
    latest_path = out_dir / "aar_latest.json"

    _write_json(json_path, aar)
    _write_json(latest_path, aar)

    # One-page TXT
    g = aar.get("grading", {})
    s = aar.get("scenario", {})
    t = aar.get("trainee", {})
    a = aar.get("analysis", {})

    lines = []
    lines.append("GLL AFTER ACTION REVIEW (AAR)")
    lines.append(f"Scenario: {s.get('scenario_id')} | Difficulty: {s.get('difficulty_used')}")
    lines.append(f"Trainee: {t.get('name')}")
    lines.append(f"Score: {g.get('score')}/100")
    lines.append("")
    lines.append("TRUTH PATTERNS:")
    lines.append(f"  {', '.join(s.get('patterns_truth') or []) or 'none'}")
    lines.append("CALLED PATTERNS:")
    lines.append(f"  {', '.join(t.get('called_patterns') or []) or 'none'}")
    lines.append(f"OSL: {t.get('osl')}")
    lines.append("")
    lines.append("SUBSCORES:")
    for k, v in (g.get('subscores') or {}).items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("INSTRUCTOR FEEDBACK:")
    for fb in (g.get("instructor_feedback") or []):
        lines.append(f"  • {fb}")
    lines.append("")
    lines.append("COMMANDER SUMMARY (TRAINEE):")
    lines.append(t.get("commander_summary", "").strip() or "[empty]")
    lines.append("")
    lines.append("WHAT HAPPENED:")
    lines.append(a.get("what_happened", ""))
    lines.append("WHAT YOU DID WELL:")
    lines.append(a.get("what_you_did_well", ""))
    lines.append("WHAT TO FIX:")
    lines.append(a.get("what_to_fix", ""))
    lines.append("")
    lines.append("NEXT REPS:")
    for r in (a.get("next_reps") or []):
        lines.append(f"  • {r}")
    lines.append("")
    lines.append("SAFE NOTICE:")
    lines.append(s.get("safe_notice", "Synthetic-only training scenario."))

    _write_txt(txt_path, "\n".join(lines))

    return {"json_path": str(json_path), "txt_path": str(txt_path), "latest_json_path": str(latest_path)}

