"""
mission_brief_html.py
"""

from pathlib import Path
from datetime import datetime
from profile_config import get_active_profile
from sensor_reliability import build_reliability_table

TEMPLATE = """
<html>
<head>
<title>Daily Mission Brief</title>
<style>
.bar {{
  height: 12px;
  background: #4caf50;
}}
</style>
</head>

<body>
<h1>Daily Mission Brief — {timestamp}</h1>
<h3>Active Profile: {profile}</h3>

<h2>Sensor Reliability</h2>
{reliability_rows}

</body>
</html>
"""

def build_html_brief():
    profile = get_active_profile()
    rows = []

    for r in build_reliability_table():
        pct = r['score']
        rows.append(f"{r['sensor'].upper()} — {pct}%<br><div class='bar' style='width:{pct}%;'></div><br>")

    html = TEMPLATE.format(
        timestamp=datetime.utcnow().isoformat() + "Z",
        profile=profile.display_name,
        reliability_rows="\n".join(rows),
    )
    return html

def write_daily_brief():
    out_path = Path(__file__).parent / "docs" / "daily_mission_brief.html"
    out_path.write_text(build_html_brief(), encoding="utf-8")
    return out_path

if __name__ == "__main__":
    print(write_daily_brief())

