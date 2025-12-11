#!/usr/bin/env python3
"""
azure_ingest_adapter.py

Ghost Lantern Labs – Azure / Cloud Ingest Adapter (Scaffold)
------------------------------------------------------------

Purpose:
    Provide a safe, non-invasive scaffold for future Azure/cloud integration.

    Today:
        - Defines a basic Azure ingest config structure.
        - Inspects config/azure_ingest_config.json if present.
        - Returns a readiness summary for cloud-based ingest.

    Future:
        - Attach to Azure Blob Storage, Event Hubs, or other services.
        - Stream telemetry into the existing fusion_ingest pipeline.

    This module performs NO network calls in its current form.
"""

import json
import os
from typing import Any, Dict, Optional


BASE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

AZURE_CONFIG_PATH = os.path.join(CONFIG_DIR, "azure_ingest_config.json")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _ensure_dirs() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)


def get_default_azure_config_template() -> Dict[str, Any]:
    """
    Provide a template for how Azure ingest configuration SHOULD look.

    This does not enforce any schema yet; it simply defines fields we expect
    to be useful once you wire up real cloud ingestion.
    """
    return {
        "enabled": False,
        "subscription_id": "YOUR_SUBSCRIPTION_ID",
        "resource_group": "YOUR_RESOURCE_GROUP",
        "workspace_name": "YOUR_WORKSPACE_OR_NAMESPACE",
        "mode": "blob|eventhub|queue|custom",
        "storage_account": {
            "name": "yourstorageaccount",
            "container": "telemetry",
            "connection_string": "UseAzureIdentityOrKeyVaultInRealDeployments",
        },
        "event_hub": {
            "namespace": "youreventhubns",
            "name": "gll-telemetry",
            "connection_string": "UseAzureIdentityOrKeyVaultInRealDeployments",
        },
        "ingest_mapping": {
            "blob": {
                "format": "jsonl|csv|custom",
                "path_schema_hint": "folder/year=/month=/day=/",
            },
            "common_fields": {
                "timestamp_field": "timestamp_utc",
                "sensor_id_field": "sensor_id",
                "payload_field": "payload",
            },
        },
        "notes": "This is a scaffold template; do NOT commit secrets here.",
    }


def inspect_azure_config() -> Dict[str, Any]:
    """
    Inspect azure_ingest_config.json and return a readiness summary.

    This is designed to be safe in environments where the config does not yet exist.
    """
    _ensure_dirs()
    cfg = _safe_read_json(AZURE_CONFIG_PATH)

    if cfg is None:
        # No config yet – this is expected for now.
        return {
            "status": "NOT_CONFIGURED",
            "message": "Azure ingest config not found; this is expected until cloud integration is enabled.",
            "config_path": AZURE_CONFIG_PATH,
            "enabled": False,
            "mode": None,
            "issues": [
                "Azure ingest is currently disabled / not configured.",
                "Create azure_ingest_config.json using the default template when you are ready to attach cloud telemetry.",
            ],
            "suggested_template": get_default_azure_config_template(),
        }

    enabled = bool(cfg.get("enabled", False))
    mode = cfg.get("mode", None)

    issues = []
    if not enabled:
        issues.append("Azure ingest is present but 'enabled' is False.")
    if not mode:
        issues.append("No 'mode' set in Azure config (expected: blob|eventhub|queue|custom).")

    storage = cfg.get("storage_account", {}) or {}
    event_hub = cfg.get("event_hub", {}) or {}

    if mode == "blob":
        if not storage.get("name"):
            issues.append("Blob mode selected but storage_account.name is missing.")
        if not storage.get("container"):
            issues.append("Blob mode selected but storage_account.container is missing.")
    elif mode == "eventhub":
        if not event_hub.get("namespace"):
            issues.append("EventHub mode selected but event_hub.namespace is missing.")
        if not event_hub.get("name"):
            issues.append("EventHub mode selected but event_hub.name is missing.")

    status = "READY" if enabled and not issues else "PARTIAL"

    return {
        "status": status,
        "message": "Azure ingest configuration inspected.",
        "config_path": AZURE_CONFIG_PATH,
        "enabled": enabled,
        "mode": mode,
        "issues": issues,
        "storage_account": {
            "name": storage.get("name"),
            "container": storage.get("container"),
        },
        "event_hub": {
            "namespace": event_hub.get("namespace"),
            "name": event_hub.get("name"),
        },
    }


if __name__ == "__main__":
    summary = inspect_azure_config()
    print(json.dumps(summary, indent=2))

