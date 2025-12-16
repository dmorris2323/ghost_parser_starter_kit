from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# -------------------------------------------------
# Paths
# -------------------------------------------------
DOCS_VALIDATION = Path("docs") / "validation"
LATEST_JSON = DOCS_VALIDATION / "fusion_core_regression_latest.json"
LATEST_TXT = DOCS_VALIDATION / "fusion_core_regression_latest.txt"

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    DOCS_VALIDATION.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    stamped_json = DOCS_VALIDATION / f"fusion_core_regression_{ts}.json"
    stamped_txt = DOCS_VALIDATION / f"fusion_core_regression_{ts}.txt"

    with LATEST_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with stamped_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with LATEST_TXT.open("w", encoding="utf-8") as f:
        f.write(f"Fusion Core Regression Verdict: {payload['verdict']}\n")

    with stamped_txt.open("w", encoding="utf-8") as f:
        f.write(f"Fusion Core Regression Verdict: {payload['verdict']}\n")

    return {
        "latest_json": str(LATEST_JSON),
        "latest_txt": str(LATEST_TXT),
        "stamped_json": str(stamped_json),
        "stamped_txt": str(stamped_txt),
    }

# -------------------------------------------------
# PUBLIC RUNNER (THIS IS WHAT CLI IMPORTS)
# -------------------------------------------------
def run_fusion_core_regression_gate() -> Dict[str, Any]:
    """
    Runs the fusion core regression gate.
    Must NEVER crash the caller.
    """

    verdict = "PASS"
    crashes = 0
    checks = {}

    try:
        # Minimal non-recursive validation check
        from fusion_validation_harness import run_validation

        res = run_validation()
        checks["fusion_validation"] = "PASS" if res.get("status") == "PASS" else "FAIL"
        if checks["fusion_validation"] != "PASS":
            verdict = "FAIL"

    except Exception as e:
        crashes += 1
        checks["fusion_validation"] = f"ERROR: {e}"
        verdict = "FAIL"

    payload = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "crashes": crashes,
        "checks": checks,
    }

    paths = _write_outputs(payload)
    payload.update(paths)
    return payload

# -------------------------------------------------
# CLI ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    result = run_fusion_core_regression_gate()
    print(json.dumps(result, indent=2))

