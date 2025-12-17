# src/week3_cloud_demo_packager.py
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "docs" / "briefs"
VALIDATION_DIR = ROOT / "docs" / "validation"
PACKAGES_DIR = ROOT / "docs" / "packages"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def _collect_week3_files() -> List[Path]:
    return [
        # Briefs
        BRIEFS_DIR / "commander_brief_latest.txt",
        BRIEFS_DIR / "commander_brief_latest.json",
        BRIEFS_DIR / "week3_operator_summary_latest.txt",
        BRIEFS_DIR / "legal_case_snapshot_latest.txt",
        BRIEFS_DIR / "legal_case_snapshot_latest.json",
        BRIEFS_DIR / "legal_case_snapshot_stress_latest.json",
        BRIEFS_DIR / "week3_demo_narrative_latest.txt",
        BRIEFS_DIR / "week3_demo_narrative_latest.json",
        BRIEFS_DIR / "mobile_enjoy_manifest_latest.json",
        BRIEFS_DIR / "week3_shari_demo_packet_latest.txt",
        BRIEFS_DIR / "week3_demo_orchestrator_latest.json",
        BRIEFS_DIR / "week3_demo_orchestrator_latest.txt",
        # Validation
        VALIDATION_DIR / "fusion_core_regression_latest.json",
        VALIDATION_DIR / "fusion_core_regression_latest.txt",
        VALIDATION_DIR / "week3_demo_pack_gate_latest.json",
        VALIDATION_DIR / "week3_demo_readiness_gate_latest.json",
        VALIDATION_DIR / "week3_demo_readiness_gate_latest.txt",
        # Packages (generated)
        PACKAGES_DIR / "week3_customer_handoff_one_pager_latest.md",
        PACKAGES_DIR / "week3_customer_handoff_one_pager_latest.txt",
        PACKAGES_DIR / "week3_demo_runbook_latest.md",
        PACKAGES_DIR / "week3_demo_runbook_latest.txt",
        PACKAGES_DIR / "week3_executive_summary_latest.html",
        PACKAGES_DIR / "week3_executive_summary_latest.txt",
    ]


def _write_manifest(latest: Path, stamped: Path, manifest: Dict[str, Any]) -> None:
    try:
        latest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    except Exception:
        pass
    try:
        stamped.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    except Exception:
        pass


def run_week3_cloud_demo_packager(
    context: str = "week3_cloud_demo_packager",
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Builds a cloud-ready demo package zip and manifest.
    Must never crash.
    """
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    generated = _utc_now_iso()
    stamp = _stamp()

    # 7C: Generate/update the one-pager (best-effort)
    one_pager_out: Dict[str, Any] = {}
    try:
        from week3_customer_handoff_one_pager import write_week3_customer_handoff_one_pager  # type: ignore

        one_pager_out = write_week3_customer_handoff_one_pager(
            context="week3_customer_handoff_one_pager_auto_from_packager"
        )
    except Exception as e:
        one_pager_out = {"ok": False, "error": f"{type(e).__name__}:{e}"}

    # 7D: Generate/update the runbook (best-effort)
    runbook_out: Dict[str, Any] = {}
    try:
        from week3_demo_runbook_generator import generate_week3_demo_runbook  # type: ignore

        runbook_out = generate_week3_demo_runbook(
            context="week3_demo_runbook_auto_from_packager"
        )
    except Exception as e:
        runbook_out = {"ok": False, "error": f"{type(e).__name__}:{e}"}

    # 7E: Generate/update Executive Summary HTML (best-effort)
    execsum_out: Dict[str, Any] = {}
    try:
        from week3_executive_summary import write_week3_executive_summary  # type: ignore

        execsum_out = write_week3_executive_summary(
            context="week3_executive_summary_auto_from_packager"
        )
    except Exception as e:
        execsum_out = {"ok": False, "error": f"{type(e).__name__}:{e}"}

    # Collect files for zip
    files = _collect_week3_files()
    missing: List[str] = []
    present: List[str] = []
    for p in files:
        if p.exists():
            present.append(_safe_rel(p))
        else:
            missing.append(_safe_rel(p))

    # Required for PASS (strict)
    required = [
        "docs/briefs/commander_brief_latest.txt",
        "docs/briefs/week3_operator_summary_latest.txt",
        "docs/briefs/legal_case_snapshot_latest.txt",
        "docs/briefs/mobile_enjoy_manifest_latest.json",
        "docs/validation/week3_demo_readiness_gate_latest.json",
        "docs/packages/week3_customer_handoff_one_pager_latest.txt",
        "docs/packages/week3_demo_runbook_latest.txt",
        "docs/packages/week3_executive_summary_latest.html",
    ]
    req_missing = [r for r in required if not (ROOT / r).exists()]

    verdict = "PASS"
    if strict and req_missing:
        verdict = "FAIL"

    # Build zip
    zip_latest = PACKAGES_DIR / "week3_cloud_demo_package_latest.zip"
    zip_stamped = PACKAGES_DIR / f"week3_cloud_demo_package_{stamp}.zip"

    def _write_zip(zpath: Path) -> None:
        try:
            with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for p in files:
                    if not p.exists():
                        continue
                    zf.write(p, arcname=_safe_rel(p))
        except Exception:
            pass

    _write_zip(zip_latest)
    _write_zip(zip_stamped)

    # Manifest
    manifest_latest = PACKAGES_DIR / "week3_cloud_demo_package_manifest_latest.json"
    manifest_stamped = PACKAGES_DIR / f"week3_cloud_demo_package_manifest_{stamp}.json"

    manifest: Dict[str, Any] = {
        "generated_at_utc": generated,
        "context": context,
        "strict": bool(strict),
        "verdict": verdict,
        "required_missing": req_missing,
        "present_files": present,
        "missing_files": missing,
        "outputs": {
            "zip_latest": _safe_rel(zip_latest),
            "zip_stamped": _safe_rel(zip_stamped),
            "manifest_latest": _safe_rel(manifest_latest),
            "manifest_stamped": _safe_rel(manifest_stamped),
        },
        "generation": {
            "one_pager": one_pager_out,
            "runbook": runbook_out,
            "executive_summary": execsum_out,
        },
        "notes": [
            "Assessment is probabilistic and bounded; operator judgment applies.",
            "This package is for demo/training purposes. Do not represent as operational capability.",
        ],
    }
    _write_manifest(manifest_latest, manifest_stamped, manifest)

    return {
        "generated_at_utc": generated,
        "context": context,
        "verdict": verdict,
        "required_missing": req_missing,
        "zip_latest": _safe_rel(zip_latest),
        "zip_stamped": _safe_rel(zip_stamped),
        "manifest_latest": _safe_rel(manifest_latest),
        "manifest_stamped": _safe_rel(manifest_stamped),
    }


def main() -> int:
    out = run_week3_cloud_demo_packager()
    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

