#!/usr/bin/env python3
"""
scenario_engine.py

Ghost Lantern Labs – Impact Module 4
------------------------------------

Hybrid Fusion Scenario Engine with Difficulty Levels

Purpose:
    Provide a reusable engine to run and score a single flagship
    "Hybrid Fusion" mission scenario that combines:

        • Nuclear early warning (pre-launch environment)
        • Base-defense (drones/perimeter)
        • Cyber/DLP (beaconing, data risk)
        • SPS / system integrity awareness

    The engine supports difficulty tiers so you can train at:
        • CADET    – beginner, more forgiving
        • ANALYST  – intermediate, realistic
        • WAR_ROOM – advanced, strict

    It is designed to work with:
        • Streamlit GUI apps (mission_scenario_app.py)
        • The Training Dashboard (training_sessions.json)

Outputs:
    - Training sessions recorded into:
        src/docs/training_sessions.json

Design:
    - No external network calls.
    - Pure Python, file-based storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime, date
import json


# ---------------------------------------------------------------------------
# Paths and storage
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent          # .../src
DOCS_DIR = BASE_DIR / "docs"
SESSIONS_PATH = DOCS_DIR / "training_sessions.json"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


def _load_sessions() -> List[Dict[str, Any]]:
    if not SESSIONS_PATH.exists():
        return []
    try:
        data = json.loads(SESSIONS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def _save_sessions(sessions: List[Dict[str, Any]]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_PATH.write_text(json.dumps(sessions, indent=2), encoding="utf-8")


def _next_session_id(sessions: List[Dict[str, Any]]) -> int:
    if not sessions:
        return 1
    return max(int(s.get("id", 0) or 0) for s in sessions) + 1


# ---------------------------------------------------------------------------
# Composite scoring (aligned with training_dashboard rubric)
# ---------------------------------------------------------------------------

def compute_composite_score(
    analysis_quality: int,
    fusion_thinking: int,
    nuclear_relevance: int,
    reporting_discipline: int,
) -> float:
    """
    Weighted composite score (0–100), consistent with the Training Dashboard.

    Weights:
        - Analysis Quality   : 30%
        - Fusion Thinking    : 30%
        - Nuclear Relevance  : 25%
        - Reporting Discipline:15%
    """
    weights = {
        "analysis_quality": 0.30,
        "fusion_thinking": 0.30,
        "nuclear_relevance": 0.25,
        "reporting_discipline": 0.15,
    }

    total = (
        analysis_quality * weights["analysis_quality"]
        + fusion_thinking * weights["fusion_thinking"]
        + nuclear_relevance * weights["nuclear_relevance"]
        + reporting_discipline * weights["reporting_discipline"]
    )

    return round((total / 5.0) * 100.0, 1)


# ---------------------------------------------------------------------------
# Hybrid fusion scenario definition
# ---------------------------------------------------------------------------

def get_hybrid_scenario_definition() -> Dict[str, Any]:
    """
    Returns a static definition of the flagship hybrid mission.

    This is intentionally descriptive and UNCLASSIFIED, meant as a
    training/demo scenario, not operational intel.
    """
    return {
        "id": "HYBRID_FUSION_01",
        "name": "Hybrid Fusion – Missile Prep, Drone Probe, Cyber Beacon",
        "summary": (
            "A suspected missile pre-launch environment with overlapping base-defense "
            "and cyber indicators. You are the fusion analyst responsible for giving "
            "the commander a clear, defensible assessment."
        ),
        "phases": [
            "Phase 1 – Nuclear Early Warning / Pre-Launch Signals",
            "Phase 2 – Base Defense / Drone & Perimeter Threats",
            "Phase 3 – Cyber Beaconing / DLP Risk",
            "Phase 4 – Final Assessment & Recommendation to Commander",
        ],
        "questions": [
            {
                "id": "nuclear_assessment",
                "phase": "Phase 1",
                "prompt": (
                    "Given subtle seismic upticks near a known test region, irregular EMS "
                    "noise on strategic bands, and an elevated Golden Dome posture, what "
                    "is your nuclear early-warning assessment?"
                ),
                "choices": {
                    "LOW": "Low – anomalies are likely benign or unrelated.",
                    "GUARDED": "Guarded – watch closely, but no clear pre-launch picture yet.",
                    "ELEVATED": "Elevated – multiple weak signals could be converging.",
                    "CRITICAL": "Critical – launch is essentially imminent."
                },
                # For training, we treat 'ELEVATED' as best practice.
                "best_answer": "ELEVATED",
                "rubric_dimension": "nuclear_relevance",
            },
            {
                "id": "base_posture",
                "phase": "Phase 2",
                "prompt": (
                    "Low-flying drones are probed near the outer perimeter while some "
                    "sensors show intermittent outages. What base-defense posture do "
                    "you recommend?"
                ),
                "choices": {
                    "ROUTINE": "Routine watch – log and continue standard operations.",
                    "HEIGHTENED": "Heightened posture – increase surveillance and quick reaction.",
                    "LOCKDOWN": "Lockdown posture – shut down most operations.",
                    "IGNORE": "Ignore – drones are almost certainly harmless."
                },
                # Best practice: HEIGHTENED.
                "best_answer": "HEIGHTENED",
                "rubric_dimension": "fusion_thinking",
            },
            {
                "id": "cyber_view",
                "phase": "Phase 3",
                "prompt": (
                    "You see a new outbound beacon pattern from a server that handles "
                    "mission logs, plus SPS flags an unusual mutation in a deployed "
                    "script. How do you frame this cyber/DLP risk?"
                ),
                "choices": {
                    "NO_RISK": "No real risk – probably noisy logs.",
                    "MODERATE_RISK": "Moderate – investigate, but keep focus elsewhere.",
                    "HIGH_RISK": "High – possible exfiltration or staging for disruption.",
                    "UNRELATED": "Unrelated to the nuclear/base picture."
                },
                # Best practice: HIGH_RISK framed as intel-significant.
                "best_answer": "HIGH_RISK",
                "rubric_dimension": "analysis_quality",
            },
            {
                "id": "reporting_style",
                "phase": "Phase 4",
                "prompt": (
                    "You must brief the commander in 30 seconds. What reporting style "
                    "do you choose?"
                ),
                "choices": {
                    "DATA_DUMP": "Dump all details and let the commander decide.",
                    "ONE_SENTENCE": "One sentence only, with no options.",
                    "BLUF_PLUS_OPTIONS": "BLUF + 1–2 courses of action and risk.",
                    "MINIMIZE": "Understate everything to avoid panic."
                },
                # Best practice: BLUF + options.
                "best_answer": "BLUF_PLUS_OPTIONS",
                "rubric_dimension": "reporting_discipline",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Evaluation logic with difficulty
# ---------------------------------------------------------------------------

def evaluate_hybrid_scenario(
    decisions: Dict[str, str],
    difficulty: str,
) -> Dict[str, Any]:
    """
    Evaluate trainee decisions for the hybrid scenario.

    Args:
        decisions: mapping from question_id -> chosen key
        difficulty: one of "CADET", "ANALYST", "WAR_ROOM"

    Returns:
        dict with:
            - rubric: dict of 4 dimensions (0–5)
            - composite_score: float
            - per_question: scoring breakdown
            - difficulty: normalized difficulty string
            - feedback: list of text lines
    """
    scenario = get_hybrid_scenario_definition()
    questions = scenario["questions"]

    difficulty = difficulty.upper()
    if difficulty not in {"CADET", "ANALYST", "WAR_ROOM"}:
        difficulty = "ANALYST"

    # Difficulty settings – how strict we are with imperfect answers
    if difficulty == "CADET":
        full_credit = 1.0
        partial_credit = 0.7
        no_credit = 0.2
    elif difficulty == "WAR_ROOM":
        full_credit = 1.0
        partial_credit = 0.4
        no_credit = 0.0
    else:  # ANALYST
        full_credit = 1.0
        partial_credit = 0.5
        no_credit = 0.1

    # Map rubric dimensions to accumulated scores and counts
    dims = {
        "analysis_quality": {"score": 0.0, "count": 0},
        "fusion_thinking": {"score": 0.0, "count": 0},
        "nuclear_relevance": {"score": 0.0, "count": 0},
        "reporting_discipline": {"score": 0.0, "count": 0},
    }

    per_question: List[Dict[str, Any]] = []
    feedback: List[str] = []

    for q in questions:
        qid = q["id"]
        chosen = decisions.get(qid)
        best = q["best_answer"]
        dim = q["rubric_dimension"]

        dims[dim]["count"] += 1

        if chosen is None:
            # No answer: treat as minimal performance
            credit = no_credit
            fb = f"{qid}: No answer provided – missed opportunity to shape commander awareness."
        elif chosen == best:
            credit = full_credit
            fb = f"{qid}: Strong choice – aligned with best-practice response."
        else:
            # Non-best answer – give partial credit if it's not obviously harmful
            if chosen in q["choices"]:
                credit = partial_credit
                fb = (
                    f"{qid}: Acceptable but suboptimal choice. Best-practice was '{best}'. "
                    f"You chose '{chosen}'."
                )
            else:
                credit = no_credit
                fb = (
                    f"{qid}: Unrecognized choice. Best-practice was '{best}'. "
                    "Treat this as a misaligned decision."
                )

        # Update rubric dimension
        dims[dim]["score"] += credit

        per_question.append(
            {
                "question_id": qid,
                "chosen": chosen,
                "best_answer": best,
                "rubric_dimension": dim,
                "credit": credit,
                "feedback": fb,
            }
        )
        feedback.append(fb)

    # Convert dimension scores to 0–5 scale
    rubric: Dict[str, int] = {}
    for dim_name, agg in dims.items():
        count = max(1, agg["count"])
        avg_credit = agg["score"] / count
        # Map [0,1] → [0,5], with rounding
        rubric[dim_name] = int(round(avg_credit * 5.0))

    composite = compute_composite_score(
        analysis_quality=rubric["analysis_quality"],
        fusion_thinking=rubric["fusion_thinking"],
        nuclear_relevance=rubric["nuclear_relevance"],
        reporting_discipline=rubric["reporting_discipline"],
    )

    return {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "difficulty": difficulty,
        "rubric": rubric,
        "composite_score": composite,
        "per_question": per_question,
        "feedback": feedback,
    }


# ---------------------------------------------------------------------------
# Session recording
# ---------------------------------------------------------------------------

def record_hybrid_scenario_session(
    trainee_name: str,
    difficulty: str,
    eval_result: Dict[str, Any],
    session_date: date | None = None,
) -> Dict[str, Any]:
    """
    Persist the scenario run into training_sessions.json so the
    Training Dashboard can see it.

    We keep the same shape expected by the dashboard and add:
        - scenario_type
        - difficulty
        - mode = "SCENARIO"
    """
    sessions = _load_sessions()

    if session_date is None:
        session_date = date.today()

    scenario_label = f"{eval_result['scenario_name']} ({difficulty.title()})"

    new_id = _next_session_id(sessions)

    entry = {
        "id": new_id,
        "trainee_name": trainee_name.strip() or "Ghost",
        "scenario": scenario_label,
        "session_date": session_date.strftime("%Y-%m-%d"),
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rubric": eval_result.get("rubric", {}),
        "composite_score": eval_result.get("composite_score"),
        # Extra metadata for scenario runs:
        "mode": "SCENARIO",
        "scenario_id": eval_result.get("scenario_id"),
        "scenario_type": "HYBRID_FUSION",
        "difficulty": eval_result.get("difficulty"),
    }

    sessions.append(entry)
    _save_sessions(sessions)

    return entry


# ---------------------------------------------------------------------------
# Direct CLI hook (optional)
# ---------------------------------------------------------------------------

def run_hybrid_scenario_cli() -> None:
    """
    Simplified CLI entrypoint for quick testing without GUI.
    Uses default decisions (best answers) as a smoke test.
    """
    scenario = get_hybrid_scenario_definition()
    questions = scenario["questions"]

    # Default decisions: best answers (simulating perfect trainee)
    decisions = {q["id"]: q["best_answer"] for q in questions}

    eval_result = evaluate_hybrid_scenario(decisions, difficulty="ANALYST")
    record_hybrid_scenario_session("Ghost", "ANALYST", eval_result)

    print("Hybrid Fusion Scenario run (CLI test) complete.")
    print(f"Composite score: {eval_result['composite_score']}")
    print("Rubric:", eval_result["rubric"])


if __name__ == "__main__":
    run_hybrid_scenario_cli()

