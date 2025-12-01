"""
legal_demo_pack.py — Ghost Lantern Labs
---------------------------------------
Builds a self-contained demo pack for the Family Law (Shari) scenario.

Outputs to:
  demos/family_law_demo/

Includes:
  - family_law_cases_sample.csv
  - family_law_fused.csv
  - family_law_scored.csv
  - family_law_brief.txt
  - threat_memory_stats.txt (if present)
  - alerts_trend.png (if present)
  - README_FAMILY_LAW_DEMO.txt
"""

from pathlib import Path
import shutil

DEMO_DIR = Path("demos/family_law_demo")


def ensure_demo_dir() -> Path:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    return DEMO_DIR


def copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists():
        shutil.copy2(src, dst)
        return True
    return False


def write_readme(dst_dir: Path):
    readme = dst_dir / "README_FAMILY_LAW_DEMO.txt"
    content = """Ghost Lantern Labs — Family Law Demo (Shari)
=================================================

This folder contains a miniature demo of how GLL can help a family law
or collections attorney prioritize cases and see where the real risk and
urgency live.

Key files:
  - family_law_cases_sample.csv
      Raw input cases (custody, support, visitation).

  - family_law_fused.csv
      Normalized version of the above, cleaned and ready for scoring.

  - family_law_scored.csv
      Same cases with GLL risk/urgency score and severity labels.

  - family_law_brief.txt
      Human-readable prioritization brief, written like an intel summary.

  - threat_memory_stats.txt (optional)
      Counts of past threat/alert memory by severity and profile.

  - alerts_trend.png (optional)
      Simple visual of alert growth over time.

Usage for demo:
  1) Explain that GLL can ingest real case data (CSV) from the firm.
  2) Show how cases become normalized (family_law_fused.csv).
  3) Show how cases are scored and labeled (family_law_scored.csv).
  4) Open family_law_brief.txt and walk through the "Top urgent cases".
  5) If available, show threat_memory_stats.txt and alerts_trend.png
     as examples of how GLL tracks patterns over time.

This is a first proof-of-concept slice of how GLL can become a
case-prioritization and risk-intel engine for law firms.
"""
    readme.write_text(content, encoding="utf-8")


def main():
    demo_dir = ensure_demo_dir()
    print(f"[INFO] Building Family Law demo pack in {demo_dir.resolve()}")

    # Core family law files
    copy_if_exists(Path("data/family_law_cases_sample.csv"), demo_dir / "family_law_cases_sample.csv")
    copy_if_exists(Path("data/family_law_fused.csv"), demo_dir / "family_law_fused.csv")
    copy_if_exists(Path("data/family_law_scored.csv"), demo_dir / "family_law_scored.csv")
    copy_if_exists(Path("family_law_brief.txt"), demo_dir / "family_law_brief.txt")

    # Optional intel/visual files
    copy_if_exists(Path("threat_memory_stats.txt"), demo_dir / "threat_memory_stats.txt")
    copy_if_exists(Path("alerts_trend.png"), demo_dir / "alerts_trend.png")

    # README
    write_readme(demo_dir)

    print("[OK] Family Law demo pack built.")


if __name__ == "__main__":
    main()

