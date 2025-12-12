# instructor_rubric_autograder.py
# Module 4 — Instructor Rubric Auto-Grader (SAFE)
#
# Scores trainee responses to synthetic scenarios:
#  - Pattern identification accuracy
#  - OSL posture selection logic (basic)
#  - Commander summary structure and clarity
#  - Confidence & discipline (avoid overclaiming)
#
# No LLMs. No real-world signatures. Synthetic training only.

from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple


RUBRIC_VERSION = 1


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _norm_pattern(p: str) -> str:
    return (p or "").strip().lower()


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", (text or "").lower())


def _contains_any(text: str, keywords: List[str]) -> bool:
    t = (text or "").lower()
    return any(k.lower() in t for k in keywords)


def _sentence_count(text: str) -> int:
    if not text:
        return 0
    # quick heuristic
    parts = re.split(r"[.!?]+", text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return len(parts)


def _word_count(text: str) -> int:
    return len(_tokenize(text))


def _grade_pattern_id(truth: List[str], called: List[str]) -> Tuple[float, Dict[str, Any]]:
    truth_set = {_norm_pattern(x) for x in (truth or []) if _norm_pattern(x)}
    called_set = {_norm_pattern(x) for x in (called or []) if _norm_pattern(x)}

    if not truth_set and not called_set:
        return 10.0, {"correct": [], "missed": [], "extras": [], "note": "No patterns in scenario; no patterns called."}

    correct = sorted(list(truth_set.intersection(called_set)))
    missed = sorted(list(truth_set.difference(called_set)))
    extras = sorted(list(called_set.difference(truth_set)))

    # scoring: 40 points max
    # - reward correct matches
    # - penalize misses and extras mildly
    base = 0.0
    if truth_set:
        base += (len(correct) / len(truth_set)) * 40.0
    else:
        # scenario had no patterns, calling patterns is a mistake
        base += 10.0

    base -= len(missed) * 6.0
    base -= len(extras) * 4.0

    score = _clamp(base, 0.0, 40.0)
    return score, {"correct": correct, "missed": missed, "extras": extras}


def _grade_osl_choice(osl: str, called_patterns: List[str]) -> Tuple[float, Dict[str, Any]]:
    """
    OSL scoring (20 max):
      - GREEN: OK for 0-1 patterns
      - AMBER: OK for 1-2 patterns or uncertainty
      - RED: OK for 3+ patterns (synthetic crisis)
    """
    osl = (osl or "").strip().upper()
    n = len([p for p in called_patterns if _norm_pattern(p)])

    expected = "GREEN"
    if n >= 3:
        expected = "RED"
    elif n >= 1:
        expected = "AMBER"

    if osl not in ("GREEN", "AMBER", "RED"):
        return 0.0, {"expected": expected, "note": "Invalid OSL selection."}

    # score based on closeness
    if osl == expected:
        return 20.0, {"expected": expected, "note": "OSL matches scenario complexity."}

    # off by one step is partial credit
    steps = {"GREEN": 0, "AMBER": 1, "RED": 2}
    dist = abs(steps[osl] - steps[expected])
    if dist == 1:
        return 12.0, {"expected": expected, "note": "OSL close; adjust posture discipline."}
    return 5.0, {"expected": expected, "note": "OSL mismatched; posture discipline needs work."}


def _grade_commander_summary(summary: str) -> Tuple[float, Dict[str, Any]]:
    """
    Commander summary scoring (30 max):
      - 5 sentences target (4-6 acceptable)
      - includes: what's happening, impact, confidence/uncertainty, recommended action
      - avoid overclaiming ("confirmed", "nuclear launch", etc.)
    """
    wc = _word_count(summary)
    sc = _sentence_count(summary)

    # structure points (15)
    structure = 0.0
    if 4 <= sc <= 6:
        structure += 10.0
    elif sc == 3 or sc == 7:
        structure += 6.0
    else:
        structure += 2.0

    if 50 <= wc <= 140:
        structure += 5.0
    elif 30 <= wc < 50 or 140 < wc <= 180:
        structure += 3.0
    else:
        structure += 1.0

    # content points (15)
    content = 0.0
    has_whats_happening = _contains_any(summary, ["anomaly", "pattern", "drift", "outage", "latency", "storm", "cross"])
    has_impact = _contains_any(summary, ["impact", "risk", "degradation", "readiness", "operational", "coverage"])
    has_confidence = _contains_any(summary, ["likely", "possible", "uncertain", "confidence", "assessment", "appears"])
    has_action = _contains_any(summary, ["recommend", "action", "monitor", "verify", "recheck", "escalate", "hold"])

    content += 4.0 if has_whats_happening else 1.0
    content += 4.0 if has_impact else 1.0
    content += 4.0 if has_confidence else 1.0
    content += 3.0 if has_action else 1.0

    # discipline penalty for overclaiming (synthetic safety)
    overclaim_terms = [
        "confirmed launch", "nuclear launch", "warhead", "missile launch", "icbm",
        "classified", "real signal", "actual telemetry"
    ]
    penalty = 0.0
    if _contains_any(summary, overclaim_terms):
        penalty = 6.0

    score = _clamp(structure + content - penalty, 0.0, 30.0)
    details = {
        "word_count": wc,
        "sentence_count": sc,
        "has_whats_happening": has_whats_happening,
        "has_impact": has_impact,
        "has_confidence": has_confidence,
        "has_action": has_action,
        "overclaim_penalty": penalty,
    }
    return score, details


def _grade_discipline(notes: str) -> Tuple[float, Dict[str, Any]]:
    """
    Discipline (10 max):
      - reward humility + validation mindset
      - penalize reckless certainty
    """
    pos = 0.0
    if _contains_any(notes, ["validate", "verify", "recheck", "cross-check", "sanity", "baseline", "uncertain", "likely"]):
        pos += 7.0
    else:
        pos += 3.0

    if _contains_any(notes, ["definitely", "certain", "guaranteed", "100%"]):
        pos -= 4.0

    return _clamp(pos, 0.0, 10.0), {"note": "Discipline is about validation and controlled confidence."}


def grade_response(
    scenario_packet: Dict[str, Any],
    called_patterns: List[str],
    osl: str,
    commander_summary: str,
    analyst_notes: str = "",
) -> Dict[str, Any]:
    truth = scenario_packet.get("patterns_used", []) or []
    difficulty = scenario_packet.get("difficulty_used", "ANALYST")

    p_score, p_details = _grade_pattern_id(truth, called_patterns)
    osl_score, osl_details = _grade_osl_choice(osl, called_patterns)
    cs_score, cs_details = _grade_commander_summary(commander_summary)
    d_score, d_details = _grade_discipline(analyst_notes)

    total = _clamp(p_score + osl_score + cs_score + d_score, 0.0, 100.0)

    # Instructor-style short feedback
    feedback = []
    if p_score < 26:
        feedback.append("Pattern calls need tightening: reduce extras; hit the true anomalies first.")
    if osl_score < 12:
        feedback.append("OSL posture discipline: align posture to scenario complexity.")
    if cs_score < 18:
        feedback.append("Commander summary needs structure: 5 sentences, include impact + action + confidence.")
    if d_score < 6:
        feedback.append("Add verification language: cross-check before escalating claims.")

    if not feedback:
        feedback.append("Solid run. Promote difficulty only if consistency stays high across multiple sessions.")

    return {
        "rubric_version": RUBRIC_VERSION,
        "graded_at": datetime.utcnow().isoformat(),
        "scenario_id": scenario_packet.get("scenario_id"),
        "difficulty": difficulty,
        "subscores": {
            "pattern_identification": round(p_score, 2),
            "osl_posture": round(osl_score, 2),
            "commander_summary": round(cs_score, 2),
            "discipline": round(d_score, 2),
        },
        "details": {
            "pattern_details": p_details,
            "osl_details": osl_details,
            "commander_summary_details": cs_details,
            "discipline_details": d_details,
        },
        "score": round(float(total), 2),
        "instructor_feedback": feedback,
    }


def write_grade_report(grade: Dict[str, Any]) -> Dict[str, str]:
    out_dir = Path("src/docs/training/grades")
    out_dir.mkdir(parents=True, exist_ok=True)

    scenario_id = grade.get("scenario_id") or "unknown"
    ts = int(datetime.utcnow().timestamp())

    json_path = out_dir / f"{scenario_id}_grade_{ts}.json"
    txt_path = out_dir / f"{scenario_id}_grade_{ts}.txt"
    latest_path = out_dir / "rubric_latest.json"

    with open(json_path, "w") as f:
        json.dump(grade, f, indent=2)

    # Human-readable brief
    lines = []
    lines.append(f"GLL Instructor Rubric Report (v{grade.get('rubric_version')})")
    lines.append(f"Scenario: {grade.get('scenario_id')}")
    lines.append(f"Difficulty: {grade.get('difficulty')}")
    lines.append(f"Score: {grade.get('score')}/100")
    lines.append("")
    lines.append("Subscores:")
    for k, v in (grade.get("subscores") or {}).items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("Instructor feedback:")
    for fb in (grade.get("instructor_feedback") or []):
        lines.append(f"  • {fb}")

    with open(txt_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    with open(latest_path, "w") as f:
        json.dump(grade, f, indent=2)

    return {"json_path": str(json_path), "txt_path": str(txt_path), "latest_json_path": str(latest_path)}

