"""
training_config.py

Training system configuration:
- instructor_lock: if True, trainees cannot change difficulty
- locked_difficulty: enforced difficulty when locked
- auto_difficulty: if True, system recommends/advances difficulty based on performance
"""

import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path("src/config/training_config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "instructor_lock": False,
    "locked_difficulty": "INTERMEDIATE",
    "auto_difficulty": False,
    "auto_policy": {
        "min_sessions_for_adapt": 4,
        "promote_if_slope_gte": 1.0,
        "demote_if_slope_lte": -1.0,
        "max_volatility_for_promote": 18.0,
    },
}


def load_training_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(CONFIG_PATH.read_text())
        # Merge defaults for forward compatibility
        merged = dict(DEFAULT_CONFIG)
        merged.update(data if isinstance(data, dict) else {})
        merged["auto_policy"] = {**DEFAULT_CONFIG["auto_policy"], **merged.get("auto_policy", {})}
        return merged
    except Exception:
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        return dict(DEFAULT_CONFIG)


def save_training_config(cfg: Dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def set_lock(enabled: bool, locked_difficulty: str = "INTERMEDIATE") -> Dict[str, Any]:
    cfg = load_training_config()
    cfg["instructor_lock"] = bool(enabled)
    cfg["locked_difficulty"] = (locked_difficulty or "INTERMEDIATE").upper()
    save_training_config(cfg)
    return cfg


def set_auto_difficulty(enabled: bool) -> Dict[str, Any]:
    cfg = load_training_config()
    cfg["auto_difficulty"] = bool(enabled)
    save_training_config(cfg)
    return cfg


def effective_difficulty(requested: str) -> str:
    """
    Returns the enforced difficulty if instructor_lock is on, else requested.
    """
    cfg = load_training_config()
    if cfg.get("instructor_lock"):
        return (cfg.get("locked_difficulty") or "INTERMEDIATE").upper()
    return (requested or "INTERMEDIATE").upper()

