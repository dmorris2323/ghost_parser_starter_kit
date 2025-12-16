"""
command_brief_exporter.py

Command-Grade Brief Exporter (HTML-first, PDF-optional)

Goal:
- Export a single "commander brief packet" from the latest training + validation artifacts.
- Always produce HTML (no dependencies).
- Optionally produce PDF if reportlab is available.
- Write a manifest JSON so exports are auditable and demo-safe.

Outputs (repo-root relative):
- docs/briefs/command_brief_latest.html
- docs/briefs/command_brief_<timestamp>.html
- docs/briefs/command_brief_latest.json  (manifest)
- docs/briefs/command_brief_<timestamp>.json
- (optional) docs/briefs/command_brief_latest.pdf / command_brief_<timestamp>.pdf
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


BRIEFS_DIR = Path("docs") / "briefs"

# Latest sources we try to include (best-effort)
SRC_TRAINING_CURVE = Path("src") / "docs" / "training" / "training_curve_latest.json"
SRC_TRAINING_FEEDBACK = Path("src") / "docs" / "training" / "training_feedback_latest.json"
SRC_FUSION_VALIDATION = Path("src") / "docs" / "validation" / "fusion_validation_report.json"
SRC_DEGRADED_VALIDATION = Path("src") / "docs" / "validation" / "degraded_fusion_validation_latest.json"
SRC_SIS_REPORT = Path("src") / "docs" / "system_integrity_report.txt"
SRC_SPS_BEHAVIOR_TXT = Path("src") / "docs" / "sps_behavior_report.txt"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        if not path.exists():
            return None, f"missing: {path}"
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            return obj, None
        return {"_non_dict_json": obj}, None
    except Exception as e:
        return None, f"error reading {path}: {e.__class__.__name__}: {e}"


def _read_text(path: Path, max_chars: int = 20000) -> Tuple[Optional[str], Optional[str]]:
    try:
        if not path.exists():
            return None, f"missing: {path}"
        txt = path.read_text(encoding="utf-8")
        if len(txt) > max_chars:
            txt = txt[:max_chars] + "\n\n[TRUNCATED]\n"
        return txt, None
    except Exception as e:
        return None, f"error reading {path}: {e.__class__.__name__}: {e}"


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _render_kv_table(d: Dict[str, Any]) -> str:
    rows = []
    for k, v in d.items():
        vv = json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v)
        rows.append(f"<tr><td><b>{_html_escape(str(k))}</b></td><td><pre>{_html_escape(vv)}</pre></td></tr>")
    return "<table>" + "".join(rows) + "</table>"


def _build_html(
    *,
    generated_at: str,
    title: str,
    manifest: Dict[str, Any],
    training_curve: Optional[Dict[str, Any]],
    training_feedback: Optional[Dict[str, Any]],
    fusion_validation: Optional[Dict[str, Any]],
    degraded_validation: Optional[Dict[str, Any]],
    sis_txt: Optional[str],
    sps_txt: Optional[str],
    notes: list[str],
) -> str:
    # Pull headline metrics safely
    agi = None
    slope = None
    vol = None
    if isinstance(training_curve, dict):
        agi = training_curve.get("AGI")
        slope = training_curve.get("improvement_slope")
        vol = training_curve.get("volatility_index")

    def _metric(label: str, value: Any) -> str:
        return f"<div class='metric'><div class='label'>{_html_escape(label)}</div><div class='value'>{_html_escape(str(value))}</div></div>"

    metrics_html = "".join(
        [
            _metric("AGI (0–100)", agi if agi is not None else "N/A"),
            _metric("Improvement slope", slope if slope is not None else "N/A"),
            _metric("Volatility index", vol if vol is not None else "N/A"),
        ]
    )

    notes_html = "".join([f"<li>{_html_escape(n)}</li>" for n in notes])

    def _section(h: str, body: str) -> str:
        return f"<section><h2>{_html_escape(h)}</h2>{body}</section>"

    style = """
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
      h1 { margin-bottom: 6px; }
      .sub { color: #555; margin-top: 0; }
      .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0; }
      .metric { border: 1px solid #ddd; border-radius: 10px; padding: 12px; }
      .label { color: #666; font-size: 12px; }
      .value { font-size: 22px; font-weight: 700; margin-top: 4px; }
      section { margin: 18px 0; padding-top: 6px; border-top: 1px solid #eee; }
      pre { white-space: pre-wrap; word-break: break-word; }
      table { border-collapse: collapse; width: 100%; }
      td { border: 1px solid #eee; vertical-align: top; padding: 8px; }
      .pill { display: inline-block; padding: 3px 10px; border-radius: 999px; border: 1px solid #ddd; font-size: 12px; margin-right: 8px; }
    </style>
    """

    header = f"""
    <h1>{_html_escape(title)}</h1>
    <p class="sub">
      Generated (UTC): {_html_escape(generated_at)} |
      <span class="pill">SAFE: synthetic + training artifacts</span>
      <span class="pill">Gates: SIS/SPS enforced</span>
    </p>
    <div class="grid">{metrics_html}</div>
    """

    body = ""
    body += _section("Executive Notes", f"<ul>{notes_html}</ul>")
    body += _section("Export Manifest", _render_kv_table(manifest))

    if training_feedback is not None:
        body += _section("Next Training Recommendation (read-only)", f"<pre>{_html_escape(json.dumps(training_feedback, indent=2))}</pre>")
    else:
        body += _section("Next Training Recommendation (read-only)", "<p><i>No training_feedback_latest.json found.</i></p>")

    if fusion_validation is not None:
        body += _section("Fusion Validation (latest)", f"<pre>{_html_escape(json.dumps(fusion_validation, indent=2))}</pre>")
    else:
        body += _section("Fusion Validation (latest)", "<p><i>fusion_validation_report.json not found.</i></p>")

    if degraded_validation is not None:
        body += _section("Degraded Fusion Validation (latest)", f"<pre>{_html_escape(json.dumps(degraded_validation, indent=2))}</pre>")
    else:
        body += _section("Degraded Fusion Validation (latest)", "<p><i>degraded_fusion_validation_latest.json not found.</i></p>")

    if sis_txt is not None:
        body += _section("SIS: System Integrity Report (latest)", f"<pre>{_html_escape(sis_txt)}</pre>")
    else:
        body += _section("SIS: System Integrity Report (latest)", "<p><i>system_integrity_report.txt not found.</i></p>")

    if sps_txt is not None:
        body += _section("SPS: Behavioral Integrity (latest)", f"<pre>{_html_escape(sps_txt)}</pre>")
    else:
        body += _section("SPS: Behavioral Integrity (latest)", "<p><i>sps_behavior_report.txt not found.</i></p>")

    return f"<!doctype html><html><head><meta charset='utf-8'>{style}</head><body>{header}{body}</body></html>"


def _try_export_pdf_from_html(html_text: str, pdf_path: Path) -> Tuple[bool, str]:
    """
    PDF is optional. We only do it if reportlab is installed.
    If not installed, we return (False, reason).
    """
    try:
        # Lazy import so environments without reportlab still work.
        from reportlab.lib.pagesizes import LETTER  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore

        _safe_mkdir(pdf_path.parent)
        c = canvas.Canvas(str(pdf_path), pagesize=LETTER)
        width, height = LETTER

        # VERY simple PDF: put a warning + point to the HTML, then dump key lines.
        # (We keep it simple to avoid turning PDF layout into a project.)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "Ghost Lantern Labs — Command Brief (PDF)")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 65, "Note: This PDF is a lightweight export. Use the HTML for full fidelity.")
        c.drawString(50, height - 80, f"Generated (UTC): {_utc_now_iso()}")

        # Dump first N lines of stripped HTML text as a quick summary
        text = html_text
        # crude strip tags for summary
        import re

        text = re.sub(r"<[^>]+>", "", text)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        y = height - 110
        c.setFont("Helvetica", 8)
        for ln in lines[:80]:
            if y < 60:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 8)
            c.drawString(50, y, ln[:120])
            y -= 10

        c.save()
        return True, "pdf_exported"
    except ModuleNotFoundError:
        return False, "reportlab_not_installed"
    except Exception as e:
        return False, f"pdf_export_error: {e.__class__.__name__}: {e}"


def export_command_brief(*, title: str = "GLL Command Brief Packet") -> Dict[str, Any]:
    """
    Returns:
      {
        "ok": bool,
        "generated_at_utc": str,
        "paths": {"html_latest":..., "html_stamped":..., "pdf_latest":..., ...},
        "manifest_latest": ...,
        "pdf_status": ...,
        "errors": {...}
      }
    """
    generated_at = _utc_now_iso()
    stamp = _ts()

    _safe_mkdir(BRIEFS_DIR)

    html_latest = BRIEFS_DIR / "command_brief_latest.html"
    html_stamped = BRIEFS_DIR / f"command_brief_{stamp}.html"

    manifest_latest = BRIEFS_DIR / "command_brief_latest.json"
    manifest_stamped = BRIEFS_DIR / f"command_brief_{stamp}.json"

    pdf_latest = BRIEFS_DIR / "command_brief_latest.pdf"
    pdf_stamped = BRIEFS_DIR / f"command_brief_{stamp}.pdf"

    errors: Dict[str, str] = {}

    training_curve, e = _read_json(SRC_TRAINING_CURVE)
    if e:
        errors["training_curve"] = e

    training_feedback, e = _read_json(SRC_TRAINING_FEEDBACK)
    if e:
        errors["training_feedback"] = e

    fusion_validation, e = _read_json(SRC_FUSION_VALIDATION)
    if e:
        errors["fusion_validation"] = e

    degraded_validation, e = _read_json(SRC_DEGRADED_VALIDATION)
    if e:
        errors["degraded_validation"] = e

    sis_txt, e = _read_text(SRC_SIS_REPORT)
    if e:
        errors["sis_report"] = e

    sps_txt, e = _read_text(SRC_SPS_BEHAVIOR_TXT)
    if e:
        errors["sps_behavior"] = e

    notes = [
        "This brief is generated from synthetic + training artifacts (safe for demo).",
        "If SIS/SPS gates are GREEN, sessions can count toward AGI and certification.",
        "PDF export is optional and may be disabled if dependencies are unavailable.",
    ]

    manifest: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "title": title,
        "sources": {
            "training_curve": str(SRC_TRAINING_CURVE),
            "training_feedback": str(SRC_TRAINING_FEEDBACK),
            "fusion_validation": str(SRC_FUSION_VALIDATION),
            "degraded_validation": str(SRC_DEGRADED_VALIDATION),
            "sis_report": str(SRC_SIS_REPORT),
            "sps_behavior": str(SRC_SPS_BEHAVIOR_TXT),
        },
        "included": {
            "training_curve": training_curve is not None,
            "training_feedback": training_feedback is not None,
            "fusion_validation": fusion_validation is not None,
            "degraded_validation": degraded_validation is not None,
            "sis_report": sis_txt is not None,
            "sps_behavior": sps_txt is not None,
        },
        "errors": errors,
    }

    html = _build_html(
        generated_at=generated_at,
        title=title,
        manifest=manifest,
        training_curve=training_curve,
        training_feedback=training_feedback,
        fusion_validation=fusion_validation,
        degraded_validation=degraded_validation,
        sis_txt=sis_txt,
        sps_txt=sps_txt,
        notes=notes,
    )

    html_latest.write_text(html, encoding="utf-8")
    html_stamped.write_text(html, encoding="utf-8")

    manifest_latest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest_stamped.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    pdf_ok_latest, pdf_status_latest = _try_export_pdf_from_html(html, pdf_latest)
    pdf_ok_stamped, pdf_status_stamped = _try_export_pdf_from_html(html, pdf_stamped)

    ok = True  # exporter succeeds even if PDF is skipped
    return {
        "ok": ok,
        "generated_at_utc": generated_at,
        "pdf": {
            "latest_ok": pdf_ok_latest,
            "stamped_ok": pdf_ok_stamped,
            "latest_status": pdf_status_latest,
            "stamped_status": pdf_status_stamped,
        },
        "paths": {
            "html_latest": str(html_latest),
            "html_stamped": str(html_stamped),
            "manifest_latest": str(manifest_latest),
            "manifest_stamped": str(manifest_stamped),
            "pdf_latest": str(pdf_latest),
            "pdf_stamped": str(pdf_stamped),
        },
        "errors": errors,
    }

