"""
mission_brief_html.py
---------------------

Converts the daily mission brief text into a simple HTML report.

 - Reads:  docs/daily_mission_brief.txt
 - Writes: docs/daily_mission_brief.html
 - Adds a profile badge based on active profile from profile_config

Intended for:
 - Browser viewing
 - Simple demos
"""

from __future__ import annotations

from pathlib import Path
import html

from profile_config import get_active_profile
from daily_mission_brief import build_daily_brief, write_daily_brief

# Paths (relative to src/)
TXT_PATH = Path("docs/daily_mission_brief.txt")
HTML_PATH = Path("docs/daily_mission_brief.html")


def _get_profile_display_name() -> str:
    """
    Safely derive a human-readable profile name from profile_config.get_active_profile().
    Supports both dict-style and simple-string returns.
    """
    try:
        profile = get_active_profile()
    except Exception:
        return "Unknown"

    # If it is a dict-like object
    try:
        if isinstance(profile, dict):
            return (
                profile.get("display_name")
                or profile.get("name")
                or profile.get("key")
                or "Unknown"
            )
    except Exception:
        pass

    # Fallback: just stringify whatever it is
    try:
        return str(profile)
    except Exception:
        return "Unknown"


def _load_or_build_text_brief() -> str:
    """
    Load the daily mission brief from TXT, or build it if missing.
    """
    if TXT_PATH.exists():
        return TXT_PATH.read_text(encoding="utf-8")

    # If no TXT yet, build one via daily_mission_brief
    # This also writes out TXT_PATH via write_daily_brief().
    write_daily_brief()
    return TXT_PATH.read_text(encoding="utf-8")


def build_html_brief() -> str:
    """
    Construct the HTML document string.
    """

    text_brief = _load_or_build_text_brief()
    profile_name = _get_profile_display_name()

    # Escape text for safe <pre>
    escaped_text = html.escape(text_brief)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GLL Daily Mission Brief</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background-color: #0b0c10;
      color: #e5e5e5;
      margin: 0;
      padding: 20px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: #151720;
      border-radius: 12px;
      padding: 24px 28px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
      border: 1px solid #272a3a;
    }}
    h1 {{
      font-size: 1.6rem;
      margin: 0 0 8px 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.8rem;
      background: #243b53;
      color: #d9e2ec;
      border: 1px solid #486581;
    }}
    .subheader {{
      font-size: 0.9rem;
      color: #9fb3c8;
      margin-bottom: 16px;
    }}
    pre {{
      background: #0f1117;
      padding: 16px 18px;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.84rem;
      line-height: 1.4;
      border: 1px solid #202337;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>
      Ghost Lantern Labs — Daily Mission Brief
      <span class="badge">Profile: {html.escape(profile_name)}</span>
    </h1>
    <div class="subheader">
      Operator view — fused system, sensor readiness, and profile context.
    </div>
    <pre>{escaped_text}</pre>
  </div>
</body>
</html>
"""
    return html_doc


def write_html_brief() -> None:
    """
    Build and save the HTML mission brief.
    """
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    html_doc = build_html_brief()
    HTML_PATH.write_text(html_doc, encoding="utf-8")
    print(f"[OK] HTML mission brief written → {HTML_PATH}")


def main():
    write_html_brief()


if __name__ == "__main__":
    main()

