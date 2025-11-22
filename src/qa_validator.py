# =========================================
# qa_validator.py — Version 0.1 (GLL QA)
# =========================================

from fusion_logger import log_event
from fusion_scoring import score_fusion
from commander_extract import commander_extract
from heatmap_prep import generate_heatmap_data
from fusion_alerts import fusion_alerts
from daily_report import build_daily_report

def run_all():
    modules = [
        ("fusion_scoring", score_fusion),
        ("commander_extract", commander_extract),
        ("heatmap_prep", generate_heatmap_data),
        ("fusion_alerts", fusion_alerts),
        ("daily_report", build_daily_report),
    ]

    print("=====================================")
    print("  GLL QA VALIDATOR — FULL PIPELINE")
    print("=====================================")

    for name, func in modules:
        try:
            print(f"\n🔍 Testing {name}...")
            func()
            print(f"✅ {name} PASSED")
            log_event("qa_validator", "pass", name)
        except Exception as e:
            print(f"❌ {name} FAILED → {e}")
            log_event("qa_validator", "fail", f"{name}: {e}")

    print("\n🏁 QA VALIDATION COMPLETE")
    print("=====================================")


if __name__ == "__main__":
    run_all()

