"""
demo_deck_outline.py
--------------------
Reads the Demo Deck Manifest and generates a human-friendly
Markdown outline for your Day 58 / Day 100 Ghost Lantern Labs demo.

Output:
    docs/demo_deck_outline_day58.md

This is what you hand to:
    • Shari
    • A future conference deck builder
    • Yourself before RSAC / AFITC / AfroTech-style demos
"""

import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"
MANIFEST = DOCS / "demo_deck_manifest_day58.json"
OUTLINE = DOCS / "demo_deck_outline_day58.md"


def load_manifest():
    if not MANIFEST.exists():
        return None
    try:
        return json.loads(MANIFEST.read_text())
    except Exception:
        return None


def section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.strip()}\n\n"


def bullet(label: str, items) -> str:
    lines = []
    lines.append(f"- **{label}:**")
    if not items:
        lines.append("  - _(none found)_")
    else:
        for p in items:
            lines.append(f"  - `{p}`")
    return "\n".join(lines) + "\n"


def build_outline(manifest: dict) -> str:
    ts = manifest.get("generated_at", datetime.utcnow().isoformat() + "Z")
    system = manifest.get("system", {})
    demos = manifest.get("demos", {})
    profiles = manifest.get("profiles", {})

    lines = []
    lines.append("# Ghost Lantern Labs — Demo Deck Outline (Day 58)\n")
    lines.append(f"_Generated from live system manifest at: **{ts}**_\n")
    lines.append("---\n")

    # 1) Executive Summary
    lines.append(section(
        "1. Executive Summary",
        """
- Ghost Lantern Labs (GLL) is a modular **cyber–fusion ISR platform**.
- Designed for **AFTAC / nuclear**, **cyber defense**, and **multi-domain sensing**.
- Offline-first AI via **Spectral Owl** and a strict **AI-Independence Plan**.
- This deck walks a commander, investor, or customer through what the live lab can already do today.
        """
    ))

    # 2) Core Fusion Engine
    lines.append(section(
        "2. Core Fusion Engine",
        "\n".join([
            bullet("Fusion Outputs", system.get("fusion_outputs")),
            bullet("Scored Outputs", system.get("scored_outputs")),
            bullet("Sensor Ingest", system.get("sensor_ingest")),
        ])
    ))

    # 3) Operator Experience
    lines.append(section(
        "3. Operator Experience",
        "\n".join([
            bullet("Operator Snapshot", system.get("operator_snapshot")),
            bullet("Mission Briefs (Text/HTML)", system.get("mission_briefs")),
            bullet("Fusion Health & Pipeline", system.get("fusion_health")),
        ])
    ))

    # 4) Spectral Owl & Threat Memory
    lines.append(section(
        "4. Spectral Owl & Threat Memory",
        """
- Spectral Owl = GLL's offline-capable reasoning engine.
- Tracks anomalies, critical events, and doctrine-linked threat memory.
        """.strip() + "\n\n" + bullet("Threat Memory Artifacts", system.get("threat_memory"))
    ))

    # 5) Visuals — Minimap & SOS Overlay
    lines.append(section(
        "5. Visual Situation Views (GUI Targets)",
        "\n".join([
            bullet("Fusion Minimap Overlay", system.get("minimap")),
            bullet("SOS Situation Overlay", system.get("sos_overlay")),
        ])
    ))

    # 6) Demo Packs (Day 54 / Day 56 / Legal Demo)
    lines.append(section(
        "6. Demo Packs (For Slides & Live Walkthroughs)",
        "\n".join([
            bullet("Day 54 Demo Pack", [demos.get("day54_demo")]),
            bullet("Day 56 Demo Pack", [demos.get("day56_demo")]),
            bullet("Family Law / Legal Demo", [demos.get("family_law_demo")]),
        ])
    ))

    # 7) Profiles & Sectors
    lines.append(section(
        "7. Profiles & Target Sectors",
        "\n".join([
            bullet("Active Profile Config", [profiles.get("active_profile")]),
            bullet("Profile Definitions", [profiles.get("profiles_folder")]),
            """
Example positioning:
- **aftac_nuclear** → AFTAC / ICADS-style nuclear detection & treaty monitoring.
- **sports_team** → Pro sports (e.g., Patriots) — health, telemetry, performance fusion.
- **law_firm** → Collections / litigation — caseload, outcomes, threat intel.
- **commercial_soc** → Blue-team SOC — logs, alerts, incidents, tickets.
            """.strip(),
        ])
    ))

    # 8) Stress, Resilience & Testing
    lines.append(section(
        "8. Resilience, Stress-Testing & Anti-DoS",
        bullet("Stress Test Artifacts", system.get("stress_test")) + """
- GLL has **bad-data labs**, **stress testers**, and **anti-DoS logic**.
- This section of the deck shows charts and outputs proving:
  - The system survives corrupted telemetry.
  - It keeps operating under noisy conditions.
        """.strip()
    ))

    # 9) Roadmap Slide (Day 58 → Day 100 → Tech School)
    lines.append(section(
        "9. Roadmap (Day 58 → Day 100 → Tech School)",
        """
- **Day 58**: Fusion engine, Spectral Owl, threat memory, minimap, SOS overlay, legal demo.
- **Day 100**: Full Day-100 demo pack + Shari demo (family law scenario) + stable GUI.
- **Tech School**: Plug in real mission problems and sensors, build AFTAC-aligned modules.
- **2026–2027**: Conference demos (RSAC, AFITC, AfroTech), early customers, serious pilots.
        """
    ))

    # 10) How to Use this Outline
    lines.append(section(
        "10. How to Use This Outline",
        """
- Hand this file to whoever builds your slides (you, Shari, or a designer).
- Each section becomes:
  - 1–2 slides with screenshots, key numbers, and 1–3 bullets.
- The file paths listed above tell you **exactly which artifacts** to screenshot or export.
        """
    ))

    return "\n".join(lines)


def main():
    manifest = load_manifest()
    if not manifest:
        OUTLINE.write_text(
            "# Ghost Lantern Labs — Demo Deck Outline (Day 58)\n\n"
            "_Error: demo_deck_manifest_day58.json not found or unreadable._\n\n"
            "Run `python demo_deck_manifest.py` first from src/.\n"
        )
        return "[WARN] Manifest not found. Wrote placeholder outline."

    outline = build_outline(manifest)
    DOCS.mkdir(exist_ok=True, parents=True)
    OUTLINE.write_text(outline)
    return f"[OK] Demo Deck Outline written → {OUTLINE}"


if __name__ == "__main__":
    print(main())

