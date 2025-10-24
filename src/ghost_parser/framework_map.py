# framework_map.py
FRAMEWORK_MAP = {
    "unauthorized access": ["MITRE:T1078", "NIST:DE.CM-7"],
    "data exfiltration": ["MITRE:T1041", "NIST:PR.DS-5"],
    "command and control": ["MITRE:T1071", "NIST:DE.CM-8"],
    "login anomaly": ["MITRE:T1110", "NIST:ID.AM-2"],
    "malware beacon": ["MITRE:T1105", "NIST:PR.PT-3"]
}

def match_framework(event_text: str):
    for k, v in FRAMEWORK_MAP.items():
        if k in event_text.lower():
            return v
    return []

