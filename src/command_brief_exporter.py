# src/command_brief_exporter.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors


OUTPUT_DIR = Path("docs") / "briefs"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def export_command_brief(
    *,
    trainee_name: str,
    training_curve: Dict[str, Any],
    validation_report: Dict[str, Any] | None,
    certification_status: Dict[str, Any],
    training_feedback: Dict[str, Any],
) -> Path:
    """
    Generate a command-grade PDF training brief.
    TRAINING SAFE — NO OPERATIONAL DATA.
    """

    _safe_mkdir(OUTPUT_DIR)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"GLL_Command_Brief_{ts}.pdf"

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.alignment = TA_LEFT
    h = styles["Heading2"]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=LETTER,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story: List[Any] = []

    # ---- HEADER ----
    story.append(Paragraph("<b>Ghost Lantern Labs — Training Command Brief</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Trainee:</b> {trainee_name}", body))
    story.append(Paragraph(f"<b>Generated:</b> {_utc_now()}", body))
    story.append(Spacer(1, 16))

    # ---- TRAINING METRICS ----
    story.append(Paragraph("Training Readiness Metrics", h))
    metrics = [
        ["AGI", training_curve.get("AGI", "—")],
        ["Improvement Slope", training_curve.get("improvement_slope", "—")],
        ["Difficulty-Weighted Avg", training_curve.get("difficulty_weighted_average", "—")],
        ["Volatility Index", training_curve.get("volatility_index", "—")],
    ]
    t = Table(metrics, colWidths=[220, 220])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # ---- VALIDATION ----
    story.append(Paragraph("Latest Validation Snapshot", h))
    if validation_report:
        verdict = validation_report.get("verdict", {})
        story.append(Paragraph(f"<b>Status:</b> {verdict.get('status', '—')}", body))
        story.append(Paragraph(f"<b>Message:</b> {verdict.get('message', '')}", body))
    else:
        story.append(Paragraph("No validation report available.", body))
    story.append(Spacer(1, 14))

    # ---- CERTIFICATION ----
    story.append(Paragraph("Operator Certification Readiness", h))
    story.append(Paragraph(f"<b>Target Difficulty:</b> {certification_status.get('target_difficulty')}", body))
    story.append(Paragraph(f"<b>Current Pass Streak:</b> {certification_status.get('current_pass_streak')}", body))
    story.append(Paragraph(f"<b>Certified:</b> {certification_status.get('certified')}", body))
    story.append(Paragraph(f"<b>Guidance:</b> {certification_status.get('guidance')}", body))
    story.append(Spacer(1, 14))

    # ---- FEEDBACK ----
    story.append(Paragraph("Next Training Recommendation", h))
    story.append(Paragraph(str(training_feedback), body))
    story.append(Spacer(1, 18))

    # ---- FOOTER ----
    story.append(Paragraph(
        "<i>This brief is generated from synthetic training data. "
        "It contains no operational or classified information.</i>",
        body
    ))

    doc.build(story)
    return out_path

