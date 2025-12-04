"""
customer_segment_brief.py

Generates a customer-segment brief for Ghost Lantern Labs (GLL),
showing how the same fusion engine supports multiple domains:

- AFTAC / nuclear ISR
- Sports teams (e.g., NFL)
- Law firms (e.g., collections / family / bankruptcy)
- Commercial SOCs

Output:
  docs/customer_segment_brief_day59.md
"""

from pathlib import Path
from datetime import datetime


DOCS_DIR = Path(__file__).resolve().parent / "docs"
OUTPUT_FILE = DOCS_DIR / "customer_segment_brief_day59.md"


def build_markdown() -> str:
    """Build the multi-segment customer brief as markdown text."""

    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    lines = []
    lines.append("# Ghost Lantern Labs — Customer Segment Brief")
    lines.append("")
    lines.append(f"_Generated: {now}_")
    lines.append("")
    lines.append(
        "> Ghost Lantern Labs (GLL) is a modular fusion+AI engine. "
        "The same core stack supports multiple missions by swapping sensors, data sources, "
        "and profiles — not rewriting code."
    )
    lines.append("")

    # ---------------------------------------------------------
    # 1) AFTAC / Nuclear ISR Segment
    # ---------------------------------------------------------
    lines.append("## 1. AFTAC / Nuclear ISR Segment")
    lines.append("")
    lines.append("**Customer Type:** AFTAC-style nuclear monitoring / treaty verification units")
    lines.append("")
    lines.append("**Primary Problem:**")
    lines.append(
        "- They must detect, confirm, and characterize nuclear events with **near-zero false positives**, "
        "across optical, seismic, radiation, and EMS channels."
    )
    lines.append("")
    lines.append("**What GLL Provides:**")
    lines.append(
        "- Fusion pipeline that ingests multi-sensor telemetry (optical/seismic/radiation/EMS)."
    )
    lines.append("- Schema-validated, sanitized data (bad data is quarantined, not ignored).")
    lines.append("- Spectral Owl analysis for critical-event detection and threat summaries.")
    lines.append("- Anti-DoS and bad-data simulation labs for resilience under attack.")
    lines.append("")
    lines.append("**Key Metrics / Value:**")
    lines.append("- Fewer false alarms due to cross-sensor validation.")
    lines.append("- Faster time-to-briefing with automated mission reports.")
    lines.append("- Offline-first design for denied or degraded comms.")
    lines.append("- Clear operator console (ghost_cli) plus HTML/GUI mission briefs.")
    lines.append("")

    # ---------------------------------------------------------
    # 2) Sports Team Segment
    # ---------------------------------------------------------
    lines.append("## 2. Sports Team Segment (e.g., NFL Franchise)")
    lines.append("")
    lines.append("**Customer Type:** Professional sports teams (NFL, NBA, etc.)")
    lines.append("")
    lines.append("**Primary Problem:**")
    lines.append(
        "- Teams are drowning in performance metrics, tracking data, and scouting intel, "
        "but struggle to fuse it into **clear, actionable decisions** for coaches and analysts."
    )
    lines.append("")
    lines.append("**What GLL Provides:**")
    lines.append(
        "- Same fusion pipeline, but sensors become **player metrics, tracking data, game events, and scouting reports**."
    )
    lines.append(
        "- Sensor reliability tells staff which data sources are trustworthy (e.g., tracking bugs, missing feeds)."
    )
    lines.append(
        "- Spectral Owl reasoning can summarize key risks, matchups, and anomalies in performance data."
    )
    lines.append("")
    lines.append("**Key Metrics / Value:**")
    lines.append("- Faster prep for games (auto-generated briefs).")
    lines.append("- Early warning on performance drops or injury-risk patterns.")
    lines.append("- Unified view of “who is actually a problem this week” for coaching staff.")
    lines.append("")

    # ---------------------------------------------------------
    # 3) Law Firm Segment
    # ---------------------------------------------------------
    lines.append("## 3. Law Firm Segment (Collections / Family / Bankruptcy)")
    lines.append("")
    lines.append("**Customer Type:** Law firms like Shari’s (collections, family law, bankruptcy).")
    lines.append("")
    lines.append("**Primary Problem:**")
    lines.append(
        "- Multiple disconnected systems: case files, court dates, payment histories, communication logs. "
        "Partners lack a **single fused picture** of risk, status, and opportunity per client/case."
    )
    lines.append("")
    lines.append("**What GLL Provides:**")
    lines.append(
        "- Treats each case as an “event” with fused inputs: financial records, court events, documents, and communications."
    )
    lines.append(
        "- Legal demo pipeline (already in your repo) shows how GLL can ingest family-law or collections data "
        "and generate a case brief."
    )
    lines.append(
        "- Reliability layer flags when key inputs are missing (e.g., court docs, payment confirmations)."
    )
    lines.append("")
    lines.append("**Key Metrics / Value:**")
    lines.append("- Faster client briefings with auto-generated summaries.")
    lines.append("- Early warning for at-risk clients/cases (missed payments, deadlines).")
    lines.append("- Traceable, auditable decision chain for partners and courts.")
    lines.append("")

    # ---------------------------------------------------------
    # 4) Commercial SOC Segment
    # ---------------------------------------------------------
    lines.append("## 4. Commercial SOC Segment (Cyber Defense)")
    lines.append("")
    lines.append("**Customer Type:** Mid-to-large enterprises with Security Operations Centers (SOCs).")
    lines.append("")
    lines.append("**Primary Problem:**")
    lines.append(
        "- SOCs drown in alerts from SIEM, EDR, NDR, and cloud logs. "
        "Analysts need **fusion + prioritization** instead of more dashboards."
    )
    lines.append("")
    lines.append("**What GLL Provides:**")
    lines.append("- Fusion engine that can ingest logs, alerts, and telemetry from multiple tools.")
    lines.append("- Anti-DoS, bad-data, and stress-test modules to evaluate SIEM resilience.")
    lines.append("- Spectral Owl to produce a “commander’s cyber brief” per shift.")
    lines.append("- Sensor reliability engine to highlight broken or noisy detections.")
    lines.append("")
    lines.append("**Key Metrics / Value:**")
    lines.append("- Reduced alert fatigue; analysts focus on fused, high-confidence events.")
    lines.append("- Better executive reporting (“What actually happened this week?”).")
    lines.append("- Easier SBIR / R&D justification: GLL becomes a test harness for new defenses.")
    lines.append("")

    # ---------------------------------------------------------
    # 5) Unified Story
    # ---------------------------------------------------------
    lines.append("## 5. Unified Story Across All Segments")
    lines.append("")
    lines.append("**Common Core Capabilities:**")
    lines.append("- Sensor/telemetry ingestion")
    lines.append("- Schema validation and sanitization")
    lines.append("- Threat / event scoring and classification")
    lines.append("- Reliability / health tracking")
    lines.append("- Mission-style brief generation (text, HTML, GUI)")
    lines.append("- Offline-first and AI-independent design")
    lines.append("")
    lines.append("**Why This Matters for SBIR & Conferences:**")
    lines.append("- Shows GLL is not a toy demo — it is a **platform**.")
    lines.append("- Proves dual-use: defense, sports, legal, and enterprise cyber.")
    lines.append("- Demonstrates a clear path from initial SBIR money to commercial revenue.")
    lines.append("")
    lines.append("_End of brief._")
    lines.append("")

    return "\n".join(lines)


def write_customer_segment_brief() -> Path:
    """Write the customer segment brief to the docs folder."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = build_markdown()
    OUTPUT_FILE.write_text(text, encoding="utf-8")
    return OUTPUT_FILE


def main():
    out = write_customer_segment_brief()
    print(f"Customer segment brief written to: {out}")


if __name__ == "__main__":
    main()

