# src/training_paths.py
from __future__ import annotations

from pathlib import Path

# Canonical training directory (preferred)
CANON_TRAINING_DIR = Path("docs") / "training"

# Legacy / alternate training directory (some modules/apps wrote here earlier)
LEGACY_TRAINING_DIR = Path("src") / "docs" / "training"


def ensure_dirs() -> None:
    CANON_TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_TRAINING_DIR.mkdir(parents=True, exist_ok=True)


def sessions_path_latest() -> Path:
    return CANON_TRAINING_DIR / "training_sessions.json"


def curve_path_latest() -> Path:
    return CANON_TRAINING_DIR / "training_curve_latest.json"


def feedback_path_latest() -> Path:
    return CANON_TRAINING_DIR / "training_feedback_latest.json"


def resolve_existing(path: Path) -> Path:
    """
    Prefer canonical path. If missing, fall back to legacy mirror.
    """
    if path.exists():
        return path

    # map canonical docs/training/* -> src/docs/training/*
    try:
        rel = path.relative_to(CANON_TRAINING_DIR)
        alt = LEGACY_TRAINING_DIR / rel
        if alt.exists():
            return alt
    except Exception:
        pass

    return path

