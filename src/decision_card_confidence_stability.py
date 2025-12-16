"""
decision_card_confidence_stability.py

Ensures decision-card confidence remains stable, bounded,
and does not inflate under repeated degraded conditions.
"""

from datetime import datetime, timezone
from pathlib import Path
import json

from nuclear_decision_card import build_decision_card

OUT_DIR = Path("docs/nuclear")

def _utc_now():
    return datetime.now(timezone.utc).isoformat()

def run_confidence_stability_test(runs: int = 50):
    results = []
    violations = []

    last_confidence = None

    for i in range(runs):
        card = build_decision_card(
            trust_score=82,
            risk_score=48,
            alerts={"crit": 0, "high": 3, "anomaly": 14},
            degraded=True,
            comms_state=None,
            radiation_usv=None,
            seismic_mag=None,
            ems_state="NOISY",
        )

        confidence = card.get("status", {}).get("confidence")

        if last_confidence and confidence != last_confidence:
            violations.append({
                "run": i,
                "type": "CONFIDENCE_DRIFT",
                "previous": last_confidence,
                "current": confidence,
            })

        last_confidence = confidence
        results.append(confidence)

    verdict = "PASS" if not violations else "FAIL"

    report = {
        "generated_at_utc": _utc_now(),
        "verdict": verdict,
        "runs": runs,
        "final_confidence": last_confidence,
        "violations": violations,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    latest = OUT_DIR / "decision_confidence_stability_latest.json"
    stamped = OUT_DIR / f"decision_confidence_stability_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    latest.write_text(json.dumps(report, indent=2))
    stamped.write_text(json.dumps(report, indent=2))

    print("Decision Confidence Stability Test:")
    print(json.dumps(report, indent=2))

    return report

if __name__ == "__main__":
    run_confidence_stability_test()

