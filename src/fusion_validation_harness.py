"""
fusion_validation_harness.py

Day 68 — Fusion Validation Harness (SAFE)
Runs a synthetic validation session:
  - generates synthetic telemetry bundle
  - computes safety-focused metrics (alerts, risk, trust proxy)
  - optionally calls existing GLL modules if present (non-fatal if missing)
  - writes report JSON + TXT

Outputs:
  - src/docs/validation/fusion_validation_report.json
  - src/docs/validation/fusion_validation_report.txt
  - src/docs/validation/fusion_validation_report_<timestamp>.json
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from synthetic_signal_generator import build_synthetic_fusion_bundle


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _docs_dir() -> Path:
    return _repo_root() / "src" / "docs"


def _stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _utc_iso() -> str:
    return datetime.utcnow().isoformat()


def _trust_proxy(bundle: Dict[str, Any]) -> float:
    """
    Trust proxy (0–100): lower trust if many anomalies/attacks/crit events.
    This is SAFE and deterministic, not pretending to be "truth".
    """
    stats = bundle.get("stats", {})
    total = float(stats.get("total_events", 0) or 0)
    if total <= 0:
        return 100.0

    anom = float(stats.get("anomaly_events", 0) or 0)
    atk = float(stats.get("attack_like_events", 0) or 0)
    crit = float(stats.get("crit_events", 0) or 0)

    # Weighted penalties
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
    return {
        "crit": int(crit),
        "high": int(high),
        "attack_like": int(atk),
        "anomaly": int(anom),
    }


def _risk_score(alerts: Dict[str, int]) -> float:
    """
    Risk score (0–100): simple weighting to provide a stable test number.
    """
    crit = alerts.get("crit", 0)
    high = alerts.get("high", 0)
    atk = alerts.get("attack_like", 0)
    anom = alerts.get("anomaly", 0)

    # Weighted linear score with clamp
    score = (crit * 6.0) + (high * 2.5) + (atk * 3.5) + (anom * 1.8)
    return _clamp(score, 0.0, 100.0)


def _pass_warn_fail(trust: float, risk: float) -> Tuple[str, str]:
    """
    Decision gate for synthetic validation.
    """
    if trust >= 80.0 and risk <= 35.0:
        return ("PASS", "Stable synthetic environment. Good baseline behavior.")
    if trust >= 60.0 and risk <= 60.0:
        return ("WARN", "Degraded synthetic environment. Expected under stress; watch drift/consistency.")
    return ("FAIL", "Synthetic environment indicates instability. Investigate scoring/trust/alerts behavior.")


def _try_real_modules(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional: attempt to call existing GLL modules without breaking validation.
    We DO NOT assume schemas; this is best-effort integration reporting only.
    """
    out: Dict[str, Any] = {"attempted": [], "results": {}, "errors": {}}

    # fusion_trust (if available)
    try:
        from fusion_trust import compute_fusion_trust  # type: ignore
        out["attempted"].append("fusion_trust.compute_fusion_trust()")
        trust_obj = compute_fusion_trust()
        out["results"]["fusion_trust"] = trust_obj
    except Exception as e:
        out["errors"]["fusion_trust"] = f"{type(e).__name__}: {e}"

    # operator_safety_layer (if available)
    try:
        from operator_safety_layer import compute_operator_safety_layer  # type: ignore
        out["attempted"].append("operator_safety_layer.compute_operator_safety_layer()")
        osl = compute_operator_safety_layer()
        out["results"]["operator_safety_layer"] = osl
    except Exception as e:
        out["errors"]["operator_safety_layer"] = f"{type(e).__name__}: {e}"

    # crisis_mode_flag (if available)
    try:
        from crisis_mode_flag import read_crisis_mode  # type: ignore
        out["attempted"].append("crisis_mode_flag.read_crisis_mode()")
        cm = read_crisis_mode()
        out["results"]["crisis_mode"] = cm
    except Exception as e:
        out["errors"]["crisis_mode_flag"] = f"{type(e).__name__}: {e}"

    # training curve (if available)
    try:
        from training_curve_engine import compute_training_curve  # type: ignore
        out["attempted"].append("training_curve_engine.compute_training_curve()")
        curve = compute_training_curve()
        out["results"]["training_curve"] = {
            "AGI": curve.get("AGI"),
            "improvement_slope": curve.get("improvement_slope"),
            "difficulty_weighted_average": curve.get("difficulty_weighted_average"),
            "volatility_index": curve.get("volatility_index"),
        }
    except Exception as e:
        out["errors"]["training_curve_engine"] = f"{type(e).__name__}: {e}"

    return out


