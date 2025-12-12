# scenario_engine.py
# War Room Scenario Engine (SAFE)
# Generates a synthetic telemetry bundle + injects fictional patterns based on difficulty profile.

import json
import random
from pathlib import Path
from datetime import datetime

from synthetic_signal_generator import build_synthetic_fusion_bundle
from pattern_injection_engine import inject_pattern
from difficulty_scaling_engine import compute_difficulty_profile, get_default_difficulty_config
from training_session_store import append_session


PATTERNS = ["drift", "latency", "outage", "storm", "cross"]


def _load_bundle(json_path: str) -> dict:
    with open(json_path, "r") as f:
        return json.load(f)


def _write(path: Path, payload: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return str(path)


def generate_scenario(difficulty: str | None = None, seed: int | None = None) -> dict:
    """
    Returns:
      scenario_id, difficulty_used, patterns_used, scenario_json_path, telemetry_json_path, note
    """
    if seed is not None:
        random.seed(seed)

    profile = compute_difficulty_profile()
    cfg = get_default_difficulty_config()

    recommended = profile["recommendation"]["recommended_level"]
    difficulty_used = (difficulty or recommended).upper()
    if difficulty_used not in cfg:
        difficulty_used = recommended

    level_cfg = cfg[difficulty_used]
    max_patterns = int(level_cfg.get("max_patterns", 1))
    noise_factor = float(level_cfg.get("noise_factor", 0.5))

    # Build base telemetry
    base = build_synthetic_fusion_bundle()
    bundle = _load_bundle(base["json_path"])

    # Inject N patterns
    patterns_used = random.sample(PATTERNS, k=min(max_patterns, len(PATTERNS)))
    evidence = []
    for p in patterns_used:
        bundle, record_path = inject_pattern(p, bundle)
        evidence.append(record_path)

    scenario_id = f"sc_{int(datetime.utcnow().timestamp())}"
    out_dir = Path("src/docs/scenarios")
    telemetry_path = out_dir / f"{scenario_id}_telemetry.json"
    scenario_path = out_dir / f"{scenario_id}_scenario.json"
    latest_path = out_dir / "scenario_latest.json"

    # Write telemetry (modified)
    _write(telemetry_path, bundle)

    # Scenario packet
    packet = {
        "scenario_id": scenario_id,
        "generated_at": datetime.utcnow().isoformat(),
        "difficulty_used": difficulty_used,
        "difficulty_recommended": recommended,
        "difficulty_config": level_cfg,
        "patterns_used": patterns_used,
        "pattern_evidence": evidence,
        "noise_factor_note": f"noise_factor={noise_factor} is a synthetic tuning knob only.",
        "tasking": [
            "1) Identify the dominant anomaly pattern(s).",
            "2) State whether this is likely sensor fault vs multi-sensor event (synthetic-only).",
            "3) Decide OSL posture (GREEN/AMBER/RED) and justify.",
            "4) Write a 5-sentence commander summary."
        ],
        "telemetry_json_path": str(telemetry_path),
    }
    _write(scenario_path, packet)
    _write(latest_path, packet)

    return {
        "scenario_id": scenario_id,
        "difficulty_used": difficulty_used,
        "difficulty_recommended": recommended,
        "patterns_used": patterns_used,
        "scenario_json_path": str(scenario_path),
        "telemetry_json_path": str(telemetry_path),
        "latest_json_path": str(latest_path),
        "note": "SAFE synthetic scenario for training only."
    }


def grade_scenario_result(
    scenario_id: str,
    difficulty_used: str,
    score: float,
    notes: str = "",
    trainee: str = "Ghost",
) -> dict:
    """
    Logs a completed scenario attempt to training sessions store.
    """
    payload = {
        "scenario_id": scenario_id,
        "difficulty": difficulty_used,
        "score": float(score),
        "trainee": trainee,
        "notes": notes[:500],
        "source": "war_room_scenario_engine",
    }
    return append_session(payload)

