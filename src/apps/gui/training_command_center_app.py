# src/apps/gui/training_command_center_app.py
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _sessions_path() -> Path:
    # canonical
    p = SRC_DIR / "docs" / "training" / "training_sessions.json"
    if p.exists():
        return p
    # fallback
    return SRC_DIR / "docs" / "training_sessions.json"


def _load_sessions() -> List[Dict[str, Any]]:
    p = _sessions_path()
    data = _read_json(p, default={"sessions": []})
    if isinstance(data, dict) and "sessions" in data:
        return list(data["sessions"])
    if isinstance(data, list):
        return data
    return []


def _compute_curve(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        from training_curve_engine import compute_training_curve  # type: ignore

        curve = compute_training_curve(sessions=sessions)
        if isinstance(curve, dict):
            return curve
    except TypeError:
        try:
            from training_curve_engine import compute_training_curve  # type: ignore

            curve = compute_training_curve()
            if isinstance(curve, dict):
                return curve
        except Exception:
            pass
    except Exception:
        pass

    if not sessions:
        return {"AGI": 0.0, "improvement_slope": 0.0, "difficulty_weighted_average": 0.0, "volatility_index": 0.0}

    scores = [float(s.get("score", 0.0) or 0.0) for s in sessions[-25:]]
    avg = sum(scores) / max(len(scores), 1)
    slope = (scores[-1] - scores[0]) / max((len(scores) - 1), 1) if len(scores) >= 2 else 0.0
    mad = sum(abs(x - avg) for x in scores) / max(len(scores), 1)

    return {
        "AGI": round(avg, 2),
        "improvement_slope": round(slope, 3),
        "difficulty_weighted_average": round(avg, 2),
        "volatility_index": round(mad, 3),
    }


def _resolve_coach_function():
    candidates = [
        ("src.apps.gui.obasi_training_coach",),
        ("apps.gui.obasi_training_coach",),
        ("obasi_training_coach",),
    ]
    for (modname,) in candidates:
        try:
            mod = __import__(modname, fromlist=["build_obasi_training_coach_speech"])
            fn = getattr(mod, "build_obasi_training_coach_speech", None)
            if callable(fn):
                return fn
        except Exception:
            continue
    return None


def _safe_coach(coach_fn, payload: Dict[str, Any]) -> str:
    if coach_fn is None:
        return "OBASI // COACH offline. (Coach module not found.)"
    try:
        out = coach_fn(**payload)
        return out if isinstance(out, str) else json.dumps(out, indent=2)
    except TypeError:
        # older signature
        try:
            out = coach_fn()
            if isinstance(out, str):
                out += "\n\n[Coach Payload]\n" + json.dumps(payload, indent=2)
                return out
            return json.dumps(out, indent=2)
        except Exception as e:
            return f"OBASI // COACH error: {e}\n\nPayload:\n{json.dumps(payload, indent=2)}"
    except Exception as e:
        return f"OBASI // COACH error: {e}\n\nPayload:\n{json.dumps(payload, indent=2)}"


def main() -> None:
    st.set_page_config(page_title="GLL Training Command Center", layout="wide")

    st.title("GLL Training Command Center")
    st.caption("A commander view: live curve metrics + Obasi guidance, no import fragility.")

    sessions = _load_sessions()
    curve = _compute_curve(sessions)

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("AGI", curve.get("AGI", 0.0))
    top2.metric("Slope", curve.get("improvement_slope", 0.0))
    top3.metric("Diff-W Avg", curve.get("difficulty_weighted_average", curve.get("AGI", 0.0)))
    top4.metric("Volatility", curve.get("volatility_index", 0.0))

    left, right = st.columns([1.1, 1.0])

    with left:
        st.subheader("Sessions (latest 25)")
        st.dataframe(list(reversed(sessions[-25:])), use_container_width=True)

    with right:
        st.subheader("Obasi Live Guidance")
        coach_fn = _resolve_coach_function()
        latest = sessions[-1] if sessions else {}

        payload = {
            "trainee_name": latest.get("trainee", "Ghost"),
            "difficulty": latest.get("difficulty", "INTERMEDIATE"),
            "agi": curve.get("AGI", 0.0),
            "improvement_slope": curve.get("improvement_slope", 0.0),
            "volatility_index": curve.get("volatility_index", 0.0),
            "difficulty_weighted_average": curve.get("difficulty_weighted_average", curve.get("AGI", 0.0)),
            "last_score": latest.get("score", None),
            "sessions_count": len(sessions),
            "notes": latest.get("notes", ""),
            "timestamp": _utc_now_iso(),
        }

        msg = _safe_coach(coach_fn, payload)
        st.code(msg)

    with st.expander("Debug"):
        st.json({"curve": curve, "latest_payload": payload})


if __name__ == "__main__":
    main()

