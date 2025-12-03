"""
mission_brief_html.py

Convert the text Daily Mission Brief into an HTML file for GUI / browser viewing.
"""

from __future__ import annotations

import html
from pathlib import Path
from datetime import datetime

from daily_mission_brief import build_mission_brief, write_daily_brief
from profile_config import get_active_profile

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ghost Lantern Labs – Daily Mission Brief</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background-color: #050711;
      color: #e5e7eb;
      margin: 0;
      padding: 20px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: #0b1020;
      border-radius: 12px;
      padding: 20px 24px;
      box-shadow: 0 15px 35px rgba(0,0,0,0.6);
      border: 1px solid #1f2933;
    }}
    h1 {{
      margin-top: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 1.6rem;
    }}
    .badge {{
      background: linear-gradient(135deg, #06b6d4, #3b82f6);
      color: #0b1020;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
    }}
    .meta {{
      font-size: 0.8rem;
      color: #9ca3af;
      margin-bottom: 12px;
    }}
    pre {{
      background: #020617;
      padding: 16px;
      border-radius: 10px;
      overflow-x: auto;
      font-size: 0.80rem;
      line-height: 1.4;
      border: 1px solid #1e293b;
    }}
    a {{
      color: #60a5fa;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>
      <span>Ghost Lantern Labs – Daily Mission Brief</span>
      <span class="badge">Profile: {profile}</span>
    </h1>
    <div class="meta">
      Generated: {timestamp}
    </div>
    <pre>{brief}</pre>
  </div>
</body>
</html>
"""


def build_html_brief() -> str:
    text_brief = build_mission_brief()
    escaped = html.escape(text_brief)
    profile = get_active_profile()
    profile_name = getattr(profile, "display_name", getattr(profile, "key", "UNKNOWN_PROFILE"))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return HTML_TEMPLATE.format(
        profile=html.escape(str(profile_name)),
        timestamp=html.escape(ts),
        brief=escaped,
    )


def write_html_brief(path: Path | None = None) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    if path is None:
        path = DOCS_DIR / "daily_mission_brief.html"

    html_text = build_html_brief()
    path.write_text(html_text, encoding="utf-8")
    return path


if __name__ == "__main__":
    # Make sure text brief exists too
    write_daily_brief()
    out = write_html_brief()
    print(f"[OK] HTML mission brief written → {out}")

