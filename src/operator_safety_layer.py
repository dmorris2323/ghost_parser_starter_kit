# operator_safety_layer.py
"""
Operator Safety Layer (OSL)
Evaluates whether an operator should be warned before trusting outputs.
"""

from pathlib import Path
import json
from fusion_trust import compute_trust

LOG = Path("docs/operator_safety_report.json")

def compute_osl():
    trust = compute_trust()
    score = trust["fusion_trust"]

    status = "GREEN"
    msg = "System stable."

    if score < 75:
        status = "YELLOW"
        msg = "Moderate risk — verify critical readings."

    if score < 55:
        status = "RED"
        msg = "High risk — fusion output may not be reliable."

    bundle = {
        "osl_status": status,
        "trust_score": score,
        "message": msg
    }

    LOG.write_text(json.dumps(bundle, indent=2))
    return bundle

def export_osl():
    return f"Operator Safety Layer report → {LOG}"

