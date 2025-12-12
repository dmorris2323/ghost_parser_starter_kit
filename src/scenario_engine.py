"""
scenario_engine.py

Difficulty-driven scenario generator for training.

Outputs a scenario object (safe synthetic) that can be used by:
- mission_scenario_app.py
- instructor grader
- validation harness

It does NOT create real-world telemetry. It only generates synthetic training artifacts.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from difficulty_scaling_engine import get_profile, normalize_difficulty
from synthetic_signal_generator import build_synthetic_fusion_bundle


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _docs_scenarios_dir() -> Path:
    return _repo_root() / "src" / "docs" / "scenarios"


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def generate_scenario(
    difficulty: str = "INTERMEDIATE",
    seed: int = 42,
    pattern_id: Optional[str] = None,
    pattern_seed: Optional[int] = None,
    write: bool = True,
) -> Dict[str, Any]:
    d = normalize_difficulty(difficulty)
    prof = get_profile(d)

    rng = random.Random(seed)

    # Translate difficulty profile into generator knobs (kept generic and safe).
    # Your synthetic generator may ignore some knobs — that’s fine.
    generator_difficulty = d
    bundle = build_synthetic_fusion_bundle(
        difficulty=generator_difficulty,
        seed=seed,
        pattern_id=pattern_id,
        pattern_seed=pattern_seed if pattern_seed is not None else seed,
        write=True,
    )

    # Scenario metadata for the instructor + trainee
    scenario = {
        "scenario_version": 1,
        "generated_at": _utc_iso(),
        "difficulty": d,
        "difficulty_profile": {
            "weight": prof.weight,
            "noise": prof.noise,
            "anomaly_rate": prof.anomaly_rate,
            "attack_like_rate": prof.attack_like_rate,
            "crit_rate": prof.crit_rate,
            "pattern_intensity_boost": prof.pattern_intensity_boost,
        },
        "seed": seed,
        "pattern_id": pattern_id.upper() if pattern_id else None,
        "training_objectives": _objectives_for(d),
        "operator_prompts": _prompts_for(d, rng),
        "bundle_paths": bundle.get("paths", {}),
        "bundle_stats": bundle.get("stats", {}),
        "injections": bundle.get("injections", []),
    }

    if write:
        out_dir = _docs_scenarios_dir()
        _safe_mkdir(out_dir)
        latest = out_dir / "scenario_latest.json"
        stamped = out_dir / f"scenario_{_stamp()}.json"
        latest.write_text(json.dumps(scenario, indent=2))
        stamped.write_text(json.dumps(scenario, indent=2))
        scenario["paths"] = {"json_latest": str(latest), "json_stamped": str(stamped)}

    return scenario


def _objectives_for(difficulty: str) -> list[str]:
    if difficulty == "BEGINNER":
        return [
            "Identify anomalies vs normal noise.",
            "Explain why trust should move up/down in simple terms.",
            "Call out one likely false positive source.",
        ]
    if difficulty == "INTERMEDIATE":
        return [
            "Correlate cross-domain signals (EMS/COMMS/CYBER).",
            "Recommend a next action (collect, verify, isolate).",
            "Explain alert prioritization clearly.",
        ]
    if difficulty == "ADVANCED":
        return [
            "Detect deception patterns (confusion, saturation, spoofing-like behavior).",
            "Propose mitigations and what evidence you need next.",
            "Maintain disciplined decision-making under pressure.",
        ]
    return [
        "Operate under adversarial pressure without losing process discipline.",
        "Minimize false confidence; demand corroboration.",
        "Recommend containment actions and define success criteria.",
    ]


def _prompts_for(difficulty: str, rng: random.Random) -> list[str]:
    base = [
        "Summarize what’s happening in 3 bullets.",
        "What’s your top risk and why?",
        "What is one thing you would verify next?",
    ]
    if difficulty in ("ADVANCED", "ADVERSARIAL"):
        base += [
            "Assume deception: what could be misleading here?",
            "What would you brief a commander in 30 seconds?",
        ]
    rng.shuffle(base)
    return base[:5]

