"""
azure_ingest.py

Simulated Azure blob ingest for Ghost Lantern Labs.

This does NOT use real Azure credentials.
It just copies files into a local "cloud_sim/fusion_archive" directory
to mimic upload/download behavior for testing and demos.
"""

import json
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path("config/cloud_settings.json")


def load_cloud_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Cloud config not found at {CONFIG_PATH}")

    with CONFIG_PATH.open("r") as f:
        cfg = json.load(f)

    return cfg


def _update_last_sync_timestamp():
    cfg = load_cloud_config()
    cfg["last_sync_timestamp"] = datetime.utcnow().isoformat() + "Z"
    with CONFIG_PATH.open("w") as f:
        json.dump(cfg, f, indent=2)


def init_blob_client():
    """
    Stub init. In real Azure, this would return a BlobServiceClient / ContainerClient.
    In simulation mode, we just ensure the local_sim_path exists.
    """
    cfg = load_cloud_config()
    if not cfg.get("sync_enabled", False):
        return {"status": "disabled", "reason": "sync_enabled is false"}

    sim_path = Path(cfg.get("local_sim_path", "cloud_sim/fusion_archive"))
    sim_path.mkdir(parents=True, exist_ok=True)

    return {
        "status": "ok",
        "provider": cfg.get("provider", "unknown"),
        "mode": "simulation" if cfg.get("simulation_mode", True) else "real",
        "sim_path": str(sim_path),
    }


def upload_fusion_output(file_path: str):
    """
    Simulated upload:
      - Verifies file exists
      - Copies it into local_sim_path with a timestamped name
    """
    cfg = load_cloud_config()
    if not cfg.get("sync_enabled", False):
        return {"status": "skipped", "reason": "sync disabled"}

    src = Path(file_path)
    if not src.exists():
        return {"status": "error", "reason": f"File not found: {src}"}

    sim_path = Path(cfg.get("local_sim_path", "cloud_sim/fusion_archive"))
    sim_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    dest_name = f"{timestamp}__{src.name}"
    dest = sim_path / dest_name

    dest.write_bytes(src.read_bytes())

    _update_last_sync_timestamp()

    return {
        "status": "uploaded",
        "source": str(src),
        "destination": str(dest),
        "mode": "simulation" if cfg.get("simulation_mode", True) else "real",
    }


def list_fusion_blobs():
    """
    Lists files in the simulated cloud container.
    """
    cfg = load_cloud_config()
    sim_path = Path(cfg.get("local_sim_path", "cloud_sim/fusion_archive"))

    if not sim_path.exists():
        return {"status": "ok", "count": 0, "files": []}

    files = sorted([f.name for f in sim_path.iterdir() if f.is_file()])

    return {
        "status": "ok",
        "count": len(files),
        "files": files,
    }


def download_latest_fusion_archive(target_dir: str = "downloads"):
    """
    Simulated download:
      - Finds latest file in sim_path
      - Copies to target_dir
    """
    cfg = load_cloud_config()
    sim_path = Path(cfg.get("local_sim_path", "cloud_sim/fusion_archive"))
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)

    if not sim_path.exists():
        return {"status": "error", "reason": "no sim_path found"}

    files = sorted(
        [f for f in sim_path.iterdir() if f.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not files:
        return {"status": "error", "reason": "no files in archive"}

    latest = files[0]
    dest = target / latest.name
    dest.write_bytes(latest.read_bytes())

    return {
        "status": "downloaded",
        "source": str(latest),
        "destination": str(dest),
    }


def cloud_sync_health_check():
    """
    High-level health check for QA + CLI.
    """
    try:
        cfg = load_cloud_config()
    except FileNotFoundError as e:
        return {"status": "error", "details": str(e)}

    init_result = init_blob_client()
    if init_result.get("status") != "ok":
        return {"status": "warning", "details": f"Init: {init_result}"}

    listing = list_fusion_blobs()

    return {
        "status": "ok",
        "details": {
            "provider": cfg.get("provider"),
            "mode": "simulation" if cfg.get("simulation_mode", True) else "real",
            "sync_enabled": cfg.get("sync_enabled", False),
        },
        "files_in_archive": listing.get("count", 0),
    }

