"""
conference_pitch_cards.py

Ghost Lantern Labs – Conference Pitch Cards (Day 59)

Builds a markdown file with ready-to-use pitch cards for different
conference environments: RSAC, AfroTech, Air/Space/Cyber, small mil events, etc.

Output:
  src/docs/conference_pitch_cards_day59.md
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"


def build_conference_cards() -> str:
    ts = datetime.now().isoformat(timespec="seconds")

    lines: List[str] = []
    lines.append("# Ghost Lantern Labs — Conference Pitch Cards (Day 59)")
    lines.append("")
    lines.append(f"_Generated: {ts}_")
    lines.append("")
    lines.append(
        "These cards are meant to be **printed or copied into slides** so you always know "
        "what to say, what to show, and what outcome you want at each conference."
    )
    lines.append("")
    lines.append("---")
    lines.append("## 1. RSAC / Security Engineering Conference Card")
    lines.append("")
    lines.append("**Audience:** CISOs, SOC leads, security engineers, threat hunters.")
    lines.append("")
    lines.append("**10-second pitch:**")
    lines.append(
        "> Ghost Lantern Labs is an AI-independent sensor-fusion workbench that turns your noisy logs, metrics, "
        "and alerts into a single daily mission brief your team can actually act on — even when the cloud or AI is degraded."
    )
    lines.append("")
    lines.append("**What you demo at the booth:**")
    lines.append("- CLI → run full fusion pipeline and reliability report.")
    lines.append("- GUI → Spectral dashboard with minimap, SOS overlay, and reliability view.")
    lines.append("- Run-history intelligence timeline and cross-sensor validation report.")
    lines.append("")
    lines.append("**What you want from them:**")
    lines.append("- A pilot where GLL ingests a small slice of their SOC telemetry.")
    lines.append("- A warm intro to their internal innovation team or CTO.")
    lines.append("")
    lines.append("---")
    lines.append("## 2. AfroTech / Tech + Culture Conference Card")
    lines.append("")
    lines.append("**Audience:** Diverse founders, engineers, VCs, ecosystem builders.")
    lines.append("")
    lines.append("**10-second pitch:**")
    lines.append(
        "> Ghost Lantern Labs is a Black-founded defense-grade fusion platform that takes the way the military watches "
        "for attacks and repackages it for companies, sports teams, and law firms that need early warning on risk."
    )
    lines.append("")
    lines.append("**What you demo at the booth:**")
    lines.append("- Family-law demo: caseload risk and aging view for a law firm.")
    lines.append("- Sports/metrics example: how the same engine can watch players or servers.")
    lines.append("- SBIR one-pager + pitch outline to show you’re building a real company, not a toy.")
    lines.append("")
    lines.append("**What you want from them:**")
    lines.append("- Intros to diverse founders who need telemetry/risk fusion.")
    lines.append("- Connections to funds that invest in dual-use / defense-adjacent tech.")
    lines.append("")
    lines.append("---")
    lines.append("## 3. AFA Air, Space & Cyber / Air & Space Conferences Card")
    lines.append("")
    lines.append("**Audience:** USAF/USSF leadership, program managers, operators, primes.")
    lines.append("")
    lines.append("**10-second pitch:**")
    lines.append(
        "> Ghost Lantern Labs is a portable fusion cell: it ingests seismic, optical, EMS, and cyber telemetry, "
        "cleans it, scores it, and hands commanders a daily Golden Dome–style mission brief that still works if the cloud or AI is offline."
    )
    lines.append("")
    lines.append("**What you demo at the booth:**")
    lines.append("- Nuclear/AFTAC-like profile and Golden Dome alignment report.")
    lines.append("- Sensor reliability + cross-sensor validation view.")
    lines.append("- AI-Independence plan and offline Spectral Owl behavior.")
    lines.append("")
    lines.append("**What you want from them:**")
    lines.append("- Conversations with requirements officers and lab reps (AFRL, AFTAC, etc.).")
    lines.append("- Guidance on the right SBIR/STTR topics or rapid prototyping programs.")
    lines.append("")
    lines.append("---")
    lines.append("## 4. Small Military / Guard / Reserve Conferences Card")
    lines.append("")
    lines.append("**Audience:** Guard/Reserve leaders, unit commanders, innovation cells.")
    lines.append("")
    lines.append("**10-second pitch:**")
    lines.append(
        "> Ghost Lantern Labs is a Reserve-built fusion platform that lets small units run large-scale ISR-style analysis "
        "on cheap hardware — Mac minis, laptops — with no dependency on a single AI vendor."
    )
    lines.append("")
    lines.append("**What you demo at the booth:**")
    lines.append("- GLL running on your own Mac mini or laptop.")
    lines.append("- Mission brief HTML + GUI showing system status and threat memory.")
    lines.append("- How profiles let a unit flip between nuclear, cyber, or logistics views.")
    lines.append("")
    lines.append("**What you want from them:**")
    lines.append("- Interest in unit-level pilot projects or innovation challenges.")
    lines.append("- Contacts into wing/Numbered Air Force/MAJCOM innovation offices.")
    lines.append("")
    lines.append("---")
    lines.append("## 5. Law / Financial Tech Side Events Card")
    lines.append("")
    lines.append("**Audience:** Law firm partners, compliance heads, fintech leaders.")
    lines.append("")
    lines.append("**10-second pitch:**")
    lines.append(
        "> Ghost Lantern Labs watches your caseload or accounts like a radar watches airspace — it fuses status, deadlines, "
        "payments, and anomalies into a daily list of ‘these are the files that will hurt you if you ignore them.’"
    )
    lines.append("")
    lines.append("**What you demo at the booth:**")
    lines.append("- Family-law or collections demo with real-looking but safe sample data.")
    lines.append("- Daily brief showing at-risk cases and looming deadlines.")
    lines.append("- How the same engine could watch fraud or charge-offs in finance.")
    lines.append("")
    lines.append("**What you want from them:**")
    lines.append("- First paid pilot (small monthly retainer for a focused use case).")
    lines.append("- Testimonials and data that GLL actually reduced risk / missed deadlines.")
    lines.append("")
    lines.append("---")
    lines.append("## 6. Personal Quick-Reference Card (Pocket Version)")
    lines.append("")
    lines.append("Keep this in your phone / pocket for when you’re caught off-guard:")
    lines.append("")
    lines.append("**Core identity:**")
    lines.append(
        "> Ghost Lantern Labs turns messy sensor and system data into a clean, commander-style daily brief so leaders know "
        "what’s breaking, what’s about to break, and what to do first."
    )
    lines.append("")
    lines.append("**Versatile closer:**")
    lines.append(
        "> We built it to survive jamming, model failures, and cloud outages for nuclear and ISR missions — but the same engine "
        "can watch sports teams, law firms, or SOCs the same way."
    )
    lines.append("")
    return "\n".join(lines)


def write_cards() -> str:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = build_conference_cards()
    out_path = DOCS_DIR / "conference_pitch_cards_day59.md"
    out_path.write_text(text)
    return str(out_path)


if __name__ == "__main__":
    path = write_cards()
    print(f"Conference pitch cards written to: {path}")

