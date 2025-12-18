# demo_freeze_loader.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # demo_freeze_loader.py lives at repo root
    return Path(__file__).resolve().parent


def load_demo_freeze_manifest() -> Dict[str, Any]:
    """
    Loads docs/demo/demo_freeze_manifest.json.
    If missing/invalid, returns a safe default with demo_safe=False.
    """
    root = _repo_root()
    p = root / "docs" / "demo" / "demo_freeze_manifest.json"
    if not p.exists():
        return {
            "schema_version": "10F.1",
            "generated_at_utc": _utc_now_iso(),
            "mode": "DEMO_FREEZE",
            "demo_safe": False,
            "required_banner_text": "",
            "error": f"missing manifest: {p}",
        }
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("manifest is not a JSON object")
        # normalize
        data.setdefault("schema_version", "10F.1")
        data.setdefault("mode", "DEMO_FREEZE")
        data.setdefault("demo_safe", False)
        data.setdefault("required_banner_text", "")
        data.setdefault("generated_at_utc", _utc_now_iso())
        return data
    except Exception as e:
        return {
            "schema_version": "10F.1",
            "generated_at_utc": _utc_now_iso(),
            "mode": "DEMO_FREEZE",
            "demo_safe": False,
            "required_banner_text": "",
            "error": f"invalid manifest: {e}",
        }


def is_demo_safe(manifest: Dict[str, Any]) -> bool:
    """
    Demo-safe means:
      - mode == DEMO_FREEZE
      - demo_safe == True
      - required_banner_text is non-empty
    """
    try:
        if (manifest or {}).get("mode") != "DEMO_FREEZE":
            return False
        if (manifest or {}).get("demo_safe") is not True:
            return False
        if not str((manifest or {}).get("required_banner_text", "")).strip():
            return False
        return True
    except Exception:
        return False

