"""
owl_confidence.py — Simple confidence scoring for Spectral Owl fallback.

Input summary dict:
    {
        "critical_alerts": int,
        "warning_alerts": int,
        "avg_reliability": float
    }

Logic:
    Start from avg_reliability.
    Subtract 5 points per critical alert.
    Subtract 1.5 points per warning.
    Floor at 10.

Output:
    float confidence score, 10–100 range.
"""


def compute_confidence(summary: dict) -> float:
    critical = int(summary.get("critical_alerts", 0) or 0)
    warning = int(summary.get("warning_alerts", 0) or 0)
    avg_reliability = float(summary.get("avg_reliability", 90.0) or 90.0)

    score = avg_reliability - (critical * 5.0) - (warning * 1.5)
    if score < 10.0:
        score = 10.0
    if score > 100.0:
        score = 100.0

    return round(score, 2)


if __name__ == "__main__":
    test_payload = {
        "critical_alerts": 1,
        "warning_alerts": 4,
        "avg_reliability": 92.0,
    }
    print("Test confidence:", compute_confidence(test_payload))

