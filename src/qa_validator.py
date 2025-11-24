# qa_validator.py
# GLL QA HARNESS — runs the full fusion pipeline and writes a summary.

from pathlib import Path
from datetime import datetime

from fusion_logger import log_event
from fusion_scoring import score_fusion
from commander_extract import commander_extract
from heatmap_prep import generate_heatmap_data
from fusion_alerts import fusion_alerts
from daily_report import build_daily_report


def run_all():
    """
    Run all major GLL modules in sequence and log pass/fail
    + write a qa_summary.txt file for human review.
    """
    modules = [
        ("fusion_scoring", score_fusion),
        ("commander_extract", commander_extract),
        ("heatmap_prep", generate_heatmap_data),
        ("fusion_alerts", fusion_alerts),
        ("daily_report", build_daily_report),
    ]

    results: list[tuple[str, str, str]] = []

    print("GLL QA VALIDATOR — FULL PIPELINE")
    print("=====================================\n")

    for name, func in modules:
        print(f"🔍 Testing {name}...")
        try:
            func()
            print(f"✅ {name} PASSED\n")
            log_event("qa_validator", "pass", name)
            results.append((name, "PASS", ""))
        except Exception as e:
            msg = f"{name}: {e}"
            print(f"❌ {name} FAILED → {e}\n")
            log_event("qa_validator", "fail", msg)
            results.append((name, "FAIL", str(e)))

    # Write QA summary file next to this script
    summary_path = Path(__file__).with_name("qa_summary.txt")
    now_str = datetime.utcnow().isoformat()

    total = len(results)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = total - passed

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("GLL QA VALIDATION SUMMARY\n")
        f.write("==========================\n")
        f.write(f"Timestamp (UTC): {now_str}\n")
        f.write(f"Total modules:   {total}\n")
        f.write(f"Passed:          {passed}\n")
        f.write(f"Failed:          {failed}\n")
        f.write("\nDetails:\n")
        for name, status, msg in results:
            line = f"- {name}: {status}"
            if msg:
                line += f" ({msg})"
            f.write(line + "\n")

    print("🏁 QA VALIDATION COMPLETE")
    print(f"🧾 Summary written to: {summary_path.name}")


if __name__ == "__main__":
    run_all()

