from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# GLL RUN GATES
# - PRE gate: must be GREEN before training sessions count or validation runs
# - POST gate: runs after actions to capture integrity state
#
# Key upgrade in this file:
#   run_gates(..., raise_on_fail=False) returns {ok: False, ...} instead of raising,
#   so Streamlit apps can display the failure without crashing.
# ──────────────────────────────────────────────────────────────────────────────


REPO_ROOT = Path(__file__).resolve().parents[1]  # .../parser_starter_kit/src -> repo root
DOCS_DIR = REPO_ROOT / "src" / "docs"
INTEGRITY_DIR = DOCS_DIR / "integrity"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False))


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text)


def _soft_import(fn_path: str, fn_name: str):
    """
    Import a function defensively so missing modules don’t crash the whole gate runner.
    Returns (callable_or_none, error_or_none)
    """
    try:
        mod = __import__(fn_path, fromlist=[fn_name])
        fn = getattr(mod, fn_name)
        return fn, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _summarize_check(name: str, ok: bool, details: str = "") -> Dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details}


def _checks_ok(checks: List[Dict[str, Any]]) -> bool:
    return all(bool(c.get("ok")) for c in checks)


def _format_report_txt(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"GLL RUN GATES REPORT")
    lines.append(f"generated_at_utc: {payload.get('generated_at_utc')}")
    lines.append(f"gate_type: {payload.get('gate_type')}")
    lines.append(f"context: {payload.get('context')}")
    lines.append(f"ok: {payload.get('ok')}")
    lines.append("")
    lines.append("CHECKS:")
    for c in payload.get("checks", []):
        status = "PASS" if c.get("ok") else "FAIL"
        lines.append(f" - {status}: {c.get('name')}")
        if c.get("details"):
            lines.append(f"    {c.get('details')}")
    lines.append("")
    if payload.get("artifacts"):
        lines.append("ARTIFACTS:")
        for k, v in payload["artifacts"].items():
            lines.append(f" - {k}: {v}")
    if payload.get("errors"):
        lines.append("")
        lines.append("ERRORS:")
        for k, v in payload["errors"].items():
            lines.append(f" - {k}: {v}")
    return "\n".join(lines).strip() + "\n"


