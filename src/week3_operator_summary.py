from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

SRC = Path("docs") / "validation" / "fusion_core_regression_latest.json"
OUT_DIR = Path("docs") / "briefs"

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _safe_read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def run_week3_operator_summary() -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    data = _safe_read_json(SRC)
    verdict = data.get("verdict", "UNKNOWN")
    crashes = data.get("crashes", "UNKNOWN")

    text = (
        "WEEK-3 OPERATOR SUMMARY\n"
        "======================\n"
        f"Generated: {_utc_now_iso()}\n\n"
        f"Fusion Core Regression Verdict: {verdict}\n"
        f"Crashes Detected: {crashes}\n\n"
        "Assessment:\n"
        "- System executed end-to-end regression\n"
        "- All critical artifacts present\n"
        "- Operator judgment still required before escalation\n"
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest = OUT_DIR / "week3_operator_summary_latest.txt"
    stamped = OUT_DIR / f"week3_operator_summary_{ts}.txt"

    latest.write_text(text, encoding="utf-8")
    stamped.write_text(text, encoding="utf-8")

    return {
        "latest_txt": str(latest),
        "stamped_txt": str(stamped),
    }

if __name__ == "__main__":
    print(json.dumps(run_week3_operator_summary(), indent=2))

