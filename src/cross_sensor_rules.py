"""
cross_sensor_rules.py — Human-Readable Cross-Sensor Rules
---------------------------------------------------------
This will eventually power advanced logic or ML.

For now it documents the logic used in the validator.
"""

RULES = [
    {
        "pattern": ["optical", "seismic", "radiation"],
        "confidence": "VERY_HIGH",
        "notes": "Matches real-world missile detection logic."
    },
    {
        "pattern": ["optical", "seismic"],
        "confidence": "HIGH",
        "notes": "Flash + ground impact = strong correlation."
    },
    {
        "pattern": ["seismic", "radiation"],
        "confidence": "HIGH",
        "notes": "Impact + burst particles = nuclear confirmation."
    },
    {
        "pattern": ["optical"],
        "confidence": "LOW",
        "notes": "Flash alone can be spoofed or noisy."
    },
    {
        "pattern": [],
        "confidence": "NONE",
        "notes": "Insufficient evidence."
    }
]

def export_rules():
    import json
    return json.dumps(RULES, indent=2)

if __name__ == "__main__":
    print(export_rules())

