"""
mission_brief_html.py — HTML wrapper for Daily Mission Brief (v4)

Reads the text brief, injects into an HTML template, and adds:
- GLL readiness JSON
- System integrity JSON

Template path (if exists):
  docs/mission_brief_template.html

Placeholders expected (but safe if missing):
  {{BRIEF_TEXT}}
  {{GLL_READINESS}}
  {{SYSTEM_INTEGRITY}}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from daily_mission_brief import write_daily_brief
from gll_readiness import compute_gll_readiness
from system_integrity import compute_system_integrity


SRC = Path(__file__).resolve().parent
DOCS = SRC / "docs"
DEFAULT_TEMPLATE = """<html>
<head>
  <title>Daily Mission Brief — Ghost Lantern Labs</title>
  <meta charset="utf-8" />
</head>
<body>
  <h1>Mission Brief — Ghost Lantern Labs</h1>
  <pre>{{BRIEF_TEXT}}</pre>

  <h2>GLL Readiness</h2>
  <pre>{{GLL_READINESS}}</pre>

  <h2>System Integrity</h2>
  <pre>{{SYSTEM_INTEGRITY}}</pre>
</body>
</html>
"""


def _load_template() -> str:
    tpl = DOCS / "mission_brief_template.html"
    if tpl.exists():
        return tpl.read_text()
    return DEFAULT_TEMPLATE


def write_html_brief(path: str | Path = "docs/daily_mission_brief.html") -> str:
    DOCS.mkdir(parents=True, exist_ok=True)

    # Ensure text brief is up to date
    txt_path = write_daily_brief()
    brief_text = Path(txt_path).read_text()

    # Compute JSON blocks
    gll = compute_gll_readiness()
    integ = compute_system_integrity()

    html = _load_template()
    html = html.replace("{{BRIEF_TEXT}}", brief_text)
    html = html.replace("{{GLL_READINESS}}", json.dumps(gll, indent=2))
    html = html.replace("{{SYSTEM_INTEGRITY}}", json.dumps(integ, indent=2))

    out = DOCS / Path(path).name
    out.write_text(html)
    return str(out)


if __name__ == "__main__":
    print(write_html_brief())