def _run_internal_gates(
    *,
    gate_type: str,
    context: str,
    update_baselines: bool = False,
) -> Dict[str, Any]:
    """
    Internal runner that ALWAYS returns a structured result and NEVER raises.
    The public run_gates() decides whether to raise based on raise_on_fail.
    """

    gate_type = gate_type.upper().strip()
    if gate_type not in {"PRE", "POST"}:
        # keep this strict — programmer error
        raise ValueError("gate_type must be 'PRE' or 'POST'")

    _safe_mkdir(INTEGRITY_DIR)

    stamp = _utc_stamp()
    report_txt = INTEGRITY_DIR / f"run_gate_{gate_type.lower()}_{context}_{stamp}.txt"
    report_json = INTEGRITY_DIR / f"run_gate_{gate_type.lower()}_{context}_{stamp}.json"

    checks: List[Dict[str, Any]] = []
    artifacts: Dict[str, str] = {}
    errors: Dict[str, str] = {}

    # ── CHECK 1: System Integrity Report (SIS) ───────────────────────────────
    # Expected module: system_integrity_report.generate_system_integrity_report
    sis_fn, sis_err = _soft_import("system_integrity_report", "generate_system_integrity_report")
    if sis_fn is None:
        checks.append(_summarize_check("SIS: system_integrity_report.generate_system_integrity_report", False, sis_err or "missing"))
        errors["sis_import"] = sis_err or "missing"
    else:
        try:
            sis_result = sis_fn()
            # sis_result can be dict or path — normalize best-effort
            sis_ok = True
            if isinstance(sis_result, dict) and "ok" in sis_result:
                sis_ok = bool(sis_result.get("ok"))
            checks.append(_summarize_check("SIS: System Integrity Report", sis_ok, "generated"))
            # capture paths if present
            if isinstance(sis_result, dict):
                for k in ("txt_path", "json_path", "path", "report_path"):
                    if k in sis_result and sis_result[k]:
                        artifacts[f"sis_{k}"] = str(sis_result[k])
        except Exception as e:
            checks.append(_summarize_check("SIS: System Integrity Report", False, f"{type(e).__name__}: {e}"))
            errors["sis_run"] = f"{type(e).__name__}: {e}"

    # ── CHECK 2: SPS Immunity Scan (Mutation/Immunity) ───────────────────────
    # Expected module: sps_mutation_watcher.run_sps_immunity_scan
    sps_imm_fn, sps_imm_err = _soft_import("sps_mutation_watcher", "run_sps_immunity_scan")
    if sps_imm_fn is None:
        checks.append(_summarize_check("SPS: sps_mutation_watcher.run_sps_immunity_scan", False, sps_imm_err or "missing"))
        errors["sps_immunity_import"] = sps_imm_err or "missing"
    else:
        try:
            imm_result = sps_imm_fn()
            imm_ok = True
            if isinstance(imm_result, dict) and "ok" in imm_result:
                imm_ok = bool(imm_result.get("ok"))
            checks.append(_summarize_check("SPS: Immunity Scan", imm_ok, "generated"))
            if isinstance(imm_result, dict):
                for k in ("txt_path", "json_path", "path", "report_path"):
                    if k in imm_result and imm_result[k]:
                        artifacts[f"sps_immunity_{k}"] = str(imm_result[k])
        except Exception as e:
            checks.append(_summarize_check("SPS: Immunity Scan", False, f"{type(e).__name__}: {e}"))
            errors["sps_immunity_run"] = f"{type(e).__name__}: {e}"

    # ── CHECK 3: SPS Behavioral Integrity Monitor ────────────────────────────
    # Expected module: sps_behavior_monitor.write_behavior_report
    sps_beh_fn, sps_beh_err = _soft_import("sps_behavior_monitor", "write_behavior_report")
    if sps_beh_fn is None:
        checks.append(_summarize_check("SPS: sps_behavior_monitor.write_behavior_report", False, sps_beh_err or "missing"))
        errors["sps_behavior_import"] = sps_beh_err or "missing"
    else:
        try:
            beh_result = sps_beh_fn()
            beh_ok = True
            if isinstance(beh_result, dict) and "ok" in beh_result:
                beh_ok = bool(beh_result.get("ok"))
            checks.append(_summarize_check("SPS: Behavioral Integrity Monitor", beh_ok, "generated"))
            if isinstance(beh_result, dict):
                for k in ("txt_path", "json_path", "path", "report_path"):
                    if k in beh_result and beh_result[k]:
                        artifacts[f"sps_behavior_{k}"] = str(beh_result[k])
        except Exception as e:
            checks.append(_summarize_check("SPS: Behavioral Integrity Monitor", False, f"{type(e).__name__}: {e}"))
            errors["sps_behavior_run"] = f"{type(e).__name__}: {e}"

    # ── Final verdict ────────────────────────────────────────────────────────
    ok = _checks_ok(checks)

    payload: Dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate_type": gate_type,
        "context": context,
        "update_baselines": bool(update_baselines),
        "ok": ok,
        "checks": checks,
        "artifacts": artifacts,
        "errors": errors,
        "report_path": str(report_txt),
        "report_json": str(report_json),
    }

    _write_json(report_json, payload)
    _write_txt(report_txt, _format_report_txt(payload))

    return payload


def run_gates(
    *,
    gate_type: str,
    context: str,
    update_baselines: bool = False,
    raise_on_fail: bool = True,
) -> Dict[str, Any]:
    """
    Run SIS + SPS and write a combined report.

    gate_type: "PRE" or "POST"
    context: string tag (e.g., "training_session_append", "fusion_validation_harness")
    update_baselines: NEVER default to True. Use only when you intentionally accept new baselines.
    raise_on_fail:
        - True  => raise RuntimeError if gate fails (good for CLI/pipelines)
        - False => return structured failure without raising (required for Streamlit UI)
    """
    result = _run_internal_gates(
        gate_type=gate_type,
        context=context,
        update_baselines=update_baselines,
    )

    if (not result.get("ok", False)) and raise_on_fail:
        raise RuntimeError(
            f"GLL {gate_type}-GATE FAIL for context '{context}'. "
            f"See {result.get('report_path')} and {result.get('report_json')}"
        )

    return result


if __name__ == "__main__":
    # Simple manual run:
    r = run_gates(gate_type="PRE", context="manual", raise_on_fail=False)
    print(json.dumps(r, indent=2))

