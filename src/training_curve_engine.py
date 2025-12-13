# src/training_curve_engine.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Any, Dict, List, Optional

from training_grading_weights import normalize_difficulty, get_profile
from training_session_store import load_sessions, DEFAULT_SESSIONS_PATH
from training_grading_weights import compute_weighted_score


OUTPUT_LATEST = Path("src/docs/training/training_curve_latest.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mean(xs: List[float]) -> float:
    if not xs:
        return 0.0
    return sum(xs) / float(len(xs))


def _std(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    var = sum((x - m) ** 2 for x in xs) / float(len(xs) - 1)
    return sqrt(var)


def _linear_slope(y: List[float]) -> float:
    """
    Simple slope of y over evenly spaced x = 0..n-1
    Returns 0 if insufficient points.
    """
    n = len(y)
    if n < 2:
        return 0.0
    x = list(range(n))
    x_mean = _mean([float(i) for i in x])
    y_mean = _mean(y)
    num = sum((float(x[i]) - x_mean) * (y[i] - y_mean) for i in range(n))
    den = sum((float(x[i]) - x_mean) ** 2 for i in range(n))
    if den == 0.0:
        return 0.0
    return num / den


def _session_score(session: Dict[str, Any]) -> float:
    rub = session.get("rubric", {}) or {}
    difficulty = normalize_difficulty(session.get("difficulty"))
    base = compute_weighted_score(
        accuracy=float(rub.get("accuracy", 0.0)),
        reasoning=float(rub.get("reasoning", 0.0)),
        stability=float(rub.get("stability", 0.0)),
        speed=float(rub.get("speed", 0.0)),
        difficulty=difficulty,
    )
    return float(base)


def compute_training_curve(
    *,
    sessions_path: Path = DEFAULT_SESSIONS_PATH,
    output_path: Path = OUTPUT_LATEST,
) -> Dict[str, Any]:
    sessions = load_sessions(sessions_path)

    valid = [s for s in sessions if bool(s.get("session_valid"))]

    scores = [_session_score(s) for s in valid]
    difficulties = [normalize_difficulty(s.get("difficulty")) for s in valid]

    agi = round(_mean(scores), 2)
    slope = round(_linear_slope(scores), 3)
    volatility = round(_std(scores), 3)

    # difficulty-weighted average (using score_multiplier)
    weighted_scores = []
    weights = []
    for sc, d in zip(scores, difficulties):
        prof = get_profile(d)
        w = float(prof.score_multiplier)
        weighted_scores.append(sc * w)
        weights.append(w)

    dwa = 0.0
    if weights and sum(weights) > 0:
        dwa = round(sum(weighted_scores) / sum(weights), 2)

    curve = {
        "version": 3,
        "generated_at": _utc_now(),
        "sessions_total": len(sessions),
        "sessions_valid": len(valid),
        # Keys your GUI expects:
        "AGI": agi,
        "improvement_slope": slope,
        "difficulty_weighted_average": dwa,
        "volatility_index": volatility,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(curve, indent=2))
    return curve


def main() -> int:
    curve = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {OUTPUT_LATEST}")
    print(f"  Total sessions: {curve['sessions_total']}")
    print(f"  Valid sessions: {curve['sessions_valid']}")
    print(f"  AGI: {curve['AGI']}")
    print(f"  Improvement slope: {curve['improvement_slope']}")
    print(f"  Difficulty-weighted avg: {curve['difficulty_weighted_average']}")
    print(f"  Volatility index: {curve['volatility_index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

