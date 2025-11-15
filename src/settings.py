from pathlib import Path

# Base directory for the src folder
BASE_DIR = Path(__file__).resolve().parent

# Where we keep our core CSV data files (for now, same as BASE_DIR)
DATA_DIR = BASE_DIR

# Core pipeline files
FUSED_FILE = DATA_DIR / "fused_output.csv"
SCORED_FILE = DATA_DIR / "scored_output.csv"
COMMANDER_FILE = DATA_DIR / "commander_extract.csv"
HEATMAP_FILE = DATA_DIR / "heatmap_data.csv"

# Log file (ops log)
OPS_LOG_FILE = BASE_DIR / "fusion_ops_log.csv"

# Daily report file
DAILY_REPORT_FILE = BASE_DIR / "daily_report.txt"

