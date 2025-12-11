#!/usr/bin/env python3
"""
obasi_training_coach.py

Ghost Lantern Labs – Obasi Training Coach

Purpose:
    Provide short, tactical guidance messages for trainees based on their
    latest composite training score. This is UI-only logic – no network,
    no external calls.

API:
    build_obasi_training_coach_speech(latest_score: float | None) -> str

    - If latest_score is None:
        Returns a general encouragement / guidance message.
    - If latest_score is provided (0–100):
        Returns a message tailored to that band.
"""

from typing import Optional


def build_obasi_training_coach_speech(latest_score: Optional[float] = None) -> str:
    """
    Build a short guidance message from Obasi, the spectral owl,
    tailored to the trainee's latest performance.

    Score bands (0–100):
        0–49   : Recovery mode – focus on fundamentals.
        50–69  : Building phase – tighten discipline and repetition.
        70–84  : Strong – refine nuclear/ISR fusion and reporting.
        85–100 : Elite – push edge cases and leadership-level thinking.
    """
    if latest_score is None:
        return (
            "Obasi: No score yet – treat this as a blank slate. Start with one solid "
            "rep today: clean analysis, clear fusion logic, and a short, sharp report. "
            "Consistency beats intensity."
        )

    try:
        s = float(latest_score)
    except (TypeError, ValueError):
        return (
            "Obasi: Score data looks odd – ignore the number and focus on the craft. "
            "Walk through your last scenario and ask: Did I answer the commander’s "
            "real question, or just repeat data?"
        )

    if s < 50:
        return (
            "Obasi: This was a rough rep, and that’s fine. Strip it back to basics – "
            "what was the mission, what did the sensors say, and what did it mean "
            "for the commander? One clean, simple story beats a messy clever one."
        )
    if s < 70:
        return (
            "Obasi: You’re in the grind zone – not failing, not elite yet. Tighten "
            "your structure: situation, indicators, assessment, and recommendation. "
            "Focus on removing friction and confusion from your briefing."
        )
    if s < 85:
        return (
            "Obasi: Strong work. Now sharpen the nuclear/ISR edge. For each scenario, "
            "ask: what’s the early-warning angle, what’s the base-defense angle, and "
            "what do we tell leadership in one sentence if time runs out?"
        )

    return (
        "Obasi: This is elite territory. Don’t get comfortable. Push yourself into "
        "edge cases – ambiguous signals, degraded sensors, conflicting reports. "
        "Practice making clear, defensible calls under uncertainty."
    )

