"""
fusion_validation_harness.py

Synthetic Fusion Validation Harness (SAFE)
- Generates synthetic bundle (SAFE training-only)
- Optionally injects adversary pattern (SAFE training-only)
- Computes baseline vs injected metrics + delta
- Attempts to run real modules (best-effort) for trust/OSL/training-curve
- Runs SIS+SPS PRE and POST gates around validation (hardening)

Outputs (always under src/docs/...):
- src/docs/validation/fusion_validation_report.json
- src/docs/validation/fusion_validation_report_<timestamp>.json
- src/docs/validation/fusion_validation_report.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# ----------------------------
# Paths (stable no matter CWD)
# ----------------------------
SRC_DIR = Path(__file__).resolve().parent
DOCS_DIR = SRC_DIR / "docs"
VALIDATION_DIR = DOCS_DIR / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _metric_pack(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute safe proxy metrics from synthetic bundle structure.
    This is NOT real missile telemetry. This is a training proxy.
    """
    alerts = bundle.get("alerts", {}) if isinstance(bundle.get("alerts", {}), dict) else {}
    trust_proxy = _coerce_float(bundle.get("trust_proxy", 0.0), 0.0)
    risk_score = _coerce_float(bundle.get("risk_score", 0.0), 0.0)

    # Normalize alert counts for reporting
    packed_alerts = {
        "total": _coerce_int(alerts.get("total", 0), 0),
        "crit": _coerce_int(alerts.get("crit", 0), 0),
        "high": _coerce_int(alerts.get("high", 0), 0),
        "attack_like": _coerce_int(alerts.get("attack_like", 0), 0),
        "anomaly": _coerce_int(alerts.get("anomaly", 0), 0),
    }

    # If total is missing, derive a reasonable total proxy
    if packed_alerts["total"] <= 0:
        packed_alerts["total"] = (
            packed_alerts["crit"]
            + packed_alerts["high"]
            + packed_alerts["attack_like"]
            + packed_alerts["anomaly"]
        )

    return {
        "trust_proxy": round(trust_proxy, 2),
        "risk_score": round(risk_score, 2),
        "alerts": packed_alerts,
    }


def _delta_pack(base: Dict[str, Any], inj: Dict[str, Any]) -> Dict[str, Any]:
    base_alerts = base.get("alerts", {}) if isinstance(base.get("alerts", {}), dict) else {}
    inj_alerts = inj.get("alerts", {}) if isinstance(inj.get("alerts", {}), dict) else {}

    return {
        "trust_proxy_delta": round(_coerce_float(inj.get("trust_proxy"), 0.0) - _coerce_float(base.get("trust_proxy"), 0.0), 2),
        "risk_score_delta": round(_coerce_float(inj.get("risk_score"), 0.0) - _coerce_float(base.get("risk_score"), 0.0), 2),
        "alerts_delta": {
            "crit": _coerce_int(inj_alerts.get("crit", 0), 0) - _coerce_int(base_alerts.get("crit", 0), 0),
            "high": _coerce_int(inj_alerts.get("high", 0), 0) - _coerce_int(base_alerts.get("high", 0), 0),
            "attack_like": _coerce_int(inj_alerts.get("attack_like", 0), 0) - _coerce_int(base_alerts.get("attack_like", 0), 0),
            "anomaly": _coerce_int(inj_alerts.get("anomaly", 0), 0) - _coerce_int(base_alerts.get("anomaly", 0), 0),
            "total": _coerce_int(inj_alerts.get("total", 0), 0) - _coerce_int(base_alerts.get("total", 0), 0),
        },
    }


@dataclass
class _BundlePaths:
    latest: str
    stamped: str


