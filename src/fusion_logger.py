import csv
import os
from datetime import datetime
from settings import OPS_LOG_FILE

# Standard header for all ops logs
HEADER = ["timestamp", "module", "status", "note"]

def log_event(module, status, note=""):
    """
    Append a clean operational log entry to the unified log file.
    Uses OPS_LOG_FILE from settings.py for consistent architecture.
    """

    timestamp = datetime.utcnow().isoformat()
    file_exists = os.path.exists(OPS_LOG_FILE)

    with open(OPS_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        # Write header only once (first run)
        if not file_exists:
            writer.writerow(HEADER)

        # Write actual event
        writer.writerow([timestamp, module, status, note])

    # Console echo for debugging during development
    print(f"📝 Logged: {module} | {status} | {note}")

if __name__ == "__main__":
    log_event("fusion_logger", "initialized", "Self-test")

