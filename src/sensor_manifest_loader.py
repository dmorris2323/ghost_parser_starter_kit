import json
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent / "sensor_manifest.json"

def load_manifest():
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text())

if __name__ == "__main__":
    print(load_manifest())

