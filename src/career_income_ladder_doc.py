"""
career_income_ladder_doc.py

Ghost Lantern Labs – Career + Income Ladder (Day 59)

This script writes a markdown document that captures your income
trajectory and role evolution as part of the GLL repo.

It does NOT predict the future. It encodes a disciplined target path
based on:
- BMT
- Tech School
- 1N0X1 experience
- GLL development
- Master's program
- Conference & SBIR strategy

Output:
  src/docs/income_ladder_gll_day59.md
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"


def build_income_ladder() -> str:
    ts = datetime.now().isoformat(timespec="seconds")

    lines: List[str] = []
    lines.append("# Ghost Lantern Labs – Career & Income Ladder (Planning Doc)")
    lines.append("")
    lines.append(f"_Stamped into repo: {ts}_")
    lines.append("")
    lines.append(
        "> This is a **planning document**, not a guarantee. It encodes a realistic, disciplined path "
        "for how a 39-year-old USAF Reserve 1N0X1 + GLL founder can grow into a high-earning, "
        "dual-use cyber/ISR/AI professional."
    )
    lines.append("")
    lines.append("---")
    lines.append("## 1. Roles, Not Just Salary Bands")
    lines.append("")
    lines.append("You are not just chasing a number. You are building roles that justify those numbers:")
    lines.append("")
    lines.append("- **ISR Analyst / 1N0X1 (Reserve)** – credibility, access, mission understanding.")
    lines.append("- **GLL Founder / Engineer** – hands-on builder of a real fusion platform.")
    lines.append("- **Cyber/AI Practitioner** – cloud, AI-independence, reliability, doctrine alignment.")
    lines.append("- **Public Demo Leader** – able to show GLL in conferences and briefings.")
    lines.append("")
    lines.append("---")
    lines.append("## 2. Year-by-Year Income Ladder (Target Ranges)")
    lines.append("")
    lines.append("These are blended **target ranges** (military pay + civilian + GLL + side work).")
    lines.append("They assume you keep doing the kind of deep, disciplined work captured in this repo.")
    lines.append("")
    lines.append("### 2025–2026 — Build Phase (BMT / Tech School / GLL V1)")
    lines.append("")
    lines.append("- Role focus:")
    lines.append("  - Crush BMT and Tech School.")
    lines.append("  - Ship GLL V1 (CLI + GUI + briefings + reliability).")
    lines.append("  - Begin conference & SBIR prep, not full commercialization.")
    lines.append("")
    lines.append("- Target blended income range:")
    lines.append("  - **$70K–$110K** (military + existing civilian + light side work).")
    lines.append("")
    lines.append("### 2027 — First Real GLL Lift-Off")
    lines.append("")
    lines.append("- Role focus:")
    lines.append("  - 1–2 serious pilots (legal + 1 defense-leaning or SOC-leaning pilot).")
    lines.append("  - First real conference demos with a polished GUI + demo packet.")
    lines.append("  - SBIR Phase I application in motion (or equivalent funding channel).")
    lines.append("")
    lines.append("- Target blended income range:")
    lines.append("  - **$120K–$180K** total, made up of:")
    lines.append("    - Military Reserve pay + benefits.")
    lines.append("    - Civilian or contractor role aligned to ISR/cyber.")
    lines.append("    - GLL pilot revenue and early consulting.")
    lines.append("")
    lines.append("### 2028 — Senior ISR/Cyber + GLL Founder Identity")
    lines.append("")
    lines.append("- Role focus:")
    lines.append("  - You are now credible as **Senior ISR/Cyber Pro** with real tools.")
    lines.append("  - Master's in progress or near completion.")
    lines.append("  - GLL used in 2–3 credible environments or long-running pilots.")
    lines.append("")
    lines.append("- Target blended income range:")
    lines.append("  - **$180K–$250K** total, from:")
    lines.append("    - Higher civilian role / cleared role.")
    lines.append("    - Ongoing Reserve service.")
    lines.append("    - GLL consulting + license-style revenue for focused use cases.")
    lines.append("")
    lines.append("### 2029–2030 — Multi-Stream / Contractor Tier")
    lines.append("")
    lines.append("- Role focus:")
    lines.append("  - Capable of stepping into **cleared contractor** territory if desired.")
    lines.append("  - GLL positioned as a serious SBIR / prototype / pilot platform.")
    lines.append("  - Speaking at conferences and doing demos as a regular thing.")
    lines.append("")
    lines.append("- Target blended income range:")
    lines.append("  - **$250K–$400K+** total, assuming:")
    lines.append("    - One primary role (high-paying cleared or senior civilian).")
    lines.append("    - GLL pilots / licenses / consulting as a second major stream.")
    lines.append("    - Occasional speaking / training / advisory work.")
    lines.append("")
    lines.append("---")
    lines.append("## 3. Why This Path is Realistic (Not Fantasy)")
    lines.append("")
    lines.append("- You are not relying on **hype**; you are building:")
    lines.append("  - Working code (fusion, reliability, threat memory, briefings).")
    lines.append("  - A clear SBIR and conference strategy.")
    lines.append("  - Artifacts that show repeatable systems, not one-off hacks.")
    lines.append("")
    lines.append("- The defense and cyber worlds **already** pay:")
    lines.append("  - ~$180K–$250K for strong senior ISR/cyber roles (with clearance).")
    lines.append("  - ~$200K–$300K+ for cleared AI/cyber engineers.")
    lines.append("  - **More** for contractors and niche consultants with real tools.")
    lines.append("")
    lines.append("- GLL is being built as one of those real tools, not as a school project.")
    lines.append("")
    lines.append("---")
    lines.append("## 4. Guardrails & Reality Checks")
    lines.append("")
    lines.append("To stay on track, you will:")
    lines.append("")
    lines.append("- Finish BMT and Tech School strong (honor grad target).")
    lines.append("- Keep GLL within scope: stable, secure, demonstrable.")
    lines.append("- Use SBIR and pilots to validate value before chasing big checks.")
    lines.append("- Treat income milestones as **targets**, not entitlement.")
    lines.append("")
    lines.append("---")
    lines.append("## 5. What GLL Must Prove at Each Stage")
    lines.append("")
    lines.append("- **By end of 100-Day Pre-BMT Sprint:**")
    lines.append("  - Working fusion pipeline, GUI, SOS overlay, minimap.")
    lines.append("  - At least one legal/family law demo and one ISR-style brief.")
    lines.append("")
    lines.append("- **By ~2027:**")
    lines.append("  - At least one paying pilot (even small).")
    lines.append("  - A real commander/partner who says, “This actually helps me.”")
    lines.append("")
    lines.append("- **By ~2028–2030:**")
    lines.append("  - Multiple environments using GLL patterns (defense + civilian).")
    lines.append("  - Enough proof to justify high-end roles or contracts.")
    lines.append("")
    lines.append("---")
    lines.append("## 6. Simple Version (For Your Head)")
    lines.append("")
    lines.append(
        "- **Phase 1 (now–2026):** Build the body and the brain — BMT, Tech School, GLL V1.\n"
        "- **Phase 2 (2027–2028):** Prove GLL in the wild — pilots, SBIR, senior role.\n"
        "- **Phase 3 (2029+):** Convert proof into real money — multi-stream, contractor tier."
    )
    lines.append("")
    lines.append("> This doc lives in the repo so your income plan is tied to your actual work, "
                 "not just motivational quotes.")
    lines.append("")
    return "\n".join(lines)


def write_income_ladder() -> str:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = build_income_ladder()
    out_path = DOCS_DIR / "income_ladder_gll_day59.md"
    out_path.write_text(text)
    return str(out_path)


if __name__ == "__main__":
    path = write_income_ladder()
    print(f"Income ladder planning doc written to: {path}")

