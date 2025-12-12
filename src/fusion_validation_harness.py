"""
fusion_validation_harness.py

Day 68 — Synthetic Fusion Validation Harness (Hardened)
Now supports:
- Pattern injection reporting (Module 2)
- Baseline vs injected delta (measures impact)
- Normalized risk score (avoids always-100 saturation in ADVERSARIAL)
- Difficulty-aware verdict rubric
- Resilient integration hooks for "real" GLL modules (function name agnostic)

Outputs:
  - src/docs/validation/fusion_validation_report.json
  - src/docs/validation/fusion_validation_report.txt
"""

from __future__ import annotations

import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from synthetic_signal_generator import build_synthetic_fusion_bundle


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _docs_dir() -> Path:
    return _repo_root() / "src" / "docs"


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _trust_proxy(bundle: Dict[str, Any]) -> float:
    stats = bundle.get("stats", {})
    total = float(stats.get("total_events", 0) or 0)
    if total <= 0:
        return 100.0
    anom = float(stats.get("anomaly_events", 0) or 0)
    atk = float(stats.get("attack_like_events", 0) or 0)
    crit = float(stats.get("crit_events", 0) or 0)

    # Penalties scale by rates not counts
    p = 0.0
    p += (anom / total) * 35.0
    p += (atk / total) * 45.0
    p += (crit / total) * 25.0

    trust = 100.0 - p
    return _clamp(trust, 0.0, 100.0)


def _alert_counts(bundle: Dict[str, Any]) -> Dict[str, int]:
    events = bundle.get("events", []) or []
    crit = sum(1 for e in events if str(e.get("severity", "")).upper() == "CRIT")
    high = sum(1 for e in events if str(e.get("severity", "")).upper() == "HIGH")
    atk = sum(1 for e in events if bool(e.get("attack_like", False)))
    anom = sum(1 for e in events if bool(e.get("anomaly", False)))
    total = len(events)
    return {"total": int(total), "crit": int(crit), "high": int(high), "attack_like": int(atk), "anomaly": int(anom)}


def _normalized_risk_score(alerts: Dict[str, int]) -> float:
    """
    Normalizes risk by total events so ADVERSARIAL doesn't auto-peg at 100.
    Returns 0–100.
    """
    total = float(alerts.get("total", 0) or 0)
    if total <= 0:
        return 0.0

    crit = float(alerts.get("crit", 0) or 0)
    high = float(alerts.get("high", 0) or 0)
    atk = float(alerts.get("attack_like", 0) or 0)
    anom = float(alerts.get("anomaly", 0) or 0)

    # Weighted rate-based risk (stable)
    rate = 0.0
    rate += (crit / total) * 1.00
    rate += (high / total) * 0.55
    rate += (atk / total) * 0.75
    rate += (anom / total) * 0.40

    # Map to 0–100 with a smooth-ish curve
    score = 100.0 * _clamp(rate / 0.85, 0.0, 1.0)
    return round(float(score), 2)


def _difficulty_rubric(difficulty: str) -> Dict[str, float]:
    d = difficulty.upper().strip()
    # These are intentionally looser for stress modes.
    if d == "BEGINNER":
        return {"pass_trust": 82.0, "pass_risk": 35.0, "warn_trust": 68.0, "warn_risk": 60.0}
    if d == "INTERMEDIATE":
        return {"pass_trust": 78.0, "pass_risk": 45.0, "warn_trust": 62.0, "warn_risk": 70.0}
    if d == "ADVANCED":
        return {"pass_trust": 72.0, "pass_risk": 55.0, "warn_trust": 58.0, "warn_risk": 78.0}
    # ADVERSARIAL should *feel* bad—PASS is rare. WARN is “expected stress but controlled.”
    if d == "ADVERSARIAL":
        return {"pass_trust": 70.0, "pass_risk": 60.0, "warn_trust": 55.0, "warn_risk": 85.0}
    return {"pass_trust": 78.0, "pass_risk": 45.0, "warn_trust": 62.0, "warn_risk": 70.0}


def _verdict(difficulty: str, trust: float, risk: float) -> Tuple[str, str]:
    r = _difficulty_rubric(difficulty)
    if trust >= r["pass_trust"] and risk <= r["pass_risk"]:
        return ("PASS", "Controlled environment for this difficulty.")
    if trust >= r["warn_trust"] and risk <= r["warn_risk"]:
        return ("WARN", "Expected stress for this difficulty; behavior remains bounded.")
    return ("FAIL", "Out-of-bounds stress behavior; investigate alerts/trust response.")


