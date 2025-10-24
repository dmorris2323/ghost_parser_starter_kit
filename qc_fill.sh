#!/usr/bin/env bash
# qc_fill.sh — append a completed Day 5 QC block to QC_LOG.txt
# Usage:  ./qc_fill.sh

set -euo pipefail

CSV="outputs/parsed.csv"
QCLOG="QC_LOG.txt"

# Ensure the latest parser output exists
if [ ! -f "$CSV" ]; then
  echo "CSV not found: $CSV. Run the parser first." >&2
  exit 1
fi

# Build a simple "ID,Flagged" list from the CSV (skip header if present)
FLAGS_FILE="$(mktemp)"
trap 'rm -f "$FLAGS_FILE"' EXIT
awk -F',' 'NR>1 && $2!="" {print $2","$8}' "$CSV" > "$FLAGS_FILE"

actual_for () {
  # Return Actual = Flag | No Flag | Skip for a given Station ID
  local id="$1"
  if grep -q "^${id}," "$FLAGS_FILE"; then
    local flag
    flag="$(grep "^${id}," "$FLAGS_FILE" | tail -n1 | cut -d',' -f2)"
    if [ "$flag" = "True" ]; then
      echo "Flag"
    else
      echo "No Flag"
    fi
  else
    echo "Skip"
  fi
}

# Compute Actuals
A940="$(actual_for PS940)"
A941="$(actual_for PS941)"   # should be Skip (bad data)
A942="$(actual_for PS942)"
A943="$(actual_for PS943)"

# Garbage line check: literal bad line must NOT appear in CSV
# (If not found, treat as Skip)
if grep -Fq "Bad Line That Makes No Sense" "$CSV"; then
  AGARBAGE="(unexpected)"
else
  AGARBAGE="Skip"
fi

# Expected outcomes for Day 5 drill
E940="Flag"
E941="Skip"
E942="Flag"
EGARBAGE="Skip"
E943="No Flag"

note() { [ "$1" = "$2" ] && echo "OK" || echo "CHECK"; }

N940="$(note "$A940" "$E940")"
N941="$(note "$A941" "$E941")"
N942="$(note "$A942" "$E942")"
NGARBAGE="$(note "$AGARBAGE" "$EGARBAGE")"
N943="$(note "$A943" "$E943")"

# Compose the finished Day 5 block
BLOCK="$(cat <<'EOF'
Day 5 QC (2025-10-10) — Autofill

| Event ID | Condition             | Expected | Actual   | Notes  |
|----------|-----------------------|----------|----------|--------|
| PS940    | Valid inside AOI      | Flag     | __A940__ | __N940__ |
| PS941    | Bad data (???/BAD)    | Skip     | __A941__ | __N941__ |
| PS942    | Valid inside AOI      | Flag     | __A942__ | __N942__ |
| (garbage)| Wrong format          | Skip     | __AGARB__| __NGARB__ |
| PS943    | Mag <3.5              | No Flag  | __A943__ | __N943__ |
EOF
)"

# Fill placeholders
BLOCK="${BLOCK/__A940__/$A940}"
BLOCK="${BLOCK/__N940__/$N940}"
BLOCK="${BLOCK/__A941__/$A941}"
BLOCK="${BLOCK/__N941__/$N941}"
BLOCK="${BLOCK/__A942__/$A942}"
BLOCK="${BLOCK/__N942__/$N942}"
BLOCK="${BLOCK/__AGARB__/$AGARBAGE}"
BLOCK="${BLOCK/__NGARB__/$NGARBAGE}"
BLOCK="${BLOCK/__A943__/$A943}"
BLOCK="${BLOCK/__N943__/$N943}"

# Show preview and append
echo "---- Preview ----"
echo "$BLOCK"
echo "-----------------"
echo "$BLOCK" >> "$QCLOG"
echo "Appended completed Day 5 QC block to $QCLOG"

