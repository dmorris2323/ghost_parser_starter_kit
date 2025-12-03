"""
sbir_readiness_assessor.py

Ghost Lantern Labs – SBIR Phase I Readiness Assessor

This module inspects existing GLL artifacts and produces:
- A human-readable assessment text file
- A JSON score object

It does NOT depend on external services. It only checks for the presence
of key files and uses simple heuristics to estimate readiness.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
ROOT_DIR = BASE_DIR.parent  # repo root


@dataclass
class CategoryScore:
    name: str
    score: int
    max_score: int
    rationale: str


@dataclass
class ReadinessResult:
    timestamp: str
    total_score: int
    max_score: int
    categories: List[CategoryScore]
    notes: str


def _exists(path: Path) -> bool:
    return path.exists()


def assess_technical_maturity() -> CategoryScore:
    """
    Looks for fusion pipeline, QA, and dashboards.
    """
    signals = [
        BASE_DIR / "fusion_scoring.py",
        BASE_DIR / "qa_validator.py",
        BASE_DIR / "fusion_ingest.py",
        BASE_DIR / "mission_brief_html.py",
        BASE_DIR / "system_metrics_rollup.py",
    ]

    present = sum(1 for p in signals if _exists(p))
    max_score = 5

    if present >= 5:
        score = 5
        rationale = "Full fusion stack, QA, and dashboards present."
    elif present >= 3:
        score = 4
        rationale = "Core fusion and QA modules present; dashboards likely operational."
    elif present >= 2:
        score = 3
        rationale = "Key technical modules exist but visible gaps remain."
    elif present >= 1:
        score = 2
        rationale = "Only a few technical elements found; still early."
    else:
        score = 1
        rationale = "Minimal technical footprint detected."

    return CategoryScore(
        name="Technical Maturity",
        score=score,
        max_score=max_score,
        rationale=rationale,
    )


def assess_ai_independence() -> CategoryScore:
    """
    Checks AI-Independence doctrine and adapter layer artifacts.
    """
    signals = [
        DOCS_DIR / "AI_Independence_Plan.md",
        DOCS_DIR / "AI_Independence_Phase2.md",
        DOCS_DIR / "AI_Independence_Phase3.md",
        BASE_DIR / "llm_phase2_adapter.py",
        BASE_DIR / "llm_provider_pool.py",
        BASE_DIR / "spectral_owl" / "llm_adapter.py",
    ]

    present = sum(1 for p in signals if _exists(p))
    max_score = 5

    if present >= 5:
        score = 5
        rationale = "Multi-phase AI-independence docs and adapter code in place."
    elif present >= 3:
        score = 4
        rationale = "Clear AI-independence plan with working adapter layer."
    elif present >= 2:
        score = 3
        rationale = "Some AI-independence artifacts; needs more depth."
    elif present >= 1:
        score = 2
        rationale = "Only early AI-independence thinking visible."
    else:
        score = 1
        rationale = "No explicit AI-independence design detected."

    return CategoryScore(
        name="AI-Independence & Offline Readiness",
        score=score,
        max_score=max_score,
        rationale=rationale,
    )


def assess_operational_fit() -> CategoryScore:
    """
    Checks doctrine mapping: Golden Dome, nuclear/ISR, mission briefs.
    """
    signals = [
        DOCS_DIR / "golden_dome_status.txt",
        DOCS_DIR / "demo_roadmap_day100.md",
        DOCS_DIR / "daily_mission_brief.txt",
        DOCS_DIR / "profile_mission_brief.txt",
        BASE_DIR / "golden_dome_alignment_report.py",
    ]

    present = sum(1 for p in signals if _exists(p))
    max_score = 5

    if present >= 5:
        score = 5
        rationale = "Strong mapping between GLL, Golden Dome, and mission briefs."
    elif present >= 3:
        score = 4
        rationale = "Clear operational tie-in to doctrine with live briefs."
    elif present >= 2:
        score = 3
        rationale = "Some doctrine alignment; needs more explicit outputs."
    elif present >= 1:
        score = 2
        rationale = "Hints of doctrine but not fully connected."
    else:
        score = 1
        rationale = "No explicit operational doctrine linkage detected."

    return CategoryScore(
        name="Operational / Doctrine Fit",
        score=score,
        max_score=max_score,
        rationale=rationale,
    )


def assess_productization_ux() -> CategoryScore:
    """
    Checks GUI, demo packs, overlays.
    """
    signals = [
        ROOT_DIR / "apps" / "gui" / "app.py",
        BASE_DIR / "generate_daily_visual_pack.py",
        BASE_DIR / "spectral_dashboard_api.py",
        BASE_DIR / "spectral_sos_overlay.py",
        DOCS_DIR / "demo_deck_manifest_day58.json",
    ]

    present = sum(1 for p in signals if _exists(p))
    max_score = 5

    if present >= 5:
        score = 5
        rationale = "GUI, visual packs, overlays, and demo manifest all present."
    elif present >= 3:
        score = 4
        rationale = "Usable GUI and demo artifacts exist; polish is next step."
    elif present >= 2:
        score = 3
        rationale = "Some UX/productization pieces; still a developer tool."
    elif present >= 1:
        score = 2
        rationale = "Barebones UX footprint."
    else:
        score = 1
        rationale = "CLI-only footprint; no productization signals."

    return CategoryScore(
        name="Productization & UX",
        score=score,
        max_score=max_score,
        rationale=rationale,
    )


def assess_business_readiness() -> CategoryScore:
    """
    Checks legal + roadmap + demo readiness.
    """
    signals = [
        ROOT_DIR / "legal" / "GLL_Legal_Framework.md",
        ROOT_DIR / "legal" / "Code116_Operating_Agreement_Draft.md",
        DOCS_DIR / "demo_roadmap_day100.md",
        DOCS_DIR / "billing_day56_evening.md",
        DOCS_DIR / "day56_evening_sitrep.txt",
    ]

    present = sum(1 for p in signals if _exists(p))
    max_score = 5

    if present >= 5:
        score = 5
        rationale = "Legal framing, billing, and roadmap show strong business posture."
    elif present >= 3:
        score = 4
        rationale = "Solid legal/roadmap artifacts; SBIR-ready posture emerging."
    elif present >= 2:
        score = 3
        rationale = "Early business scaffolding in place."
    elif present >= 1:
        score = 2
        rationale = "Only minimal legal/business artifacts found."
    else:
        score = 1
        rationale = "No visible business planning yet."

    return CategoryScore(
        name="Business / SBIR Readiness",
        score=score,
        max_score=max_score,
        rationale=rationale,
    )


def run_assessment() -> ReadinessResult:
    cats = [
        assess_technical_maturity(),
        assess_ai_independence(),
        assess_operational_fit(),
        assess_productization_ux(),
        assess_business_readiness(),
    ]
    total = sum(c.score for c in cats)
    max_total = sum(c.max_score for c in cats)

    if total >= 22:
        notes = "GLL is behaving like a near-SBIR-ready prototype."
    elif total >= 18:
        notes = "Strong prototype with clear SBIR potential once polished."
    elif total >= 14:
        notes = "Good foundation; needs more artifacts before pitching."
    else:
        notes = "Early-phase project; focus on shipping more demos and briefs."

    return ReadinessResult(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        total_score=total,
        max_score=max_total,
        categories=cats,
        notes=notes,
    )


def write_outputs() -> Dict[str, str]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    result = run_assessment()

    # Text file
    text_path = DOCS_DIR / "sbir_readiness_assessment.txt"
    lines = []
    lines.append("GHOST LANTERN LABS — SBIR PHASE I READINESS")
    lines.append("-------------------------------------------")
    lines.append(f"Timestamp: {result.timestamp}")
    lines.append("")
    for c in result.categories:
        lines.append(f"[{c.name}]  {c.score}/{c.max_score}")
        lines.append(f"  -> {c.rationale}")
        lines.append("")
    lines.append(f"TOTAL SCORE: {result.total_score}/{result.max_score}")
    lines.append("")
    lines.append("NOTES:")
    lines.append(result.notes)
    lines.append("")

    text_path.write_text("\n".join(lines))

    # JSON file
    json_path = DOCS_DIR / "sbir_readiness_score.json"
    json_ready = {
        "timestamp": result.timestamp,
        "total_score": result.total_score,
        "max_score": result.max_score,
        "categories": [asdict(c) for c in result.categories],
        "notes": result.notes,
    }
    json_path.write_text(json.dumps(json_ready, indent=2))

    return {
        "text": str(text_path),
        "json": str(json_path),
    }


if __name__ == "__main__":
    out = write_outputs()
    print("SBIR readiness assessment written:")
    for k, v in out.items():
        print(f"  {k}: {v}")

