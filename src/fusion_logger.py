from datetime import datetime
import csv, os

LOG_FILE = "fusion_ops_log.csv"

def log_event(module, status, note=""):
    """Append operational event to fusion log."""
    ts = datetime.utcnow().isoformat()
    header = ["timestamp", "module", "status", "note"]
    exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        writer.writerow([ts, module, status, note])
    print(f"📝 Logged: {module} | {status} | {note}")

if __name__ == "__main__":
    log_event("fusion_logger", "initialized", "Day38 test entry")

