"""
azure_ingest.py — Simulated Azure ingest layer for Ghost Lantern Labs (GLL)

This module provides a local "cloud simulator" so you can:
  - Upload fusion outputs (scored_output / fused_output) into an archive
  - Upload operator snapshots
  - List archived fusion files
  - Download the latest archive into a local folder
  - Run a simple cloud_sync_health_check used by QA + ghost_cli

All paths are LOCAL and safe — no real Azure calls here.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import shutil
import json
from typing import Dict, Any, List

# Base = repo_root/src
BASE = Path(__file__).resolve().parent.parent

DATA_DIR = BASE / "data"
CLOUD_SIM = BASE / "cloud_sim"
ARCHIVE_DIR = CLOUD_SIM / "fusion_archive"
OP_SNAPSHOT_DIR = CLOUD_SIM / "operator_snapshots"
CONFIG_DIR = BASE / "config"
CONFIG_FILE = CONFIG_DIR / "cloud_settings.json"


def _ensure_dirs() -> None:
    """Ensure simulated cloud directories exist."""
    CLOUD_SIM.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)
    OP_SNAPSHOT_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S")


# ---------------------------------------------------------------------------
# FUSION OUTPUT UPLOAD
# ---------------------------------------------------------------------------

def upload_fusion_output(source_path: str | Path) -> Dict[str, Any]:
    """
    Simulate uploading a fused or scored output CSV into cloud archive.

    Copies the file into:
      src/cloud_sim/fusion_archive/<timestamp>__<filename>
    """
    _ensure_dirs()

    src = Path(source_path)
    if not src.exists():
        return {
            "status": "error",
            "reason": f"source file not found: {src}"
        }

    dest_name = f"{_timestamp()}__{src.name}"
    dest_path = ARCHIVE_DIR / dest_name

    try:
        shutil.copy2(src, dest_path)
    except Exception as e:
        return {
            "status": "error",
            "reason": f"failed to copy: {e}"
        }

    return {
        "status": "uploaded",
        "source": str(src),
        "destination": str(dest_path),
        "mode": "simulation",
    }


# ---------------------------------------------------------------------------
# OPERATOR SNAPSHOT UPLOAD
# ---------------------------------------------------------------------------

def upload_operator_snapshot(snapshot_path: str | Path) -> Dict[str, Any]:
    """
    Simulate uploading an operator snapshot text file into cloud archive.

    Copies the file into:
      src/cloud_sim/operator_snapshots/<timestamp>__<filename>
    """
    _ensure_dirs()

    src = Path(snapshot_path)
    if not src.exists():
        return {
            "status": "error",
            "reason": f"snapshot file not found: {src}"
        }

    dest_name = f"{_timestamp()}__{src.name}"
    dest_path = OP_SNAPSHOT_DIR / dest_name

    try:
        shutil.copy2(src, dest_path)
    except Exception as e:
        return {
            "status": "error",
            "reason": f"failed to copy snapshot: {e}"
        }

    return {
        "status": "uploaded",
        "source": str(src),
        "destination": str(dest_path),
        "mode": "simulation",
    }


# ---------------------------------------------------------------------------
# LIST / DOWNLOAD FUSION BLOBS
# ---------------------------------------------------------------------------

def list_fusion_blobs() -> Dict[str, Any]:
    """
    List archived fusion outputs in the simulated cloud archive.
    """
    _ensure_dirs()

    files: List[str] = []
    for p in sorted(ARCHIVE_DIR.glob("*")):
        if p.is_file():
            files.append(p.name)

    return {
        "status": "ok",
        "count": len(files),
        "files": files,
    }


def download_latest_fusion_archive(dest_dir: str | Path) -> Dict[str, Any]:
    """
    Simulate downloading the most recent fusion archive file into dest_dir.
    """
    _ensure_dirs()

    candidates = sorted(
        [p for p in ARCHIVE_DIR.glob("*") if p.is_file()],
        key=lambda p: p.name,
        reverse=True,
    )

    if not candidates:
        return {
            "status": "error",
            "reason": "no fusion archives in cloud_sim/fusion_archive"
        }

    latest = candidates[0]
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / latest.name

    try:
        shutil.copy2(latest, dest_path)
    except Exception as e:
        return {
            "status": "error",
            "reason": f"failed to copy latest archive: {e}"
        }

    return {
        "status": "downloaded",
        "source": str(latest),
        "destination": str(dest_path),
        "mode": "simulation",
    }


# ---------------------------------------------------------------------------
# CLOUD SYNC HEALTH CHECK
# ---------------------------------------------------------------------------

def _load_config() -> Dict[str, Any]:
    """
    Load simulated cloud config from config/cloud_settings.json if present.
    """
    if not CONFIG_FILE.exists():
        # Default simulation config
        return {
            "provider": "azure",
            "sync_enabled": True,
            "mode": "simulation"
        }

    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        # If config is corrupted, fall back to safe defaults.
        return {
            "provider": "azure",
            "sync_enabled": False,
            "mode": "config_error",
        }


def cloud_sync_health_check() -> Dict[str, Any]:
    """
    Return a health summary used by qa_validator and ghost_cli.

    Example output:
    {
      "status": "ok",
      "details": {"provider": "azure", "mode": "simulation", "sync_enabled": true},
      "files_in_archive": 3
    }
    """
    _ensure_dirs()
    cfg = _load_config()

    files = [p for p in ARCHIVE_DIR.glob("*") if p.is_file()]
    count = len(files)

    status = "ok"
    if not cfg.get("sync_enabled", True):
        status = "warning"
    if cfg.get("mode") == "config_error":
        status = "error"

    return {
        "status": status,
        "details": cfg,
        "files_in_archive": count,
    }


if __name__ == "__main__":
    # Quick manual check
    print("Cloud sync health:", cloud_sync_health_check())
    print("Fusion blobs:", list_fusion_blobs())

