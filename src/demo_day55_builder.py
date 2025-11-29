"""
demo_day54_builder.py

Day 54 Demo Pack Builder for Ghost Lantern Labs.

This script:
  - Runs the core fusion pipeline pieces
  - Runs bad-data heatmap pipeline if available
  - Collects key artifacts
  - Writes a threat memory summary
  - Packages everything into demos/day54/ for easy demo/briefing use
"""

import subprocess
import sys
import shutil
from pathlib import Path

from spectral_owl.threat_memory_summary import build_summary

PYTHON = sys.executable


def run_step(name: str, cmd: list[str]) -> None:
    print(f"\n=== STEP: {name} ===")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        print(f"[{name}] CRASHED: {e}")
        return

    if result.returncode != 0:
        print(f"[{name}] FAILED (code {result.returncode})")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
    else:
        print(f"[{name}] PASSED")
        if result.stdout.strip():
            print("STDOUT:")
            print(result.stdout)
    print("=" * 40)


def ensure_demo_dir() -> Path:
    demo_dir = Path("demos/day54")
    demo_dir.mkdir(parents=True, exist_ok=True)
    return demo_dir


def copy_if_exists(src: Path, dest: Path) -> None:
    if src.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"Copied: {src} -> {dest}")
    else:
        print(f"Missing (skipped): {src}")


def find_latest_png() -> Path | None:
    """
    Finds the most recent PNG file in the current directory (recursively).
    Used to grab the latest heatmap-type visualization for the demo pack.
    """
    pngs = list(Path(".").rglob("*.png"))
    if not pngs:
        return None
    return max(pngs, key=lambda p: p.stat().st_mtime)


def main():
    print("\n==========================================")
    print("  GLL DAY 54 — DEMO PACK BUILDER STARTED  ")
    print("==========================================\n")

    demo_dir = ensure_demo_dir()

    # 1) Run core pipeline scripts
    run_step("fusion_scoring", [PYTHON, "fusion_scoring.py"])
    run_step("commander_extract", [PYTHON, "commander_extract.py"])
    run_step("heatmap_prep", [PYTHON, "heatmap_prep.py"])
    run_step("fusion_alerts", [PYTHON, "fusion_alerts.py"])
    run_step("daily_report", [PYTHON, "daily_report.py"])

    # 2) Run bad-data / stress visualization pipeline if present
    if Path("bad_data_heatmap_prep.py").exists():
        run_step("bad_data_heatmap_prep", [PYTHON, "bad_data_heatmap_prep.py"])
    else:
        print("\n[INFO] bad_data_heatmap_prep.py not found, skipping.\n")

    if Path("bad_data_heatmap.py").exists():
        run_step("bad_data_heatmap", [PYTHON, "bad_data_heatmap.py"])
    else:
        print("\n[INFO] bad_data_heatmap.py not found, skipping.\n")

    # 3) Collect and copy artifacts into demos/day54
    artifacts = [
        (Path("scored_output.csv"), demo_dir / "fusion_scores_day54.csv"),
        (Path("commander_extract.csv"), demo_dir / "commander_extract_day54.csv"),
        (Path("heatmap_data.csv"), demo_dir / "heatmap_data_day54.csv"),
        (Path("critical_alerts.csv"), demo_dir / "critical_alerts_day54.csv"),
        (Path("daily_report.txt"), demo_dir / "daily_report_day54.txt"),
        (Path("qa_summary.txt"), demo_dir / "qa_summary_day54.txt"),
        (Path("data/threat_memory.csv"), demo_dir / "threat_memory_day54.csv"),
    ]

    print("\n=== COPYING CORE ARTIFACTS TO demos/day54 ===")
    for src, dest in artifacts:
        copy_if_exists(src, dest)

    # 4) Generate a threat memory summary text file
    print("\n=== BUILDING THREAT MEMORY SUMMARY ===")
    try:
        summary_text = build_summary(limit=50)
        summary_path = demo_dir / "threat_memory_summary_day54.txt"
        summary_path.write_text(summary_text, encoding="utf-8")
        print(f"Wrote threat memory summary to: {summary_path}")
    except Exception as e:
        print(f"Failed to build threat memory summary: {e}")

    # 5) Grab latest PNG (heatmap or similar) and copy as heatmap_v1.png
    print("\n=== SEARCHING FOR LATEST PNG (HEATMAP) ===")
    latest_png = find_latest_png()
    if latest_png is not None:
        dest_png = demo_dir / "heatmap_v1.png"
        copy_if_exists(latest_png, dest_png)
    else:
        print("No PNG files found — heatmap_v1.png not created.")

    # 6) Write a simple README for this demo pack
    readme = demo_dir / "README_day54_demo.txt"
    readme_contents = """
GHOST LANTERN LABS — DAY 54 DEMO PACK
=====================================

This folder contains a snapshot of the GLL fusion system as of Day 54.

Files:
- fusion_scores_day54.csv          → Fused/scored telemetry
- commander_extract_day54.csv      → Commander-facing event summary
- heatmap_data_day54.csv           → Data used for heatmap visualization
- critical_alerts_day54.csv        → High-risk events surfaced by alerts engine
- daily_report_day54.txt           → Human-readable daily intelligence report
- qa_summary_day54.txt             → QA validation summary (pipeline health)
- threat_memory_day54.csv          → Historical threat memory log
- threat_memory_summary_day54.txt  → Human-readable threat memory analysis
- heatmap_v1.png                   → Latest generated heatmap / visualization (if available)

Usage:
- This pack can be sent as-is to demonstrate pipeline output.
- Pair it with a live ghost_cli session (options 1, 6, 11, 12) for an interactive demo.

"""
    readme.write_text(readme_contents.strip() + "\n", encoding="utf-8")
    print(f"\nWrote README to: {readme}")

    print("\n==========================================")
    print("  GLL DAY 54 — DEMO PACK BUILDER COMPLETE ")
    print("  Artifacts in: demos/day54/               ")
    print("==========================================\n")


if __name__ == "__main__":
    main()

