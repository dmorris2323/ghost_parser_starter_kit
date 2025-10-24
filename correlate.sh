#!/bin/bash
# correlate.sh — quick delta + verdict for radar/seismic pairs
# Usage:
#   ./correlate.sh LAT1 LON1 LAT2 LON2 TIME1 TIME2 [MAX_DEG=0.5] [MAX_MIN=10]
# Example:
#   ./correlate.sh 40.200 129.200 40.500 129.400 14:15 14:20
#   ./correlate.sh 40.200 129.200 40.500 129.400 14:15 14:20 0.4 8

if [ $# -lt 6 ]; then
  echo "Usage: $0 lat1 lon1 lat2 lon2 time1 time2 [max_deg=0.5] [max_min=10]"
  exit 1
fi

lat1="$1"; lon1="$2"; lat2="$3"; lon2="$4"; t1="$5"; t2="$6"
max_deg="${7:-0.5}"     # default 0.5 degree threshold for both lat and lon
max_min="${8:-10}"      # default 10 minutes

# absolute deltas for lat/lon
dlat=$(awk -v a="$lat1" -v b="$lat2" 'BEGIN{d=a-b; if(d<0)d*=-1; printf("%.6f", d)}')
dlon=$(awk -v a="$lon1" -v b="$lon2" 'BEGIN{d=a-b; if(d<0)d*=-1; printf("%.6f", d)}')

# delta time in minutes (absolute)
dtime=$(awk -v t1="$t1" -v t2="$t2" '
BEGIN{
  split(t1,a,":"); split(t2,b,":");
  ta=a[1]*60+a[2]; tb=b[1]*60+b[2];
  d=tb-ta; if(d<0)d*=-1;
  print d
}')

# verdicts
loc_ok=$(awk -v x="$dlat" -v y="$dlon" -v m="$max_deg" 'BEGIN{print (x<=m && y<=m) ? "YES" : "NO"}')
time_ok=$(awk -v t="$dtime" -v m="$max_min" 'BEGIN{print (t<=m) ? "YES" : "NO"}')

if [ "$loc_ok" = "YES" ] && [ "$time_ok" = "YES" ]; then
  verdict="Correlates"
else
  verdict="No link"
fi

echo "ΔLat = $dlat, ΔLon = $dlon, ΔTime = ${dtime} min"
echo "Thresholds: <= ${max_deg}° (lat & lon), <= ${max_min} min"
echo "Checks: location=$loc_ok, time=$time_ok"
echo "Verdict: $verdict"

