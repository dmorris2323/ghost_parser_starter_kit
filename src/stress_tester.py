"""
stress_tester.py — Day 53
Lightweight stress test harness for Ghost Lantern Labs.

Runs the QA validator multiple times to simulate repeated use
and catch intermittent failures.
"""

from datetime import datetime
from time import sleep

from fusion_logger import log_event
from qa_validator import run_all as run_qa


def run_stress_test(iterations: int = 5, pause_seconds: float = 1.0) -> None:
    print(f"🚨 GLL STRESS TEST — {iterations} iterations")
    log_event("stress_tester", "start", f"iterations={iterations}")

    failures = 0

    for i in range(1, iterations + 1):
        print(f"\n▶ Iteration {i}/{iterations} — {datetime.utcnow().isoformat()}")
        try:
            run_qa()
        except Exception as e:
            failures += 1
            msg = f"Iteration {i} FAILED: {e}"
            print(f"❌ {msg}")
            log_event("stress_tester", "iteration_fail", msg)
        else:
            log_event("stress_tester", "iteration_pass", f"iter={i}")
        sleep(pause_seconds)

    summary = f"Stress test complete. Failures: {failures}/{iterations}"
    print(f"\n✅ {summary}")
    log_event("stress_tester", "complete", summary)


if __name__ == "__main__":
    run_stress_test()

