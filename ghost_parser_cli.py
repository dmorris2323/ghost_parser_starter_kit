import argparse
import pandas as pd
from src.qa_validator import validate_parsed

def parse_logs(log_path):
    """Read a simple log file into a DataFrame."""
    rows = []
    with open(log_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            # Simple example structure
            row = {
                "Time": parts[0],
                "Mag": float(parts[1]) if parts[1].replace('.', '', 1).isdigit() else 0.0,
                "Lat": float(parts[2]) if len(parts) > 2 else None,
                "Lon": float(parts[3]) if len(parts) > 3 else None,
            }
            rows.append(row)
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(description="Ghost Parser CLI")
    parser.add_argument("logfile", help="Path to the log file")
    parser.add_argument("--aoi", help="Path to AOI JSON (optional)")
    parser.add_argument("-o", "--output", help="Output file name", default="parsed_output.jsonl")
    args = parser.parse_args()

    # Step 1: Parse logs
    df = parse_logs(args.logfile)
    print("Parsed events:", len(df))

    # Step 2: Run QA Validator
    qa = validate_parsed(df)
    print("QA Summary:", qa)

    # Step 3: Save to file
    df.to_json(args.output, orient="records", lines=True)
    print(f"Saved output to {args.output}")

if __name__ == "__main__":
    main()

