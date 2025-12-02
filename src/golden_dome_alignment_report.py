"""
golden_dome_alignment_report.py
--------------------------------

Computes a simple "Golden Dome" alignment report for Ghost Lantern Labs.

Golden Dome readiness is scored along a few axes:
  - Offline-first capability
  - AI-Independence phases
  - Multi-profile support (nuclear / sports / legal / SOC)
  - Threat memory + doctrine logging
  - Cloud export / archive readiness

Outputs:
  - docs/golden_dome_status.txt (human-readable summary)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"

# Key files / signals we expect if things are on track
AI_PLAN = DOCS_DIR / "AI_Independence_Plan.md"
AI_PHASE2 = DOCS_DIR / "AI_Independence_Phase2.md"
AI_PHASE3 = DOCS_DIR / "AI_Independence_Phase3.md"

OFFLINE_FLAG = BASE / "offline_mode_flag.py"
OFFLINE_STATUS = BASE / "offline_status.txt"

PROFILE_CONFIG = BASE / "profile_config.py"
PROFILE_MISSION_BRIEF = DOCS_DIR / "profile_mission_brief.txt"

THREAT_MEMORY = BASE / "data" / "threat_memory.csv"
THREAT_DOCTRINE = DOCS_DIR / "threat_memory_doctrine_report.txt"

CLOUD_READY = BASE / "CLOUD_READY.md"
CLOUD_ARCHIVE_DIR = BASE / "cloud_sim" / "fusion_archive"

OUTPUT_PATH = DOCS_DIR / "golden_dome_status.txt"


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def file_exists_check(name: str, path: Path, detail: str) -> CheckResult:
    return CheckResult(
        name=name,
        ok=path.exists(),
        detail=f"{detail} ({'FOUND' if path.exists() else 'MISSING'} @ {path})",
    )


def directory_nonempty_check(name: str, path: Path, detail: str) -> CheckResult:
    if not path.exists() or not path.is_dir():
        return CheckResult(name=name, ok=False, detail=f"{detail} (missing dir @ {path})")
    has_files = any(path.iterdir())
    return CheckResult(
        name=name,
        ok=has_files,
        detail=f"{detail} ({'FILES PRESENT' if has_files else 'EMPTY DIR'} @ {path})",
    )


def build_golden_dome_report() -> Dict[str, object]:
    checks: List[CheckResult] = []

    # AI-Independence documents
    checks.append(file_exists_check("AI_Plan", AI_PLAN, "AI-Independence doctrine documented"))
    checks.append(file_exists_check("AI_Phase2", AI_PHASE2, "Phase 2 design captured"))
    checks.append(file_exists_check("AI_Phase3", AI_PHASE3, "Phase 3 design captured"))

    # Offline-first
    checks.append(file_exists_check("Offline_Flag", OFFLINE_FLAG, "Offline mode code present"))
    checks.append(file_exists_check("Offline_Status", OFFLINE_STATUS, "Offline status log available"))

    # Profiles + mission brief
    checks.append(file_exists_check("Profile_Config", PROFILE_CONFIG, "Multi-profile config present"))
    checks.append(file_exists_check("Profile_Mission_Brief", PROFILE_MISSION_BRIEF, "Profile-aware mission brief present"))

    # Threat memory + doctrine
    checks.append(file_exists_check("Threat_Memory", THREAT_MEMORY, "Threat memory CSV present"))
    checks.append(file_exists_check("Threat_Doctrine_Report", THREAT_DOCTRINE, "Threat doctrine report present"))

    # Cloud readiness
    checks.append(file_exists_check("Cloud_Ready_Doc", CLOUD_READY, "Cloud deployment notes present"))
    checks.append(directory_nonempty_check("Cloud_Archive", CLOUD_ARCHIVE_DIR, "Cloud archive (sim) populated"))

    total = len(checks)
    passed = sum(1 for c in checks if c.ok)

    if total == 0:
        score_pct = 0
    else:
        score_pct = int(round((passed / total) * 100))

    if score_pct >= 85:
        tier = "GOLD"
    elif score_pct >= 65:
        tier = "SILVER"
    elif score_pct >= 40:
        tier = "BRONZE"
    else:
        tier = "RED / INCOMPLETE"

    lines: List[str] = []
    lines.append("=== GOLDEN DOME ALIGNMENT REPORT ===")
    lines.append(f"Score: {passed}/{total} checks passed ({score_pct}%)")
    lines.append(f"Tier:  {tier}")
    lines.append("")
    lines.append("Detail:")
    for c in checks:
        status = "OK " if c.ok else "MISS"
        lines.append(f" - [{status}] {c.name}: {c.detail}")
    lines.append("")
    lines.append("Interpretation:")
    if tier == "GOLD":
        lines.append("GOLD: GLL is strongly aligned with Golden Dome doctrine and ready for serious demos.")
    elif tier == "SILVER":
        lines.append("SILVER: Good alignment. A few missing links remain before true demo/field readiness.")
    elif tier == "BRONZE":
        lines.append("BRONZE: Foundations exist, but major gaps must be closed.")
    else:
        lines.append("RED: Golden Dome mapping is incomplete. Treat as a to-do list, not a failure.")

    report_text = "\n".join(lines)

    return {
        "score": score_pct,
        "tier": tier,
        "passed": passed,
        "total": total,
        "checks": checks,
        "text": report_text,
    }


def write_golden_dome_report() -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    result = build_golden_dome_report()
    OUTPUT_PATH.write_text(result["text"], encoding="utf-8")
    return OUTPUT_PATH


def main():
    path = write_golden_dome_report()
    print(f"[OK] Golden Dome alignment report written -> {path}")


if __name__ == "__main__":
    main()