def run_synthetic_fusion_validation(
    difficulty: str = "INTERMEDIATE",
    seed: Optional[int] = 42,
    write: bool = True,
) -> Dict[str, Any]:
    difficulty = difficulty.upper().strip()

    bundle = build_synthetic_fusion_bundle(difficulty=difficulty, seed=seed, write=True)

    trust = round(_trust_proxy(bundle), 2)
    alerts = _alert_counts(bundle)
    risk = round(_risk_score(alerts), 2)

    verdict, verdict_msg = _pass_warn_fail(trust, risk)

    real = _try_real_modules(bundle)

    report: Dict[str, Any] = {
        "report_version": 1,
        "generated_at": _utc_iso(),
        "safe_notice": "This report is generated from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "difficulty": difficulty,
            "seed": seed,
            "bundle_paths": bundle.get("paths", {}),
        },
        "synthetic_metrics": {
            "trust_proxy": trust,
            "risk_score": risk,
            "alerts": alerts,
        },
        "verdict": {
            "status": verdict,
            "message": verdict_msg,
        },
        "real_module_attempts": real,
        "recommendations": [
            "Use BEGINNER/INTERMEDIATE for baseline regression runs.",
            "Use ADVERSARIAL to test drift/resilience and SPS defenses.",
            "If FAIL occurs repeatedly on baseline, lock pipeline and run integrity checks.",
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

        report["paths"] = {
            "json_latest": str(latest_json),
            "json_stamped": str(stamped_json),
            "txt": str(txt_path),
        }

    return report


def _render_txt(report: Dict[str, Any]) -> str:
    sm = report.get("synthetic_metrics", {})
    verdict = report.get("verdict", {})
    inputs = report.get("inputs", {})
    alerts = sm.get("alerts", {})

    lines = []
    lines.append("GLL — Synthetic Fusion Validation Report (SAFE)")
    lines.append("=" * 48)
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append(f"Difficulty: {inputs.get('difficulty')}")
    lines.append(f"Seed: {inputs.get('seed')}")
    lines.append("")
    lines.append("Synthetic Metrics")
    lines.append("-" * 48)
    lines.append(f"Trust Proxy (0–100): {sm.get('trust_proxy')}")
    lines.append(f"Risk Score (0–100):  {sm.get('risk_score')}")
    lines.append(f"Alerts: CRIT={alerts.get('crit',0)} HIGH={alerts.get('high',0)} "
                 f"ATTACK_LIKE={alerts.get('attack_like',0)} ANOM={alerts.get('anomaly',0)}")
    lines.append("")
    lines.append("Verdict")
    lines.append("-" * 48)
    lines.append(f"{verdict.get('status')}: {verdict.get('message')}")
    lines.append("")
    lines.append("Notes")
    lines.append("-" * 48)
    lines.append("• This is synthetic-only telemetry: safe for demos/training.")
    lines.append("• Use this run as a regression harness before/after hardening changes.")
    return "\n".join(lines)


def write_validation_report(
    difficulty: str = "INTERMEDIATE",
    seed: Optional[int] = 42,
) -> Dict[str, str]:
    report = run_synthetic_fusion_validation(difficulty=difficulty, seed=seed, write=True)
    p = report.get("paths", {})
    return {
        "json_path": p.get("json_latest", ""),
        "txt_path": p.get("txt", ""),
        "status": report.get("verdict", {}).get("status", ""),
    }


if __name__ == "__main__":
    res = write_validation_report(difficulty="INTERMEDIATE", seed=42)
    print("Validation report written:")
    print(f"  JSON: {res['json_path']}")
    print(f"  TXT:  {res['txt_path']}")
    print(f"  Status: {res['status']}")

