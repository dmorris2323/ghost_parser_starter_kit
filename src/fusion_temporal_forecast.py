import json
from pathlib import Path
from datetime import datetime, timedelta

RUN_HISTORY = Path("data/run_history.csv")

def _load_events():
    if not RUN_HISTORY.exists():
        return []
    lines = RUN_HISTORY.read_text().strip().split("\n")[1:]
    events = []
    for ln in lines[-50:]:
        parts = ln.split(",")
        if len(parts) < 3:
            continue
        ts = parts[0]
        status = parts[2]
        events.append({"ts": ts, "status": status})
    return events

def _score_last(events):
    if not events:
        return 0
    score = 0
    for e in events:
        if "critical" in e["status"]:
            score += 2
        if "warning" in e["status"]:
            score += 1
    return score

def forecast_next_6h():
    events = _load_events()
    baseline = _score_last(events)

    # temporal decay curve (primitive but reliable)
    future = {
        "t+1h": min(100, baseline * 1.2),
        "t+3h": min(100, baseline * 0.9),
        "t+6h": min(100, baseline * 0.7),
    }

    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_count_last50": len(events),
        "baseline_score": baseline,
        "forecast": future
    }

    out = Path("docs/temporal_forecast.json")
    out.write_text(json.dumps(result, indent=2))
    return result

