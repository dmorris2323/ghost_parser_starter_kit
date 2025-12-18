# src/demo_freeze_loader.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple


def _repo_root() -> Path:
    # This file is in src/, so repo root is one level up.
    return Path(__file__).resolve().parent.parent


def _manifest_candidates() -> Tuple[Path, ...]:
    root = _repo_root()
    return (
        root / "docs" / "demo" / "demo_freeze_manifest.json",
        root / "docs" / "demo" / "demo_freeze_manifest_latest.json",
    )


def load_demo_freeze_manifest() -> Dict[str, Any]:
    """
    Loads the demo freeze manifest. Prefers demo_freeze_manifest.json,
    falls back to demo_freeze_manifest_latest.json.
    Always returns an object that includes '_loaded_from'.
    """
    for p in _manifest_candidates():
        if p.exists():
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(obj, dict):
                    obj["_loaded_from"] = str(p)
                    return obj
            except Exception:
                # try next candidate
                pass

    # fallback default (SAFE = False)
    root = _repo_root()
    return {
        "schema_version": "1.0",
        "mode": "DEMO_FREEZE",
        "demo_safe": False,
        "required_banner_text": "",
        "notes": ["Fallback manifest used; expected docs/demo/demo_freeze_manifest(.json|_latest.json)."],
        "_loaded_from": str(root / "docs" / "demo" / "MISSING_MANIFEST"),
    }


def is_demo_safe(manifest: Dict[str, Any]) -> bool:
    """
    Demo-safe means:
      - mode == DEMO_FREEZE
      - demo_safe == True (accepts bool True or string 'true')
      - required_banner_text is non-empty
    """
    mode = (manifest.get("mode") or "").strip()
    demo_safe_raw = manifest.get("demo_safe")

    # tolerate string values
    if isinstance(demo_safe_raw, str):
        demo_safe = demo_safe_raw.strip().lower() == "true"
    else:
        demo_safe = bool(demo_safe_raw)

    banner = (manifest.get("required_banner_text") or "").strip()
    return (mode == "DEMO_FREEZE") and demo_safe and (len(banner) > 0)

