# apps/gui/obasi_training_coach.py
# Obasi Coaching (SAFE) – accepts flexible inputs to avoid signature mismatches.

from __future__ import annotations


def build_obasi_training_coach_speech(*args, **kwargs) -> str:
    """
    Flexible signature to prevent Streamlit crashes when callers change.

    Expected (optional) kwargs:
      - trainee_name
      - difficulty
      - agi
      - avg_score
      - volatility
      - message_mode ("coach"|"instructor")
    """
    trainee = kwargs.get("trainee_name", "Trainee")
    difficulty = kwargs.get("difficulty", "ANALYST")
    agi = kwargs.get("agi", None)
    avg = kwargs.get("avg_score", None)
    vol = kwargs.get("volatility", None)
    mode = kwargs.get("message_mode", "coach")

    lines = []
    if mode == "instructor":
        lines.append(f"OBASI (Instructor): {trainee} current track: {difficulty}.")
        if agi is not None:
            lines.append(f"AGI={agi}. Average={avg}. Volatility={vol}.")
        lines.append("Focus: consistency first. Promote difficulty only when volatility drops.")
        return "\n".join(lines)

    # Coach mode
    lines.append(f"OBASI: {trainee}, you’re operating at **{difficulty}**.")
    if agi is not None:
        lines.append(f"Training status: AGI={agi}, Avg={avg}, Volatility={vol}.")
    lines.append("Rule: stabilize your judgment before you chase harder scenarios.")
    lines.append("Next rep: identify patterns fast, then write a clean commander summary.")
    return "\n".join(lines)

