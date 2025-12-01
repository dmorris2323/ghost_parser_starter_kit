"""
generate_daily_visual_pack.py — Ghost Lantern Labs
---------------------------------------------------
Builds a full "daily visual pack" for demos and briefs.

Outputs into:
  demos/day56/   (DAY_TAG can be changed)

Includes:
  - operator_snapshot_day56.txt
  - pipeline_health_day56.txt
  - system_metrics_day56.json / system_metrics_day56.txt
  - threat_memory_summary_day56.txt
  - threat_memory_stats_day56.txt
  - bad_data_heatmap_day56.png
  - alerts_trend_day56.png
  - baseline_drift_report_day56.txt
  - PACK_BUILT.txt
"""

from pathlib import Path
from datetime import datetime
import shutil

from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from system_metrics_rollup import build_system_metrics, write_outputs
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from bad_data_heatmap_plot import main as build_heatmap
from threat_memory_stats import main as build_threat_stats
from alerts_trend_plot import main as build_alerts_trend
from baseline_drift_check import main as run_drift_check

DAY_TAG = "day56"


def ensure_demo_dir() -> Path:
    base = Path("demos")
    base.mkdir(exist_ok=True)
    day_dir = base / DAY_TAG
    day_dir.mkdir(exist_ok=True)
    return day_dir


def copy_if_exists(src: Path, dst: Path):
    if src.exists():
        shutil.copy2(src, dst)
        return True
    return False


def main():
    day_dir = ensure_demo_dir()
    print(f"[INFO] Building daily visual pack in: {day_dir}")

    # 1) Operator snapshot
    print("[STEP] Building operator snapshot...")
    snapshot_text = build_operator_snapshot()
    snapshot_src = Path("operator_snapshot.txt")
    copy_if_exists(snapshot_src, day_dir / f"operator_snapshot_{DAY_TAG}.txt")

    # 2) Pipeline health
    print("[STEP] Evaluating pipeline health...")
    health = evaluate_pipeline_health()
    health_src = Path("pipeline_health.txt")
    copy_if_exists(health_src, day_dir / f"pipeline_health_{DAY_TAG}.txt")

    # 3) System metrics
    print("[STEP] Building system metrics...")
    metrics = build_system_metrics()
    write_outputs(metrics)
    metrics_json = Path("system_metrics.json")
    metrics_txt = Path("system_metrics.txt")
    copy_if_exists(metrics_json, day_dir / f"system_metrics_{DAY_TAG}.json")
    copy_if_exists(metrics_txt, day_dir / f"system_metrics_{DAY_TAG}.txt")

    # 4) Threat memory summary
    print("[STEP] Building threat memory summary...")
    summary_text = build_threat_summary()
    summary_path = day_dir / f"threat_memory_summary_{DAY_TAG}.txt"
    summary_path.write_text(summary_text, encoding="utf-8")

    # 5) Bad-data heatmap
    print("[STEP] Building bad-data heatmap (if data available)...")
    try:
        build_heatmap()
        heatmap_png = Path("bad_data_heatmap.png")
        if copy_if_exists(heatmap_png, day_dir / f"bad_data_heatmap_{DAY_TAG}.png"):
            print("[OK] Heatmap copied into demo pack.")
        else:
            print("[WARN] Heatmap PNG not found after generation.")
    except Exception as e:
        print(f"[WARN] Heatmap generation failed: {e}")

    # 6) Threat memory stats
    print("[STEP] Building threat memory stats...")
    try:
        build_threat_stats()
        stats_src = Path("threat_memory_stats.txt")
        if copy_if_exists(stats_src, day_dir / f"threat_memory_stats_{DAY_TAG}.txt"):
            print("[OK] Threat stats copied into demo pack.")
    except Exception as e:
        print(f"[WARN] Threat stats failed: {e}")

    # 7) Alerts trend plot
    print("[STEP] Building alerts trend plot...")
    try:
        build_alerts_trend()
        alerts_png = Path("alerts_trend.png")
        if copy_if_exists(alerts_png, day_dir / f"alerts_trend_{DAY_TAG}.png"):
            print("[OK] Alerts trend plot copied into demo pack.")
    except Exception as e:
        print(f"[WARN] Alerts trend failed: {e}")

    # 8) Baseline drift check
    print("[STEP] Running baseline drift check...")
    try:
        run_drift_check()
        drift_src = Path("baseline_drift_report.txt")
        if copy_if_exists(drift_src, day_dir / f"baseline_drift_report_{DAY_TAG}.txt"):
            print("[OK] Baseline drift report added to demo pack.")
    except Exception as e:
        print(f"[WARN] Baseline drift check failed: {e}")

    # 9) Timestamp marker
    timestamp = datetime.now().isoformat()
    (day_dir / "PACK_BUILT.txt").write_text(
        f"Daily visual pack built at {timestamp}\n", encoding="utf-8"
    )

    print("\n[OK] Daily visual pack complete.")
    print(f"Contents written to {day_dir.resolve()}")


if __name__ == "__main__":
    main()

