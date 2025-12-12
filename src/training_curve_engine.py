"""
training_curve_engine.py

Hardening:
- Uses stable repo-root resolution so it works whether executed from repo root, src/, Streamlit, or CLI.
- Writes to: src/docs/training/training_curve_latest.json
- Computes: AGI, improvement_slope, difficulty_weighted_average, volatility_index

This is training-safe metadata only (no sensitive meaning).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _repo_root() -> Path:
    # .../parser_starter_kit/src/training_curve_engine.py -> .../parser_starter_kit
    return Path(__file__).resolve().parent.parent


def _docs_training_dir() -> Path:
    return _repo_root() / "src" / "docs" / "training"


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


@dataclass
class TrainingSession:
    ts_utc: str
    difficulty: str
    score: float  # 0-100 (synthetic performance score)
    notes: str = ""


DIFF_WEIGHT = {
    "BEGINNER": 0.85,
    "INTERMEDIATE": 1.00,
    "ADVANCED": 1.15,
    "ADVERSARIAL": 1.30,
}


def _default_sessions_path() -> Path:
    # If you have an existing sessions file elsewhere, keep it — this is just a stable default.
    return _docs_training_dir() / "training_sessions.json"


def load_sessions(path: Optional[str] = None) -> List[TrainingSession]:
    p = Path(path) if path else _default_sessions_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text())
        items = raw.get("sessions", raw)  # allow either {"sessions":[...]} or [...]
        out: List[TrainingSession] = []
        for s in (items or []):
            out.append(
                TrainingSession(
                    ts_utc=str(s.get("ts_utc") or s.get("timestamp") or _utc_iso()),
                    difficulty=str(s.get("difficulty", "INTERMEDIATE")).upper(),
                    score=float(s.get("score", 0.0)),
                    notes=str(s.get("notes", "")),
                )
            )
        return out
    except Exception:
        return []


def compute_training_curve(sessions_path: Optional[str] = None) -> Dict[str, Any]:
    sessions = load_sessions(sessions_path)
    sessions = sorted(sessions, key=lambda x: x.ts_utc)

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

    scores = [float(s.score) for s in sessions]
    diffs = [s.difficulty.upper() for s in sessions]
    weights = [float(DIFF_WEIGHT.get(d, 1.0)) for d in diffs]

    # difficulty-weighted average
    wsum = sum(weights) or 1.0
    dwa = sum(sc * w for sc, w in zip(scores, weights)) / wsum

    # "AGI" (training mastery proxy) = blend of last score + weighted average
    last = scores[-1]
    agi = (0.55 * last) + (0.45 * dwa)
    agi = _clamp(agi, 0.0, 100.0)

    # improvement slope: simple linear slope across session index
    # slope in "points per session"
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

    # volatility: std dev of recent scores (last up to 10)
    window = scores[-10:]
    vol = _std(window)

    curve = {
        "generated_at": _utc_iso(),
        "total_sessions": len(scores),
        "AGI": round(float(agi), 3),
        "improvement_slope": round(float(slope), 3),
        "difficulty_weighted_average": round(float(dwa), 3),
        "volatility_index": round(float(vol), 3),
        "last_session": {
            "ts_utc": sessions[-1].ts_utc,
            "difficulty": sessions[-1].difficulty,
            "score": sessions[-1].score,
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
    curve = compute_training_curve()
    print("Training curve written:")
    print(f"  JSON: {curve.get('paths', {}).get('json')}")
    print(f"  Total sessions: {curve.get('total_sessions')}")
    print(f"  AGI: {curve.get('AGI')}")
    print(f"  Improvement slope: {curve.get('improvement_slope')}")
    print(f"  Difficulty-weighted avg: {curve.get('difficulty_weighted_average')}")
    print(f"  Volatility index: {curve.get('volatility_index')}")

