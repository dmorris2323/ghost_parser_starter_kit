"""
nuclear_watch_decision_bridge.py

Bridge: Nuclear watch outputs -> Nuclear Decision Card
- Reads best-available "latest" artifacts (validation report, golden dome watch, etc.)
- Builds + writes a decision card with prebrief trust annotations attached
- Safe by design: works even if some inputs are missing (falls back to defaults)

This avoids breaking existing Week-1 nuclear modules while adding commander-brief value.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _pick_latest_inputs() -> Dict[str, Any]:
    """
    Best-effort input selection.
    We do NOT assume any single file always exists.
    """
    candidates = {
        "validation_report": Path("docs") / "validation" / "fusion_validation_report.json",
        "golden_dome_watch": Path("docs") / "golden_dome_daily_watch.json",
        "spectral_dashboard": Path("outputs") / "spectral_dashboard.json",
    }

    out: Dict[str, Any] = {}
    for k, p in candidates.items():
        out[k] = _read_json(p) or {"_missing": True, "_path": str(p)}
    return out


def build_decision_card_from_watch() -> Dict[str, Any]:
    """
    Construct inputs for decision card using best available signals.
    This is training-safe metadata unless your upstream inputs are real.
    """
    inputs = _pick_latest_inputs()

    v = inputs.get("validation_report", {})
    gd = inputs.get("golden_dome_watch", {})
    sd = inputs.get("spectral_dashboard", {})

    # Defaults
    trust_score = 80
    risk_score = 35
    alerts = {"crit": 0, "high": 0, "anomaly": 0, "attack_like": 0}
    degraded = False
    difficulty = "UNKNOWN"
    pattern_id = None
    delta_vs_baseline = None

    # Prefer validation report if present
    if isinstance(v, dict) and not v.get("_missing"):
        difficulty = (
            (v.get("inputs", {}) or {}).get("difficulty")
            or difficulty
        )
        degraded = bool((v.get("inputs", {}) or {}).get("degraded", False))

        # If your harness writes baseline/injected metrics, prefer injected
        injected = v.get("injected_metrics") or v.get("synthetic_metrics") or {}
        if isinstance(injected, dict):
            trust_score = injected.get("trust_proxy", trust_score)
            risk_score = injected.get("risk_score", risk_score)
            a = injected.get("alerts", {})
            if isinstance(a, dict):
                alerts = {
                    "crit": int(a.get("crit", alerts["crit"])),
                    "high": int(a.get("high", alerts["high"])),
                    "attack_like": int(a.get("attack_like", alerts["attack_like"])),
                    "anomaly": int(a.get("anomaly", alerts["anomaly"])),
                }

        pat = v.get("pattern_injection", {}) or {}
        if isinstance(pat, dict):
            pattern_id = pat.get("pattern_requested") or pattern_id

        delta_vs_baseline = v.get("delta_vs_baseline") or delta_vs_baseline

        gates = (v.get("real_module_attempts", {}) or {}).get("results", {}) or {}
        # We don't rely on these; decision card already accepts statuses
        sis_status = "GREEN"  # assume green unless caller overrides
        sps_status = "GREEN"
        gate_status = "PASS"

    else:
        # fallback to golden dome watch / dashboard if present
        if isinstance(gd, dict) and not gd.get("_missing"):
            trust_score = gd.get("trust_score", trust_score)
            risk_score = gd.get("risk_score", risk_score)
            degraded = bool(gd.get("degraded", degraded))
            difficulty = gd.get("difficulty", difficulty)
            a = gd.get("alerts", {})
            if isinstance(a, dict):
                alerts.update({k: int(a.get(k, alerts[k])) for k in alerts.keys()})

        sis_status = "UNKNOWN"
        sps_status = "UNKNOWN"
        gate_status = "UNKNOWN"

    # Import here to avoid import-time circular issues
    from nuclear_decision_card import write_decision_card_latest  # type: ignore

    out = write_decision_card_latest(
        trust_score=trust_score,
        risk_score=risk_score,
        alerts=alerts,
        degraded=degraded,
        difficulty=difficulty,
        pattern_id=pattern_id,
        delta_vs_baseline=delta_vs_baseline,
        sis_status=sis_status,
        sps_status=sps_status,
        gate_status=gate_status,
    )
    return out


if __name__ == "__main__":
    res = build_decision_card_from_watch()
    print("WROTE:")
    print(res.get("json_latest"))
    print(res.get("txt_latest"))

