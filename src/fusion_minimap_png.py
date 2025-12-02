"""
fusion_minimap_png.py — Visual Mini-Map (PNG)
---------------------------------------------

Reads:
    minimap.txt (built by fusion_minimap.py)
Outputs:
    minimap.png (visual summary for demos & GUI)
"""

import matplotlib.pyplot as plt
from pathlib import Path

MINIMAP_TXT = Path(__file__).parent / "minimap.txt"
OUTPUT_PNG = Path(__file__).parent / "minimap.png"


def parse_minimap():
    """Parse minimap.txt into a structured dict."""
    if not MINIMAP_TXT.exists():
        return {"status": "error", "details": "minimap.txt not found"}

    lines = MINIMAP_TXT.read_text().splitlines()
    zones = {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith("="):
            continue

        # Example:
        # [NK_COAST]   ✔️  C:1  W:0  S:3
        if line.startswith("[") and "]" in line:
            zone = line.split("]")[0].replace("[", "")
            parts = line.split("]")
            metrics = parts[1].strip().split()

            c = int(metrics[1].replace("C:", ""))
            w = int(metrics[2].replace("W:", ""))
            s = int(metrics[3].replace("S:", ""))

            zones[zone] = {"critical": c, "warning": w, "stable": s}

    return {"status": "ok", "zones": zones}


def build_png(zones):
    labels = []
    critical = []
    warning = []
    stable = []

    for z, m in zones.items():
        labels.append(z)
        critical.append(m["critical"])
        warning.append(m["warning"])
        stable.append(m["stable"])

    # 3-bar stacked map per AOI
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, stable, label="Stable", color="#4CAF50")
    ax.bar(labels, warning, bottom=stable, label="Warning", color="#FFC107")
    ax.bar(labels, critical,
           bottom=[stable[i] + warning[i] for i in range(len(stable))],
           label="Critical",
           color="#F44336")

    ax.set_title("Ghost Lantern Labs — Sensor Fusion Mini-Map")
    ax.set_ylabel("Event Count")
    ax.legend()

    plt.tight_layout()
    fig.savefig(OUTPUT_PNG)
    plt.close(fig)

    return OUTPUT_PNG


def main():
    data = parse_minimap()
    if data.get("status") != "ok":
        return data

    out = build_png(data["zones"])
    return {
        "status": "ok",
        "file": str(out),
        "zones": data["zones"]
    }


if __name__ == "__main__":
    print(main())

