"""
spectral_snapshot_export.py — Spectral Snapshot Bundle Export

This module builds a single "snapshot bundle" of the current GLL state,
so you (or a commander, or Shari, or a future customer) can see:
  - Operator snapshot
  - Mission brief (text + HTML)
  - Sensor health
  - Threat memory stats
  - Minimap + SOS overlays
  - Active profile + AI engine

Output:
  docs/spectral_snapshot_bundle.json
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


BASE = Path(__file__).resolve().parent
DOCS_DIR = BASE / "docs"

# Common artifact locations (best-effort; missing files are skipped)
ARTIFACTS = {
    "operator_snapshot_txt": BASE / "operator_snapshot.txt",
    "system_status_txt": DOCS_DIR / "system_status_dashboard.txt",
    "sensor_health_txt": BASE / "sensor_health_report.txt",
    "threat_memory_stats_txt": BASE / "threat_memory_stats.txt",
    "daily_brief_txt": DOCS_DIR / "daily_mission_brief.txt",
    "daily_brief_html": DOCS_DIR / "daily_mission_brief.html",
    "minimap_json": BASE / "gui_minimap.json",
    "sos_overlay_json": BASE / "gui_sos_overlay.json",
    "spectral_dashboard_json": DOCS_DIR / "spectral_dashboard_bundle.json",
}


def _safe_read_text(path: Path) -> str | None:
    """Read a text file safely; return None if missing or broken."""
    try:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _safe_read_json(path: Path) -> dict | None:
    """Read a JSON file safely; return None if missing or broken."""
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _get_active_profile_info() -> dict:
    """
    Try to pull active profile info from profile_config.
    Falls back gracefully if anything is missing.
    """
    info: dict[str, str | None] = {
        "key": None,
        "display_name": None,
        "domain": None,
    }

    try:
        from profile_config import get_active_profile  # type: ignore
    except Exception:
        return info

    try:
        p = get_active_profile()
        info["key"] = getattr(p, "key", None)
        info["display_name"] = getattr(p, "display_name", None)
        info["domain"] = getattr(p, "domain", None)
        return info
    except Exception:
        return info


def _get_llm_provider_info() -> dict:
    """
    Try to pull AI provider info from llm_phase2_adapter.
    """
    info: dict[str, str | None] = {
        "active_provider": None,
        "mode": None,
    }

    try:
        from llm_phase2_adapter import get_active_provider, get_active_mode  # type: ignore
    except Exception:
        return info

    try:
        info["active_provider"] = str(get_active_provider())
    except Exception:
        pass

    try:
        info["mode"] = str(get_active_mode())
    except Exception:
        pass

    return info


def build_spectral_snapshot() -> dict:
    """
    Build an in-memory representation of the current spectral snapshot.
    """
    snapshot: dict[str, object] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "profile": _get_active_profile_info(),
        "llm": _get_llm_provider_info(),
        "artifacts": {},
    }

    # Attach textual artifacts
    for key, path in ARTIFACTS.items():
        if key.endswith("_json"):
            data = _safe_read_json(path)
        else:
            data = _safe_read_text(path)

        snapshot["artifacts"][key] = {
            "path": str(path),
            "exists": path.exists(),
            "content": data,
        }

    return snapshot


def export_spectral_snapshot(output_path: str | None = None) -> str:
    """
    Write the spectral snapshot bundle to docs/spectral_snapshot_bundle.json
    (or custom path if provided).

    Returns the output path as a string.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    bundle_path = (
        Path(output_path)
        if output_path
        else DOCS_DIR / "spectral_snapshot_bundle.json"
    )

    snapshot = build_spectral_snapshot()
    bundle_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return str(bundle_path)


if __name__ == "__main__":
    out = export_spectral_snapshot()
    print(f"Spectral snapshot bundle written to: {out}")

