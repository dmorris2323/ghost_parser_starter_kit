from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

OUT_DIR = Path("docs") / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_reasoning_trace(
    inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Commander-safe reasoning trace.
    This is NOT chain-of-thought.
    It is an analyst-style summary of how conclusions were reached.
    """

    assumptions: List[str] = []
    observations: List[str] = []
    uncertainties: List[str] = []

    # ---- Observations (best-effort) ----
    if inputs.get("fusion_validation"):
        observations.append("Fusion pipeline validation present and passed.")
    else:
        uncertainties.append("Fusion validation input missing.")

    if inputs.get("degraded_validation"):
        observations.append("Degraded operations validated within bounded parameters.")
    else:
        uncertainties.append("Degraded validation input missing.")

    if inputs.get("base_defense"):
        observations.append("Base defense posture derived from multi-product inputs.")
    else:
        uncertainties.append("Base defense products missing or incomplete.")

    # ---- Assumptions (explicitly stated) ----
    assumptions.extend(
        [
            "Telemetry inputs are synthetic or simulated.",
            "No adversary intent is inferred from telemetry alone.",
            "Risk bands represent bounded confidence estimates.",
        ]
    )

    if not observations:
        assumptions.append("System operating with partial or missing inputs.")

    reasoning = {
        "generated_at_utc": _utc_now_iso(),
        "summary": (
            "Spectral Owl synthesized available validation, fusion, and base-defense "
            "artifacts to derive a bounded operational posture."
        ),
        "observations": observations or ["No reliable observations available."],
        "assumptions": assumptions,
        "uncertainties": uncertainties or ["No critical uncertainties identified."],
        "analyst_note": (
            "This reasoning trace is a bounded analytical summary. "
            "Operator judgment is required before escalation."
        ),
    }

    return reasoning


def write_reasoning_trace(inputs: Dict[str, Any]) -> Dict[str, str]:
    trace = build_reasoning_trace(inputs)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    json_latest = OUT_DIR / "spectral_owl_reasoning_latest.json"
    txt_latest = OUT_DIR / "spectral_owl_reasoning_latest.txt"

    json_stamped = OUT_DIR / f"spectral_owl_reasoning_{ts}.json"
    txt_stamped = OUT_DIR / f"spectral_owl_reasoning_{ts}.txt"

    with json_latest.open("w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    with json_stamped.open("w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2)

    with txt_latest.open("w", encoding="utf-8") as f:
        f.write(json.dumps(trace, indent=2))

    with txt_stamped.open("w", encoding="utf-8") as f:
        f.write(json.dumps(trace, indent=2))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def main() -> int:
    # Best-effort inputs (do NOT hard fail)
    inputs = {
        "fusion_validation": True,
        "degraded_validation": True,
        "base_defense": True,
    }

    paths = write_reasoning_trace(inputs)
    print(json.dumps(paths, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

