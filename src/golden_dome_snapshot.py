import json
from pathlib import Path
from fusion_trust import compute_trust
from operator_safety_layer import compute_osl
from sensor_reliability import compute_reliability_all

OUTFILE = Path("docs/golden_dome_snapshot.json")

def build_snapshot():
    rel = compute_reliability_all()
    trust = compute_trust()
    osl = compute_osl()

    snapshot = {
        "nuclear_readiness_score": round(
            (trust["fusion_trust"] * 0.5) +
            (rel["avg_reliability"] * 0.3) +
            (100 if osl["osl_status"] == "GREEN" else 60) * 0.2,
            2
        ),
        "components": {
            "trust": trust,
            "reliability": rel,
            "safety": osl
        }
    }

    OUTFILE.write_text(json.dumps(snapshot, indent=2))
    return snapshot

