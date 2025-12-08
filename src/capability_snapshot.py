import json
from pathlib import Path
from datetime import datetime


def load_json_safe(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def build_capability_snapshot():
    BASE = Path(__file__).resolve().parent

    # Load submodules safely
    try:
        from fusion_trust import compute_trust
        fusion_trust = compute_trust()
    except Exception:
        fusion_trust = {"status": "unavailable"}

    try:
        from operator_safety_layer import compute_osl
        osl = compute_osl()
    except Exception:
        osl = {"status": "unavailable"}

    try:
        from sensor_latency import compute_latency_report
        latency = compute_latency_report()
    except Exception:
        latency = {"status": "unavailable"}

    try:
        from sensor_reliability import compute_reliability_all
        reliability = compute_reliability_all()
    except Exception:
        reliability = {"status": "unavailable"}

    try:
        from golden_dome_drift import compute_drift
        drift = compute_drift()
    except Exception:
        drift = {"status": "unavailable"}

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

    snapshot = {
        "timestamp": ts,
        "fusion_trust": fusion_trust,
        "operator_safety_layer": osl,
        "latency": latency,
        "reliability": reliability,
        "drift": drift,
    }

    return snapshot


def write_snapshot():
    SNAP_DIR = Path(__file__).resolve().parent / "docs"
    SNAP_DIR.mkdir(exist_ok=True)

    snap = build_capability_snapshot()

    latest_path = SNAP_DIR / "capability_snapshot_latest.json"
    ts_name = datetime.utcnow().strftime("capability_snapshot_%Y%m%dT%H%M%SZ.json")
    ts_path = SNAP_DIR / ts_name

    latest_path.write_text(json.dumps(snap, indent=2))
    ts_path.write_text(json.dumps(snap, indent=2))

    # Markdown export for humans
    md_path = SNAP_DIR / "capability_snapshot_latest.md"
    md = (
        "# Ghost Lantern Labs — Capability Snapshot\n"
        f"**Generated:** {snap['timestamp']}\n\n"
        "## Fusion Trust Score\n"
        f"```\n{json.dumps(snap['fusion_trust'], indent=2)}\n```\n\n"
        "## Operator Safety Layer\n"
        f"```\n{json.dumps(snap['operator_safety_layer'], indent=2)}\n```\n\n"
        "## Sensor Reliability\n"
        f"```\n{json.dumps(snap['reliability'], indent=2)}\n```\n\n"
        "## Sensor Latency\n"
        f"```\n{json.dumps(snap['latency'], indent=2)}\n```\n\n"
        "## Golden Dome Drift\n"
        f"```\n{json.dumps(snap['drift'], indent=2)}\n```\n"
    )
    md_path.write_text(md)

    return {
        "latest": str(latest_path),
        "timestamped": str(ts_path),
        "markdown": str(md_path),
    }


if __name__ == "__main__":
    out = write_snapshot()
    print("=== Capability Snapshot Generated ===")
    print(json.dumps(out, indent=2))

