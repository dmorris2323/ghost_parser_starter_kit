"""
mission_brief_html.py
---------------------

Converts the daily mission brief text into a simple HTML report.

 - Reads:  docs/daily_mission_brief.txt  (builds it if missing)
 - Builds/reads: minimap.txt via fusion_minimap.build_minimap()
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
from daily_mission_brief import write_daily_brief
from fusion_minimap import build_minimap

# Paths (relative to src/)
TXT_PATH = Path("docs/daily_mission_brief.txt")
HTML_PATH = Path("docs/daily_mission_brief.html")
MINIMAP_PATH = Path("minimap.txt")


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

    # Build one via daily_mission_brief
    write_daily_brief()
    return TXT_PATH.read_text(encoding="utf-8")


def _build_and_load_minimap() -> str:
    """
    Build the fusion mini-map (writes minimap.txt) and return its text.
    If anything fails, return a human-readable error string instead of crashing.
    """
    try:
        build_minimap()
    except Exception as e:
        return f"Mini-map build error: {e}"

    if not MINIMAP_PATH.exists():
        return "Mini-map not available (minimap.txt not found)."

    try:
        return MINIMAP_PATH.read_text(encoding="utf-8")
    except Exception as e:
        return f"Mini-map read error: {e}"


def build_html_brief() -> str:
    """
    Construct the HTML document string.
    """

    text_brief = _load_or_build_text_brief()
    minimap_text = _build_and_load_minimap()
    profile_name = _get_profile_display_name()

    # Escape text for safe <pre>
    escaped_text = html.escape(text_brief)
    escaped_minimap = html.escape(minimap_text)

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
    .grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 16px;
    }}
    .panel {{
      background: #0f1117;
      padding: 16px 18px;
      border-radius: 8px;
      border: 1px solid #202337;
    }}
    .panel h2 {{
      font-size: 1rem;
      margin-top: 0;
      margin-bottom: 8px;
      color: #d9e2ec;
    }}
    pre {{
      margin: 0;
      font-size: 0.84rem;
      line-height: 1.4;
      overflow-x: auto;
      white-space: pre;
    }}
    @media (max-width: 800px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
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
      Operator view — fused system, sensor readiness, AOI mini-map, and profile context.
    </div>

    <div class="grid">
      <div class="panel">
        <h2>Core Mission Brief</h2>
        <pre>{escaped_text}</pre>
      </div>
      <div class="panel">
        <h2>Fusion Mini-Map</h2>
        <pre>{escaped_minimap}</pre>
      </div>
    </div>
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

