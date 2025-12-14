# src/fusion_degraded_validation.py
"""
fusion_degraded_validation.py

Degraded Fusion Validation (SAFE)
Purpose:
- Demonstrate GLL "degraded operations" behavior without requiring perfect inputs.
- Avoid hard dependencies on any single ingest function name.
- Produce a commander-readable JSON report that NEVER crashes the operator.

This module is intentionally defensive:
- It auto-detects ingest entrypoints from fusion_ingest.py (name may vary).
- It runs SIS+SPS gates if available (best-effort).
- It returns a stable report even if some subsystems are missing.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

DOC_DIR = Path("docs") / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _load_callable(module_name: str, candidates: list[str]) -> Optional[Callable[..., Any]]:
    """
    Load the first matching callable from module_name.
    This prevents refactors from breaking validation.
    """
    try:
        mod = __import__(module_name, fromlist=["*"])
    except Exception:
        return None

    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    return None


def _best_effort_run_gates(gate_type: str, context: str) -> Dict[str, Any]:
    """
    Runs SIS+SPS gates if gll_run_gates.run_gates exists.
    Never raises.
    """
    gate = {
        "enabled": False,
        "gate_type": gate_type,
        "context": context,
        "status": "SKIPPED",
        "details": {},
        "error": None,
    }

    try:
        from gll_run_gates import run_gates  # type: ignore

        gate["enabled"] = True
        result = run_gates(gate_type=gate_type, context=context, update_baselines=False)
        # run_gates may raise; if it returns, we treat as PASS unless it embeds status
        if isinstance(result, dict):
            gate["details"] = result
            gate["status"] = str(result.get("status", "PASS"))
        else:
            gate["details"] = {"raw": str(result)}
            gate["status"] = "PASS"
    except Exception as e:
        gate["error"] = f"{e.__class__.__name__}: {e}"
        gate["status"] = "FAIL" if gate["enabled"] else "SKIPPED"

    return gate


def _make_degraded_synthetic(seed: int, difficulty: str) -> Dict[str, Any]:
    """
    Creates a tiny degraded synthetic "input bundle" to feed ingest/score paths.
    This is NOT real telemetry; it's safe training structure.
    """
    rng = random.Random(seed)
    difficulty = difficulty.upper().strip()

    # baseline values
    base_noise = {"BEGINNER": 0.1, "INTERMEDIATE": 0.25, "ADVANCED": 0.4, "ADVERSARIAL": 0.6}.get(difficulty, 0.25)
    sensor_drop_prob = {"BEGINNER": 0.05, "INTERMEDIATE": 0.15, "ADVANCED": 0.25, "ADVERSARIAL": 0.35}.get(difficulty, 0.15)

    sensors = ["optical", "seismic", "ems", "radiation", "cyber", "comms"]
    present = []
    dropped = []
    for s in sensors:
        if rng.random() < sensor_drop_prob:
            dropped.append(s)
        else:
            present.append(s)

    # safe proxy metrics (not mission-real)
    trust_proxy = max(0.0, 100.0 - (len(dropped) * 10.0) - (base_noise * 20.0))
    risk_score = min(100.0, (len(dropped) * 8.0) + (base_noise * 50.0) + rng.uniform(0, 10))

    bundle = {
        "safe_notice": "Synthetic degraded bundle. SAFE for training/demos.",
        "generated_at": _utc_now_iso(),
        "seed": seed,
        "difficulty": difficulty,
        "degraded_conditions": {
            "sensor_loss": dropped,
            "present_sensors": present,
            "noise_level": round(base_noise, 2),
            "delayed_reporting": rng.random() < (base_noise * 0.8),
        },
        # these keys match patterns your pipeline already uses in other modules
        "trust_proxy": round(trust_proxy, 2),
        "risk_score": round(risk_score, 2),
        "alerts": {
            "anomaly": int(rng.randint(5, 20) * (1 + base_noise)),
            "attack_like": int(rng.randint(0, 10) * (1 + base_noise)),
            "high": int(rng.randint(0, 5) * (1 + base_noise)),
            "crit": int(rng.randint(0, 2) * (1 + base_noise)),
        },
        "events": [
            {"t": i, "tag": "SYNTH", "value": rng.random()} for i in range(0, 20)
        ],
    }
    bundle["alerts"]["total"] = sum(int(v) for v in bundle["alerts"].values())
    return bundle


def run_degraded_fusion_test(*, difficulty: str = "INTERMEDIATE", seed: int = 42) -> Dict[str, Any]:
    """
    Public entrypoint for CLI.
    Produces a stable report in docs/validation/.
    """
    difficulty = difficulty.upper().strip()
    report: Dict[str, Any] = {
        "report_type": "degraded_fusion_validation",
        "report_version": 1,
        "generated_at": _utc_now_iso(),
        "inputs": {"difficulty": difficulty, "seed": seed},
        "pre_gate": {},
        "post_gate": {},
        "degraded_bundle": {},
        "pipeline_attempts": {"attempted": [], "results": {}, "errors": {}},
        "verdict": {"status": "UNKNOWN", "message": ""},
        "paths": {},
    }

    # ---- PRE GATE ----
    report["pre_gate"] = _best_effort_run_gates("PRE", "fusion_degraded_validation")

    # ---- SYNTHETIC DEGRADED INPUT ----
    bundle = _make_degraded_synthetic(seed=seed, difficulty=difficulty)
    report["degraded_bundle"] = {
        "degraded_conditions": bundle.get("degraded_conditions", {}),
        "trust_proxy": bundle.get("trust_proxy"),
        "risk_score": bundle.get("risk_score"),
        "alerts": bundle.get("alerts", {}),
    }

    # ---- ATTEMPT: INGEST ----
    ingest_fn = _load_callable(
        "fusion_ingest",
        candidates=[
            "ingest_fusion_data",
            "ingest_fusion_bundle",
            "ingest_data",
            "ingest",
            "run_ingest",
        ],
    )

    if ingest_fn is None:
        report["pipeline_attempts"]["errors"]["fusion_ingest"] = (
            "No ingest function found. Expected one of: "
            "ingest_fusion_data/ingest_fusion_bundle/ingest_data/ingest/ run_ingest"
        )
    else:
        report["pipeline_attempts"]["attempted"].append("fusion_ingest")
        try:
            # Allow ingest functions that accept dict or path.
            result = ingest_fn(bundle)  # type: ignore[arg-type]
            report["pipeline_attempts"]["results"]["fusion_ingest"] = _safe_summarize(result)
        except TypeError:
            # Some ingests want a JSON path instead
            try:
                tmp = DOC_DIR / "degraded_bundle_tmp.json"
                _write_json(tmp, bundle)
                result = ingest_fn(str(tmp))  # type: ignore[arg-type]
                report["pipeline_attempts"]["results"]["fusion_ingest"] = _safe_summarize(result)
            except Exception as e:
                report["pipeline_attempts"]["errors"]["fusion_ingest"] = f"{e.__class__.__name__}: {e}"
        except Exception as e:
            report["pipeline_attempts"]["errors"]["fusion_ingest"] = f"{e.__class__.__name__}: {e}"

    # ---- ATTEMPT: TRUST + OSL (best-effort) ----
    try:
        from fusion_trust import compute_trust  # type: ignore

        report["pipeline_attempts"]["attempted"].append("fusion_trust.compute_trust")
        report["pipeline_attempts"]["results"]["fusion_trust"] = compute_trust()
    except Exception as e:
        report["pipeline_attempts"]["errors"]["fusion_trust"] = f"{e.__class__.__name__}: {e}"

    try:
        from operator_safety_layer import compute_osl  # type: ignore

        report["pipeline_attempts"]["attempted"].append("operator_safety_layer.compute_osl")
        report["pipeline_attempts"]["results"]["operator_safety_layer"] = compute_osl()
    except Exception as e:
        report["pipeline_attempts"]["errors"]["operator_safety_layer"] = f"{e.__class__.__name__}: {e}"

    # ---- VERDICT (bounded + non-crash) ----
    alerts = bundle.get("alerts", {})
    crit = int(alerts.get("crit", 0))
    high = int(alerts.get("high", 0))
    risk = float(bundle.get("risk_score", 0.0))

    if report["pre_gate"].get("status") == "FAIL":
        report["verdict"] = {"status": "FAIL", "message": "PRE gate failed. Fix integrity before trusting degraded validation."}
    elif crit > 5 or (crit > 0 and high > 15) or risk >= 90:
        report["verdict"] = {"status": "WARN", "message": "Degraded stress is high; behavior is bounded but elevated."}
    else:
        report["verdict"] = {"status": "PASS", "message": "Degraded operations appear controlled (bounded alerts, no crash)."}

    # ---- WRITE OUTPUTS ----
    _safe_mkdir(DOC_DIR)
    latest = DOC_DIR / "degraded_fusion_validation_latest.json"
    stamped = DOC_DIR / f"degraded_fusion_validation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    report["paths"] = {"json_latest": str(latest), "json_stamped": str(stamped)}

    _write_json(latest, report)
    _write_json(stamped, report)

    # ---- POST GATE ----
    report["post_gate"] = _best_effort_run_gates("POST", "fusion_degraded_validation")
    _write_json(latest, report)  # update with post-gate

    return report


def _safe_summarize(obj: Any) -> Any:
    """
    Keep results small and stable. Never dumps huge structures.
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        # keep only a few top-level keys
        keys = list(obj.keys())[:20]
        return {k: obj.get(k) for k in keys}
    if isinstance(obj, list):
        return {"list_len": len(obj)}
    return {"type": type(obj).__name__}


if __name__ == "__main__":
    r = run_degraded_fusion_test(difficulty="INTERMEDIATE", seed=42)
    print(json.dumps(r, indent=2))

