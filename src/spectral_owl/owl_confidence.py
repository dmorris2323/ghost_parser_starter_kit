"""
owl_confidence.py — Compute fallback confidence for Spectral Owl.

Takes a simple summary dict:
{
    "critical_alerts": int,
    "warning_alerts": int,
    "avg_reliability": float
}

Returns a confidence score (0–100).
"""

def compute_confidence(raw: dict):
    crit = raw.get("critical_alerts", 0) or 0
    warnings = raw.get("warning_alerts", 0) or 0
    reliability = raw.get("avg_reliability", 90) or 90

    # Penalty per critical + warning, anchored on reliability
    score = reliability - crit * 5 - warnings * 1.5
    score = max(10, min(100, score))
    return round(score, 2)


if __name__ == "__main__":
    sample = {"critical_alerts": 1, "warning_alerts": 4, "avg_reliability": 92}
    print("Sample confidence:", compute_confidence(sample))

