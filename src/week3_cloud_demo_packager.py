# src/week3_cloud_demo_packager.py
from __future__ import annotations

import json
import shutil
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Demo lock (best-effort import)
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:
    def is_demo_locked() -> bool:
        return True

    def demo_lock_banner() -> str:
        return (
            "DEMO MODE ACTIVE — READ ONLY\n"
            "No baselines updated. No training. No mutation.\n"
            "Assessment is probabilistic and bounded; operator judgment applies."
        )


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BRIEFS = DOCS / "briefs"
VALIDATION = DOCS / "validation"
PACKAGES = DOCS / "packages"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read_bytes(p: Path) -> Optional[bytes]:
    try:
        if not p.exists():
            return None
        return p.read_bytes()
    except Exception:
        return None


def _sha256_file(p: Path) -> Optional[str]:
    try:
        b = _safe_read_bytes(p)
        if b is None:
            return None
        h = hashlib.sha256()
        h.update(b)
        return h.hexdigest()
    except Exception:
        return None


def _safe_copy(src: Path, dst: Path) -> bool:
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            return False
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def _safe_write_text(p: Path, txt: str) -> bool:
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
        return True
    except Exception:
        return False


def _safe_write_json(p: Path, obj: Any) -> bool:
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


@dataclass(frozen=True)
class PackageItem:
    key: str
    src: Path
    rel_dst: Path  # relative path inside package folder


def _package_inventory() -> List[PackageItem]:
    """
    Cloud-ready Week-3 demo inventory.
    Keep this small and “contractor shareable”.
    """
    return [
        PackageItem("commander_brief_txt", BRIEFS / "commander_brief_latest.txt", Path("briefs/commander_brief_latest.txt")),
        PackageItem("commander_brief_json", BRIEFS / "commander_brief_latest.json", Path("briefs/commander_brief_latest.json")),
        PackageItem("week3_operator_summary_txt", BRIEFS / "week3_operator_summary_latest.txt", Path("briefs/week3_operator_summary_latest.txt")),
        PackageItem("legal_case_snapshot_txt", BRIEFS / "legal_case_snapshot_latest.txt", Path("briefs/legal_case_snapshot_latest.txt")),
        PackageItem("legal_case_snapshot_json", BRIEFS / "legal_case_snapshot_latest.json", Path("briefs/legal_case_snapshot_latest.json")),
        PackageItem("mobile_enjoy_manifest_json", BRIEFS / "mobile_enjoy_manifest_latest.json", Path("briefs/mobile_enjoy_manifest_latest.json")),
        PackageItem("week3_demo_narrative_txt", BRIEFS / "week3_demo_narrative_latest.txt", Path("briefs/week3_demo_narrative_latest.txt")),
        PackageItem("week3_demo_narrative_json", BRIEFS / "week3_demo_narrative_latest.json", Path("briefs/week3_demo_narrative_latest.json")),
        PackageItem("fusion_core_regression_txt", VALIDATION / "fusion_core_regression_latest.txt", Path("validation/fusion_core_regression_latest.txt")),
        PackageItem("fusion_core_regression_json", VALIDATION / "fusion_core_regression_latest.json", Path("validation/fusion_core_regression_latest.json")),
        PackageItem("week3_demo_pack_gate_json", VALIDATION / "week3_demo_pack_gate_latest.json", Path("validation/week3_demo_pack_gate_latest.json")),
        PackageItem("week3_demo_readiness_gate_txt", VALIDATION / "week3_demo_readiness_gate_latest.txt", Path("validation/week3_demo_readiness_gate_latest.txt")),
        PackageItem("week3_demo_readiness_gate_json", VALIDATION / "week3_demo_readiness_gate_latest.json", Path("validation/week3_demo_readiness_gate_latest.json")),
        PackageItem("week3_demo_orchestrator_txt", BRIEFS / "week3_demo_orchestrator_latest.txt", Path("briefs/week3_demo_orchestrator_latest.txt")),
        PackageItem("week3_demo_orchestrator_json", BRIEFS / "week3_demo_orchestrator_latest.json", Path("briefs/week3_demo_orchestrator_latest.json")),
        PackageItem("week3_shari_demo_packet_txt", BRIEFS / "week3_shari_demo_packet_latest.txt", Path("briefs/week3_shari_demo_packet_latest.txt")),
        PackageItem("week3_shari_demo_packet_json", BRIEFS / "week3_shari_demo_packet_latest.json", Path("briefs/week3_shari_demo_packet_latest.json")),
    ]


