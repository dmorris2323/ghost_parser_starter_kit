"""
profile_config.py — Ghost Lantern Labs
--------------------------------------

Defines mission / customer profiles for GLL.

Examples:
- aftac_nuclear   → ISR / nuclear-focused lab
- sports_team     → pro/college sports analytics & operations
- law_firm        → legal operations / caseload monitoring
- commercial_soc  → commercial cyber SOC / SIEM overlay

This is the first building block that lets you "plug the same
engine" into different missions without rewriting code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import os


BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True, parents=True)

ACTIVE_PROFILE_PATH = CONFIG_DIR / "profile.txt"


@dataclass
class Profile:
    key: str
    display_name: str
    mission_context: str
    data_focus: str
    risk_language: str


PROFILES: Dict[str, Profile] = {
    "aftac_nuclear": Profile(
        key="aftac_nuclear",
        display_name="AFTAC / Nuclear ISR",
        mission_context=(
            "Fusion platform supporting nuclear monitoring, anomaly detection, and "
            "pre-launch / post-event assessment for strategic decision-makers."
        ),
        data_focus=(
            "Multi-sensor telemetry (optical, seismic, EMS, radiation) plus supporting "
            "cyber indicators and intel notes."
        ),
        risk_language=(
            "Threat levels emphasize elevated nuclear indicators, sensor anomalies near "
            "known facilities, and fusion confidence."
        ),
    ),
    "sports_team": Profile(
        key="sports_team",
        display_name="Sports Team Operations",
        mission_context=(
            "Analytics and operations picture for a professional or college sports team: "
            "performance health, workload, and risk of failure in upcoming contests."
        ),
        data_focus=(
            "Metrics from wearables, practice intensity, travel fatigue, and opponent scouting "
            "summarized into a game-readiness snapshot."
        ),
        risk_language=(
            "Threat levels translate to game risk: LOW for routine conditions, MEDIUM when fatigue "
            "or key-player flags rise, HIGH when multiple stressors converge."
        ),
    ),
    "law_firm": Profile(
        key="law_firm",
        display_name="Law Firm / Case Operations",
        mission_context=(
            "Operational picture for a law firm: caseload pressure, deadlines, client risk, and "
            "payment / collection signals."
        ),
        data_focus=(
            "Case events, deadlines, hearings, filings, and payment status used to gauge which "
            "matters need immediate attention."
        ),
        risk_language=(
            "Threat levels map to case and client risk: LOW for normal workflow, MEDIUM for upcoming "
            "deadlines or payment gaps, HIGH when court, compliance, or financial exposure spikes."
        ),
    ),
    "commercial_soc": Profile(
        key="commercial_soc",
        display_name="Commercial SOC / Cyber Fusion",
        mission_context=(
            "Security operations center view of infrastructure health, alerts, and investigations."
        ),
        data_focus=(
            "Logs, telemetry, alerts, and ticket status fused into a single threat picture "
            "for defenders."
        ),
        risk_language=(
            "Threat levels express incident posture: LOW during routine monitoring, MEDIUM when "
            "active investigations are open, HIGH during active or suspected compromise."
        ),
    ),
}


def get_profile(profile_key: str) -> Profile:
    """
    Return a Profile by key, raising KeyError if not found.
    """
    if profile_key not in PROFILES:
        raise KeyError(f"Unknown profile key: {profile_key}")
    return PROFILES[profile_key]


def get_active_profile_key() -> str:
    """
    Determine the active profile key, using:
    1) Environment variable GLL_PROFILE, if set.
    2) config/profile.txt, if present.
    3) Default "aftac_nuclear".
    """
    env_key = os.environ.get("GLL_PROFILE")
    if env_key and env_key in PROFILES:
        return env_key

    if ACTIVE_PROFILE_PATH.exists():
        txt = ACTIVE_PROFILE_PATH.read_text(encoding="utf-8").strip()
        if txt in PROFILES:
            return txt

    # Default if nothing else present
    return "aftac_nuclear"


def set_active_profile_key(profile_key: str) -> None:
    """
    Persist a profile choice into config/profile.txt
    """
    if profile_key not in PROFILES:
        raise KeyError(f"Unknown profile key: {profile_key}")
    ACTIVE_PROFILE_PATH.write_text(profile_key, encoding="utf-8")


def get_active_profile() -> Profile:
    """
    Return the active Profile object.
    """
    key = get_active_profile_key()
    return get_profile(key)


if __name__ == "__main__":
    # Simple manual test
    active = get_active_profile()
    print(f"Active profile: {active.key} ({active.display_name})")
    print(f"Context: {active.mission_context}")

