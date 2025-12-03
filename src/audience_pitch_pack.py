"""
audience_pitch_pack.py

Ghost Lantern Labs – Audience Pitch Pack (Day 59)

Builds a text file with short, targeted one-liner pitches for different audiences:
- Commander
- SBIR reviewer / investor
- Commercial CISO
- Sports GM
- Law firm managing partner

Output:
  src/docs/audience_pitches_day59.txt
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"


def build_pitches() -> str:
    ts = datetime.now().isoformat(timespec="seconds")

    lines: List[str] = []
    lines.append("Ghost Lantern Labs — Audience Pitch Pack (Day 59)")
    lines.append("------------------------------------------------")
    lines.append(f"Generated: {ts}")
    lines.append("")
    lines.append("These are short, memorized-grade pitches you can use in real conversations.")
    lines.append("Tune wording as needed, but the core message is stable.")
    lines.append("")
    lines.append("==================================================")
    lines.append("1) AFTAC / PACAF / Space Force Commander")
    lines.append("==================================================")
    lines.append("")
    lines.append(
        '“Sir/Ma’am, Ghost Lantern Labs is a sensor-fusion workbench that ingests seismic, optical, EMS, and cyber data, '
        'cleans it, scores it, and turns it into mission briefs your teams can actually act on — even when the cloud or AI '
        'is degraded.”'
    )
    lines.append("")
    lines.append("Key follow-up line:")
    lines.append(
        "“Think of it as an offline-capable fusion cell in a box that survives jamming, model failures, and bandwidth cuts.”"
    )
    lines.append("")
    lines.append("==================================================")
    lines.append("2) SBIR Reviewer / Defense Investor")
    lines.append("==================================================")
    lines.append("")
    lines.append(
        "“Ghost Lantern Labs is an AI-independent sensor fusion platform that lets operators run Golden Dome–style defense "
        "and cyber ISR missions without depending on any single cloud model or vendor.”"
    )
    lines.append("")
    lines.append("Key follow-up line:")
    lines.append(
        "“We already have a working CLI, GUI, mission briefs, reliability scoring, and doctrine alignment — we’re using SBIR "
        "to harden it with real data and scale it to partner environments.”"
    )
    lines.append("")
    lines.append("==================================================")
    lines.append("3) Commercial CISO / SOC Director")
    lines.append("==================================================")
    lines.append("")
    lines.append(
        "“Ghost Lantern Labs takes your noisy telemetry — logs, metrics, anomalies — and runs it through the same kind of "
        "fusion and reliability scoring we’d use for nuclear or missile-warning missions, then hands your team a clear daily "
        "brief with prioritized risks.”"
    )
    lines.append("")
    lines.append("Key follow-up line:")
    lines.append(
        "“Instead of another dashboard full of red dots, GLL gives you a commander-style summary: what broke, what’s about to "
        "break, and where to focus your limited people.”"
    )
    lines.append("")
    lines.append("==================================================")
    lines.append("4) Sports Team GM / Performance Director")
    lines.append("==================================================")
    lines.append("")
    lines.append(
        "“Ghost Lantern Labs is a fusion engine that you can aim at player health and performance — think of it as taking "
        "all your wearables, GPS, workload, and medical flags and turning them into a single daily risk brief for your roster.”"
    )
    lines.append("")
    lines.append("Key follow-up line:")
    lines.append(
        "“It’s the same fusion logic we’d apply to missile or cyber threats, but re-targeted to spot overuse injuries, chemistry "
        "issues, and early warning signs before they cost you games.”"
    )
    lines.append("")
    lines.append("==================================================")
    lines.append("5) Law-Firm Managing Partner (Shari’s world)")
    lines.append("==================================================")
    lines.append("")
    lines.append(
        "“Ghost Lantern Labs can watch your caseload the way a radar watches airspace — it fuses case status, deadlines, "
        "payments, and workload into one daily brief that tells you which files are about to become problems.”"
    )
    lines.append("")
    lines.append("Key follow-up line:")
    lines.append(
        "“Instead of you chasing spreadsheets and emails, GLL surfaces the three or four cases you should look at today so "
        "nothing slips, even when your team is remote or overloaded.”"
    )
    lines.append("")
    lines.append("==================================================")
    lines.append("6) Simple 10-Second Version (anyone)")
    lines.append("==================================================")
    lines.append("")
    lines.append(
        "“Ghost Lantern Labs turns messy sensor and system data into a clean daily mission brief so leaders know what’s "
        "really going wrong and what’s about to break — even if the cloud or AI is offline.”"
    )
    lines.append("")
    lines.append("Memorize-level backup:")
    lines.append(
        "“It’s a portable fusion cell: it ingests, cleans, scores, and briefs — you just point it at your world: missiles, "
        "networks, players, or cases.”"
    )
    lines.append("")
    return "\n".join(lines)


def write_pitches() -> str:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = build_pitches()
    out_path = DOCS_DIR / "audience_pitches_day59.txt"
    out_path.write_text(text)
    return str(out_path)


if __name__ == "__main__":
    path = write_pitches()
    print(f"Audience pitch pack written to: {path}")

