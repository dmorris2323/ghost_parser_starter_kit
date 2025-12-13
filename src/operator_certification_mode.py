"""
operator_certification_mode.py

Operator Certification Mode (Training Control)
- Locks difficulty + requires PASS streaks to "certify" an operator at that level.
- Designed to be SAFE and training-only, driven by synthetic sessions.

What it does:
- Reads training sessions (best effort) from:
  - src/docs/training/training_sessions_latest.json
  - docs/training/training_sessions_latest.json
  - (fallback) src/docs/training/training_sessions.json or docs/training/training_sessions.json
- Counts only sessions that are:
  - gate_status == "GREEN" (or gate_ok True), and
  - session_result in {"PASS","OK"} (or score >= threshold)
- Supports lock/unlock of difficulty via a small state file.

Writes:
- docs/training/certification_status_latest.json
- docs/training/certification_status_latest.txt
- docs/training/certification_lock.json  (state)

No scope creep: this does not change scoring, it only evaluates + records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SourcePaths:
    root: Path
    docs_dir: Path
    src_docs_dir: Path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json_any(path: Path) -> Any:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _find_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_sources() -> SourcePaths:
    root = _find_repo_root()
    return SourcePaths(
        root=root,
        docs_dir=root / "docs",
        src_docs_dir=root / "src" / "docs",
    )


def _pick_existing(primary: Path, secondary: Path) -> Path:
    return primary if primary.exists() else secondary


def _normalize_difficulty(x: Any) -> str:
    if x is None:
        return "UNKNOWN"
    s = str(x).strip().upper()
    if s in {"BEGINNER", "INTERMEDIATE", "ADVERSARIAL"}:
        return s
    return s


def _required_streak_for(difficulty: str) -> int:
    # Can be tuned later; keep it strict enough to mean something.
    d = _normalize_difficulty(difficulty)
    if d == "BEGINNER":
        return 3
    if d == "INTERMEDIATE":
        return 5
    if d == "ADVERSARIAL":
        return 7
    return 5


def _load_sessions(srcs: SourcePaths) -> Tuple[List[Dict[str, Any]], str]:
    candidates = [
        srcs.src_docs_dir / "training" / "training_sessions_latest.json",
        srcs.docs_dir / "training" / "training_sessions_latest.json",
        srcs.src_docs_dir / "training" / "training_sessions.json",
        srcs.docs_dir / "training" / "training_sessions.json",
    ]

    for p in candidates:
        data = _read_json_any(p)
        if isinstance(data, dict) and isinstance(data.get("sessions"), list):
            return [s for s in data["sessions"] if isinstance(s, dict)], str(p)
        if isinstance(data, list):
            return [s for s in data if isinstance(s, dict)], str(p)

    return [], "MISSING"


def _session_gate_green(s: Dict[str, Any]) -> bool:
    # Accept multiple shapes so we don't break when your schema evolves.
    gate_status = str(s.get("gate_status", "")).strip().upper()
    if gate_status == "GREEN":
        return True
    if isinstance(s.get("gate_ok"), bool) and s.get("gate_ok") is True:
        return True

    gates = s.get("gates")
    if isinstance(gates, dict):
        # example: {"PRE":{"status":"PASS"},"POST":{"status":"PASS"}}
        pre = gates.get("PRE", {})
        post = gates.get("POST", {})
        pre_ok = str((pre or {}).get("status", "")).upper() in {"PASS", "OK", "GREEN"}
        post_ok = str((post or {}).get("status", "")).upper() in {"PASS", "OK", "GREEN"}
        return pre_ok and post_ok

    return False


def _session_passed(s: Dict[str, Any], difficulty: str) -> bool:
    # Default: explicit result PASS/OK, else fallback to score threshold.
    res = str(s.get("result", s.get("session_result", ""))).strip().upper()
    if res in {"PASS", "OK"}:
        return True

    # If there is a numeric score, enforce difficulty expectations:
    # This ties expectations to difficulty, which is what you asked for.
    score = s.get("score")
    try:
        score_f = float(score)
    except Exception:
        score_f = None

    d = _normalize_difficulty(difficulty)
    # Conservative thresholds:
    # - Beginner: 70+
    # - Intermediate: 80+
    # - Adversarial: 90+
    thresh = 80.0
    if d == "BEGINNER":
        thresh = 70.0
    elif d == "INTERMEDIATE":
        thresh = 80.0
    elif d == "ADVERSARIAL":
        thresh = 90.0

    if score_f is not None:
        return score_f >= thresh

    return False


def _streak_count(sessions: List[Dict[str, Any]], difficulty: str) -> int:
    """
    Count consecutive qualifying sessions from most recent backward.
    Qualifying session = difficulty match AND gate green AND pass.
    """
    d = _normalize_difficulty(difficulty)

    # Most systems append newest last. We'll assume that and walk backward.
    streak = 0
    for s in reversed(sessions):
        sd = _normalize_difficulty(s.get("difficulty", s.get("difficulty_level", "UNKNOWN")))
        if sd != d:
            # If difficulty differs, streak breaks (since you're certifying one level).
            break
        if not _session_gate_green(s):
            break
        if not _session_passed(s, d):
            break
        streak += 1
    return streak


def _lock_path(srcs: SourcePaths) -> Path:
    return srcs.docs_dir / "training" / "certification_lock.json"


def _load_lock_state(srcs: SourcePaths) -> Dict[str, Any]:
    p = _lock_path(srcs)
    data = _read_json_any(p)
    if isinstance(data, dict):
        return data
    return {
        "enabled": False,
        "locked_difficulty": None,
        "updated_at": None,
    }


def set_certification_lock(*, enabled: bool, locked_difficulty: Optional[str] = None) -> Dict[str, Any]:
    srcs = _resolve_sources()
    state = _load_lock_state(srcs)
    state["enabled"] = bool(enabled)
    state["locked_difficulty"] = _normalize_difficulty(locked_difficulty) if locked_difficulty else None
    state["updated_at"] = _utc_now_iso()
    _write_json(_lock_path(srcs), state)
    return {"status": "OK", "lock_state": state, "path": str(_lock_path(srcs))}


def evaluate_certification(*, target_difficulty: str, operator_name: str = "OPERATOR") -> Dict[str, Any]:
    srcs = _resolve_sources()
    sessions, sessions_path = _load_sessions(srcs)

    d = _normalize_difficulty(target_difficulty)
    req = _required_streak_for(d)
    streak = _streak_count(sessions, d)

    certified = streak >= req

    # Outputs
    out_json = srcs.docs_dir / "training" / "certification_status_latest.json"
    out_txt = srcs.docs_dir / "training" / "certification_status_latest.txt"

    status = {
        "generated_at": _utc_now_iso(),
        "operator": operator_name,
        "target_difficulty": d,
        "required_streak": req,
        "current_streak": streak,
        "certified": certified,
        "sessions_source": sessions_path,
        "lock_state": _load_lock_state(srcs),
        "notes": [
            "Only counts sessions with GREEN gates (or equivalent) and PASS (or score threshold).",
            "Streak is evaluated from most recent backward.",
            "This is training-only; it does not change scoring or simulation behavior.",
        ],
    }

    _write_json(out_json, status)
    _write_txt(out_txt, _render_txt(status))

    return {
        "status": "OK",
        "certified": certified,
        "required_streak": req,
        "current_streak": streak,
        "paths": {"json": str(out_json), "txt": str(out_txt)},
    }


def _render_txt(status: Dict[str, Any]) -> str:
    lines = []
    lines.append("GLL OPERATOR CERTIFICATION STATUS")
    lines.append(f"Generated: {status.get('generated_at', 'UNKNOWN')}")
    lines.append("")
    lines.append(f"Operator: {status.get('operator', 'UNKNOWN')}")
    lines.append(f"Target difficulty: {status.get('target_difficulty', 'UNKNOWN')}")
    lines.append(f"Required streak: {status.get('required_streak', 0)}")
    lines.append(f"Current streak: {status.get('current_streak', 0)}")
    lines.append(f"Certified: {status.get('certified', False)}")
    lines.append("")
    lines.append("Lock state:")
    try:
        lines.append(json.dumps(status.get("lock_state", {}), indent=2))
    except Exception:
        lines.append(str(status.get("lock_state", {})))
    lines.append("")
    lines.append(f"Sessions source: {status.get('sessions_source', 'UNKNOWN')}")
    lines.append("")
    lines.append("Notes:")
    for n in status.get("notes", []):
        lines.append(f"- {n}")
    return "\n".join(lines)


def main() -> int:
    # CLI-like behavior without touching ghost_cli.py
    # Example:
    #   python src/operator_certification_mode.py eval ADVERSARIAL Ghost
    #   python src/operator_certification_mode.py lock on ADVERSARIAL
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/operator_certification_mode.py eval <DIFFICULTY> [OPERATOR_NAME]")
        print("  python src/operator_certification_mode.py lock <on|off> [DIFFICULTY]")
        return 2

    cmd = sys.argv[1].strip().lower()

    if cmd == "eval":
        if len(sys.argv) < 3:
            print("Missing difficulty.")
            return 2
        difficulty = sys.argv[2]
        operator = sys.argv[3] if len(sys.argv) >= 4 else "OPERATOR"
        result = evaluate_certification(target_difficulty=difficulty, operator_name=operator)
        print(json.dumps(result, indent=2))
        return 0

    if cmd == "lock":
        if len(sys.argv) < 3:
            print("Missing on|off.")
            return 2
        onoff = sys.argv[2].strip().lower()
        enabled = onoff in {"on", "true", "1", "yes"}
        difficulty = sys.argv[3] if len(sys.argv) >= 4 else None
        result = set_certification_lock(enabled=enabled, locked_difficulty=difficulty)
        print(json.dumps(result, indent=2))
        return 0

    print("Unknown command:", cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

