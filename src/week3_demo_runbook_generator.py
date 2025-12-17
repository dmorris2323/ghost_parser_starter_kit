# src/week3_demo_runbook_generator.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "docs" / "briefs"
VALIDATION_DIR = ROOT / "docs" / "validation"
PACKAGES_DIR = ROOT / "docs" / "packages"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_text_best_effort(p: Path) -> Optional[str]:
    try:
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _demo_lock_banner_best_effort() -> Optional[str]:
    try:
        from demo_lock import is_demo_locked, demo_lock_banner  # type: ignore

        if bool(is_demo_locked()):
            return str(demo_lock_banner())
        return None
    except Exception:
        return None


def generate_week3_demo_runbook(
    context: str = "week3_demo_runbook",
) -> Dict[str, Any]:
    """
    Writes a customer/operator runbook for running the Week-3 demo on a clean machine.
    Outputs:
      - docs/packages/week3_demo_runbook_latest.md
      - docs/packages/week3_demo_runbook_latest.txt
      - stamped variants
    Must never crash.
    """
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    generated = _utc_now_iso()
    stamp = _stamp()

    banner = _demo_lock_banner_best_effort()

    # Pull best-effort current status (optional)
    orch = _read_json_best_effort(BRIEFS_DIR / "week3_demo_orchestrator_latest.json") or {}
    readiness = _read_json_best_effort(VALIDATION_DIR / "week3_demo_readiness_gate_latest.json") or {}
    pack_manifest = _read_json_best_effort(PACKAGES_DIR / "week3_cloud_demo_package_manifest_latest.json") or {}

    orch_verdict = orch.get("verdict", "UNKNOWN")
    readiness_verdict = readiness.get("verdict", "UNKNOWN")
    package_verdict = (pack_manifest.get("verdict") or "UNKNOWN")

    # Compose runbook
    md = []
    md.append("# Week-3 Demo Runbook — Obasi / GLL (Customer Handoff)")
    md.append("")
    md.append(f"- generated_at_utc: `{generated}`")
    md.append(f"- context: `{context}`")
    md.append("")
    md.append("## 0) Demo safety (read this first)")
    if banner:
        md.append("✅ **DEMO MODE ACTIVE (READ ONLY)**")
        md.append("")
        md.append("```")
        md.append(banner)
        md.append("```")
    else:
        md.append("⚠️ Demo lock banner not detected. If this is a stakeholder demo, enable demo lock first.")
    md.append("")
    md.append("## 1) What you should expect (success criteria)")
    md.append(f"- Orchestrator verdict (latest): **{orch_verdict}**")
    md.append(f"- Readiness gate verdict (latest): **{readiness_verdict}**")
    md.append(f"- Package manifest verdict (latest): **{package_verdict}**")
    md.append("")
    md.append("## 2) Quickstart (local machine)")
    md.append("From repo root:")
    md.append("")
    md.append("```bash")
    md.append("python src/week3_demo_orchestrator.py")
    md.append("```")
    md.append("")
    md.append("Then open these files (they are demo-friendly):")
    md.append("")
    md.append("```bash")
    md.append("cat docs/briefs/week3_demo_narrative_latest.txt")
    md.append("cat docs/briefs/commander_brief_latest.txt | head -n 80")
    md.append("cat docs/briefs/legal_case_snapshot_latest.txt")
    md.append("cat docs/briefs/week3_operator_summary_latest.txt")
    md.append("cat docs/validation/week3_demo_readiness_gate_latest.txt")
    md.append("```")
    md.append("")
    md.append("## 3) If you only have the ZIP (no repo access)")
    md.append("You can still review everything **without running any code**:")
    md.append("")
    md.append("1) Unzip the package")
    md.append("```bash")
    md.append("unzip week3_cloud_demo_package_latest.zip -d week3_demo_pkg")
    md.append("cd week3_demo_pkg")
    md.append("```")
    md.append("")
    md.append("2) Read the core outputs")
    md.append("```bash")
    md.append("cat docs/briefs/week3_demo_narrative_latest.txt")
    md.append("cat docs/briefs/commander_brief_latest.txt | head -n 80")
    md.append("cat docs/briefs/legal_case_snapshot_latest.txt")
    md.append("cat docs/briefs/week3_operator_summary_latest.txt")
    md.append("cat docs/validation/week3_demo_readiness_gate_latest.txt")
    md.append("cat docs/packages/week3_customer_handoff_one_pager_latest.txt")
    md.append("```")
    md.append("")
    md.append("## 4) The “demo script” (what to say while scrolling)")
    md.append("Use this order to control narrative and avoid scope creep:")
    md.append("")
    md.append("1) **Narrative**: “This is a read-only demo pack. No baselines updated. No training. No mutation.”")
    md.append("2) **Commander brief**: bounded sections; no attribution claims from synthetic telemetry.")
    md.append("3) **Legal snapshot (Shari Hook)**: fast, familiar hook; shows the same safety philosophy.")
    md.append("4) **Operator summary**: 10-second PASS signal.")
    md.append("5) **Readiness gate**: we refuse to demo if required demo-lock markers are missing.")
    md.append("")
    md.append("## 5) Troubleshooting (common issues)")
    md.append("- If a script hangs: it’s usually waiting on a subprocess. Re-run the failing script directly.")
    md.append("- If a gate fails: read `docs/validation/*latest.txt` and fix the named violation first.")
    md.append("- If demo-lock is missing: re-run the artifact generator (e.g., `python src/legal_case_snapshot.py`).")
    md.append("")
    md.append("## 6) Non-negotiables (contractor-safe language)")
    md.append("- Outputs are **probabilistic and bounded**.")
    md.append("- Demo data is synthetic/training.")
    md.append("- Operator judgment applies before escalation.")
    md.append("")
    md_text = "\n".join(md).strip() + "\n"

    txt = []
    txt.append("WEEK-3 DEMO RUNBOOK — OBASI / GLL (CUSTOMER HANDOFF)")
    txt.append(f"generated_at_utc: {generated}")
    txt.append(f"context: {context}")
    txt.append("")
    txt.append("DEMO SAFETY:")
    if banner:
        txt.append("DEMO MODE ACTIVE — READ ONLY")
        txt.append(banner)
    else:
        txt.append("Demo lock banner not detected (enable for stakeholder demo).")
    txt.append("")
    txt.append("SUCCESS CRITERIA (best effort):")
    txt.append(f"- Orchestrator verdict: {orch_verdict}")
    txt.append(f"- Readiness verdict: {readiness_verdict}")
    txt.append(f"- Package manifest verdict: {package_verdict}")
    txt.append("")
    txt.append("QUICKSTART (repo):")
    txt.append("python src/week3_demo_orchestrator.py")
    txt.append("")
    txt.append("ZIP-ONLY REVIEW (no code):")
    txt.append("unzip week3_cloud_demo_package_latest.zip -d week3_demo_pkg")
    txt.append("cd week3_demo_pkg")
    txt.append("cat docs/briefs/week3_demo_narrative_latest.txt")
    txt.append("cat docs/briefs/commander_brief_latest.txt | head -n 80")
    txt.append("cat docs/briefs/legal_case_snapshot_latest.txt")
    txt.append("cat docs/briefs/week3_operator_summary_latest.txt")
    txt.append("cat docs/validation/week3_demo_readiness_gate_latest.txt")
    txt.append("cat docs/packages/week3_customer_handoff_one_pager_latest.txt")
    txt.append("")
    txt.append("DEMO ORDER:")
    txt.append("1) Narrative (read-only)")
    txt.append("2) Commander brief (bounded)")
    txt.append("3) Legal snapshot (Shari Hook)")
    txt.append("4) Operator summary")
    txt.append("5) Readiness gate")
    txt.append("")
    txt.append("TROUBLESHOOTING:")
    txt.append("- If a gate fails: open docs/validation/*latest.txt and fix the named violation first.")
    txt.append("- If demo lock missing: re-run the generator script for that artifact.")
    txt.append("")
    txt.append("CONTRACTOR-SAFE LANGUAGE:")
    txt.append("- Probabilistic and bounded outputs; synthetic demo data; operator judgment applies.")
    txt_text = "\n".join(txt).strip() + "\n"

    latest_md = PACKAGES_DIR / "week3_demo_runbook_latest.md"
    stamped_md = PACKAGES_DIR / f"week3_demo_runbook_{stamp}.md"
    latest_txt = PACKAGES_DIR / "week3_demo_runbook_latest.txt"
    stamped_txt = PACKAGES_DIR / f"week3_demo_runbook_{stamp}.txt"

    for p, content in [
        (latest_md, md_text),
        (stamped_md, md_text),
        (latest_txt, txt_text),
        (stamped_txt, txt_text),
    ]:
        try:
            p.write_text(content, encoding="utf-8")
        except Exception:
            pass

    res: Dict[str, Any] = {
        "generated_at_utc": generated,
        "context": context,
        "paths": {
            "latest_md": str(latest_md.relative_to(ROOT)),
            "stamped_md": str(stamped_md.relative_to(ROOT)),
            "latest_txt": str(latest_txt.relative_to(ROOT)),
            "stamped_txt": str(stamped_txt.relative_to(ROOT)),
        },
    }
    return res


def main() -> int:
    out = generate_week3_demo_runbook()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


