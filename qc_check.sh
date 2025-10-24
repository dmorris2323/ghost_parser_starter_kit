#!/usr/bin/env bash
# qc_check.sh — quick CSV checker for selected Station IDs
# Usage:
#   ./qc_check.sh PS940 PS941 PS942 PS943
# Or:
#   ./qc_check.sh -f ids.txt   # file with one ID per line

set -euo pipefail

CSV="outputs/parsed.csv"

usage() {
  echo "Usage: $0 ID [ID ...] | -f ids_file" >&2
  exit 1
}

# --- parse args ---
IDS=()
if [[ $# -eq 0 ]]; then
  usage
fi

if [[ "$1" == "-f" ]]; then
  [[ $# -eq 2 ]] || usage
  [[ -f "$2" ]] || { echo "IDs file not found: $2" >&2; exit 1; }
  # Read IDs from file (one per line)
  while IFS= read -r line; do
    [[ -n "$line" ]] && IDS+=("$line")
  done < "$2"
else
  # IDs from CLI
  for arg in "$@"; do
    IDS+=("$arg")
  done
fi

# --- sanity checks ---
[[ -f "$CSV" ]] || { echo "CSV not found: $CSV. Run the parser first."; exit 1; }

# --- build an AWK condition like: $2=="PS940"||$2=="PS941"...
COND=""
for id in "${IDS[@]}"; do
  [[ -n "$COND" ]] && COND+="||"
  # escape double quotes inside id if any
  safe_id=${id//\"/\\\"}
  COND+='($2=="'"$safe_id"'")'
done

# --- run awk ---
# Assumes CSV columns: 1=DateTime, 2=Station, ..., 8=Flagged, 9=Reasons
awk -F',' '
BEGIN { OFS=" " }
NR==1 { next } # skip header if present
'"$COND"' {
  print "Station=" $2, "Flagged=" $8, "Reasons=" $9
}
' "$CSV"

