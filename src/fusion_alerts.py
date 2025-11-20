import pandas as pd
from pathlib import Path

from fusion_logger import log_event
from settings import COMMANDER_FILE
from validators import (
    validate_required_columns,
    validate_row_integrity,
)
from error_handler import safe_run


def fusion_alerts(
    commander_file: Path | str = COMMANDER_FILE,
):
    """
    Scan commander_extract.csv for Critical events.
    If found, write critical_alerts.csv and print an alert.

    Output:
      - critical_alerts.csv (if any Critical present)
    """

    path = Path(commander_file)

    # 1) Check commander file exists
    if not path.exists():
        msg = f"Commander file not found: {path.resolve()}"
        print(f"❌ {msg}")
        log_event("fusion_alerts", "error", msg)
        return 0

    # 2) Load data
    df = pd.read_csv(path)

    # 3) Validate structure (no nulls)
    if not validate_row_integrity(df, "fusion_alerts"):
        return 0

    # 4) Ensure Confidence_Level is present
    if not validate_required_columns(df, ["Confidence_Level"], "fusion_alerts"):
        return 0

    # 5) Filter Critical events
    crit_mask = df["Confidence_Level"].astype(str).str.lower() == "critical"
    critical_events = df[crit_mask].copy()

    if len(critical_events) > 0:
        out_path = path.with_name("critical_alerts.csv")
        critical_events.to_csv(out_path, index=False)
        print("🚨 ALERT: Critical events detected!")
        print(f"{len(critical_events)} event(s) saved to {out_path.name}")
        log_event(
            "fusion_alerts",
            "completed",
            f"{len(critical_events)} critical events -> {out_path.name}",
        )
    else:
        print("✅ No critical events today — system nominal.")
        log_event("fusion_alerts", "completed", "No critical events")

    return len(critical_events)


if __name__ == "__main__":
    safe_run("fusion_alerts", fusion_alerts)

