# src/scenario_engine.py
from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from training_difficulty_engine import normalize_difficulty, get_profile


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ScenarioEvent:
    t_min: int
    domain: str
    label: str
    severity: str
    notes: str


@dataclass
class Scenario:
    scenario_version: int
    generated_at: str
    difficulty: str
    seed: int
    title: str
    intent: str
    objectives: List[str]
    injects: List[str]
    expected_operator_actions: List[str]
    timeline: List[ScenarioEvent]


def _pick(pool: List[str], rng: random.Random, k: int) -> List[str]:
    if k <= 0:
        return []
    k = min(k, len(pool))
    return rng.sample(pool, k)


def build_training_scenario(difficulty: str = "INTERMEDIATE", seed: int = 42) -> Dict[str, Any]:
    """
    Pure training-only scenario engine.
    - No real-world telemetry
    - No classified framing
    - Difficulty changes inject pressure + ambiguity

    Output is a dict safe for GUI + logging.
    """
    d = normalize_difficulty(difficulty)
    prof = get_profile(d)
    rng = random.Random(int(seed))

    # Difficulty tuning knobs
    if d == "BEGINNER":
        inject_count = 1
        ambiguity = 0.2
        time_pressure = 0.3
        severity_bias = ["LOW", "MEDIUM", "MEDIUM", "HIGH"]
    elif d == "ADVERSARIAL":
        inject_count = 3
        ambiguity = 0.75
        time_pressure = 0.8
        severity_bias = ["MEDIUM", "HIGH", "HIGH", "CRIT"]
    else:
        inject_count = 2
        ambiguity = 0.45
        time_pressure = 0.55
        severity_bias = ["LOW", "MEDIUM", "HIGH", "HIGH"]

    domains = ["CYBER", "COMMS", "EMS", "OPTICAL", "SEISMIC", "RADIATION"]

    inject_pool = [
        "CROSS_DOMAIN_CONFUSION",
        "FALSE_POSITIVE_PRESSURE",
        "SENSOR_OUTAGE_CHAIN",
        "SLOW_DRIFT_DETECTION",
        "NOISY_TELEMETRY_BURST",
        "OPERATOR_DISTRACTION",
    ]
    injects = _pick(inject_pool, rng, inject_count)

    title = f"GLL War Room Training Scenario — {prof['label']}"

    intent = (
        "Train fusion triage: detect multi-domain pressure, preserve integrity, "
        "and communicate commander-grade decisions under time constraints."
    )

    objectives = [
        "Detect and describe the anomaly pattern without overfitting.",
        "Confirm integrity gate status (SIS/SPS/OSL) before counting training.",
        "Produce a short commander-ready summary with recommended actions.",
    ]

    expected_actions = [
        "Check integrity/SPS posture first (GREEN required for ‘counted’ training).",
        "Identify top 3 contributing signals and why they matter.",
        "Call out what is unknown and what would reduce uncertainty.",
        "Recommend next collection/verification steps (training-safe).",
    ]

    # Timeline builder: 6 steps, minutes 0..30
    tl: List[ScenarioEvent] = []
    for step in range(6):
        t_min = step * 6
        domain = rng.choice(domains)

        sev = rng.choice(severity_bias)

        if rng.random() < ambiguity:
            label = "Ambiguous spike"
            notes = "Signals conflict across domains; avoid single-sensor conclusions."
        else:
            label = "Consistent anomaly"
            notes = "Signals align across at least two indicators."

        if rng.random() < time_pressure:
            notes += " Time pressure elevated; prioritize clear, defensible callouts."

        tl.append(
            ScenarioEvent(
                t_min=t_min,
                domain=domain,
                label=label,
                severity=sev,
                notes=notes,
            )
        )

    scenario = Scenario(
        scenario_version=1,
        generated_at=_utc_now(),
        difficulty=d,
        seed=int(seed),
        title=title,
        intent=intent,
        objectives=objectives,
        injects=injects,
        expected_operator_actions=expected_actions,
        timeline=tl,
    )

    out = asdict(scenario)
    out["difficulty_profile"] = prof
    # Flatten timeline events for JSON friendliness
    out["timeline"] = [asdict(e) for e in tl]
    return out


if __name__ == "__main__":
    import json

    print(json.dumps(build_training_scenario("ADVERSARIAL", 99), indent=2))

