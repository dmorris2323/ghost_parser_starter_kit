from __future__ import annotations

import json
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


OUT_DIR = Path("docs") / "validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LATEST_JSON = OUT_DIR / "fusion_core_regression_latest.json"
LATEST_TXT = OUT_DIR / "fusion_core_regression_latest.txt"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_call(label: str, fn, *args, **kwargs) -> Dict[str, Any]:
    try:
        result = fn(*args, **kwargs)
        return {"ok": True, "label": label, "result": result}
    except Exception as e:
        return {
            "ok": False,
            "label": label,
            "error_type": type(e).__name__,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def _exists(path: Path) -> bool:
    try:
        return path.exists()
    except Exception:
        return False


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _call_first_callable(module, names: List[str], *args, **kwargs):
    """
    Returns (name_used, result) calling the first callable attribute found.
    Raises AttributeError if none found.
    """
    for n in names:
        fn = getattr(module, n, None)
        if callable(fn):
            return n, fn(*args, **kwargs)
    raise AttributeError(f"No callable found in {module.__name__} for any of: {names}")


@dataclass
class RegressionReport:
    generated_at_utc: str
    verdict: str
    crashes: int
    checks: List[Dict[str, Any]]
    required_artifacts: Dict[str, bool]


def run_regression(context: str = "fusion_core_regression", update_baselines: bool = False) -> Dict[str, Any]:
    """
    Fusion Core Regression Gate
    - Runs SIS/SPS gates
    - Runs fusion validation + degraded validation
    - Runs commander brief one-shot
    - Runs key base defense products
    - Verifies "latest" artifacts exist
    """
    checks: List[Dict[str, Any]] = []
    crashes = 0

    # --- 1) SIS/SPS gates ---
    def _run_gates(gate_type: str) -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        from gll_run_gates import run_gates
        return run_gates(gate_type=gate_type, context=context, update_baselines=update_baselines)

    checks.append(_safe_call("GATES_PRE", _run_gates, "PRE"))
    checks.append(_safe_call("GATES_POST", _run_gates, "POST"))

    # --- 2) Fusion validation harness (tolerate current API) ---
    def _run_fusion_validation() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        import fusion_validation_harness as fvh

        # Try common entrypoints without changing your module.
        # Keep difficulty stable.
        name_used, res = _call_first_callable(
            fvh,
            names=[
                "run_validation_harness",     # what we tried originally
                "run_harness",                # common alt
                "run_validation",             # common alt
                "main",                       # some scripts use main()
            ],
            **({"difficulty": "INTERMEDIATE"} if hasattr(fvh, "__dict__") else {}),
        )
        return {"entrypoint": name_used, "result": res}

    checks.append(_safe_call("FUSION_VALIDATION", _run_fusion_validation))

    # --- 3) Degraded fusion validation ---
    def _run_degraded_validation() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        from fusion_degraded_validation import run_degraded_fusion_test
        return run_degraded_fusion_test(difficulty="INTERMEDIATE")

    checks.append(_safe_call("DEGRADED_FUSION_VALIDATION", _run_degraded_validation))

    # --- 4) Commander brief one-shot ---
    def _run_commander_brief_one_shot() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        from briefing_runbook import run_commander_brief_one_shot
        return run_commander_brief_one_shot(context=f"{context}_brief_one_shot", update_baselines=False)

    checks.append(_safe_call("COMMANDER_BRIEF_ONE_SHOT", _run_commander_brief_one_shot))

    # --- 5) Base Defense sealed products quickrun (best-effort, tolerate entrypoints) ---
    def _run_sensor_outage_predictor() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        import sensor_outage_predictor as sop
        name_used, res = _call_first_callable(sop, ["main", "run", "generate", "__call__"])
        return {"entrypoint": name_used, "result": res}

    def _run_installation_threat_map() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        import installation_threat_map as itm
        name_used, res = _call_first_callable(itm, ["main", "run", "generate", "build_report"])
        return {"entrypoint": name_used, "result": res}

    def _run_perimeter_incident_report() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        import perimeter_incident_report as pir
        name_used, res = _call_first_callable(pir, ["main", "run", "generate", "build_report"])
        return {"entrypoint": name_used, "result": res}

    def _run_base_defense_storyboard() -> Dict[str, Any]:
        import sys
        sys.path.insert(0, "src")
        import base_defense_storyboard as bds
        name_used, res = _call_first_callable(bds, ["main", "run", "generate", "build_storyboard"])
        return {"entrypoint": name_used, "result": res}

    checks.append(_safe_call("BASEDEF_SENSOR_OUTAGE", _run_sensor_outage_predictor))
    checks.append(_safe_call("BASEDEF_INSTALLATION_THREAT_MAP", _run_installation_threat_map))
    checks.append(_safe_call("BASEDEF_PERIMETER_INCIDENT", _run_perimeter_incident_report))
    checks.append(_safe_call("BASEDEF_STORYBOARD", _run_base_defense_storyboard))

    # Count crashes
    for c in checks:
        if not c.get("ok", False):
            crashes += 1

    # --- 6) Artifact existence checks (latest surfaces) ---
    required = {
        "src/docs/validation/fusion_validation_report.json": _exists(Path("src/docs/validation/fusion_validation_report.json")),
        "src/docs/validation/degraded_fusion_validation_latest.json": _exists(Path("src/docs/validation/degraded_fusion_validation_latest.json")),
        "docs/briefs/commander_brief_latest.txt": _exists(Path("docs/briefs/commander_brief_latest.txt")),
        "docs/briefs/prebrief_trust_annotations_latest.txt": _exists(Path("docs/briefs/prebrief_trust_annotations_latest.txt")),
        "docs/base_defense/sensor_outage_predictor_latest.json": _exists(Path("docs/base_defense/sensor_outage_predictor_latest.json")),
        "docs/base_defense/installation_threat_map_latest.json": _exists(Path("docs/base_defense/installation_threat_map_latest.json")),
        "docs/base_defense/perimeter_incident_report_latest.json": _exists(Path("docs/base_defense/perimeter_incident_report_latest.json")),
        "docs/base_defense/base_defense_storyboard_latest.json": _exists(Path("docs/base_defense/base_defense_storyboard_latest.json")),
    }

    verdict = "PASS"
    if crashes > 0:
        verdict = "FAIL"
    if not all(required.values()):
        verdict = "FAIL"

    report = RegressionReport(
        generated_at_utc=_utc_now_iso(),
        verdict=verdict,
        crashes=crashes,
        checks=checks,
        required_artifacts=required,
    ).__dict__

    # Write latest + stamped
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    stamped_json = OUT_DIR / f"fusion_core_regression_{stamp}.json"
    stamped_txt = OUT_DIR / f"fusion_core_regression_{stamp}.txt"

    _write_json(LATEST_JSON, report)
    _write_json(stamped_json, report)

    lines = []
    lines.append("Fusion Core Regression Gate")
    lines.append(f"generated_at_utc: {report['generated_at_utc']}")
    lines.append(f"verdict: {report['verdict']}")
    lines.append(f"crashes: {report['crashes']}")
    lines.append("")
    lines.append("Required artifacts:")
    for k, v in report["required_artifacts"].items():
        lines.append(f"- {k}: {'OK' if v else 'MISSING'}")
    lines.append("")
    lines.append("Checks:")
    for c in report["checks"]:
        if c["ok"]:
            lines.append(f"- PASS: {c['label']}")
        else:
            lines.append(f"- FAIL: {c['label']} ({c.get('error_type')}:{c.get('error')})")

    _write_text(LATEST_TXT, "\n".join(lines) + "\n")
    _write_text(stamped_txt, "\n".join(lines) + "\n")

    return {
        "verdict": verdict,
        "latest_json": str(LATEST_JSON),
        "latest_txt": str(LATEST_TXT),
        "stamped_json": str(stamped_json),
        "stamped_txt": str(stamped_txt),
        "crashes": crashes,
        "missing_artifacts": [k for k, v in required.items() if not v],
    }


def main() -> None:
    res = run_regression(context="day73_week3_fusion_core_regression", update_baselines=False)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

