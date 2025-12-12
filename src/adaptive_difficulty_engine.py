"""
adaptive_difficulty_engine.py

Deterministic adaptive difficulty recommender.
SAFE: training only (synthetic).
"""

from typing import Any, Dict, List

from difficulty_control_engine import get_difficulty_profile
from training_config import load_training_config

DIFF_ORDER = ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"]


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _compute_slope(scores: List[float]) -> float:
    if len(scores) < 2:
        return 0.0
    return (scores[-1] - scores[0]) / max(1, len(scores) - 1)


def _compute_volatility(scores: List[float]) -> float:
    if not scores:
        return 0.0
    avg = sum(scores) / len(scores)
    mad = sum(abs(s - avg) for s in scores) / len(scores)
    return mad


def recommend_difficulty(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    cfg = load_training_config()
    policy = cfg.get("auto_policy", {})
    min_n = int(policy.get("min_sessions_for_adapt", 4))
    promote_if = float(policy.get("promote_if_slope_gte", 1.0))
    demote_if = float(policy.get("demote_if_slope_lte", -1.0))
    max_vol_for_promote = float(policy.get("max_volatility_for_promote", 18.0))

    if not sessions:
        return {
            "recommended": "INTERMEDIATE",
            "reason": "No sessions yet; default to INTERMEDIATE baseline.",
            "slope": 0.0,
            "volatility": 0.0,
            "n": 0,
        }

    # Use last N sessions (up to 8)
    tail = sessions[-8:]
    scores = [_safe_float(s.get("score"), 0.0) for s in tail]
    slope = _compute_slope(scores)
    vol = _compute_volatility(scores)

    current = (tail[-1].get("difficulty") or "INTERMEDIATE").upper()
    if current not in DIFF_ORDER:
        current = "INTERMEDIATE"

    idx = DIFF_ORDER.index(current)

    # Decision rules (controlled)
    if len(tail) < min_n:
        return {
            "recommended": current,
            "reason": f"Need >= {min_n} sessions for adaptive moves. Holding {current}.",
            "slope": round(slope, 2),
            "volatility": round(vol, 3),
            "n": len(tail),
        }

    # Promote only if slope strong AND volatility controlled
    if slope >= promote_if and vol <= max_vol_for_promote and idx < len(DIFF_ORDER) - 1:
        nxt = DIFF_ORDER[idx + 1]
        return {
            "recommended": nxt,
            "reason": f"Slope {slope:.2f} >= {promote_if} and volatility {vol:.2f} <= {max_vol_for_promote}. Promote to {nxt}.",
            "slope": round(slope, 2),
            "volatility": round(vol, 3),
            "n": len(tail),
        }

    # Demote if regression strong
    if slope <= demote_if and idx > 0:
        nxt = DIFF_ORDER[idx - 1]
        return {
            "recommended": nxt,
            "reason": f"Slope {slope:.2f} <= {demote_if}. Demote to {nxt} for stabilization reps.",
            "slope": round(slope, 2),
            "volatility": round(vol, 3),
            "n": len(tail),
        }

    # Otherwise hold
    return {
        "recommended": current,
        "reason": "Hold difficulty; trend/volatility do not justify a move.",
        "slope": round(slope, 2),
        "volatility": round(vol, 3),
        "n": len(tail),
    }

