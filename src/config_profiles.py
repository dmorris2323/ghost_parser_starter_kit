"""
config_profiles.py — Ghost Lantern Labs
---------------------------------------
Defines high-level profiles for future plug-and-play deployments.

Examples:
  - "aftac_nuclear"
  - "sports_team"
  - "law_firm"
  - "commercial_soc"
"""

from typing import Dict, Any

PROFILES: Dict[str, Dict[str, Any]] = {
    "aftac_nuclear": {
        "description": "Nuclear / EMS / seismic fusion focus for AFTAC-style missions.",
        "domains": ["nuclear", "ems", "seismic", "space"],
        "default_threat_types": ["launch_prep", "sensor_spoof", "jamming"],
        "offline_priority": True,
        "severity_labels": {
            "HIGH": "Immediate commander attention",
            "MODERATE": "Monitor closely / watchlist",
            "LOW": "Routine background noise",
        },
    },
    "sports_team": {
        "description": "Player performance and risk fusion for elite sports organizations.",
        "domains": ["biometrics", "workload", "injury_risk"],
        "default_threat_types": ["overuse", "fatigue_spike", "impact_risk"],
        "offline_priority": False,
        "severity_labels": {
            "HIGH": "Remove from play / urgent attention",
            "MODERATE": "Limit reps / monitor closely",
            "LOW": "Normal training load",
        },
    },
    "law_firm": {
        "description": "Case progression, bottlenecks, and evidence fusion for litigation / family law firms.",
        "domains": ["case_load", "deadlines", "evidence_streams"],
        "default_threat_types": ["deadline_risk", "evidence_gap", "overload"],
        "offline_priority": False,
        "severity_labels": {
            "HIGH": "Immediate action / risk of loss",
            "MODERATE": "Needs attention this week",
            "LOW": "Routine tracking only",
        },
    },
    "commercial_soc": {
        "description": "Network / endpoint / cloud telemetry fusion for SOC environments.",
        "domains": ["network", "endpoint", "cloud"],
        "default_threat_types": ["dos", "intrusion", "exfiltration"],
        "offline_priority": True,
        "severity_labels": {
            "HIGH": "Active compromise or major outage",
            "MODERATE": "Suspicious activity / containment needed",
            "LOW": "Background noise / benign events",
        },
    },
}


def get_profile(name: str) -> Dict[str, Any]:
    return PROFILES.get(name, {})


def list_profiles() -> Dict[str, str]:
    """
    Return a map of profile_name -> description.
    """
    return {k: v["description"] for k, v in PROFILES.items()}


if __name__ == "__main__":
    # Quick self-test
    from pprint import pprint

    pprint(list_profiles())
    print()
    pprint(get_profile("aftac_nuclear"))

