# src/apps/gui/training_dashboard_app.py
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# --- Path hygiene (Streamlit import chaos insurance) ---
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _write_json(path: Path, obj: Any) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _sessions_path_candidates() -> List[Path]:
    return [
        SRC_DIR / "docs" / "training" / "training_sessions.json",
        SRC_DIR / "docs" / "training_sessions.json",
        REPO_ROOT / "docs" / "training" / "training_sessions.json",
        REPO_ROOT / "docs" / "training_sessions.json",
    ]


def _load_sessions() -> Dict[str, Any]:
    for p in _sessions_path_candidates():
        data = _read_json(p, default=None)
        if isinstance(data, dict) and "sessions" in data:
            data["_path"] = str(p)
            return data
        if isinstance(data, list):
            # legacy list-only file
            return {"sessions": data, "_path": str(p)}
    # default new
    default_path = SRC_DIR / "docs" / "training" / "training_sessions.json"
    return {"sessions": [], "_path": str(default_path)}


def _save_sessions(store: Dict[str, Any]) -> str:
    path = Path(store.get("_path") or (SRC_DIR / "docs" / "training" / "training_sessions.json"))
    to_write = {"sessions": store.get("sessions", [])}
    _write_json(path, to_write)
    return str(path)


def _compute_training_curve(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prefer calling training_curve_engine if present; otherwise compute minimal fields.
    """
    # Try your engine first
    try:
        from training_curve_engine import compute_training_curve  # type: ignore

        curve = compute_training_curve(sessions=sessions)  # engine may accept kwargs
        if isinstance(curve, dict):
            return curve
    except TypeError:
        # engine exists but different signature
        try:
            from training_curve_engine import compute_training_curve  # type: ignore

            curve = compute_training_curve()
            if isinstance(curve, dict):
                return curve
        except Exception:
            pass
    except Exception:
        pass

    # Minimal fallback curve
    if not sessions:
        return {
            "AGI": 0.0,
            "improvement_slope": 0.0,
            "difficulty_weighted_average": 0.0,
            "volatility_index": 0.0,
            "sessions": 0,
        }

    scores = []
    for s in sessions[-25:]:
        try:
            scores.append(float(s.get("score", 0.0)))
        except Exception:
            scores.append(0.0)

    avg = sum(scores) / max(len(scores), 1)
    # crude slope: last - first over window
    slope = 0.0
    if len(scores) >= 2:
        slope = (scores[-1] - scores[0]) / max((len(scores) - 1), 1)

    # crude volatility: mean absolute deviation
    mad = sum(abs(x - avg) for x in scores) / max(len(scores), 1)

    return {
        "AGI": round(avg, 2),
        "improvement_slope": round(slope, 3),
        "difficulty_weighted_average": round(avg, 2),
        "volatility_index": round(mad, 3),
        "sessions": len(sessions),
    }


def _resolve_coach_function():
    """
    Try multiple coach module locations. Return a callable or None.
    """
    candidates = [
        # canonical (you created)
        ("src/apps/gui/obasi_training_coach.py", "src.apps.gui.obasi_training_coach"),
        # compatibility dup (you created)
        ("apps/gui/obasi_training_coach.py", "apps.gui.obasi_training_coach"),
        # flat module name if someone imported it oddly
        ("obasi_training_coach.py", "obasi_training_coach"),
    ]

    for _, modname in candidates:
        try:
            mod = __import__(modname, fromlist=["build_obasi_training_coach_speech"])
            fn = getattr(mod, "build_obasi_training_coach_speech", None)
            if callable(fn):
                return fn
        except Exception:
            continue
    return None


def _safe_obasi_message(coach_fn, payload: Dict[str, Any]) -> str:
    """
    Guaranteed to return a string, even if coach_fn is an older signature.
    """
    if coach_fn is None:
        return "OBASI // COACH offline. (Coach module not found.)"

    # Preferred: kwargs
    try:
        msg = coach_fn(**payload)
        return msg if isinstance(msg, str) else json.dumps(msg, indent=2)
    except TypeError:
        # Older function signature (no kwargs / positional only)
        try:
            msg = coach_fn()
            if isinstance(msg, str):
                # add minimal telemetry so it still feels “live”
                msg += "\n\n[Coach Payload]\n" + json.dumps(payload, indent=2)
                return msg
            return json.dumps(msg, indent=2)
        except Exception as e:
            return f"OBASI // COACH error: {e}\n\nPayload:\n{json.dumps(payload, indent=2)}"
    except Exception as e:
        return f"OBASI // COACH error: {e}\n\nPayload:\n{json.dumps(payload, indent=2)}"


def _difficulty_weights(difficulty: str) -> Dict[str, float]:
    d = (difficulty or "INTERMEDIATE").upper()
    # weights used by grading/curve; keep simple + deterministic
    if d == "BEGINNER":
        return {"score_weight": 1.0, "pattern_weight": 0.7, "time_pressure": 0.6}
    if d == "ADVERSARIAL":
        return {"score_weight": 1.0, "pattern_weight": 1.2, "time_pressure": 1.1}
    return {"score_weight": 1.0, "pattern_weight": 1.0, "time_pressure": 1.0}


def main() -> None:
    st.set_page_config(page_title="GLL Training Dashboard", layout="wide")

    st.title("GLL Training Dashboard")
    st.caption("Trainee curve, difficulty control, and Obasi coaching (stable interface).")

    store = _load_sessions()
    sessions: List[Dict[str, Any]] = list(store.get("sessions", []))
    sessions_path = store.get("_path", "unknown")

    with st.sidebar:
        st.subheader("Session Control")
        trainee_name = st.text_input("Trainee name", value="Ghost")
        difficulty = st.selectbox("Difficulty", ["BEGINNER", "INTERMEDIATE", "ADVERSARIAL"], index=1)
        score = st.slider("Session score (0–100)", min_value=0, max_value=100, value=75)
        notes = st.text_area("Notes (optional)", value="", height=80)

        if st.button("Log Session"):
            sess = {
                "ts": _utc_now_iso(),
                "trainee": trainee_name,
                "difficulty": difficulty,
                "score": float(score),
                "notes": notes.strip(),
                "weights": _difficulty_weights(difficulty),
            }
            sessions.append(sess)
            store["sessions"] = sessions
            saved_to = _save_sessions(store)
            st.success(f"Logged. Saved to: {saved_to}")

        st.divider()
        st.write("Sessions file:")
        st.code(str(sessions_path))

    # Compute curve + render top metrics
    curve = _compute_training_curve(sessions)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AGI (0–100)", curve.get("AGI", 0.0))
    c2.metric("Improvement Slope", curve.get("improvement_slope", 0.0))
    c3.metric("Difficulty-Weighted Avg", curve.get("difficulty_weighted_average", curve.get("AGI", 0.0)))
    c4.metric("Volatility Index", curve.get("volatility_index", 0.0))

    st.divider()

    left, right = st.columns([1.2, 1.0])

    with left:
        st.subheader("Recent Sessions")
        if sessions:
            st.dataframe(list(reversed(sessions[-20:])), use_container_width=True)
        else:
            st.info("No sessions logged yet. Log one from the sidebar to start the curve.")

    with right:
        st.subheader("Obasi Coach Panel")
        coach_fn = _resolve_coach_function()

        payload = {
            "trainee_name": (sessions[-1].get("trainee") if sessions else "Ghost"),
            "difficulty": (sessions[-1].get("difficulty") if sessions else "INTERMEDIATE"),
            "agi": curve.get("AGI", 0.0),
            "improvement_slope": curve.get("improvement_slope", 0.0),
            "volatility_index": curve.get("volatility_index", 0.0),
            "difficulty_weighted_average": curve.get("difficulty_weighted_average", curve.get("AGI", 0.0)),
            "last_score": (sessions[-1].get("score") if sessions else None),
            "sessions_count": len(sessions),
            "notes": (sessions[-1].get("notes") if sessions else ""),
        }

        msg = _safe_obasi_message(coach_fn, payload)
        st.code(msg)

    st.divider()
    with st.expander("Debug: curve + payload"):
        st.write("Curve:")
        st.json(curve)
        st.write("Latest coach payload:")
        st.json(payload)


if __name__ == "__main__":
    main()

