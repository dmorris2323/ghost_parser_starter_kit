"""
profiles package for Ghost Lantern Labs.

Each profile is a small metadata dict that describes
how the system should "think" about its mission.
"""

from .nuclear_early_warning import profile as nuclear_early_warning

PROFILES = {
    "nuclear_early_warning": nuclear_early_warning,
}

