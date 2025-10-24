#!/bin/bash
# Quick QC check script for Day 2+ drills

echo "🔍 Checking QC_LOG.txt..."

# Check that all 5 Day-2 test IDs are present
for id in PS921 PS922 PS923 PS924 PS925; do
  if grep -q "$id" QC_LOG.txt; then
    echo "$id found ✅"
  else
    echo "Missing $id ❌"
  fi
done

# Check for blanks ("____")
if grep -q '____' QC_LOG.txt; then
  echo "⚠️  You still have blanks (____) to fill in QC_LOG.txt"
else
  echo "✅ QC_LOG looks filled"
fi

