"""
scenario_pack_builder.py

Builds a single JSON "scenario pack" that captures the current state of:
- Fusion Trust Score
- Operator Safety Layer
- Fusion Mini-Map
- SOS Overlay

Output:
  src/docs/scenario_pack_latest.json
  src/docs/scenario_pack_<timestamp>.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Try to pull live trust + OSL if available
try:
    from fusion_trust import compute_trust
except Exception:  # pragma: no cover
    compute_trust = None  # type: ignore

try:
    from operator_safety_layer import compute_osl
except Exception:  # pragma: no cover
    compute_osl = None  # type: ignore


BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)

MINIMAP_FILE = BASE / "gui_minimap.json"
SOS_FILE = BASE / "gui_sos_overlay.json"


def _load_json(path: Path, label: str):
    """Safe JSON loader with a small status wrapper."""
    if not path.exists():
        return {
            "status": "no_data",
            "message": f"{label} file not found: {path.name}",
        }

    try:
        return json.loads(path.read_text())
    except Exception as exc:  # pragma: no cover
        return {
            "status": "corrupted",
            "message": f"Failed to parse {path.name}: {exc}",
        }


def build_scenario_pack() -> dict:
    """Assemble a full scenario pack dictionary."""
    now = datetime.now(timezone.utc).isoformat()

    # Fusion Trust
    if compute_trust is not None:
        try:
            trust = compute_trust()
        except Exception as exc:  # pragma: no cover
            trust = {
                "status": "error",
                "message": f"compute_trust() failed: {exc}",
            }
    else:
        trust = {
            "status": "unavailable",
            "message": "fusion_trust module not importable",
        }

    # Operator Safety Layer
    if compute_osl is not None:
        try:
            osl = compute_osl()
        except Exception as exc:  # pragma: no cover
            osl = {
                "status": "error",
                "message": f"compute_osl() failed: {exc}",
            }
    else:
        osl = {
            "status": "unavailable",
            "message": "operator_safety_layer module not importable",
        }

    # Mini-map + SOS snapshots (from files)
    minimap = _load_json(MINIMAP_FILE, "GUI minimap")
    sos = _load_json(SOS_FILE, "SOS overlay")

    pack = {
        "generated_at": now,
        "base_dir": str(BASE),
        "fusion_trust": trust,
        "operator_safety_layer": osl,
        "minimap": minimap,
        "sos_overlay": sos,
    }

    return pack


def write_scenario_pack() -> dict:
    """Write scenario pack to docs and return a small metadata dict."""
    pack = build_scenario_pack()

    # Timestamped file
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    ts_file = DOCS_DIR / f"scenario_pack_{ts}.json"

    # Stable "latest" file
    latest_file = DOCS_DIR / "scenario_pack_latest.json"

    payload = json.dumps(pack, indent=2)
    ts_file.write_text(payload)
    latest_file.write_text(payload)

    return {
        "status": "ok",
        "latest_path": str(latest_file),
        "timestamped_path": str(ts_file),
    }


if __name__ == "__main__":
    out = write_scenario_pack()
    print("=== Scenario Pack Builder ===")
    print(f"Latest:     {out['latest_path']}")
    print(f"Timestamped:{out['timestamped_path']}")

