"""
mission_brief_html.py

Generates an HTML daily mission brief for Ghost Lantern Labs.

Sources:
  - daily_mission_brief.build_mission_brief()  → core text brief
  - sensor_readiness_brief.build_readiness_brief() → sensor status
  - docs/reliability_report.txt → reliability details (if present)
  - docs/drift_report.txt → drift prediction (if present)

Output:
  - docs/daily_mission_brief.html
"""

from __future__ import annotations

from pathlib import Path

from daily_mission_brief import build_mission_brief
from sensor_readiness_brief import build_readiness_brief

BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Ghost Lantern Labs – Daily Mission Brief</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      padding: 0;
      background: #05050a;
      color: #f5f5f5;
    }}
    .container {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2, h3 {{
      margin-top: 1.2rem;
      margin-bottom: 0.4rem;
    }}
    h1 {{
      font-size: 1.8rem;
    }}
    h2 {{
      font-size: 1.4rem;
      color: #9fd5ff;
    }}
    pre {{
      background: #11131c;
      padding: 12px 16px;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.9rem;
      line-height: 1.4;
    }}
    .section {{
      margin-bottom: 24px;
      border-bottom: 1px solid #222637;
      padding-bottom: 16px;
    }}
    .badge {{
      display: inline-block;
      background: #1e2738;
      color: #9fd5ff;
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 0.75rem;
      margin-left: 8px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Ghost Lantern Labs – Daily Mission Brief<span class="badge">Spectral Owl</span></h1>

    <div class="section">
      <h2>Core Brief</h2>
      <pre>{{CORE_BRIEF}}</pre>
    </div>

    <div class="section">
      <h2>Sensor Readiness Overview</h2>
      <pre>{{SENSOR_READINESS}}</pre>
    </div>

    <div class="section">
      <h2>Sensor Reliability Report</h2>
      <pre>{{RELIABILITY}}</pre>
    </div>

    <div class="section">
      <h2>Sensor Drift Prediction</h2>
      <pre>{{DRIFT}}</pre>
    </div>
  </div>
</body>
</html>
"""


def _load_optional(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    try:
        return path.read_text().strip()
    except Exception:
        return fallback


def write_daily_brief() -> str:
    core_text = build_mission_brief()
    readiness_text = build_readiness_brief()

    reliability_path = DOCS_DIR / "reliability_report.txt"
    drift_path = DOCS_DIR / "drift_report.txt"

    reliability_text = _load_optional(
        reliability_path,
        "Reliability report not generated yet. Run sensor_reliability.py.",
    )
    drift_text = _load_optional(
        drift_path,
        "Drift report not generated yet. Run sensor_drift_predictor.py.",
    )

    html = HTML_TEMPLATE
    html = html.replace("{{CORE_BRIEF}}", core_text)
    html = html.replace("{{SENSOR_READINESS}}", readiness_text)
    html = html.replace("{{RELIABILITY}}", reliability_text)
    html = html.replace("{{DRIFT}}", drift_text)

    out_path = DOCS_DIR / "daily_mission_brief.html"
    out_path.write_text(html)
    return str(out_path)


def main() -> None:
    out = write_daily_brief()
    print(f"[OK] HTML mission brief written → {out}")


if __name__ == "__main__":
    main()

