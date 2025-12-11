#!/usr/bin/env python3
"""
language_interpreter.py

Ghost Lantern Labs – Language Interpreter (Module 1 – Framework)
----------------------------------------------------------------

Purpose:
    Provide a safe, offline, passive framework for handling foreign-language
    text inside Ghost Lantern Labs (GLL).

    This module does NOT:
        - Call external translation APIs.
        - Scrape the internet.
        - Execute any network operations.

    Instead, it:
        - Accepts user-provided foreign text.
        - Records the declared language and mission domain.
        - Builds a structured analysis template for GLL's agents:
            • Lumen  – clarity / plain-English framing
            • Denae  – adversary cognition
            • Valdez – cyber offense/defense implications
            • Obasi  – ISR / early warning implications
            • Shari  – legal / policy framing
            • Author – briefing / narrative output

    Outputs:
        - docs/language_analysis.json
        - docs/language_analysis.txt

Usage:
    From src/:

        python language_interpreter.py

    Optional:
        - Place foreign text into docs/foreign_text_input.txt before running.
          If that file is non-empty, it will be used as the input text.
        - Otherwise, you will be prompted to paste/enter text in the terminal.
"""

import os
import json
from typing import Any, Dict, List, Optional


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

FOREIGN_TEXT_PATH = os.path.join(DOCS_DIR, "foreign_text_input.txt")
OUTPUT_JSON = os.path.join(DOCS_DIR, "language_analysis.json")
OUTPUT_TXT = os.path.join(DOCS_DIR, "language_analysis.txt")


def _ensure_docs_dir() -> None:
    os.makedirs(DOCS_DIR, exist_ok=True)


