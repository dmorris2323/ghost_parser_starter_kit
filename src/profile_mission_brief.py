"""
profile_mission_brief.py — Ghost Lantern Labs
---------------------------------------------

Wraps the standard GLL daily mission brief with a
mission/customer profile overlay.

Inputs:
- Active profile (from profile_config)
- Core brief (from daily_mission_brief.build_mission_brief)

Output:
- docs/profile_mission_brief.txt

This is what you would show to:
- AFTAC / DoD audience
- A sports team front office
- A law firm partner
- A commercial SOC lead

…without changing the underlying engine logic.
"""

from __future__ import annotations

from pathlib import Path

from daily_mission_brief import build_mission_brief
from profile_config import get_active_profile, PROFILES, set_active_profile_key


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(exist_ok=True, parents=True)

PROFILE_MISSION_BRIEF_PATH = DOCS_DIR / "profile_mission_brief.txt"


def build_profile_header() -> str:
    """
    Build the profile-specific header block.
    """
    profile = get_active_profile()

    lines: list[str] = []
    lines.append("===== GLL PROFILED MISSION BRIEF =====")
    lines.append(f"Active profile: {profile.display_name} [{profile.key}]")
    lines.append("")
    lines.append("Mission context:")
    lines.append(f"  {profile.mission_context}")
    lines.append("")
    lines.append("Data focus:")
    lines.append(f"  {profile.data_focus}")
    lines.append("")
    lines.append("Risk language:")
    lines.append(f"  {profile.risk_language}")
    lines.append("")
    lines.append("Note: Under the hood, this is the same GLL fusion engine.")
    lines.append("      Only the framing and interpretation are adjusted per profile.")
    lines.append("")
    return "\n".join(lines)


def build_profiled_brief() -> str:
    """
    Combine profile header + core daily mission brief.
    """
    header = build_profile_header()
    core_brief = build_mission_brief()

    lines: list[str] = []
    lines.append(header)
    lines.append(core_brief)
    return "\n".join(lines)


def main() -> None:
    # Optional: first-run helper if user wants to choose a profile quickly.
    # (No interactive prompt; profile can be set via config or env)
    brief = build_profiled_brief()
    PROFILE_MISSION_BRIEF_PATH.write_text(brief, encoding="utf-8")

    print("✅ Profiled mission brief generated.")
    print(f"   Path: {PROFILE_MISSION_BRIEF_PATH}")
    print("\n----- BRIEF PREVIEW (TOP) -----\n")
    # Print only the top ~40 lines for sanity
    top_lines = "\n".join(brief.splitlines()[:40])
    print(top_lines)


if __name__ == "__main__":
    main()

