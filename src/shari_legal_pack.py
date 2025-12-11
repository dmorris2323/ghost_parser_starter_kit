#!/usr/bin/env python3
"""
shari_legal_pack.py

Ghost Lantern Labs – Shari Legal & Compliance Pack (Module 1)
--------------------------------------------------------------
Generates a legal/compliance framework for GLL.
Outputs to: src/docs/legal/
"""

from pathlib import Path
from typing import Dict


LEGAL_DOCS = {
    "gll_ai_safety_and_guardrails.md": """
# Ghost Lantern Labs (GLL)
## AI Safety & Guardrails Doctrine (Module 1)

GLL is an ISR/cyber fusion training system with strict non-destructive boundaries.

### 1. Allowed
- Analyze user-provided data.
- Generate training outputs.
- Evaluate system resilience.
- Provide instructor feedback.
- Perform non-destructive fusion analysis.

### 2. Prohibited
- Cyber offense.
- Malware generation.
- System manipulation.
- External network access.
- Classification violations.
- Automated destructive code.

### 3. Guardrails
- SPS Module 1: Guardrail engine.
- SPS Module 2: Mutation watcher.
- All code changes require human authorization.
""",

    "gll_data_handling_and_privacy_doctrine.md": """
# Ghost Lantern Labs (GLL)
## Data Handling & Privacy Doctrine

### Classification
All data used in GLL must be UNCLASSIFIED and user-provided.

### Allowed Data
- Synthetic telemetry
- Training session logs
- Instructor inputs
- Foreign-language text provided by the user

### Prohibited Data
- Classified material
- PII from real systems
- Live government sensor feeds

### Privacy
- No external transmission.
- All logs remain local.
""",

    "gll_training_tool_usage_terms.md": """
# Ghost Lantern Labs (GLL)
## Training Tool Usage Terms

GLL is **for training and education only**, not operational ISR.

### Intended Users
- Students
- Instructors
- Analysts in training pipelines

### Intended Purposes
- ISR reasoning practice
- Fusion simulations
- Training scenarios
- Instructor evaluation

### Prohibited Uses
- Tactical/strategic decisions
- Replacing DCGS/USNDS/ICADS
""",

    "gll_export_control_and_classification_notes.md": """
# Ghost Lantern Labs (GLL)
## Export Control & Classification Notes

### Classification
All outputs UNCLASSIFIED.

### Restrictions
GLL must not be provided to:
- Foreign governments
- Sanctioned entities
- Organizations engaged in proliferation

Shari will review final export/legal posture during commercialization.
""",

    "gll_sps_design_brief.md": """
# Ghost Lantern Labs (GLL)
## SPS – Self-Preservation Shield (Design Brief)

### Purpose
Protect GLL against:
- Destructive edits
- Accidental code corruption
- Prompt-injection sabotage
- Dangerous command execution

### Components
1. Guardrail Engine
2. Mutation Watcher
3. File Integrity Checks

### Status Levels
- GREEN
- AMBER
- RED
"""
}


def generate_shari_legal_pack() -> Dict[str, str]:
    """
    Writes legal doctrine files to src/docs/legal/.
    """
    # __file__ = .../src/shari_legal_pack.py
    src_dir = Path(__file__).resolve().parent        # .../src
    legal_dir = src_dir / "docs" / "legal"          # .../src/docs/legal
    legal_dir.mkdir(parents=True, exist_ok=True)

    written = {}
    for filename, content in LEGAL_DOCS.items():
        path = legal_dir / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        written[filename] = str(path)

    return written


if __name__ == "__main__":
    results = generate_shari_legal_pack()
    print("Shari Legal Pack written:")
    for name, path in results.items():
        print(f"  • {name}: {path}")

