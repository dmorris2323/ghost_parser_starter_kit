"""
exercise_brief_pacific.py

Builds a consolidated 'exercise readiness' brief for Ghost Lantern Labs.
This is designed to look like a commander-facing AAR skeleton for
large-scale, distributed exercises (Pacific-style).

It pulls from:
- Active profile status
- Sensor reliability report
- Cross-sensor validation report
- Run-history intelligence summary
- Golden Dome alignment status (if present)
"""

from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read(path_str, default_text):
    """
    Safely read a text file. If anything fails, return default_text.
    """
    try:
        p = Path(path_str)
        if not p.exists():
            return default_text
        text = p.read_text().strip()
        return text if text else default_text
    except Exception:
        return default_text


def build_exercise_brief():
    """
    Assemble a multi-section exercise readiness brief from existing
    GLL outputs. All imports are wrapped in try/except so the brief
    never crashes if a module or file is missing.

    Returns:
        str: full text of the exercise brief
    """
    lines = []
    timestamp = datetime.now().isoformat(timespec="seconds")

    lines.append("GHOST LANTERN LABS — EXERCISE READINESS BRIEF")
    lines.append("------------------------------------------------")
    lines.append(f"Generated: {timestamp}")
    lines.append("")

    # === ACTIVE PROFILE / SECTOR CONTEXT ==========================
    lines.append("=== ACTIVE PROFILE CONTEXT ===")
    try:
        from profile_status import build_profile_status

        lines.append(build_profile_status())
    except Exception:
        lines.append("Profile status unavailable (profile_status module not reachable).")
    lines.append("")

    # === SENSOR RELIABILITY SUMMARY ===============================
    lines.append("=== SENSOR RELIABILITY SUMMARY ===")
    try:
        # This call should ensure docs/reliability_report.txt exists
        from sensor_reliability import export_reliability_report

        export_reliability_report()
        rel_path = DOCS_DIR / "reliability_report.txt"
        rel_text = _safe_read(rel_path, "No reliability report yet. Run Option 24 in ghost_cli.")
        lines.append(rel_text)
    except Exception:
        lines.append("Reliability module not available or failed to run.")
    lines.append("")

    # === CROSS-SENSOR VALIDATION ==================================
    lines.append("=== CROSS-SENSOR VALIDATION ===")
    try:
        from cross_sensor_report import build_report

        rep = build_report()
        cs_path = rep.get("path", DOCS_DIR / "cross_sensor_report.txt")
        cs_text = _safe_read(cs_path, "No cross-sensor report yet. Run Option 25 in ghost_cli.")
        lines.append(cs_text)
    except Exception:
        lines.append("Cross-sensor module not available or failed to run.")
    lines.append("")

    # === RUN-HISTORY INTELLIGENCE =================================
    lines.append("=== RUN-HISTORY INTELLIGENCE ===")
    try:
        from run_history_intel import main as run_history_main

        rh_text = run_history_main()
        if rh_text:
            lines.append(rh_text.strip())
        else:
            lines.append("Run-history intel pipeline returned no summary.")
    except Exception:
        lines.append("Run-history intel module not available or failed to run.")
    lines.append("")

    # === GOLDEN DOME ALIGNMENT (IF PRESENT) =======================
    gd_path = DOCS_DIR / "golden_dome_status.txt"
    gd_text = _safe_read(gd_path, None)
    if gd_text:
        lines.append("=== GOLDEN DOME ALIGNMENT ===")
        lines.append(gd_text)
        lines.append("")

    # === EXERCISE NOTES / NEXT STEPS ==============================
    lines.append("=== EXERCISE NOTES / NEXT STEPS ===")
    lines.append("- Use this brief as the core handout for large-scale exercise AARs.")
    lines.append("- Attach GUI screenshots, reliability plots, and minimap graphics.")
    lines.append("- Update profile to match the exercise domain (nuclear / legal / sports / SOC).")
    lines.append("- Run Options 21–25 in ghost_cli before generating this to get freshest data.")
    lines.append("")

    return "\n".join(lines)


def write_exercise_brief():
    """
    Write the exercise brief to docs/exercise_brief_pacific.txt.

    Returns:
        str: path to the written brief
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DIR / "exercise_brief_pacific.txt"
    text = build_exercise_brief()
    out_path.write_text(text)
    return str(out_path)


if __name__ == "__main__":
    out = write_exercise_brief()
    print(f"Exercise brief written to: {out}")

