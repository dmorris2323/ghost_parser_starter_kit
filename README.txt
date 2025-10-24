PARSER STARTER KIT — QUICKSTART

FILES
- parse_triage.py  -> the script
- raw.log          -> sample input
- aoi.json         -> optional AOI box for flagging
- outputs/         -> will be created on first run

REQUIREMENTS
- Python 3.9+ (3.11 recommended). No extra libraries needed.

RUN (from inside this folder)
  Windows (PowerShell):
    python .\parse_triage.py --in raw.log --out-csv outputs\parsed.csv --out-json outputs\parsed.jsonl --aoi aoi.json

  macOS / Linux (Terminal):
    python3 ./parse_triage.py --in raw.log --out-csv outputs/parsed.csv --out-json outputs/parsed.jsonl --aoi aoi.json

RESULTS
- outputs/parsed.csv  (open in Excel)
- outputs/parsed.jsonl
- You should see 'Flagged: 2' for the provided sample.

TIPS
- Edit raw.log to add your own synthetic lines (do NOT use real/classified data).
- If Python isn't found, install from https://www.python.org and re-open your terminal.
