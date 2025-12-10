import json
from pathlib import Path
from collections import Counter

MEM_FILE = Path("data/threat_memory.json")

def _load_memory():
    if not MEM_FILE.exists():
        return []
    try:
        data = json.loads(MEM_FILE.read_text())
        return data.get("events", [])
    except:
        return []

def analyze_patterns():
    events = _load_memory()

    if not events:
        return {"status": "no_data", "patterns": {}}

    # Count event_type frequency
    types = [e.get("event_type", "UNKNOWN") for e in events]
    counts = Counter(types)

    # Determine top threat driver
    top = counts.most_common(1)[0]

    result = {
        "status": "ok",
        "total_events": len(events),
        "top_pattern": {
            "event_type": top[0],
            "occurrences": top[1]
        },
        "all_patterns": counts
    }

    out = Path("docs/adversary_patterns.json")
    out.write_text(json.dumps(result, indent=2))
    return result

