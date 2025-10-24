#!/bin/bash
# qc_audit.sh — Compare QC_LOG Expected vs. Actual parser output (Flagged/Reasons)

set -u

CSV="outputs/parsed.csv"
LOG="QC_LOG.txt"

if [[ ! -f "$CSV" ]]; then
  echo "❌ Missing $CSV — run the parser first."
  exit 1
fi
if [[ ! -f "$LOG" ]]; then
  echo "❌ Missing $LOG — create/fill your QC_LOG.txt first."
  exit 1
fi

trim() { sed -E 's/^[[:space:]]+|[[:space:]]+$//g'; }

echo "🔎 QC AUDIT ($(date))"
echo "CSV: $CSV"
echo "LOG: $LOG"
echo

printf "%-8s | %-28s | %-9s | %-9s | %s\n" "Station" "Condition" "Expected" "Actual" "Reasons"
printf -- "%s\n" "-----------------------------------------------------------------------------------------------"

# Parse each row in QC_LOG.txt that looks like a table row with a Station ID
# Expected QC_LOG row format (markdown table):
# | PS921    | Condition text ... | Expected | Actual | Notes |
grep -E '^\|' "$LOG" | grep -E 'PS[0-9]+' | while IFS= read -r line; do
  # Split markdown columns on '|'
  # Fields: 1(empty) | 2(Station) | 3(Condition) | 4(Expected) | 5(Actual user entry) | 6(Notes) | 7(empty)
  station=$(echo "$line"   | awk -F'\\|' '{print $2}' | tr -d '|' | trim)
  cond=$(   echo "$line"   | awk -F'\\|' '{print $3}' | tr -d '|' | trim)
  expected=$(echo "$line"  | awk -F'\\|' '{print $4}' | tr -d '|' | trim)

  # Pull Actual from parsed.csv (columns: DateTime,Station,Mag,Depth_km,Lat,Lon,Type,Flagged,Reasons)
  row=$(awk -F',' -v ST="$station" '$2==ST{print $8","$9; found=1} END{if(!found) print "NA,NA"}' "$CSV")
  actual_flag=${row%%,*}
  reasons=${row#*,}

  # Normalize expected text (Flag/No Flag -> True/False)
  exp_norm=$(echo "$expected" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]+//g')
  exp_bool="NA"
  if [[ "$exp_norm" == "flag" ]]; then exp_bool="True"; fi
  if [[ "$exp_norm" == "noflag" || "$exp_norm" == "noflag/" ]]; then exp_bool="False"; fi

  status="OK"
  if [[ "$exp_bool" != "NA" && "$actual_flag" != "$exp_bool" ]]; then
    status="MISMATCH"
  fi

  printf "%-8s | %-28s | %-9s | %-9s | %s\n" "$station" "$(echo "$cond" | cut -c1-28)" "$expected" "$actual_flag ($status)" "$reasons"
done

