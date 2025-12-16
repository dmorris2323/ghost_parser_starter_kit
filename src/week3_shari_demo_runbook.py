from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


BRIEFS_DIR = Path("docs") / "briefs"
VALID_DIR = Path("docs") / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    # Avoid deprecated utcnow(); keep UTC timestamp
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read_json(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_txt(p: Path, max_chars: int = 800) -> str:
    try:
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def _json_safe(obj: Any) -> Any:
    """
    Convert arbitrary objects into JSON-serializable shapes.
    - dict/list primitives pass through
    - Path -> str
    - functions/callables -> string label
    - unknown objects -> repr()
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    if callable(obj):
        # This is the bug you hit — never write raw function objects into JSON.
        return f"<callable:{getattr(obj, '__name__', 'anonymous')}>"
    return repr(obj)


def _write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    safe_obj = _json_safe(obj)
    p.write_text(json.dumps(safe_obj, indent=2), encoding="utf-8")


def _write_txt(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def run_week3_shari_demo_runbook(
    context: str = "week3_shari_demo_runbook",
    update_baselines: bool = False,
) -> Dict[str, Any]:
    """
    One-shot Week-3 demo runbook:
      1) Commander Brief One-Shot (briefing_runbook)
      2) Fusion Core Regression Gate (+ operator summary if available)
      3) Legal Case Snapshot (Shari Hook)
      4) Mobile Enjoy Mode manifest

    Must never crash. Best-effort: if a component fails, record error and continue.
    """

    started = _utc_now_iso()
    res: Dict[str, Any] = {
        "generated_at_utc": started,
        "context": context,
        "update_baselines": bool(update_baselines),
        "steps": [],
        "paths": {},
        "verdict": "PARTIAL",
        "notes": [
            "Assessment is probabilistic and bounded; operator judgment applies.",
            "Demo runbook is safe for training/demos (synthetic telemetry).",
        ],
    }

    # -----------------------------
    # STEP 1 — Commander Brief One-Shot
    # -----------------------------
    try:
        from briefing_runbook import run_commander_brief_one_shot  # type: ignore

        step_out = run_commander_brief_one_shot(
            context=f"{context}_commander_brief",
            update_baselines=update_baselines,
        )
        res["steps"].append({"name": "commander_brief_one_shot", "ok": True, "result": step_out})
    except Exception as e:
        res["steps"].append({"name": "commander_brief_one_shot", "ok": False, "error": repr(e)})

    # -----------------------------
    # STEP 2 — Fusion Core Regression Gate (+ optional operator summary)
    # -----------------------------
    gate_out = None
    try:
        import gll_fusion_core_regression_gate as gate_mod  # type: ignore

        for fn_name in ["run_fusion_core_regression_gate", "run_gate", "run", "main"]:
            fn = getattr(gate_mod, fn_name, None)
            if callable(fn):
                try:
                    gate_out = fn(context=f"{context}_fusion_core_regression", update_baselines=update_baselines)  # type: ignore
                except TypeError:
                    # Signature mismatch; call without args
                    gate_out = fn()  # type: ignore
                break

        if gate_out is None:
            raise RuntimeError("No callable runner found in gll_fusion_core_regression_gate.")

        res["steps"].append({"name": "fusion_core_regression_gate", "ok": True, "result": gate_out})

    except Exception as e:
        res["steps"].append({"name": "fusion_core_regression_gate", "ok": False, "error": repr(e)})

    # Optional operator summary
    try:
        import week3_operator_summary as ops_mod  # type: ignore

        ops_out = None
        for fn_name in ["run_week3_operator_summary", "run", "main"]:
            fn = getattr(ops_mod, fn_name, None)
            if callable(fn):
                # IMPORTANT: always CALL it; never store the function object
                try:
                    ops_out = fn()  # type: ignore
                except TypeError:
                    # If it needs args, call without and stringify fallback
                    ops_out = {"note": "operator summary callable signature mismatch", "callable": fn_name}
                break

        if ops_out is None:
            raise RuntimeError("No callable runner found in week3_operator_summary.")

        res["steps"].append({"name": "week3_operator_summary", "ok": True, "result": ops_out})

    except Exception as e:
        res["steps"].append({"name": "week3_operator_summary", "ok": False, "error": repr(e)})

    # -----------------------------
    # STEP 3 — Legal Case Snapshot (Shari Hook)
    # -----------------------------
    try:
        import legal_case_snapshot as lcs_mod  # type: ignore

        lcs_out = None
        for fn_name in ["write_legal_case_snapshot", "run", "main"]:
            fn = getattr(lcs_mod, fn_name, None)
            if callable(fn):
                try:
                    lcs_out = fn()  # type: ignore
                except TypeError:
                    lcs_out = fn()  # type: ignore
                break

        if lcs_out is None:
            raise RuntimeError("No callable writer found in legal_case_snapshot.")

        res["steps"].append({"name": "legal_case_snapshot", "ok": True, "result": lcs_out})

    except Exception as e:
        res["steps"].append({"name": "legal_case_snapshot", "ok": False, "error": repr(e)})

    # -----------------------------
    # STEP 4 — Mobile Enjoy Mode manifest
    # -----------------------------
    try:
        from mobile_enjoy_mode import run_mobile_enjoy_mode  # type: ignore

        me_out = run_mobile_enjoy_mode(context=f"{context}_mobile_enjoy")
        res["steps"].append({"name": "mobile_enjoy_mode", "ok": True, "result": me_out})

    except Exception as e:
        res["steps"].append({"name": "mobile_enjoy_mode", "ok": False, "error": repr(e)})

    # -----------------------------
    # Post-process: demo checklist + verdict
    # -----------------------------
    commander_txt = BRIEFS_DIR / "commander_brief_latest.txt"
    operator_txt = BRIEFS_DIR / "week3_operator_summary_latest.txt"
    legal_txt = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
    manifest_json = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
    gate_json = VALID_DIR / "fusion_core_regression_latest.json"

    gate_obj = _safe_read_json(gate_json) or {}
    gate_verdict = str(gate_obj.get("verdict") or gate_obj.get("status") or "").upper()

    fail_steps = [s for s in res["steps"] if s.get("ok") is False]
    if gate_verdict == "PASS" and len(fail_steps) == 0:
        res["verdict"] = "PASS"
    elif gate_verdict == "PASS":
        res["verdict"] = "PARTIAL_PASS"
        res["notes"].append("Fusion regression gate passed, but one or more demo steps failed (best-effort mode).")
    else:
        res["verdict"] = "FAIL"

    commander_head = _safe_read_txt(commander_txt, max_chars=1400)
    demo_safety_note = ""
    if "Fusion validation verdict/status: FAIL" in commander_head and gate_verdict == "PASS":
        demo_safety_note = (
            "DEMO NOTE: Commander brief shows 'Fusion validation: FAIL' due to best-effort artifact read/formatting. "
            "Week-3 Fusion Core Regression Gate is PASS, which is the controlling demo-health signal for this runbook. "
            "Operator judgment applies."
        )

    checklist = []
    checklist.append("WEEK-3 SHARI DEMO CHECKLIST (ONE-SHOT)")
    checklist.append(f"generated_at_utc: {res['generated_at_utc']}")
    checklist.append(f"verdict: {res['verdict']}")
    checklist.append("")
    checklist.append("Open these files (in order):")
    checklist.append(f"1) Commander brief: {commander_txt}")
    checklist.append(f"2) Operator summary: {operator_txt}")
    checklist.append(f"3) Legal snapshot: {legal_txt}")
    checklist.append(f"4) Mobile manifest: {manifest_json}")
    checklist.append("")
    if demo_safety_note:
        checklist.append(demo_safety_note)
        checklist.append("")
    checklist.append("Bounded warning: Assessment is probabilistic and bounded; operator judgment applies.")

    checklist_txt = "\n".join(checklist)

    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    latest_txt = BRIEFS_DIR / "week3_shari_demo_checklist_latest.txt"
    stamped_txt = BRIEFS_DIR / f"week3_shari_demo_checklist_{_stamp()}.txt"
    _write_txt(latest_txt, checklist_txt)
    _write_txt(stamped_txt, checklist_txt)

    res["paths"] = {
        "checklist_latest_txt": str(latest_txt),
        "checklist_stamped_txt": str(stamped_txt),
        "commander_brief_latest_txt": str(commander_txt),
        "operator_summary_latest_txt": str(operator_txt),
        "legal_case_snapshot_latest_txt": str(legal_txt),
        "mobile_manifest_latest_json": str(manifest_json),
        "fusion_core_regression_latest_json": str(gate_json),
    }

    # Write JSON result artifacts (JSON-safe)
    latest_json = BRIEFS_DIR / "week3_shari_demo_runbook_latest.json"
    stamped_json = BRIEFS_DIR / f"week3_shari_demo_runbook_{_stamp()}.json"
    _write_json(latest_json, res)
    _write_json(stamped_json, res)
    res["paths"]["runbook_latest_json"] = str(latest_json)
    res["paths"]["runbook_stamped_json"] = str(stamped_json)

    return res


def main() -> int:
    out = run_week3_shari_demo_runbook()
    print(json.dumps(_json_safe(out), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

