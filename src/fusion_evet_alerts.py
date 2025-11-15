import pandas as pd

def fusion_alerts(file="commander_extract.csv"):
    df = pd.read_csv(file)
    critical_events = df[df["Confidence_Level"].str.lower() == "critical"]

    if len(critical_events) > 0:
        print("🚨 ALERT: Critical events detected!")
        critical_events.to_csv("critical_alerts.csv", index=False)
        print(f"{len(critical_events)} event(s) saved to critical_alerts.csv")
    else:
        print("✅ No critical events today — system nominal.")
    return len(critical_events)

if __name__ == "__main__":
    fusion_alerts()

