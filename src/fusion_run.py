import pandas as pd
from pathlib import Path

# Import your existing modules
import sum_of_all_fears_sim as sim
from fusion_scoring import score_fusion
from commander_extract import commander_extract
from fusion_alerts import fusion_alerts


def fusion_run(events=10):
    print("=== GLL Fusion Run: START ===")

    # 1) Simulate telemetry
    print("[1/4] Generating simulated telemetry...")
    df_sim = sim.simulate_event_series(events=events)
    print(f"    -> sum_fears_sim.csv written with {len(df_sim)} events")

    # 2) Score fusion
    print("[2/4] Scoring fusion output...")
    df_scored_head = score_fusion("sum_fears_sim.csv")
    print("    -> scored_output.csv written")
    print("    HEAD:\n", df_scored_head)

    # 3) Commander Extract
    print("[3/4] Building commander_extract.csv...")
    brief = commander_extract("scored_output.csv")
    if brief is not None:
        print("    -> commander_extract.csv written")
        print("    BRIEF HEAD:\n", brief)
    else:
        print("    !! commander_extract returned None")

    # 4) Fusion Alerts
    print("[4/4] Running fusion alerts...")
    num_crit = fusion_alerts("commander_extract.csv")
    if num_crit > 0:
        print(f"🚨 {num_crit} Critical event(s) flagged in critical_alerts.csv")
    else:
        print("✅ No Critical events today — system nominal.")

    print("=== GLL Fusion Run: COMPLETE ===")
    return num_crit


if __name__ == "__main__":
    fusion_run()

