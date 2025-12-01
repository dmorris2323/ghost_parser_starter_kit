"""
local_rules_engine.py — Ghost Lantern Labs
------------------------------------------

Dedicated local / offline "small brain" for Spectral Owl.

This is a rules-based classifier that:
- Never calls the cloud.
- Can run in denied / degraded / air-gapped environments.
- Provides simple tags useful for commanders and operators.

It is separate from llm_provider_pool.LocalRulesEngine so you can
evolve this file specifically for Spectral Owl over time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LocalRulesEngine:
    """
    Local / offline rules-based engine.

    This engine DOES NOT use any external models.
    It relies on simple keyword and pattern checks to:
    - Classify the type of threat.
    - Provide a quick human-readable assessment.
    """

    name: str = "spectral_local_rules"

    def classify_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Classify the given prompt into one of a few domains:
        - nuclear_ems
        - data_denial
        - legal
        - general
        """
        text = prompt.lower()
        tag = "general"
        reasons = []

        # Nuclear / EMS cluster
        nuclear_terms = [
            "nuclear", "icbm", "warhead", "radiation",
            "golden dome", "aftac", "detonation", "yield"
        ]
        if any(t in text for t in nuclear_terms):
            tag = "nuclear_ems"
            reasons.append("Detected nuclear/EMS-related terms.")

        # Data denial / jamming cluster
        data_denial_terms = [
            "jamming", "jammer", "gps spoof", "spoofing",
            "ddos", "dos", "data denial", "flood", "noise injection"
        ]
        if any(t in text for t in data_denial_terms):
            if tag != "general":
                tag = f"{tag}+data_denial"
            else:
                tag = "data_denial"
            reasons.append("Detected jamming/data denial terminology.")

        # Legal cluster
        legal_terms = [
            "case", "client", "lawsuit", "complaint",
            "bankruptcy", "family law", "judge", "court"
        ]
        if any(t in text for t in legal_terms):
            if tag != "general":
                tag = f"{tag}+legal"
            else:
                tag = "legal"
            reasons.append("Detected legal-domain terminology.")

        if not reasons:
            reasons.append("No strong domain-specific indicators found.")

        return {
            "engine": self.name,
            "mode": "local_rules",
            "tag": tag,
            "reasons": reasons,
        }

    def summarize(self, prompt: str) -> Dict[str, Any]:
        """
        High-level wrapper: classify and return a compact summary payload.
        """
        classification = self.classify_prompt(prompt)
        tag = classification["tag"]

        if tag.startswith("nuclear_ems"):
            assessment = (
                "This appears related to nuclear or EMS concerns. "
                "Treat as high-priority ISR/Golden Dome-related context."
            )
        elif "data_denial" in tag:
            assessment = (
                "This appears related to data denial, jamming, or flooding. "
                "Recommend focusing on sensor integrity and comms resilience."
            )
        elif "legal" in tag:
            assessment = (
                "This appears to concern legal or case-management topics. "
                "Treat as sensitive client/attorney context."
            )
        else:
            assessment = (
                "General context detected. No strong nuclear, jamming, or legal indicators."
            )

        return {
            "engine": self.name,
            "mode": "local_rules",
            "tag": tag,
            "assessment": assessment,
            "reasons": classification["reasons"],
        }


if __name__ == "__main__":
    # Simple manual test
    test_prompt = (
        "Assess the risk that this jamming activity is masking a nuclear-related launch."
    )
    engine = LocalRulesEngine()
    print(engine.summarize(test_prompt))