def _summarize_injections(bundle: Dict[str, Any]) -> Dict[str, Any]:
    injections = bundle.get("injections", []) or []
    return {
        "count": int(len(injections)),
        "items": injections,
        "pattern_requested": bundle.get("pattern_requested"),
        "pattern_seed": bundle.get("pattern_seed"),
        "pattern_error": bundle.get("pattern_error"),
    }


def _safe_call(module_name: str, fn_candidates: list[str]) -> Tuple[Optional[Any], Optional[str], Optional[str]]:
    """
    Try importing module and calling first available function name.
    Returns: (result, called_fn_name, error_str)
    """
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        return None, None, f"ImportError: {type(e).__name__}: {e}"

    for fn in fn_candidates:
        if hasattr(mod, fn):
            try:
                return getattr(mod, fn)(), fn, None
            except Exception as e:
                return None, fn, f"CallError: {type(e).__name__}: {e}"

    return None, None, f"MissingFunction: none of {fn_candidates} found in {module_name}"


def _try_real_modules() -> Dict[str, Any]:
    out: Dict[str, Any] = {"attempted": {}, "results": {}, "errors": {}}

    # fusion trust
    res, called, err = _safe_call(
        "fusion_trust",
        ["compute_fusion_trust", "compute_trust", "get_fusion_trust", "fusion_trust_score", "run_fusion_trust"],
    )
    out["attempted"]["fusion_trust"] = called
    if err:
        out["errors"]["fusion_trust"] = err
    else:
        out["results"]["fusion_trust"] = res

    # operator safety layer
    res, called, err = _safe_call(
        "operator_safety_layer",
        ["compute_operator_safety_layer", "get_operator_safety_layer", "compute_osl", "run_operator_safety_layer"],
    )
    out["attempted"]["operator_safety_layer"] = called
    if err:
        out["errors"]["operator_safety_layer"] = err
    else:
        out["results"]["operator_safety_layer"] = res

    # crisis mode flag
    res, called, err = _safe_call(
        "crisis_mode_flag",
        ["read_crisis_mode", "get_crisis_mode", "is_crisis_mode", "crisis_mode_status"],
    )
    out["attempted"]["crisis_mode_flag"] = called
    if err:
        out["errors"]["crisis_mode_flag"] = err
    else:
        out["results"]["crisis_mode"] = res

    # training curve (should be stable now)
    try:
        from training_curve_engine import compute_training_curve  # type: ignore
        curve = compute_training_curve()
        out["attempted"]["training_curve_engine"] = "compute_training_curve"
        out["results"]["training_curve"] = {
            "AGI": curve.get("AGI"),
            "improvement_slope": curve.get("improvement_slope"),
            "difficulty_weighted_average": curve.get("difficulty_weighted_average"),
            "volatility_index": curve.get("volatility_index"),
        }
    except Exception as e:
        out["errors"]["training_curve_engine"] = f"{type(e).__name__}: {e}"

    return out


def _metrics(bundle: Dict[str, Any]) -> Dict[str, Any]:
    trust = round(_trust_proxy(bundle), 2)
    alerts = _alert_counts(bundle)
    risk = _normalized_risk_score(alerts)
    return {"trust_proxy": trust, "risk_score": risk, "alerts": alerts}


