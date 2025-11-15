import csv
from fusion_logger import LOG_FILE, log_event

def check_for_alerts():
    alerts = []
    try:
        with open(LOG_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"].lower() == "error":
                    alerts.append(row)
        if alerts:
            print("🚨 ALERT: Detected issues in system logs.")
            for a in alerts:
                print(f"[{a['timestamp']}] {a['module']} - {a['note']}")
            log_event("fusion_alerts", "alert_triggered", f"{len(alerts)} active errors")
        else:
            print("✅ No active alerts. System nominal.")
            log_event("fusion_alerts", "check_complete", "All systems nominal")
    except FileNotFoundError:
        print("⚠️ No log file found.")
        log_event("fusion_alerts", "no_log_file", "")
    except Exception as e:
        log_event("fusion_alerts", "error", str(e))
        raise

if __name__ == "__main__":
    check_for_alerts()

