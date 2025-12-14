# src/obasi_training_coach.py
"""
obasi_training_coach.py

Stabilized Obasi training coach interface.

Hard contract:
- build_obasi_training_coach_speech(**payload) -> str
- Accepts any kwargs (ignores unknown keys)
- Never raises (always returns a safe string)

This is intentionally "boring but unbreakable" for Day 71 hardening.
Cinematic intro remains post–Day 100.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _as_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _safe_str(x: Any, default: str = "") -> str:
    try:
        s = str(x)
        return s if s else default
    except Exception:
        return default


def _difficulty_label(d: str) -> str:
    d = _safe_str(d, "UNKNOWN").upper().strip()
    if d in {"BEGINNER", "INTERMEDIATE", "ADVANCED", "ADVERSARIAL"}:
        return d
    return "UNKNOWN"


def build_obasi_training_coach_speech(**payload: Any) -> str:
    """
    Stable string output. Never crashes.

    Expected (optional) fields:
      trainee_name: str
      difficulty: str
      gate_status: str (GREEN/YELLOW/RED/UNKNOWN)
      curve: dict {AGI, improvement_slope, difficulty_weighted_average, volatility_index}
      sessions: list[dict]
      training_feedback: dict
    """
    try:
        trainee = _safe_str(payload.get("trainee_name", "Operator"), "Operator")
        difficulty = _difficulty_label(payload.get("difficulty", "UNKNOWN"))
        gate_status = _safe_str(payload.get("gate_status", "UNKNOWN"), "UNKNOWN").upper().strip()

        curve: Dict[str, Any] = payload.get("curve") if isinstance(payload.get("curve"), dict) else {}
        agi = _as_float(curve.get("AGI", 0.0), 0.0)
        slope = _as_float(curve.get("improvement_slope", 0.0), 0.0)
        vol = _as_float(curve.get("volatility_index", 0.0), 0.0)

        sessions: List[Dict[str, Any]] = payload.get("sessions") if isinstance(payload.get("sessions"), list) else []
        n_sessions = len(sessions)

        fb: Dict[str, Any] = payload.get("training_feedback") if isinstance(payload.get("training_feedback"), dict) else {}
        fb_line = ""
        if fb:
            rec = _safe_str(fb.get("recommended_difficulty", fb.get("recommendation", "")), "")
            patt = _safe_str(fb.get("recommended_pattern", fb.get("pattern_id", "")), "")
            if rec or patt:
                fb_line = f"\nNext recommendation: difficulty={rec or 'N/A'} pattern={patt or 'N/A'}"

        # Coaching logic (simple + deterministic)
        trend = "improving" if slope > 0.2 else ("declining" if slope < -0.2 else "stable")
        volatility_flag = "HIGH" if vol >= 15 else ("MED" if vol >= 8 else "LOW")

        msg = (
            f"OBASI COACH — {trainee}\n"
            f"Time: {_utc_now_iso()}\n"
            f"Difficulty: {difficulty} | Gate: {gate_status}\n"
            f"Sessions logged: {n_sessions}\n"
            f"AGI: {agi:.1f} | Slope: {slope:.2f} ({trend}) | Volatility: {vol:.2f} ({volatility_flag})\n"
        )

        # Actionable guidance (needle-moving)
        if gate_status not in {"GREEN", "PASS"}:
            msg += (
                "\nGate is not GREEN. Don’t chase performance right now.\n"
                "- Run SIS/SPS integrity checks\n"
                "- Fix the failing signal (imports, schema, missing files)\n"
                "- Re-run baseline validation (INTERMEDIATE, no injection)\n"
            )
        else:
            if trend == "declining" and difficulty in {"ADVANCED", "ADVERSARIAL"}:
                msg += (
                    "\nYou’re pushing hard and it’s costing stability.\n"
                    "- Drop one notch (ADVANCED→INTERMEDIATE) for 1–2 runs\n"
                    "- Rebuild baseline PASS, then re-introduce injection\n"
                )
            elif volatility_flag == "HIGH":
                msg += (
                    "\nVolatility is high. That’s useful *only* if it’s controlled.\n"
                    "- Prefer baseline+delta (with injection) to verify expected direction\n"
                    "- If delta is chaotic, tighten scoring thresholds before adding features\n"
                )
            else:
                msg += (
                    "\nSystem looks controlled. Increase difficulty only with a measurable reason.\n"
                    "- Run validation with a known pattern (e.g., CROSS_DOMAIN_CONFUSION)\n"
                    "- Confirm delta_vs_baseline moves in the expected direction\n"
                )

        if fb_line:
            msg += fb_line

        return msg

    except Exception as e:
        # Hard fail-safe: always return a string
        return f"OBASI COACH (SAFE MODE): Coach rendering error: {e.__class__.__name__}: {e}"

