"""
base_defense_storyboard_stress.py

Week-2 Base Defense Hardening
Stress Test — Base Defense Storyboard

This stress test is intentionally conservative:
- It does NOT assume the build() function takes special kwargs.
- It validates the standardized "latest" artifact exists and contains required bounded tokens.

Outputs:
- docs/base_defense/base_defense_storyboard_stress_latest.json
- docs/base_defense/base_defense_storyboard_stress_<timestamp>.json
"""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from base_defense_storyboard import build_base_defense_storyboard, write_base_defense_storyboard


OUT_DIR = Path("docs") / "base_defense"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _call_build_safely() -> Dict[str, Any]:
    """
    Calls build_base_defense_storyboard with no assumptions.
    If parameters exist, we pass None for optional-looking params ONLY.
    """
    sig = inspect.signature(build_base_defense_storyboard)
    params = list(sig.parameters.values())

    # No params → call directly
    if len(params) == 0:
        return build_base_defense_storyboard()

    # Try call with no kwargs first (common case if all params have defaults)
    try:
        return build_base_defense_storyboard()  # type: ignore[misc]
    except TypeError:
        pass

    # Build a minimal kwargs dict for params that can accept None safely.
    kwargs: Dict[str, Any] = {}
    for p in params:
        if p.default is not inspect._empty:
            # has a default; skip — the function can use its own default
            continue
        # required param: give it None (safe degraded-input posture)
        kwargs[p.name] = None

    return build_base_defense_storyboard(**kwargs)  # type: ignore[arg-type]


def main() -> None:
    crashes = 0
    violations: List[str] = []
    runs = 0

    required_tokens = ["probabilistic", "bounded", "operator judgment"]

    # Run multiple times to ensure stability (no randomness required)
    for _ in range(5):
        runs += 1
        try:
            rpt = _call_build_safely()
            write_base_defense_storyboard(rpt)

            latest_txt = OUT_DIR / "base_defense_storyboard_latest.txt"
            if not latest_txt.exists():
                violations.append("MISSING_LATEST_TXT")
                continue

            text = latest_txt.read_text(encoding="utf-8").lower()
            for tok in required_tokens:
                if tok not in text:
                    violations.append(f"MISSING_REQUIRED_TOKEN:{tok}")

        except Exception as e:
            crashes += 1
            violations.append(f"CRASH:{e.__class__.__name__}:{e}")

    verdict = "PASS" if crashes == 0 and not violations else "FAIL"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "runs": runs,
        "crashes": crashes,
        "violations": violations,
    }

    latest = OUT_DIR / "base_defense_storyboard_stress_latest.json"
    stamped = OUT_DIR / f"base_defense_storyboard_stress_{_ts()}.json"
    _write_json(latest, out)
    _write_json(stamped, out)

    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))


if __name__ == "__main__":
    main()

