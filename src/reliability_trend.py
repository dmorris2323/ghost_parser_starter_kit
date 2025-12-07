"""
reliability_trend.py — Log and inspect recent sensor reliability snapshots.

Log file:
    data/sensor_reliability_log.csv

Each entry:
    optical,seismic,ems,radiation

Functions:
    update_log(scores: dict)
    compute_trend() -> dict
"""

from pathlib import Path
import csv

LOG_FILE = Path("data/sensor_reliability_log.csv")


def update_log(scores: dict) -> str:
    """
    Append a reliability snapshot to the CSV log.
    scores should contain keys: optical, seismic, ems, radiation.
    Missing keys default to 0.
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "optical": scores.get("optical", 0),
        "seismic": scores.get("seismic", 0),
        "ems": scores.get("ems", 0),
        "radiation": scores.get("radiation", 0),
    }

    write_header = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return str(LOG_FILE)


def compute_trend() -> dict:
    """
    Return the last up-to-5 reliability snapshots.
    """
    if not LOG_FILE.exists():
        return {
            "status": "no_data",
            "message": f"{LOG_FILE} not found",
            "recent": [],
        }

    with LOG_FILE.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    recent = rows[-5:] if len(rows) > 5 else rows
    return {
        "status": "ok",
        "total_entries": len(rows),
        "recent": recent,
    }


if __name__ == "__main__":
    # Simple manual test: append a fake snapshot and print last 5
    update_log({"optical": 92, "seismic": 88, "ems": 95, "radiation": 97})
    print(compute_trend())

