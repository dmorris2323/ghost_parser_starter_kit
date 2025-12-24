from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
DEMO_DIR = DOCS_DIR / "demo"
VALID_DIR = DOCS_DIR / "validation"
BRIEFS_DIR = DOCS_DIR / "briefs"
PACKAGES_DIR = DOCS_DIR / "packages"
BASE_DEFENSE_DIR = DOCS_DIR / "base_defense"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AuditResult:
    generated_at_utc: str
    context: str
    verdict: str
    required_count: int
    required_missing: List[str]
    violations: List[str]


def _exists(p: Path) -> bool:
    try:
        return p.exists() and p.is_file() and p.stat().st_size > 0
    except Exception:
        return False


def _read_json(p: Path) -> Dict:
    return json.loads(p.read_text(encoding="utf-8"))


def run_audit() -> Dict:
    required: List[Tuple[str, Path]] = [
        # DEMO CONTRACT DOCS
        ("docs/demo/demo_freeze_manifest.json", DEMO_DIR / "demo_freeze_manifest.json"),
        ("docs/demo/demo_acceptance_statement.txt", DEMO_DIR / "demo_acceptance_statement.txt"),
        ("docs/demo/phase_ii_handoff_checklist.txt", DEMO_DIR / "phase_ii_handoff_checklist.txt"),

        # VALIDATION (latest)
        ("docs/validation/week3_demo_acceptance_latest.txt", VALID_DIR / "week3_demo_acceptance_latest.txt"),
        ("docs/validation/week3_demo_freeze_gate_latest.txt", VALID_DIR / "week3_demo_freeze_gate_latest.txt"),
        ("docs/validation/day79_demo_lockin_audit_latest.txt", VALID_DIR / "day79_demo_lockin_audit_latest.txt"),

        # CORE BRIEFS
        ("docs/briefs/commander_brief_latest.txt", BRIEFS_DIR / "commander_brief_latest.txt"),
        ("docs/briefs/commander_brief_latest.json", BRIEFS_DIR / "commander_brief_latest.json"),
        ("docs/briefs/week3_operator_summary_latest.txt", BRIEFS_DIR / "week3_operator_summary_latest.txt"),
        ("docs/briefs/legal_case_snapshot_latest.txt", BRIEFS_DIR / "legal_case_snapshot_latest.txt"),
        ("docs/briefs/legal_case_snapshot_latest.json", BRIEFS_DIR / "legal_case_snapshot_latest.json"),
        ("docs/briefs/week3_demo_narrative_latest.txt", BRIEFS_DIR / "week3_demo_narrative_latest.txt"),
        ("docs/briefs/week3_shari_demo_packet_latest.txt", BRIEFS_DIR / "week3_shari_demo_packet_latest.txt"),
        ("docs/briefs/mobile_enjoy_manifest_latest.json", BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"),

        # BASE DEFENSE
        ("docs/base_defense/installation_threat_map_latest.txt", BASE_DEFENSE_DIR / "installation_threat_map_latest.txt"),

        # PACKAGES
        ("docs/packages/week3_cloud_demo_package_latest.zip", PACKAGES_DIR / "week3_cloud_demo_package_latest.zip"),
        ("docs/packages/week3_demo_freeze_pack_latest.zip", PACKAGES_DIR / "week3_demo_freeze_pack_latest.zip"),
    ]

    missing = [label for (label, path) in required if not _exists(path)]

    violations: List[str] = []

    # DEMO FREEZE SAFETY CHECK (manifest must say demo_safe true)
    manifest_path = DEMO_DIR / "demo_freeze_manifest.json"
    if _exists(manifest_path):
        try:
            m = _read_json(manifest_path)
            mode = str(m.get("mode", "")).strip()
            demo_safe = bool(m.get("demo_safe", False))
            banner = str(m.get("required_banner_text", "")).strip()

            if mode != "DEMO_FREEZE":
                violations.append("MANIFEST_MODE_NOT_DEMO_FREEZE")
            if not demo_safe:
                violations.append("MANIFEST_DEMO_SAFE_FALSE")
            if len(banner) < 40:
                violations.append("MANIFEST_BANNER_TOO_SHORT")
        except Exception:
            violations.append("MANIFEST_PARSE_ERROR")
    else:
        violations.append("MANIFEST_MISSING")

    verdict = "PASS" if (not missing and not violations) else "FAIL"

    result = AuditResult(
        generated_at_utc=_utc_now_iso(),
        context="day80_rehearsal_pack_audit",
        verdict=verdict,
        required_count=len(required),
        required_missing=missing,
        violations=violations,
    )

    # Write outputs (latest + stamped)
    out = {
        "generated_at_utc": result.generated_at_utc,
        "context": result.context,
        "verdict": result.verdict,
        "required_count": result.required_count,
        "required_missing": result.required_missing,
        "violations": result.violations,
    }

    VALID_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = VALID_DIR / "day80_rehearsal_pack_audit_latest.json"
    latest_txt = VALID_DIR / "day80_rehearsal_pack_audit_latest.txt"
    stamped_json = VALID_DIR / f"day80_rehearsal_pack_audit_{stamp}.json"
    stamped_txt = VALID_DIR / f"day80_rehearsal_pack_audit_{stamp}.txt"

    latest_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    stamped_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = []
    lines.append("DAY 80 — REHEARSAL + PACK AUDIT")
    lines.append(f"generated_at_utc: {out['generated_at_utc']}")
    lines.append(f"verdict: {out['verdict']}")
    lines.append("")
    lines.append(f"required_count: {out['required_count']}")
    lines.append("")

    if out["required_missing"]:
        lines.append("Missing required files:")
        for x in out["required_missing"]:
            lines.append(f"- {x}")
        lines.append("")
    if out["violations"]:
        lines.append("Violations:")
        for v in out["violations"]:
            lines.append(f"- {v}")
        lines.append("")

    txt = "\n".join(lines).strip() + "\n"
    latest_txt.write_text(txt, encoding="utf-8")
    stamped_txt.write_text(txt, encoding="utf-8")

    return {
        "result": out,
        "paths": {
            "latest_json": str(latest_json),
            "latest_txt": str(latest_txt),
            "stamped_json": str(stamped_json),
            "stamped_txt": str(stamped_txt),
        },
    }


def main() -> int:
    out = run_audit()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