def _build_contractor_readme(context: str) -> str:
    banner = demo_lock_banner() if is_demo_locked() else "DEMO MODE NOT ACTIVE (unexpected for Week-3)."
    return f"""GHOST LANTERN LABS (GLL) — WEEK-3 DEMO PACKAGE (CLOUD-READY)
generated_at_utc: {_utc_now_iso()}
context: {context}

WHAT THIS IS
- A read-only, commander-safe demo package containing validated outputs from Ghost Lantern Labs.
- Built to be shared with a customer, stakeholder, mentor, or PM without sending the entire repo.

CONTRACTOR FRAMING (WHAT YOU ARE “DELIVERING”)
- A gated demo execution chain (Week-3 demo orchestrator + readiness gate)
- Commander brief (bounded, safe language)
- Operator summary (10-second PASS snapshot)
- Legal “Shari Hook” snapshot (demo module)
- Mobile enjoy manifest (artifact index for quick navigation)
- Validation artifacts for traceability

SAFETY / GOVERNANCE
{banner}

IMPORTANT DISCLAIMERS
- Outputs are generated from synthetic/simulated data unless explicitly stated otherwise.
- No attribution, intent, or causality is inferred from demo telemetry.
- Operator judgment applies before escalation or external action.

HOW TO VERIFY IN 30 SECONDS
1) Open validation/week3_demo_readiness_gate_latest.txt
2) Confirm verdict: PASS
3) Open briefs/week3_demo_orchestrator_latest.txt
4) Confirm verdict: PASS and crashes: 0

PACKAGE STRUCTURE
- briefs/      commander/operator/demo artifacts
- validation/  gates and regression results
- manifest.json
- README_CONTRACTOR.txt
"""


def build_week3_cloud_demo_package(context: str = "week3_cloud_demo_package") -> Dict[str, Any]:
    """
    Creates:
      docs/packages/week3_cloud_demo_package_<STAMP>/
      docs/packages/week3_cloud_demo_package_latest/  (mirror copy)
      docs/packages/week3_cloud_demo_package_<STAMP>.zip
      docs/packages/week3_cloud_demo_package_latest.zip
    Never crashes: missing files are reported, not fatal.
    """
    generated_at = _utc_now_iso()
    stamp = _stamp()

    PACKAGES.mkdir(parents=True, exist_ok=True)

    stamped_dir = PACKAGES / f"week3_cloud_demo_package_{stamp}"
    latest_dir = PACKAGES / "week3_cloud_demo_package_latest"

    # fresh stamped dir
    try:
        if stamped_dir.exists():
            shutil.rmtree(stamped_dir)
    except Exception:
        pass
    stamped_dir.mkdir(parents=True, exist_ok=True)

    # write contractor readme
    _safe_write_text(stamped_dir / "README_CONTRACTOR.txt", _build_contractor_readme(context))

    copied: Dict[str, Any] = {}
    missing: List[str] = []

    for item in _package_inventory():
        dst = stamped_dir / item.rel_dst
        ok = _safe_copy(item.src, dst)
        copied[item.key] = {
            "src": str(item.src),
            "dst": str(dst),
            "present": bool(ok),
            "sha256": _sha256_file(dst) if ok else None,
        }
        if not ok:
            missing.append(item.key)

    manifest: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "context": context,
        "demo_locked": bool(is_demo_locked()),
        "root": str(ROOT),
        "stamped_dir": str(stamped_dir),
        "missing": missing,
        "items": copied,
        "notes": [
            "Assessment is probabilistic and bounded; operator judgment applies.",
            "This package is read-only and safe to share."
        ],
    }
    _safe_write_json(stamped_dir / "manifest.json", manifest)

    # mirror to latest (replace)
    try:
        if latest_dir.exists():
            shutil.rmtree(latest_dir)
    except Exception:
        pass
    try:
        shutil.copytree(stamped_dir, latest_dir)
    except Exception:
        # best effort: if copytree fails, keep stamped_dir only
        pass

    # zip stamped + latest
    stamped_zip_base = str(PACKAGES / f"week3_cloud_demo_package_{stamp}")
    latest_zip_base = str(PACKAGES / "week3_cloud_demo_package_latest")

    stamped_zip = None
    latest_zip = None
    try:
        stamped_zip = shutil.make_archive(stamped_zip_base, "zip", root_dir=stamped_dir)
    except Exception:
        stamped_zip = None

    try:
        latest_zip = shutil.make_archive(latest_zip_base, "zip", root_dir=latest_dir if latest_dir.exists() else stamped_dir)
    except Exception:
        latest_zip = None

    return {
        "generated_at_utc": generated_at,
        "context": context,
        "demo_locked": bool(is_demo_locked()),
        "verdict": "PASS" if len(missing) == 0 else "WARN",
        "missing": missing,
        "stamped_dir": str(stamped_dir),
        "latest_dir": str(latest_dir) if latest_dir.exists() else None,
        "stamped_zip": stamped_zip,
        "latest_zip": latest_zip,
        "manifest_path": str((stamped_dir / "manifest.json")),
        "readme_path": str((stamped_dir / "README_CONTRACTOR.txt")),
    }


def main() -> int:
    out = build_week3_cloud_demo_package()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

