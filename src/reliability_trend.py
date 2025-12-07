import csv
from pathlib import Path

FILE = Path("data/sensor_reliability_log.csv")

def update_log(scores: dict):
    FILE.parent.mkdir(exist_ok=True)
    new = {
        "optical": scores.get("optical", 0),
        "seismic": scores.get("seismic", 0),
        "ems": scores.get("ems", 0),
        "radiation": scores.get("radiation", 0),
    }
    write_header = not FILE.exists()
    with open(FILE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=new.keys())
        if write_header:
            w.writeheader()
        w.writerow(new)

def compute_trend():
    if not FILE.exists():
        return {"trend": "no_data"}
    rows = list(csv.DictReader(FILE.open()))
    return rows[-5:]  # last 5 entries

if __name__ == "__main__":
    print(compute_trend())

