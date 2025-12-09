# Ghost Lantern Labs — Nuclear Mission Brief

**Generated at (UTC):** 2025-12-09T13:41:15.877212+00:00

**Readiness Headline:** GLL readiness status: unknown (score=n/a)

## Golden Dome Nuclear Snapshot
```json
{
  "nuclear_readiness_score": 75.6,
  "components": {
    "trust": {
      "fusion_trust": 72,
      "factors": {
        "outliers": 0,
        "drift": {
          "status": "corrupted",
          "message": "could not parse golden_dome_status.txt",
          "drift_score": 0
        },
        "reliability": {
          "sensors": {
            "global": 100.0,
            "optical": 90.0,
            "seismic": 90.0,
            "ems": 90.0,
            "radiation": 90.0
          },
          "avg_reliability": 92.0
        },
        "crisis_mode": "ON"
      }
    },
    "reliability": {
      "sensors": {
        "global": 100.0,
        "optical": 90.0,
        "seismic": 90.0,
        "ems": 90.0,
        "radiation": 90.0
      },
      "avg_reliability": 92.0
    },
    "safety": {
      "osl_status": "YELLOW",
      "trust_score": 72,
      "message": "Moderate risk \u2014 verify critical readings."
    }
  }
}
```

## Pre-Launch ISR Watchboard
```json
{
  "timestamp": "2025-12-09T13:41:15.880867Z",
  "fusion_heat_index": 5,
  "heat_level": "LOW",
  "trust_score": null,
  "drift_status": "unknown",
  "avg_reliability": null,
  "latency": null,
  "critical_alerts": null,
  "warning_alerts": null,
  "nuclear_readiness": {}
}
```

## Fusion Heat Index (Battlespace Temperature)
```json
{
  "timestamp": "2025-12-09T13:41:15.881315Z",
  "FHI": 5,
  "level": "LOW",
  "inputs": {
    "critical_alerts": 0,
    "warning_alerts": 0,
    "avg_reliability": 90,
    "drift_score": 0,
    "latency_score": 90
  }
}
```

## Notes
- Engineering / demo only — not an operational nuclear C2 system.
- Replace sample data with validated sources before real-world integration.
