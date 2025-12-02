"""
profile_mission_brief.py
------------------------

Generates a profile-aware mission brief that combines:

 - Active Profile metadata (from profile_config)
 - Daily Mission Brief (text)
 - Fusion Mini-Map (AOI map)
 - Profile context summary

Outputs:
   docs/profile_mission_brief.txt
"""

from __future__ import annotations

from pathlib import Path
import html

from profile_config import get_active_profile
from daily_mission_brief import write_daily_brief
from fusion_minimap import build_minimap

# File paths relative to src/
TXT_BRIEF_PATH = Path("docs/daily_mission_brief.txt")
PROFILE_BRIEF_PATH = Path("docs/profile_mission_brief.txt")
MINIMAP_PATH = Path("minimap.txt")


# ------------------------------------------------------------
# SAFE HELPERS
# ------------------------------------------------------------

def _safe_profile_info() -> dict:
    """
    Safely load the active profile from profile_config.
    Handles dict-returns, string-returns, and edge cases.
    Returns a dict with stable keys.
    """
    try:
        raw = get_active_profile()
    except Exception:
        return {
            "display_name": "Unknown",
            "key": "unknown",
            "notes": "Profile loader encountered an error."
        }

    # If it's already a dict-like structure
    if isinstance(raw, dict):
        return {
            "display_name": raw.get("display_name") or raw.get("name") or raw.get("key") or "Unknown",
            "key": raw.get("key", "unknown"),
            "notes": raw.get("notes", "No profile notes available.")
        }

    # If it's a plain string
    return {
        "display_name": str(raw),
        "key": str(raw).lower().replace(" ", "_"),
        "notes": "Profile returned as simple string. No metadata available."
    }


def _get_daily_brief() -> str:
    """
    Load the daily mission brief, generating it if missing.
    """
    if not TXT_BRIEF_PATH.exists():
        write_daily_brief()

    try:
        return TXT_BRIEF_PATH.read_text(encoding="utf-8")
    except Exception as e:
        return f"[ERROR reading daily brief] {e}"


def _get_minimap() -> str:
    """
    Build & load the Fusion Mini-Map.
    """
    try:
        build_minimap()
    except Exception as e:
        return f"[Mini-map build error] {e}"

    if not MINIMAP_PATH.exists():
        return "[Mini-map missing] minimap.txt not found."

    try:
        return MINIMAP_PATH.read_text(encoding="utf-8")
    except Exception as e:
        return f"[Mini-map load error] {e}"


# ------------------------------------------------------------
# BUILD MAIN PROFILE BRIEF
# ------------------------------------------------------------

def build_profile_mission_brief() -> str:
    """
    Construct the full profile-aware mission brief.
    """

    p = _safe_profile_info()
    daily_brief = _get_daily_brief()
    minimap = _get_minimap()

    lines = []
    lines.append("==============================================")
    lines.append("      GLL — PROFILE AWARE OPERATOR BRIEF")
    lines.append("==============================================")
    lines.append("")
    lines.append(f"Active Profile     : {p['display_name']}")
    lines.append(f"Profile Key        : {p['key']}")
    lines.append("")
    lines.append("PROFILE NOTES:")
    lines.append("----------------------------------------------")
    lines.append(p["notes"])
    lines.append("")
    lines.append("FUSION MINI-MAP:")
    lines.append("----------------------------------------------")
    lines.append(minimap)
    lines.append("")
    lines.append("DAILY MISSION BRIEF:")
    lines.append("----------------------------------------------")
    lines.append(daily_brief)
    lines.append("")
    lines.append("==============================================")
    lines.append("END OF PROFILE MISSION BRIEF")
    lines.append("==============================================")

    return "\n".join(lines)


def write_profile_brief() -> None:
    """
    Save profile mission brief to file.
    """
    PROFILE_BRIEF_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = build_profile_mission_brief()
    PROFILE_BRIEF_PATH.write_text(out, encoding="utf-8")
    print(f"[OK] Profile mission brief -> {PROFILE_BRIEF_PATH}")


def main():
    write_profile_brief()


if __name__ == "__main__":
    main()

