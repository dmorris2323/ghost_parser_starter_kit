"""
day62_ops_cli.py — Day 62 Ops Console for Ghost Lantern Labs

Provides a small, safe menu to exercise:
  - Golden Dome drift
  - Reliability trendline
  - Owl confidence estimator
  - Crisis Mode flag
  - Operator identity

This DOES NOT touch or depend on your main ghost_cli.py.
"""

import sys
from pathlib import Path

from golden_dome_drift import write_drift
from reliability_trend import compute_trend, update_log
from crisis_mode_flag import enable as crisis_on, disable as crisis_off, status as crisis_status
from operator_identity import get_identity, set_identity
from spectral_owl.owl_confidence import compute_confidence


def print_menu():
    print("\n=== Day 62 — GLL Ops Console ===")
    print(" 1) Golden Dome Drift Report")
    print(" 2) Show Reliability Trend (last 5 snapshots)")
    print(" 3) Append Fake Reliability Snapshot (demo)")
    print(" 4) Crisis Mode Status")
    print(" 5) Toggle Crisis Mode")
    print(" 6) Show Operator Identity")
    print(" 7) Set Operator Identity")
    print(" 8) Test Owl Confidence Model")
    print(" 9) Exit")
    print("===============================\n")


def do_drift():
    path = write_drift()
    print(f"Golden Dome drift report written to: {path}")
    if Path(path).exists():
        print(Path(path).read_text())


def do_trend():
    trend = compute_trend()
    print(trend)


def do_append_fake_trend():
    fake = {
        "optical": 92,
        "seismic": 88,
        "ems": 95,
        "radiation": 97,
    }
    path = update_log(fake)
    print(f"Appended fake snapshot to: {path}")
    print("Recent trend:", compute_trend())


def do_crisis_status():
    print("Crisis Mode:", crisis_status())


def do_crisis_toggle():
    current = crisis_status()
    print("Current Crisis Mode:", current)
    choice = input("Turn ON or OFF? ").strip().lower()
    if choice == "on":
        print(crisis_on())
    elif choice == "off":
        print(crisis_off())
    else:
        print("Invalid choice. Use 'on' or 'off'.")


def do_show_operator():
    print("Operator:", get_identity())


def do_set_operator():
    name = input("Enter operator name (e.g., Ghost): ").strip()
    print(set_identity(name))


def do_confidence_test():
    print("Testing Owl confidence model with sample summary…")
    sample = {
        "critical_alerts": 1,
        "warning_alerts": 4,
        "avg_reliability": 92.0,
    }
    print("Input summary:", sample)
    print("Computed confidence:", compute_confidence(sample))


def main():
    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            do_drift()
        elif choice == "2":
            do_trend()
        elif choice == "3":
            do_append_fake_trend()
        elif choice == "4":
            do_crisis_status()
        elif choice == "5":
            do_crisis_toggle()
        elif choice == "6":
            do_show_operator()
        elif choice == "7":
            do_set_operator()
        elif choice == "8":
            do_confidence_test()
        elif choice == "9":
            print("Exiting Day 62 Ops Console.")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

