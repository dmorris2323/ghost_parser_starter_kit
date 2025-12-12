"""
training_curve_engine.py

Hardening:
- Works from repo root, src/, Streamlit, CLI (stable repo-root resolution).
- Reads sessions from: src/docs/training/training_sessions.json
- Writes curve to:     src/docs/training/training_curve_latest.json

Single source of truth for difficulty weights:
- imports from difficulty_scaling_engine
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from difficulty_scaling_engine import normalize_difficulty, get_weight


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _docs_training_dir() -> Path:
    return _repo_root() / "src" / "docs" / "training"


def _sessions_path() -> Path:
    return _docs_training_dir() / "training_sessions.json"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _std(vals: List[float]) -> float:
    if not vals:
        return 0.0
    m = sum(vals) / len(vals)
    var = sum((x - m) ** 2 for x in vals) / len(vals)
    return math.sqrt(var)


def load_sessions() -> List[Dict[str, Any]]:
    p = _sessions_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text())
        sessions = raw.get("sessions", [])
        if isinstance(sessions, list):
            return sessions
        return []
    except Exception:
        return []


def compute_training_curve() -> Dict[str, Any]:
    sessions = load_sessions()
    if not sessions:
        curve = {
            "generated_at": _utc_iso(),
            "total_sessions": 0,
            "AGI": 0.0,
            "improvement_slope": 0.0,
            "difficulty_weighted_average": 0.0,
            "volatility_index": 0.0,
            "paths": {},
        }
        _write_curve(curve)
        return curve

    # Sort by ts_utc if present
    sessions = sorted(sessions, key=lambda s: str(s.get("ts_utc", "")))

    scores = [float(s.get("score", 0.0)) for s in sessions]
    diffs = [normalize_difficulty(str(s.get("difficulty", "INTERMEDIATE"))) for s in sessions]
    weights = [float(s.get("difficulty_weight") or get_weight(d)) for d, s in zip(diffs, sessions)]

    wsum = sum(weights) or 1.0
    dwa = sum(sc * w for sc, w in zip(scores, weights)) / wsum

    last = scores[-1]
    agi = (0.55 * last) + (0.45 * dwa)
    agi = _clamp(agi, 0.0, 100.0)

    n = len(scores)
    if n >= 2:
        xs = list(range(n))
        xmean = sum(xs) / n
        ymean = sum(scores) / n
        num = sum((x - xmean) * (y - ymean) for x, y in zip(xs, scores))
        den = sum((x - xmean) ** 2 for x in xs) or 1.0
        slope = num / den
    else:
        slope = 0.0

    vol = _std(scores[-10:])

    curve = {
        "generated_at": _utc_iso(),
        "total_sessions": len(scores),
        "AGI": round(float(agi), 3),
        "improvement_slope": round(float(slope), 3),
        "difficulty_weighted_average": round(float(dwa), 3),
        "volatility_index": round(float(vol), 3),
        "last_session": {
            "ts_utc": sessions[-1].get("ts_utc"),
            "difficulty": diffs[-1],
            "difficulty_weight": weights[-1],
            "score": scores[-1],
        },
    }
    _write_curve(curve)
    return curve


def _write_curve(curve: Dict[str, Any]) -> None:
    out_dir = _docs_training_dir()
    _safe_mkdir(out_dir)
    out_path = out_dir / "training_curve_latest.json"
    out_path.write_text(json.dumps(curve, indent=2))
    curve["paths"] = {"json": str(out_path)}


if __name__ == "__main__":
    c = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {c.get('paths', {}).get('json')}")
    print(f"  Total sessions: {c.get('total_sessions')}")
    print(f"  AGI: {c.get('AGI')}")
    print(f"  Improvement slope: {c.get('improvement_slope')}")
    print(f"  Difficulty-weighted avg: {c.get('difficulty_weighted_average')}")
    print(f"  Volatility index: {c.get('volatility_index')}")

