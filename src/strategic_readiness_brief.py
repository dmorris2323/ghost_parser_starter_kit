from pathlib import Path
from datetime import datetime


BASE = Path(__file__).parent
DOCS = BASE / "docs"


def _read_text(path: Path, fallback: str) -> str:
    """
    Safe file loader: returns fallback text if file is missing or unreadable.
    """
    if not path.exists():
        return fallback
    try:
        return path.read_text().strip()
    except Exception as e:
        return f"{fallback}\n[Error reading {path.name}: {e}]"


def build_strategic_readiness_brief(day_label: str = "Day 60") -> Path:
    """
    Build a single strategic readiness brief for GLL, pulling from:
      - Golden Dome status
      - Sensor reliability
      - Cross-sensor validation
      - AI-Independence documents

    Output: docs/strategic_readiness_brief_day60.txt
    """
    DOCS.mkdir(exist_ok=True)

    lines: list[str] = []
    lines.append(f"STRATEGIC READINESS BRIEF — {day_label}")
    lines.append(datetime.utcnow().isoformat() + "Z")
    lines.append("")

    # --- Golden Dome alignment ---
    golden = _read_text(
        DOCS / "golden_dome_status.txt",
        "Golden Dome status file not found yet. Run your Golden Dome tools first."
    )
    lines.append("=== GOLDEN DOME ALIGNMENT ===")
    lines.append(golden)
    lines.append("")

    # --- Sensor reliability summary ---
    reliability = _read_text(
        DOCS / "reliability_report.txt",
        "No reliability_report.txt yet — run CLI Option 24 to generate it."
    )
    lines.append("=== SENSOR RELIABILITY SUMMARY ===")
    lines.append(reliability)
    lines.append("")

    # --- Cross-sensor validation summary ---
    cross = _read_text(
        DOCS / "cross_sensor_report.txt",
        "No cross_sensor_report.txt yet — run CLI Option 25 to generate it."
    )
    lines.append("=== CROSS-SENSOR VALIDATION ===")
    lines.append(cross)
    lines.append("")

    # --- AI-Independence status ---
    plan = DOCS / "AI_Independence_Plan.md"
    ph2 = DOCS / "AI_Independence_Phase2.md"
    ph3 = DOCS / "AI_Independence_Phase3.md"

    ai_lines: list[str] = []
    for label, p in [
        ("Plan", plan),
        ("Phase 2", ph2),
        ("Phase 3", ph3),
    ]:
        if p.exists():
            ai_lines.append(f"- {label}: PRESENT ({p.name})")
        else:
            ai_lines.append(f"- {label}: NOT YET WRITTEN")

    lines.append("=== AI-INDEPENDENCE STATUS ===")
    lines.extend(ai_lines)
    lines.append("")

    out_path = DOCS / "strategic_readiness_brief_day60.txt"
    out_path.write_text("\n".join(lines))

    return out_path


if __name__ == "__main__":
    path = build_strategic_readiness_brief()
    print(f"Strategic readiness brief written → {path}")