def _best_effort_real_modules() -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Try to run real GLL modules for trust/OSL/training curve.
    Must never hard-fail the harness if these are missing or signatures differ.
    """
    results: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    # ---- fusion_trust (try multiple likely function names) ----
    try:
        import fusion_trust as ft  # type: ignore

        fn = None
        for name in ("compute_trust", "compute_fusion_trust", "build_fusion_trust", "run_fusion_trust"):
            if hasattr(ft, name):
                fn = getattr(ft, name)
                break

        if fn is None:
            raise AttributeError("MissingFunction: none of trust functions found in fusion_trust")

        trust_out = fn()  # keep as zero-arg; your module appears to be zero-arg style
        results["fusion_trust"] = trust_out
    except Exception as e:
        errors["fusion_trust"] = f"{e.__class__.__name__}: {e}"

    # ---- operator_safety_layer ----
    try:
        import operator_safety_layer as osl  # type: ignore

        fn = None
        for name in ("compute_osl", "compute_operator_safety_layer", "build_operator_safety_layer", "run_operator_safety_layer"):
            if hasattr(osl, name):
                fn = getattr(osl, name)
                break

        if fn is None:
            raise AttributeError("MissingFunction: none of OSL functions found in operator_safety_layer")

        osl_out = fn()  # keep as zero-arg
        results["operator_safety_layer"] = osl_out
    except Exception as e:
        errors["operator_safety_layer"] = f"{e.__class__.__name__}: {e}"

    # ---- crisis_mode_flag ----
    try:
        import crisis_mode_flag as cm  # type: ignore

        fn = None
        for name in ("read_crisis_mode", "get_crisis_mode", "is_crisis_mode", "crisis_mode_status"):
            if hasattr(cm, name):
                fn = getattr(cm, name)
                break

        if fn is None:
            raise AttributeError(
                "MissingFunction: none of ['read_crisis_mode','get_crisis_mode','is_crisis_mode','crisis_mode_status'] found in crisis_mode_flag"
            )

        cm_out = fn()
        results["crisis_mode"] = cm_out
    except Exception as e:
        errors["crisis_mode_flag"] = f"{e.__class__.__name__}: {e}"

    # ---- training_curve_engine ----
    try:
        from training_curve_engine import compute_training_curve  # type: ignore

        curve = compute_training_curve()
        results["training_curve"] = curve
    except Exception as e:
        errors["training_curve_engine"] = f"{e.__class__.__name__}: {e}"

    return results, errors


def _score_verdict(difficulty: str, baseline: Dict[str, Any], injected: Dict[str, Any]) -> Dict[str, str]:
    """
    Keep verdict conservative and training-appropriate.
    FAIL only if baseline is extreme. Otherwise PASS/WARN is fine for stress.
    """
    d = (difficulty or "").upper().strip()

    base_risk = _coerce_float(baseline.get("risk_score"), 0.0)
    inj_risk = _coerce_float(injected.get("risk_score"), 0.0)
    inj_crit = _coerce_int(injected.get("alerts", {}).get("crit", 0), 0)

    # baseline should not be catastrophic
    if base_risk >= 90.0:
        return {"status": "FAIL", "message": "Baseline synthetic environment indicates instability. Investigate scoring/trust/alerts behavior."}

    # ADVERSARIAL is allowed to look ugly; warn if crit spikes
    if d == "ADVERSARIAL" and inj_crit >= 3:
        return {"status": "WARN", "message": "Adversarial injection raised critical pressure (acceptable stress test). Review delta vs baseline."}

    # Default: controlled
    if inj_risk >= 75.0:
        return {"status": "WARN", "message": "Elevated injected risk. Review delta vs baseline and ensure expected behavior."}

    return {"status": "PASS", "message": "Controlled environment for this difficulty."}


def _render_txt(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("GLL Synthetic Fusion Validation Report (SAFE)")
    lines.append("=" * 44)
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append(f"Difficulty: {report.get('inputs', {}).get('difficulty')}")
    lines.append(f"Seed: {report.get('inputs', {}).get('seed')}")
    lines.append("")
    lines.append(str(report.get("safe_notice", "")))
    lines.append("")

    verdict = report.get("verdict", {})
    lines.append(f"VERDICT: {verdict.get('status')} — {verdict.get('message')}")
    lines.append("")

    base = report.get("baseline_metrics", {})
    inj = report.get("injected_metrics", {})
    delta = report.get("delta_vs_baseline", {})

    lines.append("Baseline Metrics")
    lines.append(f"  trust_proxy: {base.get('trust_proxy')}")
    lines.append(f"  risk_score:  {base.get('risk_score')}")
    lines.append(f"  alerts:      {base.get('alerts')}")
    lines.append("")

    lines.append("Injected Metrics")
    lines.append(f"  trust_proxy: {inj.get('trust_proxy')}")
    lines.append(f"  risk_score:  {inj.get('risk_score')}")
    lines.append(f"  alerts:      {inj.get('alerts')}")
    lines.append("")

    lines.append("Delta vs Baseline")
    lines.append(f"  trust_proxy_delta: {delta.get('trust_proxy_delta')}")
    lines.append(f"  risk_score_delta:  {delta.get('risk_score_delta')}")
    lines.append(f"  alerts_delta:      {delta.get('alerts_delta')}")
    lines.append("")

    pi = report.get("pattern_injection", {})
    lines.append("Pattern Injection")
    lines.append(f"  requested: {pi.get('pattern_requested')}")
    lines.append(f"  seed:      {pi.get('pattern_seed')}")
    lines.append(f"  error:     {pi.get('pattern_error')}")
    items = pi.get("items", [])
    if isinstance(items, list) and items:
        for it in items:
            lines.append(f"  - {it.get('pattern_id')} | intensity={it.get('intensity')} | injected_events={it.get('injected_events')}")
    lines.append("")

    rma = report.get("real_module_attempts", {})
    lines.append("Real Module Attempts (best-effort)")
    lines.append(f"  attempted: {rma.get('attempted')}")
    lines.append(f"  results:   {rma.get('results')}")
    lines.append(f"  errors:    {rma.get('errors')}")
    lines.append("")

    tf = report.get("training_feedback", None)
    if tf is not None:
        lines.append("Training Feedback (recommendation)")
        lines.append(str(tf))
        lines.append("")

    recs = report.get("recommendations", [])
    if isinstance(recs, list) and recs:
        lines.append("Recommendations")
        for r in recs:
            lines.append(f"  - {r}")
        lines.append("")

    paths = report.get("paths", {})
    lines.append("Paths")
    lines.append(str(paths))

    return "\n".join(lines)


def run_synthetic_fusion_validation(
    *,
    difficulty: str = "INTERMEDIATE",
    seed: int = 1,
    pattern_id: Optional[str] = None,
    pattern_seed: Optional[int] = None,
    update_baselines: bool = False,
) -> Dict[str, Any]:
    """
    Main entrypoint.

    difficulty: BEGINNER | INTERMEDIATE | ADVERSARIAL (string, flexible)
    seed: generator seed
    pattern_id: optional injection pattern id (ex: "CROSS_DOMAIN_CONFUSION")
    pattern_seed: optional injection seed; defaults to seed
    update_baselines: only True when you intentionally accept a new baseline for gates
    """
    difficulty = (difficulty or "INTERMEDIATE").upper().strip()
    pattern_seed = seed if pattern_seed is None else int(pattern_seed)

    # ---- PRE GATE (SIS+SPS) ----
    from gll_run_gates import run_gates  # local import to avoid hard-fail on import order
    pre_gate = run_gates(gate_type="PRE", context="fusion_validation_harness", update_baselines=update_baselines)

    # ---- Generate baseline synthetic bundle ----
    from synthetic_signal_generator import build_synthetic_fusion_bundle  # type: ignore

    baseline_bundle = build_synthetic_fusion_bundle(difficulty=difficulty, seed=int(seed))
    baseline_metrics = _metric_pack(baseline_bundle)

    # Capture paths if generator returns them
    baseline_paths = baseline_bundle.get("paths", {}) if isinstance(baseline_bundle, dict) else {}
    baseline_bundle_paths = {
        "latest": baseline_paths.get("latest"),
        "stamped": baseline_paths.get("stamped"),
    }

    # ---- Optionally inject a pattern ----
    injected_bundle = baseline_bundle
    injection_items = []
    pattern_error: Optional[str] = None

    if pattern_id:
        try:
            from pattern_injection_engine import inject_pattern  # type: ignore

            injected_bundle, injection_meta = inject_pattern(
                bundle=baseline_bundle,
                pattern_id=str(pattern_id),
                seed=int(pattern_seed),
            )
            if isinstance(injection_meta, dict):
                injection_items = injection_meta.get("items", []) if isinstance(injection_meta.get("items", []), list) else []
        except Exception as e:
            pattern_error = f"{e.__class__.__name__}: {e}"

    injected_metrics = _metric_pack(injected_bundle)
    delta_vs_baseline = _delta_pack(baseline_metrics, injected_metrics)

    verdict = _score_verdict(difficulty, baseline_metrics, injected_metrics)

    # ---- Real modules (best-effort) ----
    real_results, real_errors = _best_effort_real_modules()

    # ---- Build report ----
    stamp = _ts()
    json_latest = VALIDATION_DIR / "fusion_validation_report.json"
    json_stamped = VALIDATION_DIR / f"fusion_validation_report_{stamp}.json"
    txt_path = VALIDATION_DIR / "fusion_validation_report.txt"

    report: Dict[str, Any] = {
        "report_version": 4,
        "generated_at": _utc_now_iso(),
        "safe_notice": "This report is generated from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "difficulty": difficulty,
            "seed": int(seed),
            "pattern_id": pattern_id,
            "pattern_seed": int(pattern_seed),
            "baseline_bundle_paths": baseline_bundle_paths,
            "injected_bundle_paths": baseline_bundle_paths,  # generator currently writes same path; acceptable
        },
        "baseline_metrics": baseline_metrics,
        "injected_metrics": injected_metrics,
        "delta_vs_baseline": delta_vs_baseline,
        "pattern_injection": {
            "count": 1 if pattern_id else 0,
            "items": injection_items,
            "pattern_requested": pattern_id,
            "pattern_seed": int(pattern_seed),
            "pattern_error": pattern_error,
        },
        "verdict": verdict,
        "run_gates": {
            "pre": pre_gate,
        },
        "real_module_attempts": {
            "attempted": {
                "fusion_trust": "auto",
                "operator_safety_layer": "auto",
                "crisis_mode_flag": "auto",
                "training_curve_engine": "compute_training_curve",
            },
            "results": real_results,
            "errors": real_errors,
        },
        "recommendations": [
            "Use INTERMEDIATE without injection for baseline regression.",
            "Use ADVERSARIAL + injection to test SPS defenses and operator coaching.",
            "Use delta_vs_baseline to validate that injections change the system in expected directions.",
            "If PRE gate fails, freeze changes and fix integrity before proceeding.",
        ],
        "paths": {
            "json_latest": str(json_latest),
            "json_stamped": str(json_stamped),
            "txt": str(txt_path),
        },
    }

    # ---- Training → Validation Feedback Loop (recorded, not enforced) ----
    try:
        from training_feedback_engine import recommend_next_training  # type: ignore

        training_curve_result = (
            report.get("real_module_attempts", {})
                .get("results", {})
                .get("training_curve", {})
        )
        if not isinstance(training_curve_result, dict):
            training_curve_result = {}

        training_feedback = recommend_next_training(
            training_curve=training_curve_result,
            difficulty=str(difficulty),
            validation_verdict=str(report.get("verdict", {}).get("status", "UNKNOWN")),
        )
        report["training_feedback"] = training_feedback

        # Persist for instructors (docs/training)
        feedback_path = Path("docs") / "training" / "training_feedback_latest.json"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        feedback_path.write_text(json.dumps(training_feedback, indent=2), encoding="utf-8")

        # Record path in the report so the GUI can find it
        report.setdefault("paths", {})
        report["paths"]["training_feedback_latest"] = str(feedback_path)

    except Exception as e:
        report["training_feedback"] = {
            "status": "ERROR",
            "reason": f"Feedback engine failed: {e.__class__.__name__}: {e}",
        }
    # ---- POST GATE (SIS+SPS) ----
    try:
        post_gate = run_gates(gate_type="POST", context="fusion_validation_harness", update_baselines=False)
    except Exception as e:
        post_gate = {"status": "FAIL", "error": f"{e.__class__.__name__}: {e}"}

    report.setdefault("gates", {})
    report["gates"]["post"] = post_gate

    # ---- Write outputs ----
    _write_json(json_latest, report)
    _write_json(json_stamped, report)
    _write_txt(txt_path, _render_txt(report))

    # ---- POST GATE (SIS+SPS) ----
    post_gate = run_gates(gate_type="POST", context="fusion_validation_harness", update_baselines=False)
    report["run_gates"]["post"] = post_gate
    _write_json(json_latest, report)
    _write_json(json_stamped, report)
    _write_txt(txt_path, _render_txt(report))

    return report


if __name__ == "__main__":
    # Safe local run
    r = run_synthetic_fusion_validation(difficulty="INTERMEDIATE", seed=1)
    print(json.dumps(r, indent=2))

