from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from demo_lock import is_demo_locked, demo_lock_banner


SRC_GATE_JSON = Path("docs") / "validation" / "fusion_core_regression_latest.json"
OUT_TXT_LATEST = Path("docs") / "briefs" / "week3_operator_summary_latest.txt"
OUT_TXT_STAMPED_TMPL = Path("docs") / "briefs" / "week3_operator_summary_{stamp}.txt"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read_json(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_txt(path: Path, txt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8")


def run_week3_operator_summary() -> Dict[str, Any]:
    """
    Reads fusion_core_regression_latest.json and produces a commander-safe 10-second summary.
    Must never crash (best-effort).
    """
    gate = _safe_read_json(SRC_GATE_JSON) or {}
    verdict = str(gate.get("verdict") or gate.get("status") or "UNKNOWN")
    crashes = int(gate.get("crashes") or 0)

    lines = []
    lines.append("WEEK-3 OPERATOR SUMMARY")
    lines.append(f"generated_at_utc: {_utc_now_iso()}")
    lines.append("")
    lines.append(f"Fusion Core Regression Verdict: {verdict}")
    lines.append(f"Crashes: {crashes}")
    lines.append("")
    lines.append("Operator note: If verdict is FAIL, do not brief as GREEN. Fix regressions first.")
    lines.append("NOTICE: Assessment is probabilistic and bounded; operator judgment applies.")

    if is_demo_locked():
        lines.append("")
        lines.append(demo_lock_banner())

    txt = "\n".join(lines)

    stamped = OUT_TXT_STAMPED_TMPL.as_posix().format(stamp=_stamp())
    stamped_path = Path(stamped)

    _write_txt(OUT_TXT_LATEST, txt)
    _write_txt(stamped_path, txt)

    result: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "source": str(SRC_GATE_JSON),
        "verdict": verdict,
        "crashes": crashes,
        "txt_latest": str(OUT_TXT_LATEST),
        "txt_stamped": str(stamped_path),
    }

    if is_demo_locked():
        result["demo_lock"] = True

    return result


def main() -> int:
    res = run_week3_operator_summary()
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

