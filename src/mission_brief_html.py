"""
mission_brief_html.py

Wraps the text daily mission brief in an HTML template:
docs/mission_brief_template.html

Supported placeholders in the template:

{{BRIEF_TEXT}}
{{CRISIS_MODE}}
{{OPERATOR}}
{{FUSION_TRUST}}
{{OSL}}
{{SENSOR_LATENCY}}
{{GOLDEN_DOME_TILE}}
{{GOLDEN_DOME_DRIFT}}
"""

from pathlib import Path
import json

from daily_mission_brief import write_daily_brief
from crisis_mode_flag import status as crisis_status
from operator_identity import get_identity
from fusion_trust import compute_trust
from operator_safety_layer import compute_osl
from sensor_latency import compute_latency_report

# Optional Golden Dome tile/drift imports
try:
    from golden_dome_tile import build_golden_dome_tile
except ImportError:
    build_golden_dome_tile = None

try:
    from golden_dome_drift import compute_drift
except ImportError:
    compute_drift = None


TEMPLATE_HTML = Path("docs/mission_brief_template.html")
OUTPUT_HTML = Path("docs/daily_mission_brief.html")


def build_html() -> str:
    """
    Build the HTML mission brief content as a string.
    """
    # 1) Get the plain-text brief (also writes docs/daily_mission_brief.txt)
    brief_text = write_daily_brief()

    # 2) Load template
    if TEMPLATE_HTML.exists():
        html = TEMPLATE_HTML.read_text()
    else:
        # Minimal fallback if template missing
        html = """<html>
<head><title>Daily Mission Brief</title></head>
<body>
<h1>Mission Brief — Ghost Lantern Labs</h1>
<pre>{{BRIEF_TEXT}}</pre>

<h2>Fusion Trust Score</h2>
<pre>{{FUSION_TRUST}}</pre>

<h2>Operator Safety Layer</h2>
<pre>{{OSL}}</pre>

<h2>Sensor Latency</h2>
<pre>{{SENSOR_LATENCY}}</pre>

<p>Crisis Mode: {{CRISIS_MODE}}</p>
<p>Operator: {{OPERATOR}}</p>

<h2>Golden Dome Readiness</h2>
<pre>{{GOLDEN_DOME_TILE}}</pre>

<h2>Golden Dome Drift</h2>
<pre>{{GOLDEN_DOME_DRIFT}}</pre>
</body>
</html>
"""

    # 3) Core replacements
    html = html.replace("{{BRIEF_TEXT}}", brief_text)
    html = html.replace("{{CRISIS_MODE}}", crisis_status())
    html = html.replace("{{OPERATOR}}", get_identity())

    # Fusion Trust + OSL
    try:
        trust = compute_trust()
        html = html.replace("{{FUSION_TRUST}}", json.dumps(trust, indent=2))
    except Exception:
        html = html.replace("{{FUSION_TRUST}}", '"fusion_trust_error"')

    try:
        osl = compute_osl()
        html = html.replace("{{OSL}}", json.dumps(osl, indent=2))
    except Exception:
        html = html.replace("{{OSL}}", '"osl_error"')

    # Sensor Latency
    try:
        lat = compute_latency_report()
        html = html.replace("{{SENSOR_LATENCY}}", json.dumps(lat, indent=2))
    except Exception:
        html = html.replace("{{SENSOR_LATENCY}}", '"latency_error"')

    # Golden Dome Tile
    if build_golden_dome_tile is not None:
        try:
            # If you have a stats object elsewhere, you can wire it in.
            # Here we use simple safe defaults.
            tile = build_golden_dome_tile(
                reliability=92.0,
                agreement=88.0,
                profile=get_identity(),
            )
            html = html.replace("{{GOLDEN_DOME_TILE}}", json.dumps(tile, indent=2))
        except Exception:
            html = html.replace("{{GOLDEN_DOME_TILE}}", '"golden_dome_tile_error"')
    else:
        html = html.replace("{{GOLDEN_DOME_TILE}}", '"golden_dome_tile_unavailable"')

    # Golden Dome Drift
    if compute_drift is not None:
        try:
            drift = compute_drift()
            html = html.replace("{{GOLDEN_DOME_DRIFT}}", json.dumps(drift, indent=2))
        except Exception:
            html = html.replace("{{GOLDEN_DOME_DRIFT}}", '"golden_dome_drift_error"')
    else:
        html = html.replace("{{GOLDEN_DOME_DRIFT}}", '"golden_dome_drift_unavailable"')

    return html


def write_html_brief() -> str:
    """
    Build and write docs/daily_mission_brief.html.
    Returns the HTML string.
    """
    html = build_html()
    OUTPUT_HTML.parent.mkdir(exist_ok=True, parents=True)
    OUTPUT_HTML.write_text(html)
    return html


if __name__ == "__main__":
    out = write_html_brief()
    print(out)

