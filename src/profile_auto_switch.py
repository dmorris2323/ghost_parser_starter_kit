"""
profile_auto_switch.py
----------------------

Quick domain → profile key mapper.

Used by:
 - ghost_cli.py Option 15 ("Switch Profile (Quick Select)")

Domains:
 - nuclear → aftac_nuclear
 - sports  → sports_team
 - legal   → law_firm
 - soc     → commercial_soc
"""

from profile_config import set_active_profile_key


DOMAIN_TO_PROFILE = {
    "nuclear": "aftac_nuclear",
    "sports": "sports_team",
    "legal": "law_firm",
    "soc": "commercial_soc",
}


def auto_switch(domain: str):
    """
    Switch active profile based on a simple domain string.

    Returns a small status dict so CLI can show a clean message.
    """

    domain = (domain or "").strip().lower()

    if domain not in DOMAIN_TO_PROFILE:
        return {
            "status": "fail",
            "reason": f"Unsupported domain '{domain}'. Use nuclear/sports/legal/soc."
        }

    profile_key = DOMAIN_TO_PROFILE[domain]

    try:
        set_active_profile_key(profile_key)
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
            "profile": profile_key,
        }

    return {
        "status": "ok",
        "profile": profile_key,
    }


if __name__ == "__main__":
    # Simple self-test when run directly
    for d in ["nuclear", "sports", "legal", "soc", "bad_domain"]:
        print(f"\n[TEST] auto_switch({d!r})")
        print(auto_switch(d))

