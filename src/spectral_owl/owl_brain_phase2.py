"""
owl_brain_phase2.py — Ghost Lantern Labs
----------------------------------------
Spectral Owl wired into the Phase 2 multi-provider LLM adapter.

Behavior:
- Reads scored_output.csv (fused/Scored events).
- Builds a summary prompt for the LLM.
- Calls run_llm_with_fallback(...) from llm_phase2_adapter.
- Prints an operator-style summary:
    - how many events
    - which provider actually answered
    - the model's response

This does NOT replace your existing owl_brain.py.
It's a new, Phase-2-specific runner you can evolve separately.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import csv
from typing import List, Dict, Any

from llm_phase2_adapter import run_llm_with_fallback

SCORED_OUTPUT = Path("scored_output.csv")


def load_scored_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run fusion_scoring.py first to generate scored_output.csv."
        )

    events: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    return events


def build_prompt_from_events(events: List[Dict[str, Any]]) -> str:
    """
    Build a compact analysis prompt from the scored events.

    Assumes there is a 'score' column and possibly fields like:
    - id, Seismic_Mag, Radiation_uSv, Comms_State, etc.
    """
    total = len(events)
    if total == 0:
        return "There are no events in scored_output.csv. Confirm the system is quiet."

    # Try to parse score and sort descending
    def parse_score(e: Dict[str, Any]) -> float:
        try:
            return float(e.get("score", 0.0))
        except ValueError:
            return 0.0

    sorted_events = sorted(events, key=parse_score, reverse=True)
    top = sorted_events[:3]

    lines = []
    lines.append(
        f"There are {total} fused events in scored_output.csv. "
        f"Here are the top {len(top)} by score:"
    )
    for e in top:
        ident = e.get("id", "UNKNOWN")
        score = e.get("score", "UNKNOWN")
        seismic = e.get("Seismic_Mag", e.get("seismic_mag", "N/A"))
        rad = e.get("Radiation_uSv", e.get("radiation_usv", "N/A"))
        comms = e.get("Comms_State", e.get("comms_state", "N/A"))
        lines.append(
            f"- id={ident}, score={score}, Seismic={seismic}, "
            f"Radiation={rad}, Comms={comms}"
        )

    lines.append(
        "As Spectral Owl, provide a concise threat assessment for a commander: "
        "is this situation stable, elevated, or critical? Note if this looks like "
        "data denial / jamming, nuclear/EMS concern, or general noise."
    )
    return "\n".join(lines)


def run_phase2_owl_analysis() -> Dict[str, Any]:
    events = load_scored_events(SCORED_OUTPUT)
    prompt = build_prompt_from_events(events)

    # Call Phase 2 adapter with some basic params.
    result = run_llm_with_fallback(
        prompt,
        max_tokens=128,
        temperature=0.2,
    )

    return {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "num_events": len(events),
        "provider_tried": result["provider_tried"],
        "final_provider": result["final_provider"],
        "llm_result": result["result"],
    }


def main():
    try:
        summary = run_phase2_owl_analysis()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return

    print("=== Spectral Owl Phase 2 Analysis ===")
    print(f"Timestamp (UTC): {summary['timestamp_utc']}")
    print(f"Total fused events: {summary['num_events']}")
    print(f"Providers tried: {', '.join(summary['provider_tried'])}")
    print(f"Final provider: {summary['final_provider']}")
    print("")
    print("LLM Engine Payload:")
    print(summary["llm_result"])


if __name__ == "__main__":
    main()