def _read_from_file_if_available(path: str) -> Optional[str]:
    """
    Return file contents if the file exists and is non-empty.
    Otherwise, return None.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return data if data else None
    except Exception:
        return None


def _prompt_for_text() -> str:
    """
    Prompt the operator to paste or type foreign text.

    For now, we keep it simple: a single multiline input via EOF (Ctrl+D).
    """
    print("")
    print("=== Ghost Lantern Labs – Language Interpreter (Module 1) ===")
    print("No docs/foreign_text_input.txt found or it was empty.")
    print("Paste or type the foreign-language text below.")
    print("When finished, press Ctrl+D (on macOS/Linux) to end input.")
    print("------------------------------------------------------------")

    chunks: List[str] = []
    try:
        while True:
            line = input()
            chunks.append(line)
    except EOFError:
        pass

    text = "\n".join(chunks).strip()
    if not text:
        raise ValueError("No text provided; cannot build language analysis.")
    return text


def _prompt_for_metadata() -> Dict[str, str]:
    """
    Ask the operator to describe the language and mission domain.
    """
    print("")
    print("Describe the language and mission context for this text.")
    language = input("Language (e.g., Mandarin Chinese, Russian, Farsi, Korean): ").strip()
    if not language:
        language = "UNKNOWN"

    print("")
    print("Select / describe the primary mission domain for this text:")
    print("  - nuclear_early_warning")
    print("  - defensive_cyber_intel")
    print("  - joint_base_defense")
    print("  - general_fusion")
    domain = input("Domain (type one of the above or your own label): ").strip()
    if not domain:
        domain = "general_fusion"

    source = input("Optional: Source/context note (e.g., 'Weibo post', 'threat report', 'SIGINT excerpt'): ").strip()
    if not source:
        source = "unspecified_source"

    return {
        "language": language,
        "domain": domain,
        "source_note": source,
    }


def build_language_analysis_payload(
    foreign_text: str,
    meta: Dict[str, str],
) -> Dict[str, Any]:
    """
    Build the structured analysis payload for the language interpreter.
    """
    language = meta.get("language", "UNKNOWN")
    domain = meta.get("domain", "general_fusion")
    source_note = meta.get("source_note", "unspecified_source")

    # High-level suggestions for how GLL should treat this text.
    suggested_questions: List[str] = [
        "What is the core message or claim in this text?",
        "What indicators of intent, capability, or posture are present?",
        "What assumptions or biases might be embedded in this source?",
        "Is there any mention of timelines, locations, or units?",
        "Does this support or contradict existing assessments in GLL?",
    ]

    if "nuclear" in domain.lower():
        suggested_questions.extend([
            "Does this text mention tests, launches, alerts, drills, or technical nuclear terms?",
            "Does it hint at changes in alert posture or early warning systems?",
        ])
    if "cyber" in domain.lower():
        suggested_questions.extend([
            "Does this text reference malware, vulnerabilities, infrastructure, or specific targets?",
            "Is there any indication of TTPs (tactics, techniques, procedures)?",
        ])
    if "defense" in domain.lower() or "base" in domain.lower():
        suggested_questions.extend([
            "Is there any mention of perimeter, airspace, drones, bases, or security forces?",
            "Does this suggest any near-term risk to installations or joint forces?",
        ])

    return {
        "title": "Ghost Lantern Labs – Language Interpreter Analysis (Module 1)",
        "language": language,
        "domain": domain,
        "source_note": source_note,
        "foreign_text": foreign_text,
        "agent_perspectives": {
            "Lumen": {
                "role": "clarity_and_plain_english",
                "notes": "",
            },
            "Denae": {
                "role": "adversary_cognition_and_intent",
                "notes": "",
            },
            "Valdez": {
                "role": "cyber_offense_defense_implications",
                "notes": "",
            },
            "Obasi": {
                "role": "ISR_and_early_warning_implications",
                "notes": "",
            },
            "Shari": {
                "role": "legal_policy_and_rules_of_engagement",
                "notes": "",
            },
            "Author": {
                "role": "briefing_narrative_and_communication",
                "notes": "",
            },
        },
        "suggested_analytic_questions": suggested_questions,
        "intended_use": (
            "This artifact is meant to serve as a structured entry point for foreign-language text. "
            "Analysts (or AI agents in the future) can fill in the agent_perspectives fields and "
            "derive nuclear, cyber, ISR, and policy-relevant conclusions."
        ),
    }


def _format_text_report(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Language Interpreter Analysis (Module 1)")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Language        : {payload.get('language', 'UNKNOWN')}")
    lines.append(f"Domain          : {payload.get('domain', 'UNKNOWN')}")
    lines.append(f"Source / Context: {payload.get('source_note', '')}")
    lines.append("")
    lines.append("Original Foreign Text:")
    lines.append("-" * 26)
    lines.append(payload.get("foreign_text", "").strip())
    lines.append("")
    lines.append("Agent Perspectives (empty slots to be filled by analyst / AI agents):")
    lines.append("-" * 70)

    agent_persp = payload.get("agent_perspectives", {}) or {}
    for agent_name, data in agent_persp.items():
        lines.append(f"[{agent_name}] – Role: {data.get('role', '')}")
        lines.append(f"Notes: {data.get('notes', '') or '<to be filled>'}")
        lines.append("")

    lines.append("Suggested Analytic Questions:")
    lines.append("-" * 70)
    for q in payload.get("suggested_analytic_questions", []):
        lines.append(f"  - {q}")
    lines.append("")
    lines.append("Intended Use:")
    lines.append(payload.get("intended_use", ""))
    lines.append("")

    return "\n".join(lines)


def run_language_interpreter() -> Dict[str, Any]:
    """
    Orchestrator:
        - Ensure docs dir exists.
        - Load foreign text (file or prompt).
        - Ask for language/domain metadata.
        - Build analysis payload.
        - Write JSON + TXT outputs.
    """
    _ensure_docs_dir()

    foreign_text = _read_from_file_if_available(FOREIGN_TEXT_PATH)
    if foreign_text is None:
        foreign_text = _prompt_for_text()

    meta = _prompt_for_metadata()
    payload = build_language_analysis_payload(foreign_text, meta)

    # Write JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f_json:
        json.dump(payload, f_json, indent=2)

    # Write TXT
    text_report = _format_text_report(payload)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f_txt:
        f_txt.write(text_report)

    return {
        "json_path": OUTPUT_JSON,
        "txt_path": OUTPUT_TXT,
        "payload": payload,
    }


if __name__ == "__main__":
    result = run_language_interpreter()
    print("Language Interpreter analysis written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

