"""
Nuclear Product Consistency Gate
Ensures Decision Card, Prelaunch Watchboard, and Prebrief Annotations
are logically aligned and bounded under ambiguity.

Week-1 Nuclear Hardening — FINAL SEAL
"""

from pathlib import Path
from datetime import datetime, timezone
import json


BASE = Path("docs")
OUT_DIR = BASE / "nuclear"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DECISION_CARD = BASE / "decision_cards" / "nuclear_decision_card_latest.json"
WATCHBOARD = BASE / "nuclear" / "prelaunch_watchboard_latest.json"
PREBRIEF = BASE / "briefs" / "prebrief_trust_annotations_latest.json"


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def run_gate():
    violations = []

    card = load_json(DECISION_CARD)
    wb = load_json(WATCHBOARD)
    pb = load_json(PREBRIEF)

    if not card:
        violations.append("MISSING_DECISION_CARD")
    if not wb:
        violations.append("MISSING_WATCHBOARD")
    if not pb:
        violations.append("MISSING_PREBRIEF")

    if not violations:
        posture_card = card.get("escalation", {}).get("posture")
        posture_pb = pb.get("trust_posture", {}).get("posture")

        if posture_card != posture_pb:
            violations.append(
                f"POSTURE_MISMATCH: decision_card={posture_card}, prebrief={posture_pb}"
            )

        ambiguity_flags = card.get("ambiguity_flags", [])
        annotations_txt = json.dumps(pb).lower()

        if ambiguity_flags:
            for token in ["probabilistic", "bounded", "operator judgment"]:
                if token not in annotations_txt:
                    violations.append(f"MISSING_REQUIRED_TOKEN:{token}")

    verdict = "PASS" if not violations else "FAIL"

    result = {
        "generated_at_utc": _utc_now(),
        "verdict": verdict,
        "violations": violations,
    }

    stamped = OUT_DIR / f"nuclear_product_consistency_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    latest = OUT_DIR / "nuclear_product_consistency_latest.json"
    latest_txt = OUT_DIR / "nuclear_product_consistency_latest.txt"

    stamped.write_text(json.dumps(result, indent=2))
    latest.write_text(json.dumps(result, indent=2))
    latest_txt.write_text(
        f"Nuclear Product Consistency Gate\n"
        f"generated_at_utc: {result['generated_at_utc']}\n"
        f"verdict: {verdict}\n"
        f"violations: {len(violations)}\n"
        + ("\n".join(violations) if violations else "No violations detected.")
    )

    return {
        "json_latest": str(latest),
        "txt_latest": str(latest_txt),
        "json_stamped": str(stamped),
        "verdict": verdict,
        "violations": violations,
    }


if __name__ == "__main__":
    out = run_gate()
    print("Nuclear Product Consistency Gate:")
    print(json.dumps(out, indent=2))