def run_synthetic_fusion_validation(
    difficulty: str = "INTERMEDIATE",
    seed: Optional[int] = 42,
    pattern_id: Optional[str] = None,
    pattern_seed: Optional[int] = None,
    write: bool = True,
) -> Dict[str, Any]:
    difficulty = difficulty.upper().strip()

    # Baseline run (no injection) for delta measurement
    baseline_bundle = build_synthetic_fusion_bundle(difficulty=difficulty, seed=seed, pattern_id=None, write=True)
    baseline_metrics = _metrics(baseline_bundle)

    # Injected run (optional)
    injected_bundle = build_synthetic_fusion_bundle(
        difficulty=difficulty,
        seed=seed,
        pattern_id=pattern_id,
        pattern_seed=pattern_seed,
        write=True,
    )
    injected_metrics = _metrics(injected_bundle)
    injections_summary = _summarize_injections(injected_bundle)

    # Delta
    delta = {
        "trust_proxy_delta": round(injected_metrics["trust_proxy"] - baseline_metrics["trust_proxy"], 2),
        "risk_score_delta": round(injected_metrics["risk_score"] - baseline_metrics["risk_score"], 2),
        "alerts_delta": {
            k: int(injected_metrics["alerts"].get(k, 0)) - int(baseline_metrics["alerts"].get(k, 0))
            for k in ["crit", "high", "attack_like", "anomaly", "total"]
        },
    }

    status, msg = _verdict(difficulty, injected_metrics["trust_proxy"], injected_metrics["risk_score"])

    real = _try_real_modules()

    report: Dict[str, Any] = {
        "report_version": 3,
        "generated_at": _utc_iso(),
        "safe_notice": "This report is generated from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "difficulty": difficulty,
            "seed": seed,
            "pattern_id": pattern_id.upper() if pattern_id else None,
            "pattern_seed": pattern_seed if pattern_seed is not None else seed,
            "baseline_bundle_paths": baseline_bundle.get("paths", {}),
            "injected_bundle_paths": injected_bundle.get("paths", {}),
        },
        "baseline_metrics": baseline_metrics,
        "injected_metrics": injected_metrics,
        "delta_vs_baseline": delta,
        "pattern_injection": injections_summary,
        "verdict": {"status": status, "message": msg},
        "real_module_attempts": real,
        "recommendations": [
            "If ADVERSARIAL is WARN with bounded deltas, that’s acceptable training stress.",
            "If baseline is FAIL, freeze changes and run system integrity before adding features.",
            "Use delta_vs_baseline to validate that injections change the system in expected directions.",
        ],
    }

    if write:
        out_dir = _docs_dir() / "validation"
        _safe_mkdir(out_dir)
        latest_json = out_dir / "fusion_validation_report.json"
        stamped_json = out_dir / f"fusion_validation_report_{_stamp()}.json"
        txt_path = out_dir / "fusion_validation_report.txt"

        latest_json.write_text(json.dumps(report, indent=2))
        stamped_json.write_text(json.dumps(report, indent=2))
        txt_path.write_text(_render_txt(report))

        report["paths"] = {"json_latest": str(latest_json), "json_stamped": str(stamped_json), "txt": str(txt_path)}

    return report


def _render_txt(report: Dict[str, Any]) -> str:
    inp = report.get("inputs", {})
    base = report.get("baseline_metrics", {})
    inj = report.get("injected_metrics", {})
    d = report.get("delta_vs_baseline", {})
    v = report.get("verdict", {})
    pinj = report.get("pattern_injection", {})

    def fmt_alerts(a: Dict[str, Any]) -> str:
        return f"CRIT={a.get('crit',0)} HIGH={a.get('high',0)} ATTACK={a.get('attack_like',0)} ANOM={a.get('anomaly',0)} TOTAL={a.get('total',0)}"

    lines = []
    lines.append("GLL — Synthetic Fusion Validation Report (SAFE)")
    lines.append("=" * 60)
    lines.append(f"Generated:   {report.get('generated_at')}")
    lines.append(f"Difficulty:  {inp.get('difficulty')}")
    lines.append(f"Seed:        {inp.get('seed')}")
    lines.append(f"Pattern:     {inp.get('pattern_id') or 'None'}")
    lines.append("")
    lines.append("Baseline Metrics")
    lines.append("-" * 60)
    lines.append(f"Trust Proxy: {base.get('trust_proxy')}    Risk: {base.get('risk_score')}")
    lines.append(f"Alerts: {fmt_alerts(base.get('alerts', {}))}")
    lines.append("")
    lines.append("Injected Metrics")
    lines.append("-" * 60)
    lines.append(f"Trust Proxy: {inj.get('trust_proxy')}    Risk: {inj.get('risk_score')}")
    lines.append(f"Alerts: {fmt_alerts(inj.get('alerts', {}))}")
    lines.append("")
    lines.append("Delta vs Baseline")
    lines.append("-" * 60)
    lines.append(f"Trust Δ: {d.get('trust_proxy_delta')}    Risk Δ: {d.get('risk_score_delta')}")
    lines.append(f"Alerts Δ: {d.get('alerts_delta')}")
    lines.append("")
    lines.append("Pattern Injection")
    lines.append("-" * 60)
    lines.append(f"Injections: {pinj.get('count', 0)}")
    if pinj.get("pattern_error"):
        lines.append(f"Pattern error: {pinj.get('pattern_error')}")
    if pinj.get("items"):
        ex = pinj["items"][0]
        lines.append(f"Example: {ex.get('pattern_id')} — {ex.get('label')} (injected_events={ex.get('injected_events')})")
    lines.append("")
    lines.append("Verdict")
    lines.append("-" * 60)
    lines.append(f"{v.get('status')}: {v.get('message')}")
    lines.append("")
    lines.append("Notes")
    lines.append("-" * 60)
    lines.append("• This is synthetic telemetry only (safe).")
    lines.append("• Use delta_vs_baseline to confirm patterns move metrics in expected directions.")
    return "\n".join(lines)


if __name__ == "__main__":
    r = run_synthetic_fusion_validation(difficulty="ADVERSARIAL", seed=99, pattern_id="CROSS_DOMAIN_CONFUSION", pattern_seed=99)
    print(json.dumps(r, indent=2))

