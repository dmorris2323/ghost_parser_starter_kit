"""
spectral_fallback_tree.py — Fallback response builder for Spectral Owl.

Used when:
  - LLM provider fails
  - Network / API issues
  - We want a predictable "degraded mode" summary.

Integration points:
  - spectral_owl/owl_router.py calls build_fallback_response(summary)
  - ghost_cli.py Option 28 can run this as a test harness
"""

from spectral_owl.owl_confidence import compute_confidence


def build_fallback_response(summary: dict):
    """
    Build a simple, deterministic fallback payload.

    Expected summary keys (best-effort):
      - critical_alerts: int
      - warning_alerts: int
      - avg_reliability: float

    Returns:
      {
        "source": "fallback",
        "summary": {...},
        "confidence": float
      }
    """
    if summary is None:
        summary = {}

    return {
        "source": "fallback",
        "summary": summary,
        "confidence": compute_confidence(summary),
    }


def demo_summary():
    """Small demo summary for CLI / manual testing."""
    return {
        "critical_alerts": 0,
        "warning_alerts": 3,
        "avg_reliability": 91.0,
    }


if __name__ == "__main__":
    sample = demo_summary()
    out = build_fallback_response(sample)
    print("=== Fallback Response Demo ===")
    print(out)

